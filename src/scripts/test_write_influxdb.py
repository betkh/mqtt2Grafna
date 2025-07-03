#!/usr/bin/env python3
"""
Test Write to InfluxDB Script
Test if we can write data directly to InfluxDB

# WORKING CODE!

pipenv run python src/scripts/test_write_influxdb.py
"""

import os
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import time

# InfluxDB Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "myorg")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "weather_data")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")

if not INFLUXDB_TOKEN:
    raise ValueError("INFLUXDB_TOKEN environment variable is required")


def test_write_to_influxdb():
    """Test writing data directly to InfluxDB"""
    try:
        # Create client
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,  # type: ignore
            org=INFLUXDB_ORG
        )

        # Test connection
        health = client.health()
        print(f"✅ InfluxDB Connection: {health.status}")

        # Create write API
        write_api = client.write_api(write_options=SYNCHRONOUS)

        # Create test data points
        current_time = datetime.utcnow()

        # Temperature point
        temp_point = Point("temperature") \
            .field("temperature", 25.5) \
            .time(current_time)

        # Humidity point
        humidity_point = Point("humidity") \
            .field("humidity", 60.0) \
            .time(current_time)

        print(f"📝 Writing test data at {current_time}")

        # Write data
        write_api.write(bucket=INFLUXDB_BUCKET, record=[
                        temp_point, humidity_point])

        print("✅ Successfully wrote test data to InfluxDB!")

        # Wait a moment for data to be available
        time.sleep(2)

        # Query to verify data was written
        query_api = client.query_api()
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1m)
          |> limit(n: 5)
        '''

        print("\n🔍 Querying to verify data was written...")
        result = query_api.query(query)

        if result:
            print("✅ Data found in InfluxDB:")
            for table in result:
                for record in table.records:
                    print(
                        f"   {record.get_measurement()}: {record.get_field()} = {record.get_value()}")
        else:
            print("❌ No data found in query")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("🚀 Testing Direct Write to InfluxDB...")
    print("=" * 50)

    success = test_write_to_influxdb()

    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Can write directly to InfluxDB!")
        print("✅ The issue is likely with Telegraf configuration")
    else:
        print("❌ FAILED: Cannot write to InfluxDB")
        print("🔧 Check token and connection settings")


if __name__ == "__main__":
    main()
