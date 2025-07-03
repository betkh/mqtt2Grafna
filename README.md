# MQTT Python Application with Docker

This project demonstrates how to use a containerized Mosquitto MQTT broker with Python applications to publish and subscribe to messages on the "data/temperature" topic.

## Project Structure

```
mqtt2Grafana/
├── docker-compose.yml              # Docker Compose configuration
├── Pipfile                         # Python dependencies (pipenv)
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── src/                            # Source code
│   ├── scripts/                    # Main application scripts
│   │   ├── publisher.py            # MQTT publisher script
│   │   ├── subscriber_A.py         # MQTT subscriber for temperature data
│   │   ├── subscriber_B.py         # MQTT subscriber for humidity data
│   │   ├── setup_grafana.py        # Grafana setup script
│   │   ├── setup_influxdb_token.py # InfluxDB token setup script
│   │   └── test_influxdb.py        # InfluxDB testing script
│   └── utils/                      # Utility scripts
│       └── start_visualization.sh  # Startup script
├── telegraf/                       # Telegraf configuration
│   └── telegraf.conf               # MQTT to InfluxDB data collection
├── config/                         # Configuration files
│   └── env.example                 # Environment variables template
├── docs/                           # Documentation
│   ├── troubleshooting.md          # Troubleshooting guide
│   ├── influx-token-management.md  # InfluxDB token management guide
│   ├── influxdb-querying.md        # InfluxDB querying guide
│   └── grafana-influxdb-setup.md   # Grafana InfluxDB setup guide
└── mosquitto/                      # Mosquitto broker files
    ├── config/
    │   └── mosquitto.conf          # Mosquitto broker configuration
    ├── data/                       # Persistent data storage
    └── log/                        # Log files
```

## Prerequisites

- Docker and Docker Compose installed
- Python 3.7+ installed
- pipenv (Python virtual environment manager)

> **📋 Environment Setup**: If you're setting up this project on Linux/Ubuntu, check out our detailed [Environment Setup Guide](docs/Environment-setup-Linux.md) for step-by-step installation instructions for Docker, Python, and pipenv.

## Initial Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd mqtt2Grafana

# Setup environment variables (includes your InfluxDB token)
./setup_env.sh

# Or manually create .env file
cp config/env.example .env
# Edit .env file with your credentials

```

**Note**: The `.env` file is automatically ignored by git. The `setup_env.sh` script will create it with your InfluxDB token.

> **🔐 Security Note**: For production use, consider creating a custom InfluxDB token instead of using the default one. See the [InfluxDB Token Management](#influxdb-token-management) section for detailed instructions.

## Project Organization

The project is organized into logical groups for better maintainability:

- **`src/scripts/`** - Main application scripts (MQTT publishers, subscribers, data collectors)
- **`src/utils/`** - Utility scripts and helper tools
- **`config/`** - Configuration files and templates
- **`docs/`** - Documentation & troubleshooting guides
- **`mosquitto/`** - Mosquitto MQTT broker configuration and data

## Setup Instructions

### 2. Install Python Dependencies

- Install pipenv if you don't have it

  ```bash
  pip install pipenv
  ```

- Install dependencies in virtual environment

  ```bash
  pipenv install
  ```

### 3. Start All Services

**macOS/Windows:**

```bash
docker-compose -p mqtt2grafna up -d
```

**Linux:**

```bash
docker compose -p mqtt2grafna up -d
```

> **Note**: On Linux, use `docker compose` (without hyphen). On macOS/Windows, use `docker-compose` (with hyphen).

This will start:

- **Mosquitto MQTT broker** on port 1883 (MQTT) and 9001 (WebSocket)
- **InfluxDB** on port 8086 (time-series database)
- **Grafana** on port 3000 (web interface)
- **Telegraf** (data collector) - automatically collects MQTT data and writes to InfluxDB

### 4. Verify Services are Running

**macOS/Windows:**

```bash
docker ps
```

**Linux:**

```bash
docker ps
```

You should see the `mqtt2grafna_mosquitto`, `mqtt2grafna_influxdb`, `mqtt2grafna_grafana`, and `mqtt2grafna_telegraf` containers running.

### 5. Setup Grafana (One-time setup)

```bash
pipenv run python src/scripts/setup_grafana.py
```

This will:

- Clean up any existing InfluxDB data for fresh start
- Configure InfluxDB as a data source in Grafana
- Create a temperature monitoring dashboard
- Handle existing data sources by recreating them

## How to run :

**Start Services (includes Telegraf for data collection):**

**macOS/Windows:**

```bash
docker-compose -p mqtt2grafna up -d
```

**Linux:**

```bash
docker compose -p mqtt2grafna up -d
```

> **📊 Data Collection**: Telegraf automatically collects MQTT data and writes to InfluxDB. No need to run the Python data collector script.

**Terminal 2 - Start Subscriber A (Temperature):**

- Subscribes to "data/temperature" topic

  ```bash
  pipenv run python src/scripts/subscriber_A.py
  ```

**Terminal 3 - Start Subscriber B (Humidity):**

- Subscribes to "data/humidity" topic

  ```bash
  pipenv run python src/scripts/subscriber_B.py
  ```

**Terminal 4 - Start the Publisher:**

- publisher - randomly generates data and publishes to separate topics

  ```bash
  pipenv run python src/scripts/publisher.py
  ```

**Browser - View Grafana Dashboard:**
Open http://localhost:3000

## Accessing Services via Localhost

### Grafana Dashboard

- **URL**: `http://localhost:3000` or `http://HOST_IP:3000`
- **Username**: `admin`
- **Password**: `admin`
- **Features**: Real-time temperature monitoring, customizable dashboards

### InfluxDB Web Interface

- **URL**: `http://localhost:8086` or `http://HOST_IP:8086`
- **Username**: `admin`
- **Password**: `adminpassword`
- **Organization**: `myorg`
- **Features**: Data exploration, query editor, bucket management

> **💡 Tip**: Both services are accessible via web browser. Grafana is for visualization, while InfluxDB provides data storage and query capabilities.

## Documentation

- [Environment Setup (Linux)](docs/Environment-setup-Linux.md)
- [InfluxDB Token Management](docs/influx-token-management.md)
- [InfluxDB Querying Guide](docs/influxdb-querying.md)
- [Grafana InfluxDB Setup](docs/grafana-influxdb-setup.md)
- [SQL Setup Guide (InfluxDB v3)](docs/sql-setup-guide.md)
- [Temperature CSV Guide](docs/temperature-csv-guide.md)
- [Best Practices](docs/bestpractices.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Remote Access](docs/remoteaccess.md)

## What the Application Does

### Publisher (`src/scripts/publisher.py`)

- Connects to the MQTT broker
- Publishes temperature data to "data/temperature" topic every second
- Publishes humidity data to "data/humidity" topic every second
- Each topic contains its specific data type with timestamp
- Uses QoS level 1 for reliable message delivery

### Telegraf Data Collector

- **Automatically runs** as part of the Docker Compose stack
- **Subscribes to MQTT** messages from both "data/temperature" and "data/humidity" topics
- **Parses JSON data** and extracts temperature and humidity values separately
- **Writes to InfluxDB** with proper timestamps and tags for each measurement type
- **Reliable and efficient** data collection with built-in error handling
- **No manual intervention** required - starts automatically with services

### Subscriber A (`src/scripts/subscriber_A.py`)

- Connects to the MQTT broker
- Subscribes to the "data/temperature" topic
- Receives and displays temperature data only
- Shows temperature value and timestamp

### Subscriber B (`src/scripts/subscriber_B.py`)

- Connects to the MQTT broker
- Subscribes to the "data/humidity" topic
- Receives and displays humidity data only
- Shows humidity value and timestamp

## Sample Output

### Publisher Output:

```
Connecting to MQTT broker at localhost:1883...
Connected to MQTT broker at localhost:1883
Publishing messages to topics:
   Temperature: data/temperature
   Humidity: data/humidity
Press Ctrl+C to stop...

Message #1 published:
   Temperature Topic: data/temperature
     Temperature: 23.45°C
     Timestamp: 2024-01-15T10:30:45.123456
   Humidity Topic: data/humidity
     Humidity: 65.32%
     Timestamp: 2024-01-15T10:30:45.123456
```

### Subscriber A Output (Temperature Data):

```
Connecting to MQTT broker at localhost:1883...
Connected to MQTT broker at localhost:1883
Subscribed to topic: data/temperature
Starting message loop...
Press Ctrl+C to stop...

Temperature data received:
   Temperature: 23.45°C
   Timestamp: 2024-01-15T10:30:45.123456
```

### Subscriber B Output (Humidity Data):

```
Connecting to MQTT broker at localhost:1883...
Connected to MQTT broker at localhost:1883
Subscribed to topic: data/humidity
Starting message loop...
Press Ctrl+C to stop...

Humidity data received:
   Humidity: 65.32%
   Timestamp: 2024-01-15T10:30:45.123456
```

## Data Model and Storage

### InfluxDB Data Schema

**Measurement**: `temperature`

- **Field**: `value` (float) - Temperature in Celsius
- **Tag**: `location` (string) - Location identifier
- **Timestamp**: ISO 8601 format

**Example Data Point**:

```
measurement: temperature
tags: location="Weather Station 1"
fields: value=23.45
time: 2024-01-15T10:30:45.123456Z
```

### Testing Data Storage

To verify data is being stored in InfluxDB:

```bash
pipenv run python src/scripts/test_influxdb.py
```

This script will:

- Test InfluxDB connectivity
- Query recent temperature data
- Display data summary (count, min, max, average)

## Grafana Visualization

### Accessing Grafana

#### Local Access

- **URL**: http://localhost:3000 or `http://YOUR_HOST_IP:3000`
- **Username**: `admin`
- **Password**: `admin`

> **🌐 Remote Access**: To access Grafana and other services from other devices on your network (phones, tablets, other computers), see our comprehensive [Remote Access Guide](docs/remoteaccess.md) for detailed instructions on IP configuration, firewall setup, and troubleshooting.

### Dashboard Features

- Real-time temperature monitoring
- Time-series visualization
- Auto-refresh every 5 seconds
- Temperature data from the last hour
- Celsius unit display

### Data Flow

1. **Publisher** → MQTT topics `data/temperature` and `data/humidity`
2. **Data Collector** → InfluxDB time-series database (separate measurements)
3. **Grafana** → Visualizes data from InfluxDB

### Example InfluxDB Queries

For comprehensive query examples and advanced InfluxDB usage, see our [InfluxDB Querying Guide](docs/influxdb-querying.md).

**Basic query examples:**

```flux
# Query recent temperature data (last hour)
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> sort(columns: ["_time"])

# Query recent humidity data (last hour)
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "humidity")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> sort(columns: ["_time"])
```

<!-- **Query average temperature by location**:

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "value")
  |> group(columns: ["location"])
  |> mean()
```

**Query temperature statistics**:

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "value")
  |> group()
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
``` -->

## InfluxDB Token Management

For security in production environments, you should create a custom InfluxDB token instead of using the default one.

> **🔐 Quick Setup**: Choose your preferred method:
>
> - **CLI**: `docker exec -it mqtt2grafna_influxdb influx` then `influx auth create --org myorg --bucket weather_data --write-bucket weather_data`
> - **Web Interface**: http://localhost:8086 → Data → API Tokens
> - **Automated Script**: `pipenv run python src/scripts/setup_influxdb_token.py`

For detailed instructions on token creation, management, and security best practices, see our comprehensive [InfluxDB Token Management Guide](docs/influx-token-management.md).

### Default Token (Development Only)

The current setup uses a default token: `my-super-secret-auth-token`

⚠️ **Warning**: This token is for development only. Always use a custom token for production environments.

## Configuration

The Mosquitto broker is configured in `mosquitto/config/mosquitto.conf`:

- Anonymous connections allowed
- MQTT on port 1883
- WebSocket support on port 9001
- Persistent storage enabled
- Logging to both file and stdout

### Python Script Settings

You can modify the following variables in all Python scripts:

- `MQTT_BROKER`: Broker hostname (default: "localhost")
- `MQTT_PORT`: Broker port (default: 1883)
- `MQTT_TOPIC_TEMPERATURE`: Temperature topic name (default: "data/temperature")
- `MQTT_TOPIC_HUMIDITY`: Humidity topic name (default: "data/humidity")
- `MQTT_CLIENT_ID`: Client identifier

## Troubleshooting

> **🔧 Need Help?**: For comprehensive troubleshooting, including Docker issues, network problems, and data recovery, see our detailed [Troubleshooting Guide](docs/troubleshooting.md).

### Quick Fixes

**Services not starting?**

**macOS/Windows:**

```bash
docker-compose ps
docker-compose logs
```

**Linux:**

```bash
docker compose ps
docker compose logs
```

**Can't connect to MQTT?**

**macOS/Windows:**

```bash
docker-compose restart mosquitto
```

**Linux:**

```bash
docker compose restart mosquitto
```

**Grafana not showing data?**

```bash
pipenv run python src/scripts/data_collector.py
```

**InfluxDB authentication issues?**

- Check if the token in `telegraf/telegraf.conf` matches your InfluxDB token
- Verify token permissions in InfluxDB web interface (http://localhost:8086)
- See [InfluxDB Token Management Guide](docs/influx-token-management.md) for token creation instructions

**Python import errors?**

```bash
pipenv install
```

## Stopping the Application

1. **Stop Python scripts**: Press `Ctrl+C` in the terminal running the scripts
2. **Stop MQTT broker**:

   **macOS/Windows:**

   ```bash
   docker-compose down
   ```

   **Linux:**

   ```bash
   docker compose down
   ```

## Clean Up

To completely remove the application and data:

**macOS/Windows:**

```bash
# Method 1: Stop all containers first
docker stop $(docker ps -aq)
docker-compose down -v

# Method 2: Use --remove-orphans flag
docker-compose down -v --remove-orphans

# Method 3: Force remove (if above methods fail)
docker-compose down -v --force
```

**Linux:**

```bash
# Method 1: Stop all containers first
sudo docker stop $(sudo docker ps -aq)
docker compose down -v

# Method 2: Use --remove-orphans flag
docker compose down -v --remove-orphans

# Method 3: Force remove (if above methods fail)
docker compose down -v --force
```

> **💡 Tip**: If you still get "volume in use" errors, use the complete cleanup sequence:
>
> ```bash
> # Complete cleanup (WARNING: This removes ALL Docker data)
> docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker volume prune -f
> ```

**Remove virtual environment:**

```bash
pipenv --rm
```

**Remove the project directory:**

```bash
rm -rf /path/to/mqtt2Grafana
```

## Next Steps

<!-- - Add authentication to the MQTT broker
- Implement message persistence
- Add SSL/TLS encryption
- Create a web interface using WebSocket connections -->

- Scale to multiple publishers/subscribers
- Add message filtering and routing

```
docker restart mqtt2grafna_telegraf

docker exec mqtt2grafna_mosquitto mosquitto_sub -t "data/temperature" -C 3

docker logs mqtt2grafna_telegraf --since 10m | grep -E "(Connected|Received|Error|Warning)"

# see if we can write directly to InfluxDB:
pipenv run python src/scripts/test_write_influxdb.py

# check if Telegraf is receiving MQTT messages:
docker logs mqtt2grafna_telegraf --tail 10

# check if the publisher is still running and if Telegraf is receiving data:
ps aux | grep publisher

# check if there are any recent errors and also verify that the publisher is still running:
docker logs mqtt2grafna_telegraf --since 5m 2>&1 | grep -i error

#wait a bit longer and test again, as it might take a moment for data to start flowing:
sleep 15 && pipenv run python src/scripts/test_influxdb_data.py


#check if there are any errors in the Telegraf logs
docker logs mqtt2grafna_telegraf 2>&1 | grep -i error

#querying via terminal
docker exec -it mqtt2grafna_influxdb influx query 'show measurements' --org myorg --token $INFLUXDB_TOKEN

```
