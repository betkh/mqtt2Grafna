# SQL Setup Guide for InfluxDB v3

This guide helps you set up Grafana to use **pure SQL queries** with InfluxDB v3.

## Prerequisites

- InfluxDB v3.0 or higher (supports Flight SQL protocol)
- Grafana 10.0 or higher
- Docker Compose setup

## Step 1: Update Docker Compose

Make sure your `docker-compose.yml` uses InfluxDB v3:

```yaml
influxdb:
  image: influxdb:3.0
  container_name: mqtt2grafna_influxdb
  ports:
    - "8086:8086" # InfluxDB HTTP API
    - "8087:8087" # Flight SQL port
  environment:
    - DOCKER_INFLUXDB_INIT_MODE=setup
    - DOCKER_INFLUXDB_INIT_USERNAME=admin
    - DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword
    - DOCKER_INFLUXDB_INIT_ORG=myorg
    - DOCKER_INFLUXDB_INIT_BUCKET=weather_data
    - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-auth-token
  volumes:
    - influxdb_data:/var/lib/influxdb3
```

## Step 2: Restart Services

```bash
# Stop current services
docker-compose down

# Remove old volumes (WARNING: This will delete existing data)
docker volume rm mqtt2grafna_influxdb_data

# Start with InfluxDB v3
docker-compose up -d
```

## Step 3: Configure Grafana Data Source

1. **Open Grafana**: http://localhost:3000
2. **Login**: admin/admin
3. **Go to**: Configuration → Data Sources
4. **Click**: "Add data source"
5. **Select**: "InfluxDB"

### Data Source Settings:

```yaml
Name: InfluxDB-SQL
URL: http://influxdb:8086
Access: Server (default)
Version: Flux (enables SQL support)
Token: my-super-secret-auth-token
Organization: myorg
Database: (leave empty)
User: (leave empty)
Password: (leave empty)
```

### Advanced Settings:

```yaml
Default Bucket: weather_data
Min time interval: 1s
Max time interval: 1h
```

## Step 4: Create Dashboard with SQL Queries

1. **Go to**: Dashboards → New Dashboard
2. **Click**: "Add new panel"
3. **Select**: Your InfluxDB data source
4. **Query Type**: Select "SQL" from dropdown

## Step 5: Sample SQL Queries

### Basic Temperature Query

```sql
SELECT time, temperature
FROM weather_data.autogen.temperature
WHERE time >= $__timeFrom() AND time <= $__timeTo()
ORDER BY time DESC
LIMIT 100
```

### Basic Humidity Query

```sql
SELECT time, humidity
FROM weather_data.autogen.humidity
WHERE time >= $__timeFrom() AND time <= $__timeTo()
ORDER BY time DESC
LIMIT 100
```

### Combined Temperature and Humidity

```sql
SELECT t.time, t.temperature, h.humidity
FROM weather_data.autogen.temperature t
JOIN weather_data.autogen.humidity h ON t.time = h.time
WHERE t.time >= $__timeFrom() AND t.time <= $__timeTo()
ORDER BY t.time DESC
LIMIT 100
```

### Average Temperature

```sql
SELECT AVG(temperature) as avg_temp
FROM weather_data.autogen.temperature
WHERE time >= $__timeFrom() AND time <= $__timeTo()
```

### Temperature Statistics

```sql
SELECT
    AVG(temperature) as avg_temp,
    MIN(temperature) as min_temp,
    MAX(temperature) as max_temp,
    COUNT(temperature) as count
FROM weather_data.autogen.temperature
WHERE time >= $__timeFrom() AND time <= $__timeTo()
```

### 5-Minute Temperature Averages

```sql
SELECT
    time_bucket('5 minutes', time) as time,
    AVG(temperature) as avg_temp
FROM weather_data.autogen.temperature
WHERE time >= $__timeFrom() AND time <= $__timeTo()
GROUP BY time_bucket('5 minutes', time)
ORDER BY time
```

### Temperature Above 25°C

```sql
SELECT time, temperature
FROM weather_data.autogen.temperature
WHERE time >= $__timeFrom() AND time <= $__timeTo()
  AND temperature > 25.0
ORDER BY time DESC
```

### Humidity Below 60%

```sql
SELECT time, humidity
FROM weather_data.autogen.humidity
WHERE time >= $__timeFrom() AND time <= $__timeTo()
  AND humidity < 60.0
ORDER BY time DESC
```

## Step 6: Grafana Variables for SQL

Use these Grafana time variables in your SQL queries:

- `$__timeFrom()` - Start time of the selected time range
- `$__timeTo()` - End time of the selected time range
- `$__timeFilter()` - Complete time filter condition

## Step 7: Example Dashboard Setup

**Panel 1: Temperature Time Series**

- **Query Type**: SQL
- **Query**: Basic Temperature Query above
- **Visualization**: Time series
- **Y-axis**: Temperature (°C)

**Panel 2: Humidity Time Series**

- **Query Type**: SQL
- **Query**: Basic Humidity Query above
- **Visualization**: Time series
- **Y-axis**: Humidity (%)

**Panel 3: Statistics Panel**

- **Query Type**: SQL
- **Query**: Temperature Statistics above
- **Visualization**: Stat
- **Fields**: avg_temp, min_temp, max_temp, count

**Panel 4: Combined Chart**

- **Query Type**: SQL
- **Query**: Combined Temperature and Humidity above
- **Visualization**: Time series
- **Y-axis**: Dual axis (Temperature left, Humidity right)

## Troubleshooting

### Error: "flightsql: rpc error: code = Unavailable"

**Cause**: InfluxDB v2.x doesn't support Flight SQL protocol

**Solution**:

1. Upgrade to InfluxDB v3.0+
2. Make sure Flight SQL port (8087) is exposed
3. Use correct data source configuration

### Error: "Connection refused"

**Cause**: Flight SQL service not running

**Solution**:

1. Check if InfluxDB v3 is running: `docker ps | grep influxdb`
2. Verify Flight SQL port is accessible: `curl http://localhost:8087`
3. Check InfluxDB logs: `docker logs mqtt2grafna_influxdb`

### Error: "Table not found"

**Cause**: Wrong table name format

**Solution**: Use correct table names:

- `weather_data.autogen.temperature`
- `weather_data.autogen.humidity`

## Verification Commands

### Test InfluxDB v3

```bash
# Check InfluxDB version
docker exec mqtt2grafna_influxdb influx version

# Test Flight SQL connection
curl -I http://localhost:8087
```

### Test SQL Queries

```bash
# Connect to InfluxDB and test SQL
docker exec -it mqtt2grafna_influxdb influx sql
```

## Key Differences from InfluxDB v2

- **Flight SQL Support**: Native SQL protocol
- **Table Names**: `bucket.retention_policy.measurement` format
- **SQL Functions**: Standard SQL functions (AVG, MIN, MAX, COUNT)
- **Time Functions**: `time_bucket()` for time grouping
- **Port**: Additional port 8087 for Flight SQL
