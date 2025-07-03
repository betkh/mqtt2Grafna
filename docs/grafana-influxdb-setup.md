# Grafana InfluxDB Setup Guide

This guide helps you properly configure Grafana to connect to InfluxDB and fix common connection issues.

## Grafana Data Source Configuration

### Step 1: Add InfluxDB Data Source

1. **Open Grafana**: http://localhost:3000
2. **Login**: admin/admin
3. **Go to**: Configuration → Data Sources
4. **Click**: "Add data source"
5. **Select**: "InfluxDB"

### Step 2: Configure InfluxDB Connection

**Basic Settings:**

- **Name**: `InfluxDB` (or any name you prefer)
- **URL**: `http://influxdb:8086` (use container name, not localhost)
- **Access**: `Server (default)`

**Auth Settings:**

- **Database**: Leave empty
- **User**: Leave empty
- **Password**: Leave empty
- **Token**: `your-custom-token-here` (the token you created via InfluxDB UI)
- **Organization**: `myorg`

**InfluxDB Details:**

- **Version**: `Flux`
- **Min time interval**: `1s`
- **Max time interval**: `1h`

### Step 3: Important Configuration Fixes

**To fix the HTTP/2 connection error:**

1. **Use Container Name**: Make sure URL is `http://influxdb:8086` (not localhost)
2. **Select Flux Version**: Choose "Flux" not "InfluxQL"
3. **Use Token Authentication**: Use your custom token, not username/password
4. **Set Organization**: Must be `myorg`

### Step 4: Test Connection

Click "Save & Test". You should see:

```
Data source is working
```

## Troubleshooting Connection Issues

### Error: "flightsql: rpc error: code = Unavailable"

**Cause**: Grafana trying to use HTTP/2 Flight SQL protocol with InfluxDB v2.x

**Solutions:**

#### Solution 1: Use Correct URL Format

```yaml
# Wrong
URL: http://localhost:8086

# Correct
URL: http://influxdb:8086
```

#### Solution 2: Use Flux Version

- **Version**: Select "Flux" (not "InfluxQL")
- **Query Language**: Use Flux queries in panels

#### Solution 3: Check Token Permissions

Make sure your token has:

- **Read** access to the `weather_data` bucket
- **Read** access to the `myorg` organization

#### Solution 4: Verify InfluxDB is Running

```bash
# Check if InfluxDB container is running
docker ps | grep influxdb

# Check InfluxDB logs
docker logs mqtt2grafna_influxdb
```

### Error: "401 Unauthorized"

**Cause**: Invalid token or missing permissions

**Solutions:**

1. **Verify token**: Copy token exactly from InfluxDB UI
2. **Check permissions**: Token needs read access to bucket and org
3. **Use correct organization**: Must be `myorg`

### Error: "Connection refused"

**Cause**: InfluxDB not accessible from Grafana

**Solutions:**

1. **Use container name**: `http://influxdb:8086`
2. **Check network**: Both containers should be on same Docker network
3. **Verify services**: Both Grafana and InfluxDB should be running

## Working Configuration Example

**Data Source Settings:**

```yaml
Name: InfluxDB
URL: http://influxdb:8086
Access: Server (default)
Version: Flux
Token: your-custom-token-here
Organization: myorg
Database: (leave empty)
User: (leave empty)
Password: (leave empty)
```

## Creating Your First Dashboard

### Step 1: Create Dashboard

1. **Go to**: Dashboards → New Dashboard
2. **Click**: "Add new panel"

### Step 2: Configure Query

1. **Data Source**: Select your InfluxDB data source
2. **Query Type**: Flux
3. **Enter Query**:

```flux
from(bucket: "weather_data")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
```

### Step 3: Save Dashboard

1. **Click**: "Apply"
2. **Click**: "Save dashboard"
3. **Name**: "Temperature Monitoring"

## Using SQL Queries in Grafana

### Step 1: Configure Data Source for SQL

**Data Source Settings:**

```yaml
Name: InfluxDB
URL: http://influxdb:8086
Access: Server (default)
Version: InfluxQL (for SQL queries)
Database: weather_data
User: admin
Password: admin123
Token: (leave empty)
Organization: (leave empty)
```

### Step 2: Create Dashboard with SQL Queries

1. **Go to**: Dashboards → New Dashboard
2. **Click**: "Add new panel"
3. **Select**: Your InfluxDB data source
4. **Query Type**: InfluxQL (SQL-like queries)

### Step 3: Sample SQL Queries

#### Basic Temperature Query

```sql
SELECT time, temperature
FROM temperature
WHERE $__timeFilter()
ORDER BY time DESC
LIMIT 100
```

#### Basic Humidity Query

```sql
SELECT time, humidity
FROM humidity
WHERE $__timeFilter()
ORDER BY time DESC
LIMIT 100
```

#### Combined Temperature and Humidity

```sql
SELECT time, temperature, humidity
FROM temperature, humidity
WHERE $__timeFilter()
ORDER BY time DESC
LIMIT 100
```

#### Average Temperature (Last Hour)

```sql
SELECT mean(temperature) as avg_temp
FROM temperature
WHERE $__timeFilter()
```

#### Temperature Statistics

```sql
SELECT
    mean(temperature) as avg_temp,
    min(temperature) as min_temp,
    max(temperature) as max_temp,
    count(temperature) as count
FROM temperature
WHERE $__timeFilter()
```

#### 5-Minute Temperature Averages

```sql
SELECT mean(temperature) as avg_temp
FROM temperature
WHERE $__timeFilter()
GROUP BY time(5m)
```

#### Temperature Above 25°C

```sql
SELECT time, temperature
FROM temperature
WHERE $__timeFilter()
  AND temperature > 25.0
ORDER BY time DESC
```

#### Humidity Below 60%

```sql
SELECT time, humidity
FROM humidity
WHERE $__timeFilter()
  AND humidity < 60.0
ORDER BY time DESC
```

### Step 4: Grafana Variables for InfluxQL

Use these Grafana time variables in your InfluxQL queries:

- `$__timeFilter()` - Complete time filter condition (recommended)
- `$__timeFrom()` - Start time of the selected time range
- `$__timeTo()` - End time of the selected time range
- `$__interval` - Time interval for grouping

### Step 5: Example Dashboard Setup

**Panel 1: Temperature Time Series**

- **Query Type**: InfluxQL
- **Query**: Basic Temperature Query above
- **Visualization**: Time series
- **Y-axis**: Temperature (°C)

**Panel 2: Humidity Time Series**

- **Query Type**: InfluxQL
- **Query**: Basic Humidity Query above
- **Visualization**: Time series
- **Y-axis**: Humidity (%)

**Panel 3: Statistics Panel**

- **Query Type**: InfluxQL
- **Query**: Temperature Statistics above
- **Visualization**: Stat
- **Fields**: avg_temp, min_temp, max_temp, count

**Panel 4: Combined Chart**

- **Query Type**: InfluxQL
- **Query**: Combined Temperature and Humidity above
- **Visualization**: Time series
- **Y-axis**: Dual axis (Temperature left, Humidity right)

### Step 6: Save and Test

1. **Click**: "Apply" to test the query
2. **Verify**: Data appears in the visualization
3. **Save**: Dashboard with a meaningful name

## Alternative: Using InfluxQL (Legacy)

If you prefer SQL-like queries:

**Data Source Settings:**

```yaml
Name: InfluxDB-SQL
URL: http://influxdb:8086
Access: Server (default)
Version: InfluxQL
Database: weather_data
User: admin
Password: adminpassword
```

**Query Example:**

```sql
SELECT mean(temperature) FROM temperature
WHERE $__timeFilter()
GROUP BY time($__interval)
```

## Verification Commands

### Test InfluxDB from Grafana Container

```bash
# Test if Grafana can reach InfluxDB
docker exec -it mqtt2grafna_grafana curl -I http://influxdb:8086/health

# Test with token
docker exec -it mqtt2grafna_grafana curl -H "Authorization: Token your-token" http://influxdb:8086/api/v2/buckets?org=myorg
```

### Check Network Connectivity

```bash
# Verify both containers are on same network
docker network ls
docker network inspect mqtt2grafna_network
```

## Common Issues and Solutions

### Issue: "No data points"

**Solution**: Check if data exists in InfluxDB

```bash
docker exec -it mqtt2grafna_influxdb influx query 'SELECT COUNT(*) FROM temperature' --org myorg --token your-token
```

### Issue: "Invalid query"

**Solution**: Use correct Flux syntax

```flux
# Correct Flux query
from(bucket: "weather_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "temperature")
```

### Issue: "Bucket not found"

**Solution**: Verify bucket name is `weather_data`

```bash
docker exec -it mqtt2grafna_influxdb influx query 'show buckets' --org myorg --token your-token
```

## References

- [Grafana InfluxDB Documentation](https://grafana.com/docs/grafana/latest/datasources/influxdb/)
- [InfluxDB Flux Language](https://docs.influxdata.com/flux/)
- [InfluxDB v2 API](https://docs.influxdata.com/influxdb/v2.7/api/)
