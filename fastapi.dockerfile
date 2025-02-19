FROM python:3.9-slim
WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
# RUN mkdir -p /app/app/public/uploads/prompts \
#     /app/app/public/uploads/images \
#     /app/app/public/uploads/logs \
#     /app/app/public/reports \
#     && chown -R 1000:1000 /app/app/public

# Copy .env file
COPY .env .

# Copy the rest of the application
COPY . .
WORKDIR /app/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7001"]