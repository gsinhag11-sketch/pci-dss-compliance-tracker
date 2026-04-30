from flask import Blueprint, request, jsonify, current_app
import time

query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
def query():
    start = time.time()   # ⏱ start timer

    data = request.get_json()
    question = data.get("question", "")

    chroma = current_app.config.get("CHROMA")

    docs = chroma.query(question)

    if not docs:
        answer = "No relevant data found"
    else:
        answer = docs[0]

    end = time.time()   # ⏱ end timer
    duration = end - start

    # ✅ Store response times
    times = current_app.config.get("RESPONSE_TIMES")
    times.append(duration)

    # Keep only last 10
    if len(times) > 10:
        times.pop(0)

    return jsonify({"answer": answer})