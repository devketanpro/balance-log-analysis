FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into the container
COPY . .

# Default command (optional - if you want to auto-run a script)
# CMD ["python3", "scripts/generate_report.py"]
