# Real-Time ML Pipeline for Fuel Efficiency Forecasting

This project demonstrates a complete, end-to-end streaming machine learning pipeline for predicting vehicle fuel efficiency. It uses Kafka (via Redpanda) to simulate a real-time data stream, processes the data through a Bronze/Silver architecture, and continuously retrains a model. A Streamlit dashboard provides a live view of the model's performance.

```mermaid
graph TB
    %% Definitions
    A[Vehicle Data Source] -->|JSON Stream| B(Redpanda Message Bus)
    B -->|Consumer Service| C[(Bronze Layer\nRaw Parquet)]
    C -->|Cleaning Process| D[(Silver Layer\nProcessed Data)]
    D -->|Data Drift Trigger| E{Continuous Trainer}
    E -->|Retrain Model| F[Scikit-learn Model Artifact]
    F -->|Serve Metrics R²/MAE| G[Streamlit Dashboard]

    %% Styling
    style A fill:#f9f,stroke:#333,stroke-width:2px,font-size:16px
    style B fill:#ff9,stroke:#f66,stroke-width:4px,color:red,font-size:16px
    style C fill:#e1e1e1,stroke:#333,stroke-width:2px,font-size:16px
    style D fill:#c0c0c0,stroke:#333,stroke-width:2px,font-size:16px
    style E fill:#ffcc99,stroke:#333,stroke-width:2px,font-size:16px
    style F fill:#ccffcc,stroke:#333,stroke-width:2px,font-size:16px
    style G fill:#9ff,stroke:#333,stroke-width:2px,font-size:16px
    linkStyle default stroke-width:2px,fill:none,stroke:black,font-size:14px

Live demo - https://dashboard-5p9c.onrender.com/
## Features

- **Real-Time Data Ingestion**: A Python script (`producer.py`) reads vehicle data and streams it into Kafka.
- **Kafka Message Bus**: Redpanda is used as a lightweight, Docker-based Kafka-compatible message broker.
- **Bronze/Silver Data Layers**:
  - **Bronze**: Raw, unfiltered data is consumed from Kafka and stored in Parquet files.
  - **Silver**: Data is cleaned, transformed, and enriched, creating an analysis-ready dataset.
- **Continuous Model Training**: A trainer script (`consumer_trainer.py`) monitors the Silver layer and retrains a Scikit-learn model whenever new data arrives.
- **Live Monitoring Dashboard**: A Streamlit application (`training_monitor.py`) visualizes the model's performance (R² and MAE) in real-time and allows for pipeline control.


## Project Structure

```
├── dashboard/
│   └── training_monitor.py   # Streamlit monitoring UI
├── data/
│   └── Cars_Cleaned.xlsx     # Source data
├── ingestion/
│   └── producer.py           # Streams data into Kafka
├── transform/
│   ├── consumer_to_parquet.py # Bronze layer writer
│   ├── consumer_to_silver.py  # Silver layer writer
│   └── consumer_trainer.py    # Model trainer
├── docker-compose.yml        # Docker Compose for Redpanda (Kafka)
├── requirements.txt          # Python dependencies
├── .gitignore                # Files to ignore for Git
├── .env.example              # Environment variable template
└── README.md                 # This file
```
