from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import LLM
import traceback
import time  # Import time module for tracking
from main import main

app = Flask(__name__)
CORS(app)
llm = LLM()
csv_file_path = "datasets/samples.csv"

@app.route("/api/generate-report", methods=["POST"])
def generate_report():
    try:
        data = request.get_json()
        user_query = data.get("query")

        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        # Call the main function to process the query and generate the report
        report = main(user_query)

        return jsonify(report)
    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error in generate_report:", error_trace)
        return jsonify({"error": str(e), "trace": error_trace}), 500


@app.route("/api/llm-query", methods=["POST"])
def query_llm():
    start_time = time.time()  # Start time for the endpoint
    data = request.get_json()
    prompt = data.get("message")

    if not prompt:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Time tracking for generating SQL query
        sql_start_time = time.time()
        sql_query = llm.generate_sql_query(prompt)
        sql_end_time = time.time()
        sql_duration = sql_end_time - sql_start_time
        print(f"Time to generate SQL query: {sql_duration:.4f} seconds")

        # Time tracking for executing SQL query
        exec_start_time = time.time()
        response_text = llm.execute_sql_query(sql_query=sql_query, csv_file=csv_file_path)
        exec_end_time = time.time()
        exec_duration = exec_end_time - exec_start_time
        print(f"Time to execute SQL query: {exec_duration:.4f} seconds")

        # Time tracking for converting response to JSON
        json_start_time = time.time()
        json_response = response_text.to_dict(orient="records")
        json_end_time = time.time()
        json_duration = json_end_time - json_start_time
        print(f"Time to convert response to JSON: {json_duration:.4f} seconds")

        total_time = time.time() - start_time
        print(f"Total time for request processing: {total_time:.4f} seconds")
        
        return jsonify({"reply": json_response})
    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error in execute_sql_query:", error_trace)
        return jsonify({"error": str(e), "trace": error_trace}), 500

if __name__ == "__main__":
    app.run(port=5000)
