import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import sys
import os
from llm import *
from autogen import ConversableAgent
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from prompts import Prompts
from typing import Dict, Any
from webagent import summarize_online_and_review_data
# from webAgent import main as web_agent_main

#from dataframe_analyzer import is_data_relevant, is_sample_size_sufficient

warnings.filterwarnings("ignore", category=DeprecationWarning)
from datetime import datetime

import os
import sqlite3
import logging
import visualization_executor

# Set up logging
logging.basicConfig(filename="pipeline.log", level=logging.INFO)

project_dir = os.getcwd()

def query_database(db_path: str, query: str) -> pd.DataFrame:
    """
    Executes an SQL query on the given SQLite database and returns the results as a DataFrame.
    """
    conn = sqlite3.connect(db_path)
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

def fetch_and_process_data(csv_path):
    # Load the carsalesdata.csv file
    df = pd.read_csv(csv_path)
    logging.info(f"Loaded carsalesdata.csv with {df.shape[0]} rows.")

    # Simulate data cleaning
    df.dropna(inplace=True)  # Example cleaning step
    logging.info("Data cleaned. Dropped NA values.")

    # Save to SQLite database
    conn = sqlite3.connect('data/sqlite_db/data.db')
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

# def evaluate_query_results(data: Any, original_prompt: str, sql_generator_agent: ConversableAgent, llm: LLM) -> None:
#     """
#     Evaluates query results and determines next actions based on data quality.

#     - If data is relevant and useful, calls the data analyst function with the data and original prompt.
#     - If data is not relevant or the sample size is too small, prompts Agent 1 for a new SQL query.
#     """
#     if is_data_relevant(data) and is_sample_size_sufficient(data):
#         # Data meets quality criteria - send to analyst
#         logging.info("Data is relevant and sufficient. Proceeding to analysis.")
#         analyze_data(data, original_prompt)
#     else:
#         # Data does not meet quality criteria - request new SQL query from Agent 1
#         logging.warning("Data is not relevant or insufficient. Reinvoking Agent 1 for a new SQL query.")
#         new_prompt = f"""The previous SQL query did not yield relevant or sufficient results.
#         Original request: "{original_prompt}"
#         Please generate a new SQL query with refined conditions to improve relevance or increase the sample size."""
        
#         # Generate a new SQL query using Agent 1
#         new_query = llm.generate_sql_query(new_prompt)
#         logging.info(f"Generated new SQL query: {new_query}")

#         # Execute the new SQL query using Agent 2
#         csv_file_path = "datasets/samples.csv"
#         new_data = llm.execute_sql_query(new_query, csv_file_path)

#         # Re-evaluate the new results
#         evaluate_query_results(new_data, original_prompt, sql_generator_agent, llm)

def analyze_data(data: Any, prompt: str) -> None:
    """
    Function call to data analyst with validated data and original prompt.
    """
    logging.info("Sending data to data analyst for further analysis.")
    print("Data is relevant and sufficient. Sending to data analyst.")
    print(f"Prompt: {prompt}")
    print(f"Data: {data}")

def main(user_query):
    api_key = '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'
    llm = LLM()
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}

    evaluation_agent = ConversableAgent("data_eval_agent",
                                        system_message=Prompts.evaluation,
                                        llm_config=llm_config)
    evaluation_agent.register_for_llm(name="data_eval_agent", description="Evaluates data and gauges whether it is good enough or not for use in answering prompt.")
    evaluation_agent.register_for_execution(name="data_eval_agent")


    # agent 0a in diagram
    db_eda_agent = ConversableAgent("db_eda_agent", 
                                    system_message=Prompts.database_EDA_agent_prompt, 
                                    llm_config=llm_config)
    db_eda_agent.register_for_llm(name="db_eda_agent", description="Performs exploratory data analysis on the database and return useful information.")
    db_eda_agent.register_for_execution(name="db_eda_agent")

    # agent 0b in diagram
    metric_agent = ConversableAgent("metric_agent", 
                                    system_message=Prompts.metric_agent_prompt, 
                                    llm_config=llm_config)
    metric_agent.register_for_llm(name="metric_agent", description="Combines EDA with dealership-specific frameworks to provide metrics to look at")
    metric_agent.register_for_execution(name="metric_agent")
    

   # RAG Agent
    

    # Get all file paths in the 'Frameworks' directory; to setup RAG
    frameworks_dir = 'Frameworks'
    docs_paths = [os.path.join(frameworks_dir, file) for file in os.listdir(frameworks_dir) if os.path.isfile(os.path.join(frameworks_dir, file))]

    # retrieve_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
    
    # # agent 0b with rag
    # ragproxyagent = RetrieveUserProxyAgent(
    #     #         name="ragproxyagent",
    #     system_message=Prompts.RAG_agent_prompt,
    #     # retrieve_config = {
    #     #     "task":"qa",
    #     #     "docs_path":docs_paths
    #     # })
    #     name="RAG Proxy Agent",
    #     is_termination_msg=None,  # Assuming termination_msg is defined elsewhere
    #     # system_message="Running RAG agent who has extra content retrieval power for solving difficult problems.",
    
    #     human_input_mode="NEVER",
    #     max_consecutive_auto_reply=3,
    #     retrieve_config={
    #         "task": "qa",
    #         "model" : "gpt-4o-mini",
    #         "docs_path": docs_paths
    #     },
    #     code_execution_config=False
    # )
    
    # ragproxyagent.register_for_llm(name="ragproxyagent")
    # ragproxyagent.register_for_execution(name="ragproxyagent")




    # agent 3 in diagram
    data_analyst_agent = ConversableAgent("data_analyst_agent", 
                                    system_message=Prompts.data_analyst_agent_prompt, 
                                    llm_config=llm_config)
    data_analyst_agent.register_for_llm(name="data_analyst_agent", description="Performs data analysis on the SQL query results and web sentiment data and return useful information.")
    # data_analyst_agent.register_for_execution(name="data_analyst_agent")

    



    # agent 4 in diagram
    visualization_agent = ConversableAgent("visualization_agent", 
                                    system_message=Prompts.visualization_agent_prompt, 
                                    llm_config=llm_config)
    visualization_agent.register_for_llm(name="visualization_agent", description="Performs data visualization on the SQL query results and web sentiment data and return useful information.")
    visualization_agent.register_for_execution(name="visualization_agent")

 

    # Agentic Workflow
    csv_path = 'data/raw/carsalesdata.csv'
    db_path = 'data/sqlite_db/data.db'
    fetch_and_process_data(csv_path)

    data_sample = query_database(db_path, "SELECT * FROM transactions LIMIT 20;").to_string(index=False)

    print(f"EDA Agent will analyze {db_path} in context of {user_query}")
    eda_response = db_eda_agent.generate_reply(
        messages=[
            {"role": "user", "content": f"Analyze the database at {db_path} based on this query: {user_query}. Here is a sample of the data:\n{data_sample}\n"}
        ]
    )
    print("Agent Response:\n", eda_response)


    # Using EDA response, use RAG Agent to find metrics that could be interesting to look at

    print(f"The metric agent is now analyzing the previous EDA response")

    # metric_response = ragproxyagent.generate_reply(
    #     messages=[
    #         {"role": "user", "content": f"Analyze the response given here, and pay attention to the schema of the database: {eda_response}. Using your knowledge from documents passed in, return 7-8 metrics that would be worthwhile to look more into. Provide explanations for each one."}
    #     ]
    # )


    # Function to read all .txt files in the frameworks folder and return their contents as strings
    # def read_frameworks_as_strings(directory_path):
    #     frameworks_content = {}
    #     for filename in os.listdir(directory_path):
    #         if filename.endswith('.txt'):
    #             file_path = os.path.join(directory_path, filename)
    #             with open(file_path, 'r') as file:
    #                 content = file.read()
    #                 frameworks_content[filename] = content
    #     return frameworks_content

    # # Path to the frameworks folder
    # frameworks_folder_path = 'Frameworks'

    # # Read the .txt files and store their contents
    # frameworks_data = read_frameworks_as_strings(frameworks_folder_path)

    # # Convert the contents into f-strings for easy parsing
    # frameworks_fstrings = {name: f"{content}" for name, content in frameworks_data.items()}
    # metric_response = metric_agent.generate_reply(
    #     messages=[
    #         {"role": "user", "content": f"Based on this query: {eda_response}, and these sources: {frameworks_fstrings}, analyze potential metrics that would be useful for {user_query}"}
    #     ]
    # )

    # print("Metric/RAG Response", metric_response)

    # use counter avoid inf loop
    count = 0
    while True:
        count += 1
        # Generate SQL query
        sql_query = llm.generate_sql_query(eda_response, user_query)
        print(f"SQL Query Generated: \n {sql_query}")

        sql_result = llm.execute_sql_query(sql_query, csv_path)
        if isinstance(sql_result, pd.DataFrame):
            print(f"SQL Query executed successfully: {sql_result}")
        result_satisfactory = evaluation_agent.generate_reply(messages=[
            {"role": "user", "content": f"Does the SQL data output: {sql_result} contain enough data to help us answer the user's query: {user_query}? Be lenient :)\n"}
        ])
        if "continue" in result_satisfactory or count == 3:
            print("Data retrieved from the database is satisfactory. Advancing to analysis.")
            break
        elif "redo" in result_satisfactory:
            print("Data received from querying database is not relevant or enough to answer prompt. Regenerating a new query.")
            continue


    #Add call to web scraper agent
    web_sentiments = []


    #(TODO: adjust analysis/visualization agents to take correct types, assuming df and array right now.)
    #Logic for data analyst agent

    # web_summary = summarize_online_and_review_data(user_query)
    # print(web_summary)

    analysis_response = data_analyst_agent.generate_reply(
        messages=[
            {
                "role": "user",
                "content": f"Analyze the SQL query results and web sentiments based on this query: {user_query}. "
                        f"SQL Results: {sql_result.to_string(index=False)}\n"
                        f"Web Sentiments: {web_sentiments}\n"
            }
        ]
    )
    print("Data Analyst Agent Response:\n", analysis_response)

    #Logic for visualization agent 
    print(f"Visualization Agent now generating code...")
    visualization_code = visualization_agent.generate_reply(
        messages=[
            {
                "role": "user",
                "content": f"Generate visualization code for the SQL query results and web sentiments based on this query: {user_query}. "
                           f"SQL Results: {sql_result.to_string(index=False)}\n"
                           f"Web Sentiments: {web_sentiments}\n"
            }
        ]
    )

    # Execute the generated visualization code
    visualizations = visualization_executor.execute_visualization_code(visualization_code, sql_result, web_sentiments)
    
    # Return both analysis and visualizations
    return {
        "analysis": analysis_response,
        "visualizations": visualizations
    }



if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some car when executing main."
    main(sys.argv[1])