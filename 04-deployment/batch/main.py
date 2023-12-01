#!/usr/bin/env python
# coding: utf-8

import os
import sys
import uuid
from datetime import datetime

import mlflow
import pandas as pd
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from prefect import flow, get_run_logger, task
from prefect.context import get_run_context

load_dotenv()

KEY = os.environ["AWS_ACCESS_KEY_ID"]
SECRET = os.environ["AWS_SECRET_ACCESS_KEY"]
ENDPOINT_URL = os.environ["MLFLOW_S3_ENDPOINT_URL"]

STORAGE_SETTING = {
    "key": KEY,
    "secret": SECRET,
    "client_kwargs": {"endpoint_url": ENDPOINT_URL},
}


def generate_uuids(n):
    ride_ids = []
    for i in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids


def read_dataframe(filename: str):
    df = pd.read_parquet(filename, storage_options=STORAGE_SETTING)

    df["duration"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    df["ride_id"] = generate_uuids(len(df))

    return df


def prepare_dictionaries(df: pd.DataFrame):
    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)

    df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]

    categorical = ["PU_DO"]
    numerical = ["trip_distance"]
    dicts = df[categorical + numerical].to_dict(orient="records")
    return dicts


def load_model(run_id):
    logged_model = f"s3://mlflow/1/{run_id}/artifacts/model"
    model = mlflow.pyfunc.load_model(logged_model)
    return model


def save_results(df, y_pred, run_id, output_file):
    df_result = pd.DataFrame()
    df_result["ride_id"] = df["ride_id"]
    df_result["lpep_pickup_datetime"] = df["lpep_pickup_datetime"]
    df_result["PULocationID"] = df["PULocationID"]
    df_result["DOLocationID"] = df["DOLocationID"]
    df_result["actual_duration"] = df["duration"]
    df_result["predicted_duration"] = y_pred
    df_result["diff"] = df_result["actual_duration"] - df_result["predicted_duration"]
    df_result["model_version"] = run_id

    df_result.to_parquet(output_file, index=False, storage_options=STORAGE_SETTING)


def get_paths(run_date, taxi_type, run_id):
    prev_month = run_date - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month

    input_file = (
        f"s3://nyc-taxi/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet"
    )
    output_file = f"s3://nyc-taxi/prediction/{taxi_type}_tripdata_{year:04d}-{month:02d}-{run_id}.parquet"

    return input_file, output_file


@task
def apply_model(input_file, run_id, output_file):
    logger = get_run_logger()

    logger.info(f"reading the data from {input_file}...")
    df = read_dataframe(input_file)
    dicts = prepare_dictionaries(df)

    logger.info(f"loading the model with RUN_ID={run_id}...")
    model = load_model(run_id)

    logger.info(f"applying the model...")
    y_pred = model.predict(dicts)

    logger.info(f"saving the result to {output_file}...")

    save_results(df, y_pred, run_id, output_file)
    return output_file


@flow
def ride_duration_prediction(taxi_type: str, run_id: str, run_date: datetime = None):
    if run_date is None:
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time

    input_file, output_file = get_paths(run_date, taxi_type, run_id)

    apply_model(input_file=input_file, run_id=run_id, output_file=output_file)


def run():
    taxi_type = sys.argv[1]  # 'green'
    year = int(sys.argv[2])  # 2021
    month = int(sys.argv[3])  # 3

    run_id = sys.argv[4]  # 'af26d9773a70453eb64af49b73d61501'

    ride_duration_prediction(
        taxi_type=taxi_type,
        run_id=run_id,
        run_date=datetime(year=year, month=month, day=1),
    )


if __name__ == "__main__":
    run()

"""
Konsep batch prediction ini adalah kita menunggu datanya terkumpul terlebih dahulu baru dipredict dan hasilnya juga banyak.

Misalkan untuk data bulanan maka prediksi akan dischedule selama satu bulan sekali.

Sangat pusing pake prefect, karena susah kalo integrasi di local (komunikasi antar service pada docker container), dokumentasi juga minim atau skill issue?
"""
