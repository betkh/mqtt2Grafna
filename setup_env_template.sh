#!/bin/bash

# Setup Environment Variables Template for MQTT2Grafana
# Copy this file to setup_env.sh and replace the token with your actual InfluxDB token

echo "🚀 Setting up environment variables for MQTT2Grafana..."

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# Create .env file with your token
cat > .env << EOF
# InfluxDB Configuration
INFLUXDB_TOKEN=your-actual-influxdb-token-here
INFLUXDB_INIT_ADMIN_TOKEN=your-actual-influxdb-admin-token-here

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883

# InfluxDB Configuration
INFLUXDB_URL=http://localhost:8086
INFLUXDB_ORG=myorg
INFLUXDB_BUCKET=weather_data
EOF

echo "✅ Environment variables set up successfully!"
echo "📝 Created .env file with your InfluxDB token"
echo ""
echo "🔐 IMPORTANT: Keep your .env file secure and never commit it to version control!"
echo "📋 The .env file is already in .gitignore to prevent accidental commits"
echo ""
echo "🚀 You can now start the application:"
echo "   docker-compose up -d"
echo ""
echo "🔍 To test the setup:"
echo "   pipenv run python src/scripts/test_influxdb_data.py" 