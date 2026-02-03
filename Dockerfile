FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 1. Create a constraint file to force the typing-extensions version
RUN echo "typing-extensions>=4.14.1" > constraints.txt

# 2. Install everything using the constraint
# --no-deps for pythainav ensures it doesn't block the build
RUN pip install --no-cache-dir pythainav==0.2.1 --no-deps && \
    pip install --no-cache-dir -c constraints.txt -r requirements.txt

# 3. Final safety check
RUN pip install --no-cache-dir --force-reinstall "typing-extensions>=4.14.1"

COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]