FROM apache/airflow:2.9.3-python3.11

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir \
        dbt-core==1.8.2 \
        dbt-postgres==1.8.2

ENV PYTHONPATH=/opt/airflow/project