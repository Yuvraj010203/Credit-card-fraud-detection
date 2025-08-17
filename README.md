# Credit Card Fraud Detection System

A comprehensive, real-time credit card fraud detection system built with microservices architecture, machine learning, and graph analytics.

## 🏗️ Architecture

The system consists of multiple microservices:

- **API Service**: FastAPI-based REST API for fraud scoring and decision management
- **Inference Service**: Real-time ML inference using ensemble models (LightGBM, Autoencoder, Graph Neural Networks)
- **Enricher Service**: Stream processing for transaction enrichment with geo, device, and merchant data
- **Trainer Service**: Automated ML model training and evaluation pipeline
- **Graph Builder Service**: Neo4j-based graph construction for relationship analysis
- **Simulator Service**: Transaction data simulator for testing and demo
- **Dashboard**: React-based web dashboard for monitoring and visualization

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+ (for dashboard development)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd credit-card-fraud-detection
   ```

2. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the system**
   ```bash
   make setup    # First time setup
   make up       # Start all services
   ```

4. **Access the services**
   - Dashboard: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Grafana: http://localhost:3001 (admin/admin123)
   - Neo4j Browser: http://localhost:7474

## 🔧 Development

### Project Structure
```
fraud-detection-system/
├── services/           # Microservices
│   ├── api/           # REST API service
│   ├── inference/     # ML inference service
│   ├── enricher/      # Data enrichment service
│   ├── trainer/       # Model training service
│   ├── graph-builder/ # Graph construction service
│   ├── simulator/     # Transaction simulator
│   └── dashboard/     # Web dashboard
├── shared/            # Shared utilities and schemas
├── config/            # Configuration files
├── data/              # Sample data and model artifacts
├── notebooks/         # Jupyter notebooks for analysis
├── monitoring/        # Grafana dashboards and alerts
├── docs/              # Documentation
└── tests/             # Integration and performance tests
```

### Available Commands

```bash
make help              # Show all available commands
make build             # Build all Docker images
make up                # Start all services
make down              # Stop all services
make logs              # Show logs for all services
make test              # Run tests
make lint              # Run code linting
make format            # Format code
make generate-data     # Generate sample data
make backup            # Backup data
make restore           # Restore data
```

## 📊 Features

### Real-time Fraud Detection
- **Sub-100ms inference latency**
- **Ensemble ML models** (LightGBM + Autoencoder + Graph Neural Networks)
- **Real-time feature engineering** with velocity and graph features
- **Explainable AI** with SHAP values and feature importance

### Advanced Analytics
- **Graph-based fraud detection** using transaction networks
- **Anomaly detection** with autoencoders
- **Velocity features** across multiple time windows
- **Geospatial analysis** for location-based risk scoring

### Production Ready
- **Microservices architecture** with Docker containers
- **Event-driven processing** with Apache Kafka
- **Horizontal scaling** with Kubernetes support
- **Comprehensive monitoring** with Prometheus and Grafana
- **CI/CD pipeline** with automated testing

### Machine Learning Pipeline
- **Automated model training** with hyperparameter optimization
- **Model versioning** and A/B testing
- **Data drift detection** and model retraining
- **Feature store** with real-time and batch features

## 🔍 API Usage

### Score a Transaction
```bash
curl -X POST "http://localhost:8000/api/v1/scoring/score" \
     -H "Content-Type: application/json" \
     -d '{
       "transaction": {
         "transaction_id": "txn_123",
         "user_id": "user_456", 
         "merchant_id": "merchant_789",
         "amount": 150.00,
         "currency": "USD"
       }
     }'
```

### Get Fraud Decisions
```bash
curl "http://localhost:8000/api/v1/decisions?limit=10"
```

## 📈 Monitoring

The system includes comprehensive monitoring:

- **Real-time dashboards** showing fraud rates, transaction volumes, and model performance
- **Alerting** for high fraud rates, model drift, and system issues
- **Performance metrics** for latency, throughput, and resource usage
- **Model monitoring** with accuracy, precision, recall, and F1 scores

## 🧪 Testing

### Run Tests
```bash
make test                    # All tests
make test-integration        # Integration tests
make test-performance        # Performance tests
```

### Generate Sample Data
```bash
make generate-data           # Generate sample transactions
make start-simulator         # Start real-time transaction simulation
```

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please:
1. Check the [troubleshooting guide](docs/TROUBLESHOOTING.md)
2. Search existing [issues](https://github.com/company/fraud-detection-system/issues)
3. Create a new issue with detailed information

## 🙏 Acknowledgments

- Built with FastAPI, React, Apache Kafka, Neo4j, and PostgreSQL
- Machine learning powered by LightGBM, TensorFlow, and scikit-learn
- Monitoring with Prometheus and Grafana
- Containerized with Docker and orchestrated with Docker Compose
