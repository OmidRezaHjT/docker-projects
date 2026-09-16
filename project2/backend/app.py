from flask import Flask, Response
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests"
)

@app.before_request
def count_request():
    REQUEST_COUNT.inc()

@app.route("/")
def home():
    return "Hello from Project 2!"

@app.route("/health")
def health():
    return "OK"

@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype="text/plain"
    )

app.run(host="0.0.0.0", port=5000)
