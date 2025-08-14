# Balance Log Analysis
Balance Log Analysis is a tool for processing and visualizing transaction logs from systems that manage subscriber credit and debit activities.
It extracts relevant wallet-related events from raw log files, parses and normalizes JSON data, and produces:
 * Structured Excel reports for accounting and analysis
 * Interactive dashboards using Streamlit for visual insights

## Table of Contents
* Project Structure
* Run with Docker
* Access the Dashboard
* Media Files for Visualizations

## Project Structure
balance-log-analysis/
│
├── data/                      # Place your .gz log files here
│   └── balance-sync-logs/      # Example: logs from production system
│
├── output/                     # Generated Excel reports will be saved here
│
├── scripts/                    # Python scripts for processing
│   ├── read_logs.py             # Extracts relevant JSON records from .gz logs
│   ├── verify_data.py           # Parses JSON into structured tabular data
│   ├── visualization.py         # Interactive Streamlit dashboard for visualization
│
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration to run scripts & dashboard
└── README.md

## Run with Docker
Make sure Docker is installed and running on your system.

## Step 1: 
Build the Docker image

``` docker build -t balance-log-analyzer . ```


## Step 2: 
Run the container

``` docker run -it \
  -p 8501:8501 \
  -v "$PWD/data:/app/data" \
  -v "$PWD/output:/app/output" \
  balance-log-analyzer 
```


## Access the Dashboard
Once running, you can open the dashboard in your browser at:
http://localhost:8501

## Media Files for Visualizations
These images are generated from the data analysis process and are used to illustrate patterns, trends, and insights found in the balance log data.


<img height="350" src="https://github.com/devketanpro/balance-log-analysis/blob/main/media/Screenshot%20from%202025-08-14%2014-28-58.png">


<img height="350" src="https://github.com/devketanpro/balance-log-analysis/blob/main/media/Screenshot%20from%202025-08-14%2014-29-21.png">


<img height="350" src="https://github.com/devketanpro/balance-log-analysis/blob/main/media/Screenshot%20from%202025-08-14%2014-29-35.png">


<img height="350" src="https://github.com/devketanpro/balance-log-analysis/blob/main/media/Screenshot%20from%202025-08-14%2014-29-51.png">

