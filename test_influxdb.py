#!/usr/bin/env python3
"""
InfluxDB Test Script
Tests connectivity and queries stored temperature data
"""

from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta

# InfluxDB Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-auth-token"
INFLUXDB_ORG = "myorg"
INFLUXDB_BUCKET = "weather_data"


def test_connection():
    """Test InfluxDB connection"""
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        health = client.health()
        print(f"InfluxDB Health: {health}")
        return client
    except Exception as e:
        print(f"Failed to connect to InfluxDB: {e}")
        return None


def query_recent_data(client, hours=1):
    """Query recent temperature data"""
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -{hours}h)
        |> filter(fn: (r) => r["_measurement"] == "temperature")
        |> filter(fn: (r) => r["_field"] == "value")
        |> sort(columns: ["_time"])
    '''

    try:
        result = client.query_api().query(query)
        return result
    except Exception as e:
        print(f"Error querying data: {e}")
        return None


def print_data_summary(result):
    """Print summary of query results"""
    if not result:
        print("No data found")
        return

    count = 0
    min_temp = float('inf')
    max_temp = float('-inf')
    total_temp = 0

    for table in result:
        for record in table.records:
            count += 1
            temp = record.get_value()
            total_temp += temp
            min_temp = min(min_temp, temp)
            max_temp = max(max_temp, temp)
            print(
                f"Time: {record.get_time()}, Temperature: {temp}°C, Location: {record.values.get('location', 'N/A')}")

    if count > 0:
        avg_temp = total_temp / count
        print(f"\nSummary:")
        print(f"Total records: {count}")
        print(f"Min temperature: {min_temp}°C")
        print(f"Max temperature: {max_temp}°C")
        print(f"Average temperature: {avg_temp:.2f}°C")
    else:
        print("No temperature data found")


def main():
    """Main test function"""
    print("Testing InfluxDB Connection and Data...")
    print("=" * 50)

    # Test connection
    client = test_connection()
    if not client:
        return

    print("\nQuerying recent temperature data (last hour)...")
    print("-" * 50)

    # Query recent data
    result = query_recent_data(client, hours=1)
    print_data_summary(result)

    # Close connection
    client.close()


if __name__ == "__main__":
    main()
