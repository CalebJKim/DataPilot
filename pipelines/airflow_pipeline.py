from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pandas as pd

def fetch_data():
    data = {
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['New York', 'Los Angeles', 'Chicago']
    }
    df = pd.DataFrame(data)
    df.to_csv('/tmp/fetched_data.csv', index=False)
    print("Data fetched and saved to /tmp/fetched_data.csv")
    print(df)

def print_data():
    df = pd.read_csv('/tmp/fetched_data.csv')
    print("Data from CSV:")
    print(df)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG('simple_data_pipeline', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:

    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data
    )

    print_data_task = PythonOperator(
        task_id='print_data',
        python_callable=print_data
    )

    fetch_data_task >> print_data_task
