#!/bin/bash

echo "Starting MQTT Temperature Visualization System"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Start all services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker-compose ps

# Setup Grafana (if not already done)
echo "Setting up Grafana..."
pipenv run python setup_grafana.py

echo ""
echo "Setup complete!"
echo "=============="
echo "Grafana Dashboard: http://localhost:3000"
echo "Username: admin"
echo "Password: admin"
echo ""
echo "To start data collection and visualization:"
echo "1. Terminal 1: pipenv run python data_collector.py"
echo "2. Terminal 2: pipenv run python publisher.py"
echo "3. Browser: Open http://localhost:3000"
echo ""
echo "Press any key to continue..."
read -n 1 