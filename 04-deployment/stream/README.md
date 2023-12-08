## Machine Learning for Streaming

* Scenario
* Creating the role 
* Create a Lambda function, test it
* Create a Kinesis stream
* Connect the function to the stream
* Send the records 

Links

* [Tutorial: Using Amazon Lambda with Amazon Kinesis](https://docs.amazonaws.cn/en_us/lambda/latest/dg/with-kinesis-example.html)

## Code snippets

### Sending data


```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data "Hello, this is a test."
```

Decoding base64

```python
base64.b64decode(data_encoded).decode('utf-8')
```

Record example

```json
{
    "ride": {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    }, 
    "ride_id": 123
}
```

Sending this record

```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data '{
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66
        }, 
        "ride_id": 156
    }'
```

### Test event


```json
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49630081666084879290581185630324770398608704880802529282",
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ==",
                "approximateArrivalTimestamp": 1654161514.132
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49630081666084879290581185630324770398608704880802529282",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::XXXXXXXXX:role/lambda-kinesis-role",
            "awsRegion": "eu-west-1",
            "eventSourceARN": "arn:aws:kinesis:eu-west-1:XXXXXXXXX:stream/ride_events"
        }
    ]
}
```

### Reading from the stream

```bash
KINESIS_STREAM_OUTPUT='ride_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode | jq
``` 


### Running the test

```bash
export PREDICTIONS_STREAM_NAME="ride_predictions"
export RUN_ID="af26d9773a70453eb64af49b73d61501"
export TEST_RUN="True"

python test.py
```

### Putting everything to Docker

```bash
docker build -t stream-model-duration:v1 .

docker run -it --rm \
    -p 6969:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="af26d9773a70453eb64af49b73d61501" \
    -e TEST_RUN="True" \
    -e AWS_DEFAULT_REGION="ap-southeast-1" \
    stream-model-duration:v1
```

URL for testing:

* http://localhost:6969/2015-03-31/functions/function/invocations



### Configuring AWS CLI to run in Docker

To use AWS CLI, you may need to set the env variables:

```bash
docker run -it --rm \
    -p 6969:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="af26d9773a70453eb64af49b73d61501" \
    -e TEST_RUN="True" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    stream-model-duration:v1
```

Alternatively, you can mount the `.aws` folder with your credentials to the `.aws` folder in the container:

```bash
docker run -it --rm \
    -p 6969:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="af26d9773a70453eb64af49b73d61501" \
    -e TEST_RUN="True" \
    -v ~/.aws:/root/.aws \
    stream-model-duration:v1
```

### Publishing Docker images

Creating an ECR repo

```bash
aws ecr create-repository --repository-name duration-model
```

Logging in

```bash
$(aws ecr get-login --no-include-email)
```

Pushing 

```bash
REMOTE_URI="922880748478.dkr.ecr.ap-southeast-1.amazonaws.com/duration-model"
REMOTE_TAG="v2"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="stream-model-duration:v2"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```

>PS: Sebenarnya ada banyak cara deploy service (terutama yang sudah di-dockerize) di AWS. Bisa menggunakan Serverless Lambda atau pake VPC EC2.

## Personal Note

Tahapan dalam praktek ini:
* Membuat roles untuk lambda agar mendapat akses kinesis dan s3 (mlflow model registry)
* Pembuatan image serverless function:
  * Membuat pipenv dengan depedencies boto3, mlflow, dan scikit-learn
  * Membuat lambda serverless function (file `lambda_function.py`)
  * Wrap semuanya pada Dockerfile (cari image lambda python dulu di Amazon ECR)
  * Build image di local dan push ke ECR
* Pengaturan pada AWS:
  * Membuat stream kinesis baru yaitu `ride_events` dan `ride_predictions`
  * Buat lambda function baru dan ambil image ecr yang telah dipush sebelumnya
  * Tambahkan trigger pada lambda tersebut dengan kinesis stream `ride_events`
  * Test dengan sample data
``` json
  {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49647060812288014558888668248268683467178536947444350978",
                # base64 encoded data
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDE1NgogICAgfQ==",
                "approximateArrivalTimestamp": 1701761035.582
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49647060812288014558888668248268683467178536947444350978",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::922880748478:role/lambda-kinesis-role",
            "awsRegion": "ap-southeast-1",
            "eventSourceARN": "arn:aws:kinesis:ap-southeast-1:922880748478:stream/ride_events"
        }
    ]
}
  
```

* Error handling:
  * Cek akses pada user, roles, atau policies apakah ada yang belum ditambahkan
  * Tambah memori pada lambda function jika ada error timeout atau out of memory