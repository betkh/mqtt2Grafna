# InfluxDB Querying Guide

This guide shows how to access and query data from InfluxDB in the MQTT to Grafana project.

## Accessing InfluxDB

### Web Interface

- **URL**: http://localhost:8086
- **Username**: `admin`
- **Password**: `adminpassword`
- **Organization**: `myorg`
- **Bucket**: `weather_data`

### Command Line Access

```bash
# Connect to InfluxDB container
docker exec -it mqtt2grafna_influxdb influx

# Or if you want to see the tables directly (with organization)
docker exec -it mqtt2grafna_influxdb influx query 'show measurements' --org myorg
```

### Important Note

All InfluxDB CLI commands require the `--org myorg` parameter to specify the organization. This is required for InfluxDB v2.x.

### Working Examples

```bash
# List all measurements (tables) - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'show measurements' --org myorg --token YOUR_TOKEN

# View recent temperature data - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'SELECT * FROM temperature ORDER BY time DESC LIMIT 5' --org myorg --token YOUR_TOKEN

# View recent humidity data - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'SELECT * FROM humidity ORDER BY time DESC LIMIT 5' --org myorg --token YOUR_TOKEN
```

### Using Your Custom Token

Since you created a custom token via the UI, you need to use that token instead of the default one. Replace `YOUR_TOKEN` in the commands above with your actual token.

**To find your token:**

1. Go to http://localhost:8086
2. Login with admin/adminpassword
3. Go to **Data** → **API Tokens**
4. Copy your custom token

## Viewing Tables and Data Structure

### List All Measurements (Tables)

```bash
# Via CLI (with organization and token) - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'show measurements' --org myorg --token YOUR_TOKEN

# Or connect to InfluxDB first
docker exec -it mqtt2grafna_influxdb influx
# Then run:
use myorg
use weather_data
show measurements

# Using influxdb3 query command (alternative method) - Replace YOUR_TOKEN with your custom token
docker-compose exec mqtt2grafna_influxdb influxdb3 query "SHOW TABLES" --database weather_data --token YOUR_TOKEN
```

### View Data Structure

```bash
# Connect to InfluxDB
docker exec -it mqtt2grafna_influxdb influx

# Switch to your organization and bucket
use myorg
use weather_data

# Show the schema of temperature measurement
show tag keys from temperature
show field keys from temperature

# Show the schema of humidity measurement
show tag keys from humidity
show field keys from humidity
```

### View Recent Data

```bash
# Connect to InfluxDB
docker exec -it mqtt2grafna_influxdb influx

# View last 10 temperature records
select * from temperature order by time desc limit 10

# View last 10 humidity records
select * from humidity order by time desc limit 10
```

## Query Examples

### Using Flux (InfluxDB's Native Language)

#### 1. View All Recent Data (Last Hour)

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> sort(columns: ["_time"])
```

#### 2. Basic Temperature Query

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> limit(n: 10)
```

#### 3. Basic Humidity Query

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "humidity")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> limit(n: 10)
```

#### 4. Temperature and Humidity Together

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature" or r["_measurement"] == "humidity")
  |> sort(columns: ["_time"])
```

#### 5. Average Temperature (Last Hour)

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> mean()
```

#### 6. Average Humidity (Last Hour)

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "humidity")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> mean()
```

#### 7. Temperature Statistics (Last Hour)

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> group()
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

#### 8. 5-Minute Temperature Averages

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
```

#### 9. Maximum Temperature (Last 24 Hours)

```flux
from(bucket: "weather_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> max()
```

#### 10. Minimum Humidity (Last Hour)

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "humidity")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> min()
```

#### 11. Temperature Above 25°C

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> filter(fn: (r) => r["_value"] > 25.0)
```

#### 12. Humidity Below 60%

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "humidity")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> filter(fn: (r) => r["_value"] < 60.0)
```

#### 13. Last 50 Records of Each Measurement

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature" or r["_measurement"] == "humidity")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 50)
```

#### 14. Data Count by Measurement

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> group(columns: ["_measurement"])
  |> count()
```

#### 15. Temperature Trend (Moving Average)

```flux
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> movingAverage(n: 5)
```

### Using SQL (InfluxQL)

#### 1. Basic Temperature Query

```sql
SELECT * FROM temperature
WHERE time > now() - 1h
ORDER BY time DESC
LIMIT 10
```

#### 2. Average Temperature (Last Hour)

```sql
SELECT MEAN(temperature) FROM temperature
WHERE time > now() - 1h
```

#### 3. Temperature and Humidity Together

```sql
SELECT time, temperature FROM temperature
WHERE time > now() - 1h
UNION ALL
SELECT time, humidity FROM humidity
WHERE time > now() - 1h
ORDER BY time DESC
```

## Running Queries

### Via Web Interface

1. Go to http://localhost:8086
2. Click on "Data Explorer"
3. Select your bucket: `weather_data`
4. Choose "Script Editor" mode
5. Paste your Flux query and click "Submit"

### Via Command Line

```bash
# Run Flux query (with organization and token) - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'from(bucket: "weather_data") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "temperature")' --org myorg --token YOUR_TOKEN

# Run SQL query (with organization and token) - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'SELECT * FROM temperature WHERE time > now() - 1h LIMIT 5' --org myorg --token YOUR_TOKEN
```

### Via Python

```python
from influxdb_client import InfluxDBClient

# Connect to InfluxDB
client = InfluxDBClient(
    url="http://localhost:8086",
    token="your-token-here",
    org="myorg"
)

# Run Flux query
query_api = client.query_api()
query = '''
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> limit(n: 5)
'''

result = query_api.query(query=query, org="myorg")
for table in result:
    for record in table.records:
        print(f"Time: {record.get_time()}, Temperature: {record.get_value()}")
```

## Data Export

### Export to CSV

```bash
# Export temperature data to CSV (with organization and token) - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'SELECT * FROM temperature WHERE time > now() - 1h' --org myorg --token YOUR_TOKEN --format csv > temperature_data.csv

# Export humidity data to CSV (with organization and token) - Replace YOUR_TOKEN with your custom token
docker exec -it mqtt2grafna_influxdb influx query 'SELECT * FROM humidity WHERE time > now() - 1h' --org myorg --token YOUR_TOKEN --format csv > humidity_data.csv
```

## Quick Reference

### Common Commands

```bash
# List measurements
show measurements

# Show data structure
show tag keys from temperature
show field keys from temperature

# View recent data
SELECT * FROM temperature ORDER BY time DESC LIMIT 10

# Get average
SELECT MEAN(temperature) FROM temperature WHERE time > now() - 1h
```

### Time Ranges

- Last hour: `WHERE time > now() - 1h`
- Last 24 hours: `WHERE time > now() - 24h`
- Today: `WHERE time > today()`
- Specific date: `WHERE time > '2024-01-15T00:00:00Z'`

## Troubleshooting

### No Data Found?

```bash
# Check if measurements exist
show measurements

# Check if bucket has data
show retention policies

# Verify time range
SELECT COUNT(*) FROM temperature WHERE time > now() - 1h
```

### Permission Issues?

- Verify your token has read access
- Check organization and bucket names
- Ensure InfluxDB is running: `docker ps | grep influxdb`
