import json
import logging
import time
from flask import Flask, request

app = Flask(__name__)

log_handler = logging.FileHandler("/var/log/flask/app.log")
logger = logging.getLogger("flask-app")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


@app.after_request
def log_request(response):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
        "remote_addr": request.remote_addr,
    }
    logger.info(json.dumps(log_entry))
    return response


@app.route("/")
def home():
    return {"message": "Hello from Flask"}


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
