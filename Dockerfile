FROM python:3.11-slim

WORKDIR /app

# 1. System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements
COPY requirements.txt .

# 3. THE FIX: Install packages one-by-one with --no-deps 
# This stops the 'ResolutionImpossible' check from even starting.
RUN pip install --no-cache-dir pythainav==0.2.1 --no-deps && \
    pip install --no-cache-dir fastapi uvicorn pydantic pandas yfinance --no-deps

# 4. MANUALLY install the critical dependencies that were stripped by --no-deps
# We ensure typing-extensions is the NEW version for 'Self' support.
RUN pip install --no-cache-dir requests dateparser furl fuzzywuzzy importlib-metadata "typing-extensions>=4.14.1"

# 5. Final project setup
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]