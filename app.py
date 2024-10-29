from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import LLM

app = Flask(__name__)
CORS(app)
llm = LLM()

@app.route("/api/llm-query", methods=["POST"])
def query_llm():
    data = request.get_json()
    prompt = data.get("message")

    if not prompt:
        return jsonify({"error": "No message provided"}), 400

    try:
        response_text = llm.generate_sql_query(prompt)
        return jsonify({"reply": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
