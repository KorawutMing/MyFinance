# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies (for building some Python libs)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first for faster builds (caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from the root folder into the container
COPY . .

# IMPORTANT: Set PYTHONPATH so 'api' can find the 'GlobalTicker' folder
ENV PYTHONPATH=/app

# Expose the FastAPI port
EXPOSE 8000

# Run the API using uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]