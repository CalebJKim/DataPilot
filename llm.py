import google.generativeai as genai
import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd
import re
import yaml

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
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

    def generate_sql_query(self, natural_language_prompt: str) -> str:
        sql_generation_prompt = self.prompts['system_prompts']['sql_generation_agent']
        formatted_prompt = sql_generation_prompt + natural_language_prompt
        response = self.invoke(formatted_prompt)
        formatted_response = self.clean_sql_query(response)
        print(formatted_response)
        return formatted_response
    
    def execute_sql_query(self, sql_query: str, csv_file: str):
        df = pd.read_csv(csv_file)
        with sqlite3.connect(':memory:') as conn:
            df.to_sql('transactions', conn, index=False, if_exists='replace')
            try:
                results = pd.read_sql_query(sql_query, conn)
                return results
            except Exception as e:
                return f"Query Execution Error: {e}"
    
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
    
    query = llm.generate_sql_query(raw_query)
    
    csv_file_path = "datasets/samples.csv"
    result = llm.execute_sql_query(query, csv_file_path)
    print(result.to_dict(orient="records"))

    print(result)