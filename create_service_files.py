#!/usr/bin/env python3

"""
Script to create remaining service files.
"""

import os
from pathlib import Path

BASE_DIR = Path("/Users/parthbatwara/Desktop/Code/credit-card-fraud-detection")

# Define all the additional files to create
service_files = {
    # Trainer service
    "services/trainer/Dockerfile": """# Dockerfile for trainer service
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN adduser --disabled-password --gecos '' traineruser
RUN chown -R traineruser:traineruser /app
USER traineruser

CMD ["python", "-m", "app.main"]""",

    "services/trainer/requirements.txt": """lightgbm==4.1.0
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.24.4
tensorflow==2.15.0
torch==2.1.2
psycopg2-binary==2.9.9
minio==7.2.0
mlflow==2.8.1
networkx==3.2.1
node2vec==0.4.6
prometheus-client==0.19.0
structlog==23.2.0
python-dotenv==1.0.0
pydantic==2.5.0
sqlalchemy==2.0.23
optuna==3.5.0""",

    # Graph builder service
    "services/graph-builder/Dockerfile": """# Dockerfile for graph builder service
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN adduser --disabled-password --gecos '' graphuser
RUN chown -R graphuser:graphuser /app
USER graphuser

CMD ["python", "-m", "app.main"]""",

    "services/graph-builder/requirements.txt": """neo4j==5.15.0
networkx==3.2.1
node2vec==0.4.6
kafka-python==2.0.2
pandas==2.1.4
numpy==1.24.4
prometheus-client==0.19.0
structlog==23.2.0
python-dotenv==1.0.0
pydantic==2.5.0""",

    # Simulator service
    "services/simulator/Dockerfile": """# Dockerfile for simulator service
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN adduser --disabled-password --gecos '' simulatoruser
RUN chown -R simulatoruser:simulatoruser /app
USER simulatoruser

CMD ["python", "-m", "app.main"]""",

    "services/simulator/requirements.txt": """kafka-python==2.0.2
pandas==2.1.4
numpy==1.24.4
faker==20.1.0
python-dateutil==2.8.2
prometheus-client==0.19.0
structlog==23.2.0
python-dotenv==1.0.0
pydantic==2.5.0
typer==0.9.0
rich==13.7.0""",

    # Dashboard service
    "services/dashboard/Dockerfile": """# Dockerfile for React dashboard
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]""",

    "services/dashboard/package.json": """{
  "name": "fraud-detection-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.1",
    "react-scripts": "5.0.1",
    "axios": "^1.3.4",
    "recharts": "^2.5.0",
    "antd": "^5.3.0",
    "moment": "^2.29.4",
    "lodash": "^4.17.21",
    "socket.io-client": "^4.6.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}""",

    "services/dashboard/public/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Fraud Detection Dashboard"
    />
    <title>Fraud Detection Dashboard</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>""",

    "services/dashboard/src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",

    "services/dashboard/src/App.js": """import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import TransactionList from './components/transactions/TransactionList';
import './App.css';

const { Content } = Layout;

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header />
        <Layout>
          <Sidebar />
          <Layout style={{ padding: '24px' }}>
            <Content>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/transactions" element={<TransactionList />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;""",

    "services/dashboard/src/App.css": """.App {
  text-align: center;
}

.site-layout-content {
  min-height: 280px;
  padding: 24px;
  background: #fff;
}""",

    # Configuration files
    "config/prometheus/prometheus.yml": """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'fraud-api'
    static_configs:
      - targets: ['api:8000']

  - job_name: 'fraud-inference'
    static_configs:
      - targets: ['inference:8001']

  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka:9092']""",

    "config/nginx/default.conf": """upstream api {
    server api:8000;
}

upstream dashboard {
    server dashboard:3000;
}

server {
    listen 80;
    server_name localhost;

    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}""",

    # Sample data files
    "data/sample/transactions.csv": """transaction_id,user_id,merchant_id,amount,currency,timestamp,is_fraud
tx_001,user_001,merchant_001,150.00,USD,2024-01-01 10:00:00,0
tx_002,user_002,merchant_002,2500.00,USD,2024-01-01 10:05:00,1
tx_003,user_003,merchant_001,75.50,USD,2024-01-01 10:10:00,0""",

    "data/sample/merchants.csv": """merchant_id,name,category,location
merchant_001,Coffee Shop,Food & Dining,New York
merchant_002,Electronics Store,Electronics,Los Angeles
merchant_003,Gas Station,Automotive,Chicago""",

    "data/sample/cards.csv": """card_id,user_id,card_type,issued_date,status
card_001,user_001,VISA,2023-01-15,ACTIVE
card_002,user_002,MASTERCARD,2023-02-20,ACTIVE
card_003,user_003,AMEX,2023-03-10,ACTIVE""",

    "data/models/.gitkeep": "# Keep this directory",
    "data/embeddings/.gitkeep": "# Keep this directory",

    # Scripts
    "scripts/setup.sh": """#!/bin/bash
# Setup script for fraud detection system
echo "Setting up fraud detection system..."

# Copy environment file
cp .env.example .env

# Start infrastructure services
docker-compose up -d postgres redis kafka neo4j minio

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Initialize databases
python scripts/init_db.py
python scripts/init_kafka.py
python scripts/init_neo4j.py

echo "Setup complete!"
""",

    "scripts/init_db.py": """#!/usr/bin/env python3
# Database initialization script
print("Initializing PostgreSQL database...")
# Add database initialization logic here
""",

    "scripts/init_kafka.py": """#!/usr/bin/env python3
# Kafka initialization script
print("Initializing Kafka topics...")
# Add Kafka topic creation logic here
""",

    "scripts/init_neo4j.py": """#!/usr/bin/env python3
# Neo4j initialization script
print("Initializing Neo4j database...")
# Add Neo4j setup logic here
""",

    "scripts/generate_sample_data.py": """#!/usr/bin/env python3
# Sample data generation script
print("Generating sample data...")
# Add sample data generation logic here
""",

    "scripts/backup.sh": """#!/bin/bash
# Backup script
echo "Creating backup..."
# Add backup logic here
""",

    "scripts/restore.sh": """#!/bin/bash
# Restore script
echo "Restoring from backup..."
# Add restore logic here
""",

    # Monitoring
    "monitoring/alerts/rules.yml": """groups:
  - name: fraud_detection_alerts
    rules:
      - alert: HighFraudRate
        expr: fraud_detection_rate > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High fraud detection rate"
          description: "Fraud detection rate is {{ $value }}"
""",

    # Documentation
    "docs/README.md": """# Fraud Detection System Documentation

## Overview
Real-time credit card fraud detection system using machine learning.

## Architecture
- Microservices architecture
- Event-driven with Kafka
- Real-time inference
- Graph-based features
""",

    "docs/API.md": """# API Documentation

## Endpoints

### Health Check
- `GET /health` - Health check

### Scoring
- `POST /api/v1/scoring/score` - Score a transaction

### Decisions
- `GET /api/v1/decisions` - Get fraud decisions
""",

    "docs/DEPLOYMENT.md": """# Deployment Guide

## Prerequisites
- Docker
- Docker Compose

## Steps
1. Clone repository
2. Copy `.env.example` to `.env`
3. Run `make setup`
4. Run `make up`
""",

    "docs/ARCHITECTURE.md": """# Architecture Documentation

## System Overview
The fraud detection system consists of multiple microservices:

1. API Service - REST API
2. Inference Service - ML inference
3. Enricher Service - Data enrichment
4. Trainer Service - Model training
5. Graph Builder Service - Graph construction
6. Simulator Service - Transaction simulation
7. Dashboard - Web UI
""",

    "docs/TROUBLESHOOTING.md": """# Troubleshooting Guide

## Common Issues

### Service won't start
- Check Docker logs: `docker-compose logs <service>`
- Verify environment variables
- Check port conflicts

### Database connection issues
- Ensure PostgreSQL is running
- Check connection parameters
""",

    # Test fixtures
    "tests/fixtures/sample_transactions.json": """[
  {
    "transaction_id": "tx_001",
    "user_id": "user_001",
    "merchant_id": "merchant_001",
    "amount": 150.00,
    "currency": "USD",
    "timestamp": "2024-01-01T10:00:00Z",
    "is_fraud": false
  }
]""",
}

def create_service_files():
    """Create all service files."""
    for file_path, content in service_files.items():
        full_path = BASE_DIR / file_path
        
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with content
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"Created: {file_path}")

if __name__ == "__main__":
    create_service_files()
    print(f"\\nCreated {len(service_files)} additional files!")
