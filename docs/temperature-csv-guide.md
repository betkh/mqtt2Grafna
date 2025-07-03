# Temperature Data Collector Guide

This guide explains how to use the new temperature data collector that writes subscriber_A data to both CSV and InfluxDB.

## Overview

The `temperature_data_collector.py` script:

- Subscribes to temperature data from MQTT topic `data/temperature`
- Writes data to `temperature_data.csv` file
- Also writes data to InfluxDB for querying
- Provides real-time data collection and storage

## Setup

### 1. Install Dependencies

```bash
pipenv install
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Start Publisher (in one terminal)

```bash
pipenv run python src/scripts/publisher.py
```

### 4. Start Temperature Data Collector (in another terminal)

```bash
pipenv run python src/scripts/temperature_data_collector.py
```

## CSV File Format

The `temperature_data.csv` file contains:

| Column      | Description                     |
| ----------- | ------------------------------- |
| timestamp   | ISO timestamp from MQTT message |
| temperature | Temperature value in Celsius    |
| datetime    | Human-readable datetime         |

Example:

```csv
timestamp,temperature,datetime
2024-01-15T10:30:45.123456Z,23.45,2024-01-15 10:30:45
2024-01-15T10:30:46.123456Z,24.12,2024-01-15 10:30:46
```

## Querying CSV Data

Use the `query_csv.py` script to query your CSV data:

### Show Recent Data

```bash
# Show last 10 records
pipenv run python src/scripts/query_csv.py --recent 10

# Show last 50 records
pipenv run python src/scripts/query_csv.py --recent 50
```

### Show Statistics

```bash
pipenv run python src/scripts/query_csv.py --stats
```

### Filter by Temperature

```bash
# Show temperatures above 25°C
pipenv run python src/scripts/query_csv.py --min-temp 25

# Show temperatures below 20°C
pipenv run python src/scripts/query_csv.py --max-temp 20

# Show temperatures between 20-25°C
pipenv run python src/scripts/query_csv.py --min-temp 20 --max-temp 25
```

### Filter by Time

```bash
# Show data from last 2 hours
pipenv run python src/scripts/query_csv.py --hours 2

# Show data from specific time range
pipenv run python src/scripts/query_csv.py --start-time "2024-01-15 10:00:00" --end-time "2024-01-15 11:00:00"
```

### Export Filtered Data

```bash
# Export temperatures above 25°C to new CSV
pipenv run python src/scripts/query_csv.py --min-temp 25 --export high_temps.csv

# Export last hour data to new CSV
pipenv run python src/scripts/query_csv.py --hours 1 --export last_hour.csv
```

## Querying InfluxDB Data

Since the data is also written to InfluxDB, you can query it using:

### Using InfluxDB CLI

```bash
# Show recent temperature data
docker exec mqtt2grafna_influxdb influx query --org myorg --token $INFLUXDB_TOKEN 'from(bucket: "weather_data") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "temperature") |> limit(n: 10)'

# Get average temperature for the last hour
docker exec mqtt2grafna_influxdb influx query --org myorg --token $INFLUXDB_TOKEN 'from(bucket: "weather_data") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "temperature") |> mean()'
```
