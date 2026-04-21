from flask import Blueprint

report_bp = Blueprint("report", __name__)

@report_bp.route("/generate-report", methods=["POST"])
def generate_report():
    return {"message": "generate-report endpoint - coming Day 6"}