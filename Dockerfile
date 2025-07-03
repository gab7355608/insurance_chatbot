FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir rasa==3.6.15 rasa-sdk

# Copy requirements if exists
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy project files
COPY . /app/

# Create a non-root user
RUN useradd -m -u 1001 rasa
RUN chown -R rasa:rasa /app
USER rasa

# Expose ports
EXPOSE 5005 5055

# Default command
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"] 