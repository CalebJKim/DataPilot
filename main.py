import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from llm import *
from autogen import ConversableAgent
from prompts import Prompts
from typing import Dict, Any
from dataframe_analyzer import is_data_relevant, is_sample_size_sufficient

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

def is_data_relevant(data: Any) -> bool:
    """
    Placeholder function to check if the data is relevant.
    """
    # Implement your logic to determine data relevance
    return bool(data)  # Example: Returns True if data is not empty

def is_sample_size_sufficient(data: Any) -> bool:
    """
    Placeholder function to check if the sample size is sufficient.
    """
    # Implement your logic to check sample size
    return len(data) >= 10  # Example: Sample size is sufficient if >= 10 rows

def evaluate_query_results(data: Any, original_prompt: str, sql_generator_agent: ConversableAgent) -> None:
    """
    Evaluates query results and determines next actions based on data quality.

    - If data is relevant and useful, calls the data analyst function with the data and original prompt.
    - If data is not relevant or the sample size is too small, prompts Agent 1 for a new SQL query.
    """
    if is_data_relevant(data) and is_sample_size_sufficient(data):
        # Data meets quality criteria - send to analyst
        analyze_data(data, original_prompt)
    else:
        # Data does not meet quality criteria - request new SQL query from Agent 1
        new_prompt = f"""The previous SQL query did not yield relevant or sufficient results.
        Original request: "{original_prompt}"
        Please generate a new SQL query with refined conditions to improve relevance or increase the sample size."""
        sql_generator_agent.initiate_chat(new_prompt)

def analyze_data(data: Any, prompt: str) -> None:
    """
    Function call to data analyst with validated data and original prompt.
    """
    # Simulate sending data to a data analyst
    print("Data is relevant and sufficient. Sending to data analyst.")
    print(f"Prompt: {prompt}")
    print(f"Data: {data}")

def main():
    api_key = None #os.environ.get("OPENAI_API_KEY")
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
    glide_analysis_agent = ConversableAgent("glide_analysis_agent", 
                                        system_message=Prompts.database_EDA_agent_prompt, 
                                        llm_config=llm_config)
    glide_analysis_agent.register_for_llm(name="glide_analysis_agent", description="Analyzes how the pilot maintains best glide speed.")(glide_analysis_agent)
    glide_analysis_agent.register_for_execution(name="glide_analysis_agent")(glide_analysis_agent)

if __name__ == "__main__":
    main()