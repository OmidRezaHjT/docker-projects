import os
import psycopg2
from flask import Flask

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


@app.route("/")
def home():
    try:
        conn = get_connection()
        conn.close()
        return "Hello from Docker Backend! Database: connected"
    except Exception as e:
        return f"Database connection failed: {e}", 500


app.run(host="0.0.0.0", port=5000)
