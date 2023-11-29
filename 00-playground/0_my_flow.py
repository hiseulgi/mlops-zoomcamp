import httpx
from prefect import flow, task


@task(retries=2)
def get_repo_info(repo_owner: str, repo_name: str):
    """Get info about a repo - will retry twice after failing"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    api_response = httpx.get(url)
    api_response.raise_for_status()
    repo_info = api_response.json()
    return repo_info


@task
def get_contributors(repo_info: dict):
    contributors_url = repo_info["contributors_url"]
    response = httpx.get(contributors_url)
    response.raise_for_status()
    contributors = response.json()
    return contributors


@flow(name="Repo Info", log_prints=True)
def repo_info(repo_owner: str = "PrefectHQ", repo_name: str = "prefect"):
    """
    Given a GitHub repository, logs the number of stargazers
    and contributors for that repo.
    """
    repo_info = get_repo_info(repo_owner, repo_name)
    print(f"Stars 🌠 : {repo_info['stargazers_count']}")

    contributors = get_contributors(repo_info)
    print(f"Number of contributors 👷: {len(contributors)}")


if __name__ == "__main__":
    # create your first deployment
    # repo_info.serve(name="my-first-deployment")

    # create your first scheduled deployment
    # repo_info.serve(name="my-first-deployment", cron="0 0 * * *")

    pass

"""
Personal note:
Ini adalah basic dari prefect dimana kita membuat kode python sesuai aturan prefect kemudian pada main kita memanggil method serve pada flow yang telah kita buat.
Ketika di run, maka kode ini akan me-listen menunggu perintah run baik secara langsung maupun yang terjadwal.

Ps: Jadi berbeda yang ada pada mlops-zoomcamp, dimana ia membuat worker sendiri, dan kode flow sendiri. Yang mana kode flow akan dikirimkan ke worker untuk diproses.

Ref: https://docs.prefect.io/latest/getting-started/quickstart/
"""
