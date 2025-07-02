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
│   │   ├── subscriber_A.py         # MQTT subscriber for full data
│   │   ├── subscriber_B.py         # MQTT subscriber for temperature only
│   │   ├── data_collector.py       # MQTT to InfluxDB data collector
│   │   ├── setup_grafana.py        # Grafana setup script
│   │   └── test_influxdb.py        # InfluxDB testing script
│   └── utils/                      # Utility scripts
│       └── start_visualization.sh  # Startup script
├── config/                         # Configuration files
│   └── env.example                 # Environment variables template
├── docs/                           # Documentation
│   └── troubleshooting.md          # Troubleshooting guide
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
cd dockerProject

# Create environment file
cp config/env.example .env

# Edit .env file with your credentials (optional - defaults are provided)

```

**Note**: The `.env` is automatically ignored by git. Default values are provided, customize.

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

```bash
docker-compose -p mqtt2grafna up -d
```

This will start:

- **Mosquitto MQTT broker** on port 1883 (MQTT) and 9001 (WebSocket)
- **InfluxDB** on port 8086 (time-series database)
- **Grafana** on port 3000 (web interface)

### 4. Verify Services are Running

```bash
docker-compose ps
```

You should see the `mqtt_broker`, `influxdb`, and `grafana` containers running.

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

**Terminal 1 - Start Data Collector:**

- MQTT -> Influx Data collector

  ```bash
  pipenv run python src/scripts/data_collector.py
  ```

**Terminal 2 - Start Subscriber A:**

- subscriber for full data

  ```bash
  pipenv run python src/scripts/subscriber_A.py
  ```

**Terminal 3 - Start Subscriber B:**

- subscriber for temp

  ```bash
  pipenv run python src/scripts/subscriber_B.py
  ```

**Terminal 4 - Start the Publisher:**

- publisher - randomly generates data and publishes to topic

  ```bash
  pipenv run python src/scripts/publisher.py
  ```

**Browser - View Grafana Dashboard:**
Open http://localhost:3000

## What the Application Does

### Publisher (`src/scripts/publisher.py`)

- Connects to the MQTT broker
- Publishes weather data to the "data/temperature" topic every second
- Data includes: temperature, humidity, pressure, wind speed, location, and timestamp
- Uses QoS level 1 for reliable message delivery

### Data Collector (`src/scripts/data_collector.py`)

- Subscribes to MQTT messages from the "data/temperature" topic
- Extracts temperature data and stores it in InfluxDB
- Enables real-time visualization in Grafana
- Runs continuously to collect time-series data

### Subscriber A (`src/scripts/subscriber_A.py`)

- Connects to the MQTT broker
- Subscribes to the "data/temperature" topic
- Receives and displays all published data (full weather information)
- Shows temperature, humidity, pressure, wind speed, location, and timestamp

### Subscriber B (`src/scripts/subscriber_B.py`)

- Connects to the MQTT broker
- Subscribes to the "data/temperature" topic
- Receives the same messages but only displays temperature-related information
- Shows only temperature, timestamp, and location

## Sample Output

### Publisher Output:

```
Connecting to MQTT broker at localhost:1883...
Connected to MQTT broker at localhost:1883
Publishing messages to topic: data/temperature
Press Ctrl+C to stop...

Message #1 published:
   Topic: data/temperature
   Temperature: 23.45°C
```

### Subscriber A Output (Full Data):

```
Connecting to MQTT broker at localhost:1883...
Connected to MQTT broker at localhost:1883
Subscribed to topic: data/temperature
Starting message loop...
Press Ctrl+C to stop...

Message received from topic: data/temperature
   QoS: 1
   Timestamp: 2024-01-15 10:30:45
   Full Data:
     timestamp: 2024-01-15T10:30:45.123456
     temperature: 23.45
     humidity: 65.32
     pressure: 1013.25
     wind_speed: 8.7
     location: Weather Station 1
```

### Subscriber B Output (Temperature Only):

```
Connecting to MQTT broker at localhost:1883...
Connected to MQTT broker at localhost:1883
Subscribed to topic: data/temperature
Starting message loop...
Press Ctrl+C to stop...

Temperature data received:
   Temperature: 23.45°C
   Timestamp: 2024-01-15T10:30:45.123456
   Location: Weather Station 1
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

1. **Publisher** → MQTT topic `data/temperature`
2. **Data Collector** → InfluxDB time-series database
3. **Grafana** → Visualizes data from InfluxDB

### Example InfluxDB Queries

**Query recent temperature data (last hour)**:

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "value")
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
- `MQTT_TOPIC`: Topic name (default: "data/temperature")
- `MQTT_CLIENT_ID`: Client identifier

## Troubleshooting

> **🔧 Need Help?**: For comprehensive troubleshooting, including Docker issues, network problems, and data recovery, see our detailed [Troubleshooting Guide](docs/troubleshooting.md).

### Quick Fixes

**Services not starting?**

```bash
docker-compose ps
docker-compose logs
```

**Can't connect to MQTT?**

```bash
docker-compose restart mosquitto
```

**Grafana not showing data?**

```bash
pipenv run python src/scripts/data_collector.py
```

**Python import errors?**

```bash
pipenv install
```

## Stopping the Application

1. **Stop Python scripts**: Press `Ctrl+C` in the terminal running the scripts
2. **Stop MQTT broker**:
   ```bash
   docker-compose down
   ```

## Clean Up

To completely remove the application and data:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (this will delete all data)
docker-compose down -v

# Remove virtual environment
pipenv --rm

# Remove the project directory
rm -rf /path/to/dockerProject
```

## Next Steps

<!-- - Add authentication to the MQTT broker
- Implement message persistence
- Add SSL/TLS encryption
- Create a web interface using WebSocket connections -->

- Scale to multiple publishers/subscribers
- Add message filtering and routing
