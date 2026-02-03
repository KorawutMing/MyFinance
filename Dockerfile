FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# STEP 1: Install pythainav in complete isolation
# We use --no-deps so pip doesn't even look at the typing-extensions constraint.
RUN pip install --no-cache-dir pythainav==0.2.1 --no-deps

# STEP 2: Install your other requirements
# We create a temporary requirements file without pythainav to avoid re-triggering the conflict
COPY requirements.txt .
RUN sed -i '/pythainav/d' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# STEP 3: The "Hammer"
# Force the exact version of typing-extensions that FastAPI needs to run.
RUN pip install --no-cache-dir --force-reinstall "typing-extensions>=4.14.1"

# Copy project files
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]