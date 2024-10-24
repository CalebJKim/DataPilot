import google.generativeai as genai
import os
from dotenv import load_dotenv
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
        return self.invoke(formatted_prompt)

if __name__ == "__main__":
    llm = LLM()
    print(llm.generate_sql_query("""
                                 Retrieve all data from only the past month in the salaries table, sorted in descending order by total income. 
                                 Break ties by base income value.
                                 """))