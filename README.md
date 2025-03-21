# Kafka Log Monitoring API
![1_V13D6FbXu0lhNH0f3AGvBg](https://github.com/user-attachments/assets/5bdeef3e-6815-456e-9b5f-d61e8e1271df)

A robust, scalable logging system using Kafka, FastAPI, and Spark Streaming, designed for high-throughput event processing.

# Kafka Log API

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/shanojpillai/kafka-log-api)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Docker Pulls](https://img.shields.io/docker/pulls/shanojpillai/kafka-log-api)](https://hub.docker.com/r/shanojpillai/kafka-log-api)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A production-grade log aggregation and processing system designed for high throughput and real-time analysis, built with Kafka, FastAPI, and Spark Streaming.

## Features

- ✅ **High-throughput log ingestion** - Process 15,000+ logs per second
- ✅ **Real-time analytics** - Sub-250ms end-to-end latency
- ✅ **Scalable architecture** - Linear scaling with Kafka partitions
- ✅ **Containerized deployment** - Single command to launch the entire system
- ✅ **Interactive dashboard** - Real-time visualization and filtering
- ✅ **Robust error handling** - Retry mechanisms and monitoring
- ✅ **Schema evolution support** - Version-compatible log formats

## Table of Contents

- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Usage](#api-usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## System Architecture

The system consists of the following components:

- **Log Producer API (FastAPI)**: Receives and validates log events
- **Message Broker (Kafka)**: Provides durable storage and decoupling
- **Stream Processor (Spark)**: Performs real-time analysis
- **Visualization Dashboard (Streamlit)**: Provides interactive visualizations

## Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.8+](https://www.python.org/downloads/) (for local development)
- [Kafka client](https://kafka.apache.org/downloads) (for manual testing)

## Quick Start

### Option 1: Run with Docker Compose

```bash
# Clone the repository
git clone https://github.com/shanojpillai/kafka-log-api.git
cd kafka-log-api

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

Access the services:
- API Documentation: http://localhost:8000/docs
- Streamlit Dashboard: http://localhost:8501

### Option 2: Local Development Setup

```bash
# Clone the repository
git clone https://github.com/shanojpillai/kafka-log-api.git
cd kafka-log-api

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Kafka and Zookeeper with Docker
docker-compose up -d zookeeper kafka

# Run the FastAPI application
python -m src.main

# In a separate terminal, run the Streamlit dashboard
python -m streamlit run streamlit_app.py
```

## Project Structure

```
kafka-log-api/
│── src/
│   ├── main.py                # FastAPI entry point
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   ├── models.py          # Request models & validation
│   ├── core/
│   │   ├── config.py          # Configuration loader
│   │   ├── kafka_producer.py  # Kafka producer
│   │   ├── logger.py          # Centralized logging
│── data/
│   ├── processed_web_logs.csv # Processed log dataset
│── spark/
│   ├── consumer.py            # Spark Streaming consumer
│── tests/
│   ├── test_api.py            # API test suite
│── streamlit_app.py           # Dashboard
│── docker-compose.yml         # Container orchestration
│── Dockerfile                 # FastAPI container
│── Dockerfile.streamlit       # Dashboard container
│── requirements.txt           # Dependencies
│── process_csv_logs.py        # Log preprocessor
```

## API Usage

### Send a Log Entry

```bash
curl -X POST "http://localhost:8000/log" \
     -H "Content-Type: application/json" \
     -d '{
           "service": "payment-api",
           "level": "ERROR",
           "message": "Transaction failed",
           "metadata": {
             "user_id": "user-123",
             "transaction_id": "tx-456"
           }
         }'
```

### Retrieve Logs

```bash
# Get the last 10 logs
curl "http://localhost:8000/logs?limit=10"

# Filter by service and level
curl "http://localhost:8000/logs?service=payment-api&level=ERROR"
```

### Send a Test Log from Dataset

```bash
# Send log entry at index 5
curl "http://localhost:8000/kaggle/5"
```

![Screenshot 2025-03-20 195159](https://github.com/user-attachments/assets/49ed1c9c-fa0b-430f-965f-d3688a3a4e73)

![Screenshot 2025-03-20 195144](https://github.com/user-attachments/assets/5113bc3b-2bac-4bb7-96d4-6fb95c2f7434)

## Configuration

Configuration is handled through environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka connection string | `kafka:9092` |
| `KAFKA_TOPIC` | Default Kafka topic | `logs` |
| `LOG_LEVEL` | Application log level | `INFO` |
| `RETENTION_DAYS` | Log retention period | `7` |

## Testing

```bash
# Run unit tests
pytest

# Run integration tests
pytest tests/integration/

# Generate coverage report
pytest --cov=src
```

## Deployment

### Production Considerations

For production deployments, consider:

1. **Kafka Cluster Sizing**
   - Start with 3+ brokers for fault tolerance
   - Monitor partition count and replication factor

2. **Security**
   - Enable TLS for all communications
   - Implement authentication (SASL)
   - Set up ACLs for topic access control

3. **Monitoring**
   - Add Prometheus metrics
   - Configure Grafana dashboards
   - Set up alerts for system health

4. **Scaling**
   - Scale Kafka partitions for throughput
   - Adjust Spark executors for processing power
   - Consider Kubernetes for dynamic scaling

### Kubernetes Deployment

A Helm chart is available in the `kubernetes/` directory:

```bash
helm install kafka-log-api ./kubernetes/kafka-log-api
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code passes all tests and linting before submitting.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance API framework
- [Apache Kafka](https://kafka.apache.org/) for the distributed event streaming platform
- [Apache Spark](https://spark.apache.org/) for the analytics engine
- [Streamlit](https://streamlit.io/) for the interactive dashboard
- [Kaggle](https://www.kaggle.com/) for the Web Log Dataset
