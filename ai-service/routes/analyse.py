from flask import Blueprint

analyse_bp = Blueprint("analyse", __name__)

@analyse_bp.route("/analyse-document", methods=["POST"])
def analyse_document():
    return {"message": "analyse-document endpoint - coming Day 9"}