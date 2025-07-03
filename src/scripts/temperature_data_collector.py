#!/usr/bin/env python3
"""
Temperature Data Collector
Subscribes to temperature data from MQTT and writes to CSV + InfluxDB
"""

import json
import csv
import time
import os
from datetime import datetime
import paho.mqtt.client as mqtt
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "data/temperature"
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-auth-token"
INFLUXDB_ORG = "myorg"
INFLUXDB_BUCKET = "weather_data"
CSV_FILENAME = "temperature_data.csv"


class TemperatureDataCollector:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.influx_client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        self.write_api = self.influx_client.write_api(
            write_options=SYNCHRONOUS)

        # Setup CSV file
        self.setup_csv()

        # Setup MQTT callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def setup_csv(self):
        """Initialize CSV file with headers"""
        csv_exists = os.path.exists(CSV_FILENAME)

        with open(CSV_FILENAME, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'temperature', 'datetime']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not csv_exists:
                writer.writeheader()
                print(f"Created CSV file: {CSV_FILENAME}")
            else:
                print(f"Appending to existing CSV file: {CSV_FILENAME}")

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            client.subscribe(MQTT_TOPIC)
            print(f"Subscribed to topic: {MQTT_TOPIC}")
        else:
            print(f"Failed to connect to MQTT broker, return code: {rc}")

    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            # Parse JSON message
            data = json.loads(msg.payload.decode())
            temperature = data.get('temperature')
            timestamp = data.get('timestamp')

            if temperature is not None and timestamp is not None:
                # Convert timestamp to datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

                # Write to CSV
                self.write_to_csv(timestamp, temperature, dt)

                # Write to InfluxDB
                self.write_to_influxdb(temperature, dt)

                print(
                    f"Temperature: {temperature}°C | Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON message: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def write_to_csv(self, timestamp, temperature, dt):
        """Write temperature data to CSV file"""
        try:
            with open(CSV_FILENAME, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'temperature', 'datetime']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writerow({
                    'timestamp': timestamp,
                    'temperature': temperature,
                    'datetime': dt.strftime('%Y-%m-%d %H:%M:%S')
                })
        except Exception as e:
            print(f"Error writing to CSV: {e}")

    def write_to_influxdb(self, temperature, dt):
        """Write temperature data to InfluxDB"""
        try:
            point = Point("temperature") \
                .field("temperature", temperature) \
                .time(dt)

            self.write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")

    def start(self):
        """Start the data collector"""
        print("Starting Temperature Data Collector...")
        print(f"CSV file: {CSV_FILENAME}")
        print(f"InfluxDB bucket: {INFLUXDB_BUCKET}")
        print("Press Ctrl+C to stop...")

        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

            # Start the loop
            self.mqtt_client.loop_forever()

        except KeyboardInterrupt:
            print("\nStopping Temperature Data Collector...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        try:
            self.mqtt_client.disconnect()
            self.influx_client.close()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")


def main():
    collector = TemperatureDataCollector()
    collector.start()


if __name__ == "__main__":
    main()
