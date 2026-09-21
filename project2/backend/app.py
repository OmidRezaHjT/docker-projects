from flask import Flask, request
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

@app.before_request
def log_request():
    logging.info(
        "%s %s",
        request.method,
        request.path
    )

@app.route("/")
def home():
    return "Hello from Project 2!"

@app.route("/health")
def health():
    return "OK"

@app.route("/metrics")
def metrics():
    from flask import Response
    from prometheus_client import generate_latest

    return Response(
        generate_latest(),
        mimetype="text/plain"
    )

app.run(host="0.0.0.0", port=5000)
