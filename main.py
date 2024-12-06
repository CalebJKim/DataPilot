import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import warnings
import sklearn
from llm import *

warnings.filterwarnings("ignore", category=DeprecationWarning)
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score

from xgboost import XGBClassifier
from xgboost import plot_importance
from sklearn.preprocessing import LabelEncoder

import kagglehub

project_dir = os.getcwd()

import os
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import sqlite3
import logging

# Set up logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO)

def fetch_data():
    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()

    # Define dataset and download path
    dataset = "ealaxi/paysim1"
    download_path = "./data"

    # Download dataset
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    api.dataset_download_files(dataset, path=download_path, unzip=True)

    logging.info("Dataset downloaded and unzipped.")

def process_data():
    # List all files in the data folder
    data_folder = './data'
    files = os.listdir(data_folder)
    
    # Check if there are any files and read the first one
    if files:
        first_file = files[0]
        df = pd.read_csv(os.path.join(data_folder, first_file))
        logging.info(f"Loaded dataset from {first_file} with {df.shape[0]} rows.")
    else:
        logging.warning("No files found in the data folder.")

    # Simulate data cleaning
    df.dropna(inplace=True)  # Example cleaning step
    logging.info("Data cleaned. Dropped NA values.")

    # Save to SQLite database
    conn = sqlite3.connect('data_pipeline.db')
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    conn.close()
    logging.info("Data saved to SQLite database.")

# Simulate the data ingestion process
fetch_data()
process_data()

# Apache Airflow DAG simulation


def airflow_fetch_data():
    fetch_data()

def airflow_process_data():
    process_data()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

dag = DAG('data_ingestion_dag', default_args=default_args, schedule_interval='@daily')

fetch_data_task = PythonOperator(
    task_id='fetch_data',
    python_callable=airflow_fetch_data,
    dag=dag,
)

process_data_task = PythonOperator(
    task_id='process_data',
    python_callable=airflow_process_data,
    dag=dag,
)

fetch_data_task >> process_data_task  # Set task dependencies
