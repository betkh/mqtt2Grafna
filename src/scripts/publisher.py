#!/usr/bin/env python3
"""
MQTT Publisher Script
Publishes temperature data to "data/temperature" topic and humidity data to "data/humidity" topic
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_TEMPERATURE = "data/temperature"
MQTT_TOPIC_HUMIDITY = "data/humidity"
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


def create_temperature_data():
    """Create sample temperature data"""
    return {
        "timestamp": datetime.now().isoformat(),
        "temperature": round(random.uniform(15.0, 30.0), 2)
    }


def create_humidity_data():
    """Create sample humidity data"""
    return {
        "timestamp": datetime.now().isoformat(),
        "humidity": round(random.uniform(40.0, 80.0), 2)
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

        print(f"Publishing messages to topics:")
        print(f"   Temperature: {MQTT_TOPIC_TEMPERATURE}")
        print(f"   Humidity: {MQTT_TOPIC_HUMIDITY}")
        print("Press Ctrl+C to stop...")

        # Publish messages every second for real-time visualization
        message_count = 0
        while True:
            # Create sample data
            temp_data = create_temperature_data()
            humidity_data = create_humidity_data()
            message_count += 1

            # Convert to JSON
            temp_payload = json.dumps(temp_data, indent=2)
            humidity_payload = json.dumps(humidity_data, indent=2)

            # Publish temperature message
            temp_result = client.publish(
                MQTT_TOPIC_TEMPERATURE, temp_payload, qos=1)

            # Publish humidity message
            humidity_result = client.publish(
                MQTT_TOPIC_HUMIDITY, humidity_payload, qos=1)

            print(f"\nMessage #{message_count} published:")
            print(f"   Temperature Topic: {MQTT_TOPIC_TEMPERATURE}")
            print(f"     Temperature: {temp_data['temperature']}°C")
            print(f"     Timestamp: {temp_data['timestamp']}")
            print(f"   Humidity Topic: {MQTT_TOPIC_HUMIDITY}")
            print(f"     Humidity: {humidity_data['humidity']}%")
            print(f"     Timestamp: {humidity_data['timestamp']}")

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
