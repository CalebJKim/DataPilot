import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from llm import *
from autogen import ConversableAgent
from prompts import Prompts

warnings.filterwarnings("ignore", category=DeprecationWarning)
from datetime import datetime

project_dir = os.getcwd()

import os
import pandas as pd
import sqlite3
import logging

# Set up logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO)

def fetch_and_process_data():
    # Load the carsalesdata.csv file
    data_path = os.path.join(project_dir, 'data/carsalesdata.csv')
    df = pd.read_csv(data_path)
    logging.info(f"Loaded carsalesdata.csv with {df.shape[0]} rows.")

    # Simulate data cleaning
    df.dropna(inplace=True)  # Example cleaning step
    logging.info("Data cleaned. Dropped NA values.")

    # Save to SQLite database
    conn = sqlite3.connect('data_pipeline.db')
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    conn.close()
    logging.info("Data saved to SQLite database.")

def main():
    api_key = None #os.environ.get("OPENAI_API_KEY")
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
    db_eda_agent = ConversableAgent("db_eda_agent", 
                                        system_message=Prompts.database_EDA_agent_prompt, 
                                        llm_config=llm_config)
    db_eda_agent.register_for_llm(name="db_eda_agent", description="Performs exploratory data analysis on the database and return useful information.")(db_eda_agent)
    db_eda_agent.register_for_execution(name="db_eda_agent")(db_eda_agent)

if __name__ == "__main__":
    main()