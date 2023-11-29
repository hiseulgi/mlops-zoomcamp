from prefect.filesystems import RemoteFileSystem

minio_block = RemoteFileSystem(
    basepath="s3://mlops-zoomcamp",
    settings={
        "key": "NrSKGyspQzXnR6VKpXk3",
        "secret": "x75gGhGvuCuAiTyKGK8tdwJoyLTXVAUX8N13QNKG",
        "client_kwargs": {"endpoint_url": "http://localhost:9000"},
    },
)
minio_block.save("mlops-zoomcamp")
