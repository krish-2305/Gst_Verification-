# Use official Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
COPY packages.txt .
RUN apt-get update && \
    tr -d '\r' < packages.txt | xargs -r apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Set environment variables from .env
ENV PYTHONUNBUFFERED=1

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "main.py"]
