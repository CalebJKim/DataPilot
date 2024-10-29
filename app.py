from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import LLM
import traceback

app = Flask(__name__)
CORS(app)
llm = LLM()
csv_file_path = "datasets/samples.csv"

@app.route("/api/llm-query", methods=["POST"])
def query_llm():
    data = request.get_json()
    prompt = data.get("message")

    if not prompt:
        return jsonify({"error": "No message provided"}), 400

    try:
        sql_query = llm.generate_sql_query(prompt)
        response_text = llm.execute_sql_query(sql_query=sql_query, csv_file=csv_file_path)
        json_response = response_text.to_dict(orient="records")
        return jsonify({"reply": json_response})
    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error in execute_sql_query:", error_trace)
        return jsonify({"error": str(e), "trace": error_trace}), 500

if __name__ == "__main__":
    app.run(port=5000)
