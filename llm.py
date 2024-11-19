import google.generativeai as genai
import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd
import re
import yaml
import time  # Import time module for tracking

class LLM:
    def __init__(self, model_name="gemini-1.5-pro-latest"):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

        with open('prompts.yaml', 'r') as file:
            self.prompts = yaml.safe_load(file)

    def invoke(self, prompt: str) -> str:
        invoke_start = time.time()
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        invoke_end = time.time()
        print(f"Time to invoke model and generate response: {invoke_end - invoke_start:.4f} seconds")
        return response.text

    def generate_sql_query(self, natural_language_prompt: str) -> str:
        start_time = time.time()

        sql_generation_prompt = self.prompts['system_prompts']['sql_generation_agent']
        formatted_prompt = sql_generation_prompt + natural_language_prompt
        print("Formatted prompt prepared.")

        # Invoke the model
        invoke_start = time.time()
        response = self.invoke(formatted_prompt)
        invoke_end = time.time()
        print(f"Time for invoke in SQL generation: {invoke_end - invoke_start:.4f} seconds")

        # Clean SQL query
        clean_start = time.time()
        formatted_response = self.clean_sql_query(response)
        clean_end = time.time()
        print(f"Time to clean SQL query: {clean_end - clean_start:.4f} seconds")

        total_time = time.time() - start_time
        print(f"Total time for SQL generation: {total_time:.4f} seconds")
        return formatted_response
    
    def execute_sql_query(self, sql_query: str, csv_file: str):
        execution_start = time.time()

        # Read CSV
        read_start = time.time()
        df = pd.read_csv(csv_file)
        read_end = time.time()
        print(f"Time to read CSV file: {read_end - read_start:.4f} seconds")

        # Execute SQL query in SQLite
        with sqlite3.connect(':memory:') as conn:
            df.to_sql('transactions', conn, index=False, if_exists='replace')
            try:
                sql_start = time.time()
                results = pd.read_sql_query(sql_query, conn)
                sql_end = time.time()
                print(f"Time to execute SQL query: {sql_end - sql_start:.4f} seconds")
                return results
            except Exception as e:
                print(f"Query Execution Error: {e}")
                return f"Query Execution Error: {e}"
        execution_end = time.time()
        print(f"Total time for SQL query execution: {execution_end - execution_start:.4f} seconds")
    
    @staticmethod
    def clean_sql_query(query: str) -> str:
        """
        Cleans the LLM response to extract only the SQL query.
        Removes backticks and extraneous characters.
        """
        query = re.sub(r'[`]', '', query)
        query = query.strip()

        sql_start = re.search(r"(SELECT|INSERT|UPDATE|DELETE)\b", query, re.IGNORECASE)
        if sql_start:
            query = query[sql_start.start():]

        sql_end = query.find(';')
        if sql_end != -1:
            query = query[:sql_end + 1]

        return query

if __name__ == "__main__":
    llm = LLM()

    raw_query = """
                Retrieve all transactions of type "TRANSFER" and "CASH_OUT" where the transaction amount is above 100. 
                Include columns for the step, type, amount, origin account balance before (oldbalanceOrg) and after (newbalanceOrig) the transaction, 
                and the destination account balance before and after the transaction. 
                Sort the results by transaction amount in descending order.
                """

    start_time = time.time()
    print("Starting SQL query generation and execution pipeline.")

    # Generate SQL Query
    query_generation_start = time.time()
    query = llm.generate_sql_query(raw_query)
    query_generation_end = time.time()
    print(f"Time to generate SQL query: {query_generation_end - query_generation_start:.4f} seconds")

    # Execute SQL Query
    execution_start = time.time()
    csv_file_path = "datasets/samples.csv"
    result = llm.execute_sql_query(query, csv_file_path)
    execution_end = time.time()
    print(f"Time to execute SQL query and process results: {execution_end - execution_start:.4f} seconds")

    # Print Results
    print(result.to_dict(orient="records"))
    print(result)

    end_time = time.time()
    print(f"Total time for script execution: {end_time - start_time:.4f} seconds")
