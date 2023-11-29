import httpx
from prefect import flow


@flow(log_prints=True)
def get_repo_info(repo_name: str = "PrefectHQ/prefect"):
    url = f"https://api.github.com/repos/{repo_name}"
    response = httpx.get(url)
    response.raise_for_status()
    repo = response.json()
    print(f"{repo_name} repository statistics 🤓:")
    print(f"Stars 🌠 : {repo['stargazers_count']}")
    print(f"Forks 🍴 : {repo['forks_count']}")


if __name__ == "__main__":
    # disini menggunakan method deploy, bukan serve
    get_repo_info.deploy(
        name="my-first-deployment",
        work_pool_name="my-docker-pool",
        image="my-first-deployment-image:tutorial",
        push=False,
    )


"""
Workers and work pools are a bridge between the Prefect orchestration layer and infrastructure for flow runs that can be dynamically provisioned
To transition from persistent infrastructure to dynamic infrastructure, use flow.deploy instead of flow.serve.

Personal Note:
- Cara deployment dengan serve (flow.serve) merupakan persistent infra (tidak scalable)
- Cara deployment dengan worker workpool (flow.deploy) merupakan dynamic infra (scalable)
- Namun kembali lagi tergantung kebutuhan karena dengan serve saja cukup untuk scheduling dan orchestration

Tiga hal penting pada worker & work pool
Deployment - flow yang dikirimkan ke work pool untuk dieksekusi oleh worker
Work Pool - pusat flow
Worker - pekerja yang mengambil flow dari work pool yang kemudian akan mengeksekusinya 

Listener worker type docker tidak dapat di run pada container, karena container docker tidak dapat membuat kontainer lainnnya (perlu orchestration, k8s misalnya)
- Script tersebut tidak dapat dijalankan di dalam container docker, harus dari machine/host langsung
- Script `prefect worker start` akan melisten dari terminal apakah ada permintaan atau tidak
- Jika ada permintaan, maka akan membuat container baru
- Karena pada machine/host dapat membuat docker container secara langsung

Acknowledgement:
- https://docs.prefect.io/latest/tutorial/workers/
"""
