#!/usr/bin/env python3
"""
Test InfluxDB Data Script
Check if data is being written to InfluxDB

# WORKING CODE!

sleep 10 && pipenv run python src/scripts/test_influxdb_data.py
"""

import os
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from datetime import datetime, timedelta

# InfluxDB Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "myorg")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "weather_data")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")

if not INFLUXDB_TOKEN:
    raise ValueError("INFLUXDB_TOKEN environment variable is required")


def test_influxdb_connection():
    """Test connection to InfluxDB"""
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,  # type: ignore
            org=INFLUXDB_ORG
        )

        # Test connection
        health = client.health()
        print(f"✅ InfluxDB Connection: {health.status}")

        return client
    except Exception as e:
        print(f"❌ InfluxDB Connection Error: {e}")
        return None


def query_recent_data(client):
    """Query recent data from InfluxDB"""
    try:
        query_api = QueryApi(client)

        # Query for recent temperature data
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "temperature")
          |> limit(n: 10)
        '''

        print("\n🔍 Querying recent temperature data...")
        result = query_api.query(query)

        if not result:
            print("❌ No data found in InfluxDB")
            return False

        print(f"✅ Found {len(result)} data points:")
        for table in result:
            for record in table.records:
                print(
                    f"   Time: {record.get_time()} | Temperature: {record.get_value()}°C")

        return True

    except Exception as e:
        print(f"❌ Query Error: {e}")
        return False


def query_humidity_data(client):
    """Query recent humidity data from InfluxDB"""
    try:
        query_api = QueryApi(client)

        # Query for recent humidity data
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "humidity")
          |> limit(n: 5)
        '''

        print("\n🔍 Querying recent humidity data...")
        result = query_api.query(query)

        if not result:
            print("❌ No humidity data found in InfluxDB")
            return False

        print(f"✅ Found {len(result)} humidity data points:")
        for table in result:
            for record in table.records:
                print(
                    f"   Time: {record.get_time()} | Humidity: {record.get_value()}%")

        return True

    except Exception as e:
        print(f"❌ Humidity Query Error: {e}")
        return False


def get_data_statistics(client):
    """Get basic statistics about the data"""
    try:
        query_api = QueryApi(client)

        # Count total records
        count_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1h)
          |> count()
        '''

        print("\n📊 Data Statistics (Last Hour):")
        result = query_api.query(count_query)

        if result:
            for table in result:
                for record in table.records:
                    print(f"   Total records: {record.get_value()}")

        # Temperature statistics
        temp_stats_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "temperature")
          |> mean()
        '''

        result = query_api.query(temp_stats_query)
        if result:
            for table in result:
                for record in table.records:
                    print(
                        f"   Average temperature: {record.get_value():.2f}°C")

        return True

    except Exception as e:
        print(f"❌ Statistics Error: {e}")
        return False


def main():
    print("🚀 Testing InfluxDB Data Collection...")
    print("=" * 50)

    # Test connection
    client = test_influxdb_connection()
    if not client:
        return

    # Query recent data
    temp_success = query_recent_data(client)
    humidity_success = query_humidity_data(client)

    # Get statistics
    get_data_statistics(client)

    # Summary
    print("\n" + "=" * 50)
    if temp_success and humidity_success:
        print("🎉 SUCCESS: Data is being written to InfluxDB!")
        print("✅ You can now create line graphs in Grafana")
    else:
        print("⚠️  ISSUE: Some data may not be reaching InfluxDB")
        print("🔧 Check Telegraf configuration and logs")

    client.close()


if __name__ == "__main__":
    main()
