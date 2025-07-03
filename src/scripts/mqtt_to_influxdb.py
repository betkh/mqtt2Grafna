#!/usr/bin/env python3
"""
MQTT to InfluxDB Direct Writer
Subscribes to MQTT topics and writes directly to InfluxDB

# WORKING CODE!

pipenv run python src/scripts/mqtt_to_influxdb.py
"""

import json
import paho.mqtt.client as mqtt
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import time
import os

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TEMPERATURE_TOPIC = "data/temperature"
HUMIDITY_TOPIC = "data/humidity"

# InfluxDB Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "myorg")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "weather_data")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")

if not INFLUXDB_TOKEN:
    raise ValueError("INFLUXDB_TOKEN environment variable is required")


class MQTTToInfluxDB:
    def __init__(self):
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Initialize InfluxDB client
        self.influx_client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,  # type: ignore
            org=INFLUXDB_ORG
        )
        self.write_api = self.influx_client.write_api(
            write_options=SYNCHRONOUS)

        # Statistics
        self.temp_count = 0
        self.humidity_count = 0

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print(f"✅ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            client.subscribe(TEMPERATURE_TOPIC)
            client.subscribe(HUMIDITY_TOPIC)
            print(f"📡 Subscribed to: {TEMPERATURE_TOPIC}")
            print(f"📡 Subscribed to: {HUMIDITY_TOPIC}")
        else:
            print(f"❌ Failed to connect to MQTT broker, return code: {rc}")

    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            # Parse JSON message
            data = json.loads(msg.payload.decode())

            # Convert timestamp to datetime
            timestamp_str = data.get('timestamp')
            if timestamp_str:
                # Remove 'Z' and parse
                dt = datetime.fromisoformat(
                    timestamp_str.replace('Z', '+00:00'))
            else:
                dt = datetime.utcnow()

            # Create InfluxDB point based on topic
            if msg.topic == TEMPERATURE_TOPIC:
                temperature = data.get('temperature')
                if temperature is not None:
                    point = Point("temperature") \
                        .field("temperature", float(temperature)) \
                        .time(dt)

                    self.write_api.write(bucket=INFLUXDB_BUCKET, record=point)
                    self.temp_count += 1
                    print(
                        f"🌡️  Temperature: {temperature}°C | Time: {dt.strftime('%H:%M:%S')} | Count: {self.temp_count}")

            elif msg.topic == HUMIDITY_TOPIC:
                humidity = data.get('humidity')
                if humidity is not None:
                    point = Point("humidity") \
                        .field("humidity", float(humidity)) \
                        .time(dt)

                    self.write_api.write(bucket=INFLUXDB_BUCKET, record=point)
                    self.humidity_count += 1
                    print(
                        f"💧 Humidity: {humidity}% | Time: {dt.strftime('%H:%M:%S')} | Count: {self.humidity_count}")

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
        except Exception as e:
            print(f"❌ Error processing message: {e}")

    def start(self):
        """Start the MQTT to InfluxDB bridge"""
        print("🚀 Starting MQTT to InfluxDB Bridge...")
        print(f"📊 InfluxDB Bucket: {INFLUXDB_BUCKET}")
        print("Press Ctrl+C to stop...")

        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

            # Start the loop
            self.mqtt_client.loop_forever()

        except KeyboardInterrupt:
            print("\n⏹️  Stopping MQTT to InfluxDB bridge...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        try:
            self.mqtt_client.disconnect()
            self.influx_client.close()
            print(
                f"✅ Cleanup completed. Total written: {self.temp_count} temp, {self.humidity_count} humidity")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")


def main():
    bridge = MQTTToInfluxDB()
    bridge.start()


if __name__ == "__main__":
    main()
