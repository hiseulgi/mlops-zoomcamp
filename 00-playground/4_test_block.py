from prefect.filesystems import RemoteFileSystem

minio_block = RemoteFileSystem.load("mlops-zoomcamp")

# download a file from minio to local
minio_block.get_directory(from_path="data", local_path="new_data")
