from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "data-engineering",
    "retries": 1,
}


DBT_PROJECT_DIR = "/opt/airflow/project/dbt"
DBT_LOG_PATH = "/tmp/dbt_logs"
DBT_TARGET_PATH = "/tmp/dbt_target"


with DAG(
    dag_id="ecommerce_data_pipeline",
    description="End-to-end ecommerce data pipeline: ingestion, dbt run, dbt tests and dbt docs",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["ecommerce", "postgres", "dbt"],
) as dag:

    ingest_raw_data = BashOperator(
        task_id="ingest_raw_data",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m ingestion.pipelines.run_all_ingestion"
        ),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"mkdir -p {DBT_LOG_PATH} {DBT_TARGET_PATH} && "
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run "
            f"--profiles-dir . "
            f"--log-path {DBT_LOG_PATH} "
            f"--target-path {DBT_TARGET_PATH}"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"mkdir -p {DBT_LOG_PATH} {DBT_TARGET_PATH} && "
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt test "
            f"--profiles-dir . "
            f"--log-path {DBT_LOG_PATH} "
            f"--target-path {DBT_TARGET_PATH}"
        ),
    )

    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            f"mkdir -p {DBT_LOG_PATH} {DBT_TARGET_PATH} && "
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt docs generate "
            f"--profiles-dir . "
            f"--log-path {DBT_LOG_PATH} "
            f"--target-path {DBT_TARGET_PATH}"
        ),
    )

    ingest_raw_data >> dbt_run >> dbt_test >> dbt_docs_generate