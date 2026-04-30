import json
import logging
import time
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from services.shared import groq_client

query_bp = Blueprint("query", __name__)
logger = logging.getLogger(__name__)

MODEL_NAME = "llama-3.3-70b-versatile"


def build_error_meta():
    return {
        "confidence": 0.0,
        "model_used": MODEL_NAME,
        "tokens_used": 0,
        "response_time_ms": 0,
        "cached": False
    }


def clean_response(text: str):
    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


@query_bp.route("/query", methods=["POST"])
def query():
    start_time = time.time()

    data = request.get_json(silent=True)

    if not data or "question" not in data:
        return jsonify({
            "data": {
                "error": "Field 'question' is required",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "meta": build_error_meta()
        }), 400

    question = data["question"].strip()

    # ✅ Get context from Chroma (RAG)
    chroma = current_app.config.get("CHROMA")
    context_docs = chroma.query(question) if chroma else []
    context = "\n".join(context_docs) if context_docs else ""

    prompt = f"""
You are a PCI-DSS compliance expert.

Answer the user question using the provided context.

Question:
{question}

Context:
{context}

Return JSON only:
{{
  "answer": "Clear answer",
  "sources": ["source 1", "source 2"],
  "generated_at": "{datetime.now(timezone.utc).isoformat()}"
}}
"""

    result = groq_client.call(prompt, temperature=0.3)

    # ⏱ track response time
    duration = time.time() - start_time
    times = current_app.config.get("RESPONSE_TIMES", [])
    times.append(duration)

    if len(times) > 10:
        times.pop(0)

    current_app.config["RESPONSE_TIMES"] = times

    try:
        ai_text = result.get("data", "")
        parsed = json.loads(clean_response(ai_text))

        return jsonify({
            "data": parsed,
            "meta": result.get("meta", build_error_meta())
        }), 200

    except Exception as e:
        logger.error(f"/query parse error: {str(e)}")

        return jsonify({
            "data": {
                "answer": result.get("data", ""),
                "sources": [],
                "generated_at": datetime.now(timezone.utc).isoformat()
            },
            "meta": result.get("meta", build_error_meta())
        }), 200