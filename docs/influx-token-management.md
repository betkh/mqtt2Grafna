# InfluxDB Token Management

This guide covers how to create, manage, and secure InfluxDB tokens for the MQTT to Grafana project.

## Overview

InfluxDB uses API tokens for authentication. The default setup uses a development token, but for production environments, you should create custom tokens with appropriate permissions.

## Quick Start - Choose Your Method

### Method 1: Using InfluxDB CLI (Recommended for CLI users)

1. **Start the services:**

   ```bash
   docker-compose -p mqtt2grafna up -d
   ```

2. **Access InfluxDB CLI:**

   ```bash
   docker exec -it mqtt2grafna_influxdb influx
   ```

3. **Create a new token:**

   ```bash
   influx auth create \
     --org myorg \
     --bucket weather_data \
     --write-bucket weather_data \
     --description "Telegraf MQTT Data Collection"
   ```

4. **Copy the generated token** and update `telegraf/telegraf.conf`:

   ```bash
   # Edit the telegraf.conf file
   nano telegraf/telegraf.conf
   ```

   Replace the token line:

   ```ini
   token = "your-new-generated-token-here"
   ```

5. **Restart Telegraf:**
   ```bash
   docker-compose -p mqtt2grafna restart telegraf
   ```

### Method 2: Using InfluxDB Web Interface (Recommended for GUI users)

1. **Start the services:**

   ```bash
   docker-compose -p mqtt2grafna up -d
   ```

2. **Access InfluxDB Web Interface:**

   - Open http://localhost:8086 in your browser
   - Login with:
     - **Username**: `admin`
     - **Password**: `adminpassword`

3. **Create a new token:**

   - Go to **Data** → **API Tokens**
   - Click **Generate API Token** → **Custom API Token**
   - Configure the token:
     - **Description**: `Telegraf MQTT Data Collection`
     - **Permissions**:
       - **Read/Write** access to the `weather_data` bucket
       - **Read** access to the `myorg` organization
   - Click **Save**

4. **Copy the generated token** (it will look like: `abc123def456...`)

5. **Update Telegraf configuration:**

   ```bash
   # Edit the telegraf.conf file
   nano telegraf/telegraf.conf
   ```

   Replace the token line:

   ```ini
   token = "your-new-generated-token-here"
   ```

6. **Restart Telegraf:**
   ```bash
   docker-compose -p mqtt2grafna restart telegraf
   ```

## Alternative Methods

### Method 3: Automated Script (Optional)

For convenience, you can use our automated token setup script:

```bash
# Start services first
docker-compose -p mqtt2grafna up -d

# Run the token setup script
pipenv run python src/scripts/setup_influxdb_token.py
```

This script will:

- ✅ Check if InfluxDB is running
- ✅ Login to InfluxDB automatically
- ✅ Create a new API token with proper permissions
- ✅ Update `telegraf/telegraf.conf` with the new token
- ✅ Provide next steps for restarting services

### Method 4: Using Environment Variables

1. **Create a `.env` file** (if not exists):

   ```bash
   cp config/env.example .env
   ```

2. **Add your token to `.env`:**

   ```bash
   INFLUXDB_TOKEN=your-new-generated-token-here
   ```

3. **Update `docker-compose.yml`** to use the environment variable:

   ```yaml
   environment:
     - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}
   ```

4. **Update `telegraf/telegraf.conf`** to use the environment variable:
   ```ini
   token = "${INFLUXDB_TOKEN}"
   ```

## Token Permissions

### Required Permissions for Telegraf

Your token needs the following permissions:

- **Read** access to the organization (`myorg`)
- **Read/Write** access to the bucket (`weather_data`)

### Permission Structure

```json
{
  "permissions": [
    {
      "action": "read",
      "resource": {
        "orgID": "your-org-id",
        "type": "orgs"
      }
    },
    {
      "action": "write",
      "resource": {
        "orgID": "your-org-id",
        "type": "buckets",
        "id": "your-bucket-id"
      }
    },
    {
      "action": "read",
      "resource": {
        "orgID": "your-org-id",
        "type": "buckets",
        "id": "your-bucket-id"
      }
    }
  ]
}
```

## Security Best Practices

### Token Security

- **Never commit tokens to version control**
- **Use environment variables** for production deployments
- **Rotate tokens regularly** (every 90 days recommended)
- **Use minimal required permissions** for each token
- **Monitor token usage** in InfluxDB web interface

### Production Deployment

1. **Use environment variables:**

   ```bash
   export INFLUXDB_TOKEN="your-secure-token"
   ```

2. **Store tokens securely:**

   - Use secret management services (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Never hardcode tokens in configuration files
   - Use different tokens for different environments

3. **Regular token rotation:**
   - Set up automated token rotation processes
   - Monitor token expiration dates
   - Have a rollback plan for token changes

### Development vs Production

| Environment | Token Type    | Security Level                 |
| ----------- | ------------- | ------------------------------ |
| Development | Default token | Low (for testing only)         |
| Production  | Custom token  | High (with proper permissions) |

## Default Token (Development Only)

The current setup uses environment variables for token management. See `config/env.example` for the template and run `./setup_env.sh` to create your `.env` file.

⚠️ **Warning**: This token is for development only. Always use a custom token for production environments.

## Troubleshooting

### Common Issues

#### Token Authentication Errors

**Symptoms:**

- Telegraf fails to write to InfluxDB
- Error messages about authentication
- No data appearing in Grafana

**Solutions:**

1. **Verify token is correct:**

   ```bash
   # Check current token in telegraf.conf
   grep "token" telegraf/telegraf.conf
   ```

2. **Test token manually:**

   ```bash
   # Use curl to test token
   curl -H "Authorization: Token your-token-here" \
        http://localhost:8086/api/v2/buckets?org=myorg
   ```

3. **Check token permissions:**
   - Go to InfluxDB web interface
   - Navigate to **Data** → **API Tokens**
   - Verify token has correct permissions

#### Token Expired or Invalid

**Symptoms:**

- Sudden authentication failures
- Error messages about invalid token

**Solutions:**

1. **Create a new token** using one of the methods above
2. **Update configuration** with the new token
3. **Restart services:**
   ```bash
   docker-compose -p mqtt2grafna restart telegraf
   ```

### Verification Steps

After creating a new token, verify it's working:

1. **Check Telegraf logs:**

   ```bash
   docker-compose -p mqtt2grafna logs telegraf
   ```

2. **Verify data in InfluxDB:**

   - Open http://localhost:8086
   - Go to **Data Explorer**
   - Query for recent data

3. **Check Grafana dashboard:**
   - Open http://localhost:3000
   - Verify data is being displayed

## Token Management Commands

### List All Tokens

```bash
# Via web interface
# Go to Data → API Tokens

# Via CLI
docker exec -it mqtt2grafna_influxdb influx auth list
```

### Delete a Token

```bash
# Via web interface
# Go to Data → API Tokens → Delete

# Via CLI
docker exec -it mqtt2grafna_influxdb influx auth delete --id token-id
```

### Update Token Description

```bash
# Via web interface
# Go to Data → API Tokens → Edit

# Via CLI
docker exec -it mqtt2grafna_influxdb influx auth update --id token-id --description "New description"
```

## Advanced Configuration

### Multiple Tokens for Different Services

For complex setups, you might want different tokens for different services:

```ini
# telegraf.conf for MQTT data collection
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "${TELEGRAF_TOKEN}"
  organization = "myorg"
  bucket = "weather_data"

# Additional output for monitoring
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "${MONITORING_TOKEN}"
  organization = "myorg"
  bucket = "monitoring_data"
```

### Token with Limited Scope

For enhanced security, create tokens with minimal permissions:

```bash
# Token for read-only access
influx auth create \
  --org myorg \
  --bucket weather_data \
  --read-bucket weather_data \
  --description "Read-only access for dashboards"

# Token for specific bucket only
influx auth create \
  --org myorg \
  --bucket weather_data \
  --write-bucket weather_data \
  --description "Write access for weather data only"
```

## References

- [InfluxDB Authentication Documentation](https://docs.influxdata.com/influxdb/v2.7/security/tokens/)
- [Telegraf InfluxDB Output Plugin](https://docs.influxdata.com/telegraf/v1.24/data_formats/output/influxdb/)
- [Docker InfluxDB Setup](https://docs.influxdata.com/influxdb/v2.7/install/?t=Docker)
