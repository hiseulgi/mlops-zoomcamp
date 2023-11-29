from datetime import timedelta

import httpx
from prefect import flow, get_run_logger, task
from prefect.tasks import task_input_hash


# menambah caching pada task, dimana kita dapat menyimpan result dari task pada cache dan dapat memanggilnya lagi berikutnya dengan cepat
@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
)
def get_url(url: str, params: dict = None):
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()


# subflow, untuk memudahkan tracking
@flow
def get_open_issues(repo_name: str, open_issues_count: int, per_page: int = 100):
    issues = []
    pages = range(1, -(open_issues_count // -per_page) + 1)
    for page in pages:
        issues.append(
            # concurrency execution
            # dengan memanggil task dengan method submit, kita dapat mengubah eksekusinya dari sekuential ke konkuren
            get_url.submit(
                f"https://api.github.com/repos/{repo_name}/issues",
                params={"page": page, "per_page": per_page, "state": "open"},
            )
        )

    # dan untuk mengambil nilainya, kita perlu method result
    return [i for p in issues for i in p.result()]


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def get_repo_info(repo_name: str = "PrefectHQ/prefect"):
    url = f"https://api.github.com/repos/{repo_name}"
    repo_stats = get_url(url)
    issues = get_open_issues(repo_name, repo_stats["open_issues_count"])
    issues_per_user = len(issues) / len(set([i["user"]["id"] for i in issues]))

    print(f"{repo_name} repository statistics 🤓:")
    print(f"Stars 🌠 : {repo_stats['stargazers_count']}")
    print(f"Forks 🍴 : {repo_stats['forks_count']}")
    print(f"Average open issues per user 💌 : {issues_per_user:.2f}")


if __name__ == "__main__":
    # run flow (langsung tereksekusi pada terminalnya)
    # get_repo_info()

    # deploy flow
    # ketika bagian ini tereksekusi, maka ia akan me-listen permintaan run atau scheduling yang telah diatur
    # bersifat blocking pada terminal ia di-run, dan me-listen secara async
    get_repo_info.serve(
        name="my-first-deployment",
        cron="* * * * *",
        tags=["testing", "tutorial"],
        description="Given a GitHub repository, logs repository statistics for that repo.",
        version="tutorial/deployments",
    )

    pass

"""
Personal Note:
Deploying a flow is the act of specifying when, where, and how it will run.
Dengan deployment kita dapat memanggil flow kita melalui API ataupun UI serta dapat mengatur scheduling, event-based trigerring.

Kita juga dapat melakukan pada deployment pada docker, ya intinya kita run script di atas di dalam container. lengkapnya di https://docs.prefect.io/guides/docker/ (ini bukan worker ya konsepnya, tapi serve)

Jadi secara umum ada dua paradigma dalam menjalankan flow, yaitu serve (seperti diatas) dan worker approaches (seperti pada mlops-zoomcamp). lengkapnya di https://docs.prefect.io/concepts/deployments/#two-approaches-to-deployments
"""
