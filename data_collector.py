#!/usr/bin/env python3
"""
MQTT to InfluxDB Data Collector
Subscribes to MQTT messages and stores temperature data in InfluxDB
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "data/temperature"
MQTT_CLIENT_ID = "python_data_collector"

# InfluxDB Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-auth-token"
INFLUXDB_ORG = "myorg"
INFLUXDB_BUCKET = "weather_data"


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC, qos=1)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker, return code: {rc}")


def on_message(client, userdata, msg):
    """Callback when message is received"""
    try:
        # Parse JSON message
        data = json.loads(msg.payload.decode())

        # Extract temperature data
        temperature = data.get('temperature')
        timestamp = data.get('timestamp')
        location = data.get('location')

        if temperature is not None:
            # Parse timestamp
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1] + '+00:00'

            # Create InfluxDB point
            point = Point("temperature") \
                .field("value", float(temperature)) \
                .tag("location", location) \
                .time(datetime.fromisoformat(timestamp))

            # Write to InfluxDB
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)

            print(
                f"Temperature data stored: {temperature}°C at {location} - {timestamp}")

    except json.JSONDecodeError:
        print(f"Error parsing JSON message: {msg.payload.decode()}")
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscribed to topic"""
    print(f"Subscribed with message ID: {mid}, QoS: {granted_qos}")


def main():
    """Main function to collect and store data"""
    global write_api

    # Initialize InfluxDB client
    try:
        influx_client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        print(f"Connected to InfluxDB at {INFLUXDB_URL}")
    except Exception as e:
        print(f"Failed to connect to InfluxDB: {e}")
        return

    # Create MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        print("Starting data collection...")
        print("Press Ctrl+C to stop...")

        # Start the loop
        client.loop_forever()

    except KeyboardInterrupt:
        print("\nStopping data collector...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        client.disconnect()
        influx_client.close()
        print("Data collector disconnected")


if __name__ == "__main__":
    main()
