#!/bin/bash
# scripts/setup.sh - Complete system setup script

set -e

echo "🚀 Setting up Fraud Detection System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    print_status "All dependencies are installed ✅"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example. Please review and update the configuration."
    else
        print_status ".env file already exists, skipping..."
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating project directories..."
    
    mkdir -p data/{models,sample,geoip,training}
    mkdir -p logs
    mkdir -p ssl
    mkdir -p monitoring/grafana/{dashboards,provisioning}
    mkdir -p config/{kafka,neo4j,nginx,prometheus}
    
    print_status "Directories created ✅"
}

# Generate sample data
generate_sample_data() {
    print_status "Generating sample data..."
    
    python3 scripts/generate_sample_data.py
    
    print_status "Sample data generated ✅"
}

# Start infrastructure services
start_infrastructure() {
    print_status "Starting infrastructure services..."
    
    # Start core infrastructure
    docker-compose up -d postgres redis kafka neo4j minio qdrant
    
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    print_status "Checking service health..."
    
    # Wait for PostgreSQL
    until docker-compose exec -T postgres pg_isready -U fraud -d frauddb; do
        print_warning "Waiting for PostgreSQL..."
        sleep 2
    done
    
    # Wait for Kafka
    until docker-compose exec -T kafka kafka-topics.sh --bootstrap-server kafka:9092 --list &> /dev/null; do
        print_warning "Waiting for Kafka..."
        sleep 2
    done
    
    print_status "Infrastructure services are ready ✅"
}

# Initialize databases
initialize_databases() {
    print_status "Initializing databases..."
    
    # Initialize PostgreSQL
    python3 scripts/init_db.py
    
    # Initialize Kafka topics
    python3 scripts/init_kafka.py
    
    # Initialize Neo4j
    python3 scripts/init_neo4j.py
    
    print_status "Databases initialized ✅"
}

# Build and start application services
start_application() {
    print_status "Building and starting application services..."
    
    # Build services
    docker-compose build api inference enricher graph-builder trainer dashboard
    
    # Start application services
    docker-compose up -d api inference enricher graph-builder trainer dashboard
    
    print_status "Application services started ✅"
}

# Start monitoring (optional)
start_monitoring() {
    print_status "Starting monitoring stack..."
    
    docker-compose --profile monitoring up -d
    
    print_status "Monitoring stack started ✅"
    print_status "Grafana available at: http://localhost:3001 (admin/admin_password_2024)"
    print_status "Prometheus available at: http://localhost:9090"
}

# Start simulator (optional)
start_simulator() {
    print_status "Starting transaction simulator..."
    
    docker-compose --profile simulation up -d
    
    print_status "Transaction simulator started ✅"
}

# Main execution
main() {
    echo "======================================"
    echo "  Fraud Detection System Setup"
    echo "======================================"
    echo
    
    check_dependencies
    create_env_file
    create_directories
    
    # Ask user what to setup
    echo
    echo "Setup options:"
    echo "1. Full setup (recommended for first time)"
    echo "2. Infrastructure only"
    echo "3. Application services only"
    echo "4. Custom setup"
    echo
    
    read -p "Choose setup option (1-4): " choice
    
    case $choice in
        1)
            print_status "Starting full setup..."
            generate_sample_data
            start_infrastructure
            initialize_databases
            start_application
            
            read -p "Start monitoring stack? (y/n): " monitoring
            if [[ $monitoring =~ ^[Yy]$ ]]; then
                start_monitoring
            fi
            
            read -p "Start transaction simulator? (y/n): " simulator
            if [[ $simulator =~ ^[Yy]$ ]]; then
                start_simulator
            fi
            ;;
        2)
            start_infrastructure
            initialize_databases
            ;;
        3)
            start_application
            ;;
        4)
            echo "Available components:"
            echo "- infrastructure: PostgreSQL, Redis, Kafka, Neo4j, MinIO"
            echo "- application: API, Inference, Enricher, Graph Builder, Trainer"
            echo "- dashboard: React frontend"
            echo "- monitoring: Prometheus, Grafana"
            echo "- simulator: Transaction simulator"
            
            read -p "Enter components to start (space-separated): " components
            
            for component in $components; do
                case $component in
                    infrastructure)
                        start_infrastructure
                        initialize_databases
                        ;;
                    application)
                        start_application
                        ;;
                    dashboard)
                        docker-compose up -d dashboard
                        ;;
                    monitoring)
                        start_monitoring
                        ;;
                    simulator)
                        start_simulator
                        ;;
                    *)
                        print_warning "Unknown component: $component"
                        ;;
                esac
            done
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo
    print_status "✅ Setup completed successfully!"
    echo
    echo "🌐 Services available at:"
    echo "   - API Documentation: http://localhost:8080/docs"
    echo "   - Dashboard: http://localhost:3000"
    echo "   - Neo4j Browser: http://localhost:7474"
    echo "   - MinIO Console: http://localhost:9001"
    echo
    echo "📋 Next steps:"
    echo "   1. Review the .env configuration"
    echo "   2. Access the dashboard to monitor transactions"
    echo "   3. Check the API documentation for integration"
    echo "   4. Review logs: docker-compose logs -f [service-name]"
    echo
    print_status "Happy fraud hunting! 🔍"
}

# Run main function