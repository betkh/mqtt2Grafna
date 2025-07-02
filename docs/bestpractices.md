# Docker Compose Best Practices

This document outlines best practices for managing Docker Compose projects to prevent common issues like volume conflicts, naming collisions, and deployment problems.

## 1. Explicit Volume Naming

### Problem

Docker Compose auto-generates volume names based on the project directory name. When you rename project folders, this creates conflicts between old and new volumes.

### Solution

Always define explicit volume names in your `docker-compose.yml`:

```yaml
volumes:
  influxdb_data:
    name: mqtt2grafna_influxdb_data
  grafana_data:
    name: mqtt2grafna_grafana_data
```

### Benefits

- Prevents volume conflicts when renaming project directories
- Makes volume management more predictable
- Easier to identify volumes in `docker volume ls`

## 2. Project Name Management

### Use Environment Variables

Create a `.env` file in your project root:

```bash
COMPOSE_PROJECT_NAME=mqtt2grafna
INFLUXDB_INIT_USERNAME=admin
INFLUXDB_INIT_PASSWORD=adminpassword
INFLUXDB_INIT_ORG=myorg
INFLUXDB_INIT_BUCKET=weather_data
INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-auth-token
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

### Use Project Flag

Always specify the project name when running commands:

```bash
# Instead of: docker-compose up -d
docker-compose -p mqtt2grafna up -d

# Or set environment variable
export COMPOSE_PROJECT_NAME=mqtt2grafna
docker-compose up -d
```

## 3. Proper Cleanup Commands

### When Switching Projects

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Or if you want to keep volumes but remove everything else
docker-compose down

# To remove everything including images
docker-compose down -v --rmi all
```

### When Renaming Project Directories

1. Stop all containers: `docker-compose down`
2. Remove old volumes: `docker volume rm old_project_name_volume_name`
3. Rename the directory
4. Start with new configuration: `docker-compose up -d`

## 4. Container Naming Strategy

### Use Explicit Container Names

In your `docker-compose.yml`, specify container names:

```yaml
services:
  mosquitto:
    container_name: mqtt2grafna_mosquitto
  influxdb:
    container_name: mqtt2grafna_influxdb
  grafana:
    container_name: mqtt2grafna_grafana
```

### Benefits

- Easier to identify containers across multiple projects
- Prevents naming conflicts
- More predictable container management

## 5. Network Management

### Use Explicit Network Names

```yaml
networks:
  mqtt_network:
    name: mqtt2grafna_network
    driver: bridge
```

### Benefits

- Prevents network conflicts between projects
- Easier to manage network connectivity
- Clear separation between different environments

## 6. Environment Configuration

### Use .env Files

Store sensitive configuration in `.env` files:

```bash
# .env
COMPOSE_PROJECT_NAME=mqtt2grafna
INFLUXDB_INIT_USERNAME=admin
INFLUXDB_INIT_PASSWORD=secure_password_here
GRAFANA_ADMIN_PASSWORD=secure_password_here
```

### Reference in docker-compose.yml

```yaml
environment:
  - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_INIT_USERNAME}
  - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_INIT_PASSWORD}
  - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
```

## 7. Development vs Production

### Use Different Compose Files

- `docker-compose.yml` - Base configuration
- `docker-compose.dev.yml` - Development overrides
- `docker-compose.prod.yml` - Production overrides

### Example Usage

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 8. Troubleshooting Commands

### Check Project Status

```bash
# List all containers for the project
docker-compose ps

# List all volumes
docker volume ls | grep project_name

# List all networks
docker network ls | grep project_name
```

### Debug Issues

```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs service_name

# Follow logs in real-time
docker-compose logs -f service_name
```

### Clean Slate

```bash
# Remove everything and start fresh
docker-compose down -v --rmi all
docker system prune -f
docker-compose up -d
```

## 9. Version Control Best Practices

### .gitignore Entries

```
# Docker
.env
docker-compose.override.yml
*.log

# Volumes (if using bind mounts)
data/
logs/
```

### Documentation

- Keep `docker-compose.yml` well-documented with comments
- Document any custom configurations
- Include setup instructions in README.md

## 10. Security Considerations

### Secrets Management

```yaml
# Use Docker secrets for sensitive data
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Network Security

```yaml
# Use internal networks when possible
networks:
  internal:
    internal: true
  external:
    external: true
```

## 11. Performance Optimization

### Resource Limits

```yaml
services:
  influxdb:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "0.5"
        reservations:
          memory: 512M
          cpus: "0.25"
```

### Volume Optimization

```yaml
volumes:
  data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/data
```

## 12. Monitoring and Health Checks

### Add Health Checks

```yaml
services:
  influxdb:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8086/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Benefits

- Automatic container restart on failure
- Better monitoring and alerting
- Improved reliability

## Summary

Following these best practices will help you:

- Avoid volume and naming conflicts
- Maintain consistent project structure
- Improve security and performance
- Make troubleshooting easier
- Ensure reliable deployments

Remember to always use explicit naming, proper cleanup procedures, and environment-specific configurations for the best Docker Compose experience.
