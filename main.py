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

import os
import sqlite3
import logging

# Set up logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO)

project_dir = os.getcwd()

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
    return bool(data) and not data.empty

def is_sample_size_sufficient(data: Any) -> bool:
    """
    Placeholder function to check if the sample size is sufficient.
    """
    return len(data) >= 10

def evaluate_query_results(data: Any, original_prompt: str, sql_generator_agent: ConversableAgent, llm: LLM) -> None:
    """
    Evaluates query results and determines next actions based on data quality.

    - If data is relevant and useful, calls the data analyst function with the data and original prompt.
    - If data is not relevant or the sample size is too small, prompts Agent 1 for a new SQL query.
    """
    if is_data_relevant(data) and is_sample_size_sufficient(data):
        # Data meets quality criteria - send to analyst
        logging.info("Data is relevant and sufficient. Proceeding to analysis.")
        analyze_data(data, original_prompt)
    else:
        # Data does not meet quality criteria - request new SQL query from Agent 1
        logging.warning("Data is not relevant or insufficient. Reinvoking Agent 1 for a new SQL query.")
        new_prompt = f"""The previous SQL query did not yield relevant or sufficient results.
        Original request: "{original_prompt}"
        Please generate a new SQL query with refined conditions to improve relevance or increase the sample size."""
        
        # Generate a new SQL query using Agent 1
        new_query = llm.generate_sql_query(new_prompt)
        logging.info(f"Generated new SQL query: {new_query}")

        # Execute the new SQL query using Agent 2
        csv_file_path = "datasets/samples.csv"
        new_data = llm.execute_sql_query(new_query, csv_file_path)

        # Re-evaluate the new results
        evaluate_query_results(new_data, original_prompt, sql_generator_agent, llm)

def analyze_data(data: Any, prompt: str) -> None:
    """
    Function call to data analyst with validated data and original prompt.
    """
    logging.info("Sending data to data analyst for further analysis.")
    print("Data is relevant and sufficient. Sending to data analyst.")
    print(f"Prompt: {prompt}")
    print(f"Data: {data}")

def main():
    api_key = None  # os.environ.get("OPENAI_API_KEY")
    llm = LLM(model_name="gemini-1.5-pro-latest")
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
    db_eda_agent = ConversableAgent("db_eda_agent", 
                                    system_message=Prompts.database_EDA_agent_prompt, 
                                    llm_config=llm_config)
    db_eda_agent.register_for_llm(name="db_eda_agent", description="Performs exploratory data analysis on the database and return useful information.")(db_eda_agent)
    db_eda_agent.register_for_execution(name="db_eda_agent")(db_eda_agent)

    # Agentic Workflow
    fetch_and_process_data() # At this point, data should be in a SQLite DB
    eda_response = db_eda_agent.run({"query": "Analyze the 'data_table' table in the SQLite database and provide useful insights.", "db_path": "data.db"})
    

if __name__ == "__main__":
    main()