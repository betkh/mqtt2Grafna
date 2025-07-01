#!/usr/bin/env python3
"""
Grafana Setup Script
Configures InfluxDB data source and creates dashboard for temperature visualization
"""

import requests
import json
import time
import os
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Grafana Configuration
GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = os.getenv("GRAFANA_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_PASSWORD", "165268")

# InfluxDB Configuration
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "myorg")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "weather_data")


def cleanup_influxdb():
    """Clean up InfluxDB data for fresh start"""
    print("Cleaning up InfluxDB data...")
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

        # Delete all data from the bucket
        delete_api = client.delete_api()
        delete_api.delete(
            start="1970-01-01T00:00:00Z",
            stop="2025-12-31T23:59:59Z",
            predicate='_measurement="temperature"',
            bucket=INFLUXDB_BUCKET
        )
        print("InfluxDB data cleaned successfully!")
        client.close()
    except Exception as e:
        print(f"Warning: Could not clean InfluxDB data: {e}")


def wait_for_grafana():
    """Wait for Grafana to be ready"""
    print("Waiting for Grafana to be ready...")
    while True:
        try:
            response = requests.get(f"{GRAFANA_URL}/api/health")
            if response.status_code == 200:
                print("Grafana is ready!")
                break
        except requests.exceptions.ConnectionError:
            print("Grafana not ready yet, waiting...")
            time.sleep(5)


def create_datasource():
    """Create InfluxDB data source in Grafana"""
    print("Creating InfluxDB data source...")

    datasource_config = {
        "name": "InfluxDB",
        "type": "influxdb",
        "url": INFLUXDB_URL,
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "version": "Flux",
            "organization": INFLUXDB_ORG,
            "defaultBucket": INFLUXDB_BUCKET
        },
        "secureJsonData": {
            "token": INFLUXDB_TOKEN
        }
    }

    try:
        # First, try to delete existing data source if it exists
        try:
            delete_response = requests.delete(
                f"{GRAFANA_URL}/api/datasources/name/InfluxDB",
                auth=(GRAFANA_USER, GRAFANA_PASSWORD)
            )
            if delete_response.status_code == 200:
                print("Existing InfluxDB data source deleted.")
            elif delete_response.status_code == 404:
                print("No existing data source found.")
            else:
                print(
                    f"Warning: Could not delete existing data source: {delete_response.text}")
        except Exception as e:
            print(f"Warning: Error deleting existing data source: {e}")

        # Create new data source
        response = requests.post(
            f"{GRAFANA_URL}/api/datasources",
            json=datasource_config,
            auth=(GRAFANA_USER, GRAFANA_PASSWORD)
        )

        if response.status_code == 200:
            print("InfluxDB data source created successfully!")
            return response.json()["id"]
        else:
            print(f"Failed to create data source: {response.text}")
            return None

    except Exception as e:
        print(f"Error creating data source: {e}")
        return None


def create_dashboard():
    """Create temperature dashboard"""
    print("Creating temperature dashboard...")

    dashboard_config = {
        "dashboard": {
            "title": "Temperature Monitoring",
            "panels": [
                {
                    "title": "Temperature Over Time",
                    "type": "timeseries",
                    "targets": [
                        {
                            "refId": "A",
                            "query": f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "temperature") |> filter(fn: (r) => r["_field"] == "value")',
                            "datasource": {
                                "type": "influxdb",
                                "uid": "InfluxDB"
                            }
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            },
                            "custom": {
                                "axisLabel": "",
                                "axisPlacement": "auto",
                                "barAlignment": 0,
                                "drawStyle": "line",
                                "fillOpacity": 10,
                                "gradientMode": "none",
                                "hideFrom": {
                                    "legend": False,
                                    "tooltip": False,
                                    "vis": False
                                },
                                "lineInterpolation": "linear",
                                "lineWidth": 1,
                                "pointSize": 5,
                                "scaleDistribution": {
                                    "type": "linear"
                                },
                                "showPoints": "never",
                                "spanNulls": False,
                                "stacking": {
                                    "group": "A",
                                    "mode": "none"
                                },
                                "thresholdsStyle": {
                                    "mode": "off"
                                }
                            },
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {
                                        "color": "green",
                                        "value": None
                                    }
                                ]
                            },
                            "unit": "celsius"
                        }
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 12,
                        "x": 0,
                        "y": 0
                    }
                }
            ],
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "refresh": "5s"
        },
        "folderId": 0,
        "overwrite": True
    }

    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/dashboards/db",
            json=dashboard_config,
            auth=(GRAFANA_USER, GRAFANA_PASSWORD)
        )

        if response.status_code == 200:
            print("Temperature dashboard created successfully!")
            dashboard_url = f"{GRAFANA_URL}{response.json()['url']}"
            print(f"Dashboard URL: {dashboard_url}")
            return dashboard_url
        else:
            print(f"Failed to create dashboard: {response.text}")
            return None

    except Exception as e:
        print(f"Error creating dashboard: {e}")
        return None


def main():
    """Main setup function"""
    print("Setting up Grafana for temperature monitoring...")

    # Clean up InfluxDB for fresh start
    cleanup_influxdb()

    # Wait for Grafana to be ready
    wait_for_grafana()

    # Create data source
    datasource_id = create_datasource()
    if not datasource_id:
        print("Failed to create data source. Exiting.")
        return

    # Create dashboard
    dashboard_url = create_dashboard()
    if not dashboard_url:
        print("Failed to create dashboard. Exiting.")
        return

    print("\nSetup completed successfully!")
    print(f"Grafana URL: {GRAFANA_URL}")
    print(f"Username: {GRAFANA_USER}")
    print(f"Password: {GRAFANA_PASSWORD}")
    print(f"Dashboard URL: {dashboard_url}")
    print("\nNote: InfluxDB has been cleaned for fresh start.")


if __name__ == "__main__":
    main()
