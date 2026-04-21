from flask import Blueprint

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    return {"message": "recommend endpoint - coming Day 4"}