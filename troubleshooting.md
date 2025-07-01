# Troubleshooting Guide

## Grafana Not Showing Data

If you can't see data in Grafana, follow these steps:

### 1. Check if Data Collector is Running

The data collector must be running to bridge MQTT data to InfluxDB:

```bash
pipenv run python data_collector.py
```

You should see output like:

```
Connected to MQTT broker at localhost:1883
Subscribed to topic: data/temperature
Connected to InfluxDB at http://localhost:8086
Temperature data stored: 23.45°C at Weather Station 1 - 2024-01-15T10:30:45.123456
```

### 2. Test InfluxDB Data Storage

Check if data is actually being stored in InfluxDB:

```bash
pipenv run python test_influxdb.py
```

This will show:

- InfluxDB connection status
- Recent temperature data
- Data summary (count, min, max, average)

### 3. Verify Complete Data Flow

Run all components in this order:

**Terminal 1 - Start Data Collector:**

```bash
pipenv run python data_collector.py
```

**Terminal 2 - Start Publisher:**

```bash
pipenv run python publisher.py
```

**Terminal 3 - Test InfluxDB:**

```bash
pipenv run python test_influxdb.py
```

**Browser - Check Grafana:**

- Open http://localhost:3000
- Login with admin/admin
- Go to "Temperature Monitoring" dashboard

### 4. Check Docker Services

Verify all services are running:

```bash
docker-compose ps
```

You should see:

- `mqtt_broker` - Running
- `influxdb` - Running
- `grafana` - Running

### 5. Check Service Logs

**InfluxDB logs:**

```bash
docker-compose logs influxdb
```

**Grafana logs:**

```bash
docker-compose logs grafana
```

**MQTT logs:**

```bash
docker-compose logs mosquitto
```

### 6. Restart Services

If services aren't working properly:

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Setup Grafana again
pipenv run python setup_grafana.py
```

### 7. Manual Grafana Setup

If automatic setup fails, manually configure Grafana:

1. Open http://localhost:3000
2. Login with admin/admin
3. Go to Configuration → Data Sources
4. Add InfluxDB data source:

   - URL: http://influxdb:8086
   - Access: Server (default)
   - Version: Flux
   - Organization: myorg
   - Default Bucket: weather_data
   - Token: my-super-secret-auth-token

5. Create dashboard:
   - Add new panel
   - Select InfluxDB data source
   - Use this query:
   ```flux
   from(bucket: "weather_data")
     |> range(start: -1h)
     |> filter(fn: (r) => r["_measurement"] == "temperature")
     |> filter(fn: (r) => r["_field"] == "value")
   ```

## Common Error Messages

### "Connection refused"

- Check if Docker containers are running
- Verify ports are not in use by other applications

### "Import error"

- Install missing dependencies: `pipenv install`

### "No data found"

- Ensure data collector is running
- Check if publisher is sending data
- Verify InfluxDB bucket exists

### "Grafana setup failed"

- Wait for Grafana to be fully ready (may take 30-60 seconds)
- Check Grafana logs for specific errors
- Try manual setup as described above
