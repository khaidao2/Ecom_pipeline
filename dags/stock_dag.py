"""
Stock Pipeline - Sample Airflow DAG
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def process_stock_data():
    """Process raw stock data"""
    print("Processing stock data...")
    # Add your processing logic here
    pass

def run_dbt_models():
    """Run dbt models"""
    print("Running dbt models...")
    # Add dbt run command here
    pass

with DAG(
    'stock_pipeline',
    default_args=default_args,
    description='Stock data pipeline',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
    tags=['stock', 'pipeline'],
) as dag:

    # Task 1: Check if market data API is available
    check_api = HttpSensor(
        task_id='check_market_api',
        http_conn_id='market_data_api',
        endpoint='/api/health',
        timeout=30,
        poke_interval=10,
    )

    # Task 2: Ingest raw data
    ingest_data = PythonOperator(
        task_id='ingest_raw_data',
        python_callable=process_stock_data,
    )

    # Task 3: Process with Flink (via Docker)
    process_stream = DockerOperator(
        task_id='flink_stream_processing',
        image='flink:1.18-java11',
        command='jobmanager',
        docker_url='unix://var/run/docker.sock',
        network_mode='stock-pipeline_pipeline-net',
        auto_remove='success',
    )

    # Task 4: Run dbt transformations
    transform_data = PythonOperator(
        task_id='dbt_transform',
        python_callable=run_dbt_models,
    )

    # Task 5: Load to StarRocks
    load_to_warehouse = PythonOperator(
        task_id='load_to_starrocks',
        python_callable=lambda: print("Loading to StarRocks..."),
    )

    # Define task dependencies
    check_api >> ingest_data >> process_stream >> transform_data >> load_to_warehouse
