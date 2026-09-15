FROM python:3.12-slim
WORKDIR /app
COPY app.py .
RUN pip install --no-cache-dir flask psycopg2-binary
EXPOSE 5000
CMD ["python", "app.py"]
