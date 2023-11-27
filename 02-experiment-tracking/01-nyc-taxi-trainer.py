import pickle
import warnings

import mlflow
import pandas as pd
import xgboost as xgb
from dotenv import load_dotenv
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import mean_squared_error

warnings.filterwarnings("ignore")

load_dotenv()

mlflow.set_tracking_uri("http://localhost:5000/")
mlflow.set_experiment("nyc-taxi")


def read_dataframe(filename):
    if filename.endswith(".csv"):
        df = pd.read_csv(filename)

        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    elif filename.endswith(".parquet"):
        df = pd.read_parquet(filename)

    df["duration"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)

    return df


def main():
    train_data_path = "./data/green_tripdata_2021-01.parquet"
    val_data_path = "./data/green_tripdata_2021-02.parquet"

    df_train = read_dataframe(train_data_path)
    df_val = read_dataframe(val_data_path)

    df_train["PU_DO"] = df_train["PULocationID"] + "_" + df_train["DOLocationID"]
    df_val["PU_DO"] = df_val["PULocationID"] + "_" + df_val["DOLocationID"]

    categorical = ["PU_DO"]
    numerical = ["trip_distance"]

    dv = DictVectorizer()

    train_dicts = df_train[categorical + numerical].to_dict(orient="records")
    X_train = dv.fit_transform(train_dicts)

    val_dicts = df_val[categorical + numerical].to_dict(orient="records")
    X_val = dv.transform(val_dicts)

    target = "duration"
    y_train = df_train[target].values
    y_val = df_val[target].values

    train = xgb.DMatrix(X_train, label=y_train)
    valid = xgb.DMatrix(X_val, label=y_val)

    best_params = {
        "learning_rate": 0.3214173396011475,
        "max_depth": 92,
        "min_child_weight": 1.604667145599219,
        "objective": "reg:linear",
        "reg_alpha": 0.03537825375271799,
        "reg_lambda": 0.007233385550663513,
        "seed": 42,
    }

    best_model = xgb.train(
        params=best_params,
        dtrain=train,
        num_boost_round=20,
        evals=[(valid, "validation")],
        early_stopping_rounds=25,
    )

    # evaluate model
    y_pred = best_model.predict(valid)
    rmse = mean_squared_error(y_val, y_pred, squared=False)
    mlflow.log_metric("validation-rmse", rmse)

    # log model
    mlflow.xgboost.log_model(best_model, artifact_path="models")

    # log preprocessor artifact
    preprocessor_path = "./models/preprocessor.bin"
    with open(preprocessor_path, "wb") as f_out:
        pickle.dump(dv, f_out)
    mlflow.log_artifact(preprocessor_path, artifact_path="preprocessor")

    # note:
    # jangan pakai autolog, karena rawan bug


if __name__ == "__main__":
    main()
