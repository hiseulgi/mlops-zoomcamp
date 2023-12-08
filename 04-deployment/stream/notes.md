## AWS Kinesis Response

```
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49647060812288014558888668248263847763900017820167045122",
                # base64 encoded data
                "data": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0Lg==",
                "approximateArrivalTimestamp": 1701760153.593
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49647060812288014558888668248263847763900017820167045122",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::922880748478:role/lambda-kinesis-role",
            "awsRegion": "ap-southeast-1",
            "eventSourceARN": "arn:aws:kinesis:ap-southeast-1:922880748478:stream/ride_events"
        }
    ]
}
```

```
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