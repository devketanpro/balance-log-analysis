# Use a minimal Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirement and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts and data
COPY scripts/ scripts/
COPY data/ data/

# Create output directory
RUN mkdir -p output

# Expose Streamlit default port
EXPOSE 8501

# Run scripts: first read_logs.py, then generate_report.py, then launch Streamlit app
CMD bash -c "python scripts/read_logs.py && python scripts/generate_report.py && streamlit run scripts/visulization.py --server.address=0.0.0.0 --server.port=8501"
