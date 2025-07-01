#!/usr/bin/env python3
"""
MQTT Publisher Script
Publishes messages to the "data/temperature" topic
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "data/temperature"
MQTT_CLIENT_ID = "python_publisher"


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"Failed to connect to MQTT broker, return code: {rc}")


def on_publish(client, userdata, mid):
    """Callback when message is published"""
    print(f"Message published with ID: {mid}")


def create_sample_data():
    """Create sample temperature data"""
    return {
        "timestamp": datetime.now().isoformat(),
        "temperature": round(random.uniform(15.0, 30.0), 2),
        "humidity": round(random.uniform(40.0, 80.0), 2),
        "pressure": round(random.uniform(1000.0, 1020.0), 2),
        "wind_speed": round(random.uniform(0.0, 15.0), 2),
        "location": "Weather Station 1"
    }


def main():
    """Main function to publish messages"""
    # Create MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)

    # Set callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        # Start the loop
        client.loop_start()

        # Wait a moment for connection
        time.sleep(2)

        print(f"Publishing messages to topic: {MQTT_TOPIC}")
        print("Press Ctrl+C to stop...")

        # Publish messages every second for real-time visualization
        message_count = 0
        while True:
            # Create sample data
            data = create_sample_data()
            message_count += 1

            # Convert to JSON
            payload = json.dumps(data, indent=2)

            # Publish message
            result = client.publish(MQTT_TOPIC, payload, qos=1)

            print(f"\nMessage #{message_count} published:")
            print(f"   Topic: {MQTT_TOPIC}")
            print(f"   Temperature: {data['temperature']}°C")

            # Wait 1 second before next message
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping publisher...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        client.loop_stop()
        client.disconnect()
        print("Publisher disconnected")


if __name__ == "__main__":
    main()
