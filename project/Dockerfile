FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "pipeline.py"]
CMD ["--generate-demo", "--output", "/app/reports"]
