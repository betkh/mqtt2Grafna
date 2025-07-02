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

### "Connection Refused"

- Make sure the Docker container is running
- Check if services are healthy: `docker-compose ps`
- Verify ports are not in use by other applications

### "Import Error"

- Install the required Python package: `pipenv install paho-mqtt`
- Ensure you're in the virtual environment: `pipenv shell`
- Check if all dependencies are installed: `pipenv install`

### "Port Already in Use"

- Check if port 1883 is available: `lsof -i :1883`
- Stop conflicting services
- Use different ports in docker-compose.yml if needed

## Docker Service Issues

### Service Not Starting

```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs [service_name]

# Follow logs in real-time
docker-compose logs -f [service_name]
```

### Container Health Issues

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Restart specific service
docker-compose restart [service_name]

# Rebuild and restart
docker-compose up -d --build [service_name]
```

### Volume and Data Issues

```bash
# Check volume status
docker volume ls | grep mqtt2grafna

# Remove and recreate volumes (WARNING: This will delete data)
docker-compose down -v
docker-compose up -d

# Backup data before cleanup
docker run --rm -v mqtt2grafna_influxdb_data:/data -v $(pwd):/backup alpine tar czf /backup/influxdb_backup.tar.gz -C /data .
```

## Network and Connectivity Issues

### MQTT Connection Problems

```bash
# Test MQTT connectivity
mosquitto_pub -h localhost -p 1883 -t "test/topic" -m "test message"

# Check MQTT broker logs
docker-compose logs mosquitto

# Verify MQTT configuration
cat mosquitto/config/mosquitto.conf
```

### InfluxDB Connection Issues

```bash
# Test InfluxDB connectivity
curl -I http://localhost:8086/health

# Check InfluxDB logs
docker-compose logs influxdb

# Test InfluxDB API
curl -H "Authorization: Token my-super-secret-auth-token" \
  "http://localhost:8086/api/v2/buckets?org=myorg"
```

### Grafana Access Issues

```bash
# Test Grafana connectivity
curl -I http://localhost:3000

# Check Grafana logs
docker-compose logs grafana

# Verify Grafana configuration
docker exec mqtt2grafna_grafana cat /etc/grafana/grafana.ini | grep -E "(server|http)"
```

## Python Script Issues

### Virtual Environment Problems

```bash
# Ensure you're in the virtual environment
pipenv shell

# Reinstall dependencies
pipenv install --dev

# Check Python version
pipenv run python --version
```

### Script Execution Issues

```bash
# Run with verbose output
pipenv run python -v src/scripts/publisher.py

# Check script permissions
ls -la src/scripts/

# Test individual components
pipenv run python -c "import paho.mqtt.client; print('MQTT library OK')"
```

## Performance Issues

### High Resource Usage

```bash
# Check container resource usage
docker stats

# Monitor system resources
top
htop

# Check disk space
df -h
docker system df
```

### Slow Response Times

- Check network latency between components
- Verify sufficient system resources
- Consider increasing container memory limits
- Monitor InfluxDB query performance

## Recovery Procedures

### Complete Reset

If everything is broken and you need a fresh start:

```bash
# Stop all services
docker-compose down

# Remove all containers, networks, and volumes
docker-compose down -v --remove-orphans

# Clean up Docker system
docker system prune -f

# Rebuild everything
docker-compose up -d --build

# Wait for services to be ready
sleep 30

# Setup Grafana
pipenv run python src/scripts/setup_grafana.py
```

### Data Recovery

```bash
# Backup InfluxDB data
docker run --rm -v mqtt2grafna_influxdb_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/influxdb_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore InfluxDB data
docker run --rm -v mqtt2grafna_influxdb_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/influxdb_backup_YYYYMMDD_HHMMSS.tar.gz -C /data
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs**: Use `docker-compose logs [service_name]`
2. **Verify your setup**: Follow the [Environment Setup Guide](Environment-setup-Linux.md)
3. **Review best practices**: Check [Best Practices](bestpractices.md)
4. **Check remote access**: See [Remote Access Guide](remoteaccess.md)
5. **Search existing issues**: Look for similar problems in the documentation

### Useful Commands Summary

```bash
# Quick health check
docker-compose ps && curl -I http://localhost:3000 && curl -I http://localhost:8086/health

# View all logs
docker-compose logs

# Check resource usage
docker stats --no-stream

# Test connectivity
ping localhost && telnet localhost 1883 && telnet localhost 3000
```
