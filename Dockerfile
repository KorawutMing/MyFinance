FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# STEP 1: Install all requirements. If it errors, use --no-deps for pythainav
RUN pip install --no-cache-dir -r requirements.txt || \
    (pip install --no-cache-dir --no-deps pythainav==0.2.1 && \
     pip install --no-cache-dir -r requirements.txt)

# STEP 2: The "Hammer" - Force the correct typing-extensions for FastAPI
RUN pip install --no-cache-dir --upgrade --force-reinstall typing-extensions>=4.14.1

COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]