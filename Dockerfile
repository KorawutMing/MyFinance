FROM python:3.11-slim

WORKDIR /app

# 1. System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements
COPY requirements.txt .

# 3. THE ISOLATION INSTALL: Use --no-deps for the main packages
RUN pip install --no-cache-dir pythainav==0.2.1 --no-deps && \
    pip install --no-cache-dir fastapi uvicorn pydantic pandas yfinance --no-deps

# 4. THE DEPENDENCY BRIDGE: Install the missing links manually
# Added 'starlette' and 'pydantic-settings' to fix the current crash
RUN pip install --no-cache-dir \
    starlette \
    pydantic-settings \
    click \
    h11 \
    requests \
    dateparser \
    furl \
    fuzzywuzzy \
    importlib-metadata \
    "typing-extensions>=4.14.1"

# 5. Final project setup
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]