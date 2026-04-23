import logging
from flask import Flask
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.categorise import categorise_bp
from routes.report import report_bp
from routes.analyse import analyse_bp
from routes.batch import batch_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = Flask(__name__)

# Register all blueprints
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(categorise_bp)
app.register_blueprint(report_bp)
app.register_blueprint(analyse_bp)
app.register_blueprint(batch_bp)

@app.route("/")
def home():
    return {"message": "PCI-DSS AI Service Running", "version": "1.0.0"}

@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "pci-dss-ai-service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    