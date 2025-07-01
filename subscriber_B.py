#!/usr/bin/env python3
"""
MQTT Subscriber B Script
Subscribes to the "data/temperature" topic for temperature data only
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "data/temperature"
MQTT_CLIENT_ID = "python_subscriber_B"


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        # Subscribe to topic
        client.subscribe(MQTT_TOPIC, qos=1)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker, return code: {rc}")


def on_message(client, userdata, msg):
    """Callback when message is received"""
    try:
        # Parse JSON message
        data = json.loads(msg.payload.decode())

        print(f"\nTemperature data received:")
        print(f"   Temperature: {data.get('temperature', 'N/A')}°C")
        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"   Location: {data.get('location', 'N/A')}")

    except json.JSONDecodeError:
        print(f"\nRaw message received: {msg.payload.decode()}")
    except Exception as e:
        print(f"Error processing message: {e}")


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscribed to topic"""
    print(f"Subscribed with message ID: {mid}, QoS: {granted_qos}")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print(f"Unexpected disconnection, return code: {rc}")
    else:
        print("Disconnected from MQTT broker")


def main():
    """Main function to subscribe to messages"""
    # Create MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect

    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        print("Starting message loop...")
        print("Press Ctrl+C to stop...")

        # Start the loop (this will block and handle messages)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\nStopping subscriber B...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        client.disconnect()
        print("Subscriber B disconnected")


if __name__ == "__main__":
    main()
