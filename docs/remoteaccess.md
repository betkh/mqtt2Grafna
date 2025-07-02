# Remote Access Guide

This guide explains how to access the MQTT2Grafana services from other devices on your network, such as phones, tablets, or other computers.

## Overview

The Docker Compose setup exposes several services that can be accessed remotely:

- **Grafana**: Web interface for data visualization (Port 3000)
- **InfluxDB**: Time-series database API (Port 8086)
- **Mosquitto MQTT**: Message broker (Port 1883)

## Finding Your Host IP Address

### Linux/macOS

```bash
# Method 1: Using ifconfig
ifconfig | grep "inet " | grep -v 127.0.0.1

# Method 2: Using hostname
hostname -I

# Method 3: Using ip command
ip route get 1.1.1.1 | awk '{print $7; exit}'
```

### Windows

```bash
# Using ipconfig
ipconfig | findstr "IPv4"

# Alternative: Using PowerShell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"}
```

### Example Output

```
192.168.1.100    # Your local network IP
10.0.0.15        # Alternative local network IP
```

## Accessing Services Remotely

### 1. Grafana Dashboard

**URL Format**: `http://YOUR_HOST_IP:3000`

**Example**: `http://192.168.1.100:3000`

**Default Credentials**:

- Username: `admin`
- Password: `admin`

**Features Available Remotely**:

- Real-time temperature monitoring
- Dashboard customization
- Data exploration
- User management (if configured)

### 2. InfluxDB API

**URL Format**: `http://YOUR_HOST_IP:8086`

**Example**: `http://192.168.1.100:8086`

**Available Endpoints**:

- `/health` - Health check
- `/api/v2/` - API endpoints
- `/ui/` - Web interface (if enabled)

**Authentication**:

- Token: `my-super-secret-auth-token`
- Organization: `myorg`

### 3. MQTT Broker

**Host**: `YOUR_HOST_IP`
**Port**: `1883`

**Example**: `192.168.1.100:1883`

**Connection Details**:

- Protocol: MQTT
- Authentication: Anonymous (default)
- QoS: 0, 1, or 2 supported

## Network Configuration

### Firewall Setup

#### Ubuntu/Debian (ufw)

```bash
# Allow Grafana port
sudo ufw allow 3000

# Allow InfluxDB port
sudo ufw allow 8086

# Allow MQTT port
sudo ufw allow 1883

# Check status
sudo ufw status
```

#### macOS (pfctl)

```bash
# Edit /etc/pf.conf to add rules
# Example rule: pass in proto tcp from any to any port 3000

# Reload rules
sudo pfctl -f /etc/pf.conf
sudo pfctl -e
```

#### Windows (Firewall)

```powershell
# Allow Grafana
netsh advfirewall firewall add rule name="Grafana" dir=in action=allow protocol=TCP localport=3000

# Allow InfluxDB
netsh advfirewall firewall add rule name="InfluxDB" dir=in action=allow protocol=TCP localport=8086

# Allow MQTT
netsh advfirewall firewall add rule name="MQTT" dir=in action=allow protocol=TCP localport=1883
```

### Docker Network Configuration

The services are configured to bind to all network interfaces (`0.0.0.0`):

```yaml
# From docker-compose.yml
ports:
  - "3000:3000" # Grafana
  - "8086:8086" # InfluxDB
  - "1883:1883" # MQTT
```

This allows external connections by default.

## Security Considerations

### Production Recommendations

1. **Change Default Passwords**:

   ```bash
   # Grafana: Change via web interface
   # InfluxDB: Set custom token
   # MQTT: Add authentication
   ```

2. **Use HTTPS/SSL**:

   - Set up reverse proxy (nginx, traefik)
   - Configure SSL certificates
   - Redirect HTTP to HTTPS

3. **Network Segmentation**:

   - Use VPN for remote access
   - Implement IP whitelisting
   - Consider internal-only access

4. **Authentication**:
   - Enable MQTT authentication
   - Use strong InfluxDB tokens
   - Implement Grafana user management

### Development vs Production

| Aspect         | Development         | Production              |
| -------------- | ------------------- | ----------------------- |
| Authentication | Default credentials | Strong passwords/tokens |
| Network        | Local network       | VPN/SSL                 |
| Firewall       | Basic rules         | Strict IP whitelisting  |
| Monitoring     | Basic               | Comprehensive logging   |

## Troubleshooting

### Connection Issues

#### 1. Check Service Status

```bash
# Verify containers are running
docker-compose ps

# Check specific service
docker-compose ps grafana
docker-compose ps influxdb
docker-compose ps mosquitto
```

#### 2. Verify Port Binding

```bash
# Check which ports are bound
docker port mqtt2grafna_grafana
docker port mqtt2grafna_influxdb
docker port mqtt2grafna_mosquitto

# Expected output:
# 3000/tcp -> 0.0.0.0:3000
# 8086/tcp -> 0.0.0.0:8086
# 1883/tcp -> 0.0.0.0:1883
```

#### 3. Test Local Connectivity

```bash
# Test Grafana
curl -I http://localhost:3000

# Test InfluxDB
curl -I http://localhost:8086/health

# Test MQTT (using mosquitto_pub)
mosquitto_pub -h localhost -p 1883 -t "test/topic" -m "test message"
```

#### 4. Check Firewall Status

```bash
# Ubuntu/Debian
sudo ufw status

# macOS
sudo pfctl -s rules

# Windows
netsh advfirewall show allprofiles
```

#### 5. Network Diagnostics

```bash
# Test network connectivity
ping YOUR_HOST_IP

# Check if ports are reachable
telnet YOUR_HOST_IP 3000
telnet YOUR_HOST_IP 8086
telnet YOUR_HOST_IP 1883

# Alternative using nc (netcat)
nc -zv YOUR_HOST_IP 3000
nc -zv YOUR_HOST_IP 8086
nc -zv YOUR_HOST_IP 1883
```

### Common Error Messages

#### "Connection Refused"

- Service not running
- Port not exposed
- Firewall blocking

#### "Connection Timeout"

- Network connectivity issues
- Firewall blocking
- Wrong IP address

#### "Authentication Failed"

- Wrong credentials
- Service not configured for remote access
- Token expired

## Mobile Access

### Smartphone/Tablet Access

1. **Ensure devices are on the same network**
2. **Use the host IP address**:
   ```
   http://192.168.1.100:3000
   ```
3. **Bookmark the URL** for easy access
4. **Consider using mobile-optimized dashboards**

### Mobile App Options

- **Grafana Mobile App**: Official app for iOS/Android
- **MQTT Explorer**: For MQTT testing
- **InfluxDB Studio**: For database management

## Advanced Configuration

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL/HTTPS Setup

```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Or self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout private.key -out certificate.crt
```

### Load Balancer Configuration

For high availability, consider:

- Multiple Grafana instances
- InfluxDB clustering
- MQTT broker clustering

## Monitoring Remote Access

### Log Monitoring

```bash
# Monitor access logs
docker-compose logs -f grafana
docker-compose logs -f influxdb
docker-compose logs -f mosquitto
```

### Health Checks

```bash
# Automated health check script
#!/bin/bash
curl -f http://localhost:3000/api/health || echo "Grafana down"
curl -f http://localhost:8086/health || echo "InfluxDB down"
```

## Next Steps

1. **Set up monitoring** for remote access
2. **Implement security measures** for production
3. **Configure backup strategies**
4. **Set up alerting** for service availability

For more information, see:

- [Troubleshooting Guide](troubleshooting.md)
- [Best Practices](bestpractices.md)
- [Environment Setup](Environment-setup-Linux.md)
