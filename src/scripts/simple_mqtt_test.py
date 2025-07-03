#!/usr/bin/env python3
"""
Simple MQTT Test Script
Test MQTT data format and reception

# WORKING CODE!
sleep 10 && pipenv run python src/scripts/simple_mqtt_test.py  
"""

import json
import paho.mqtt.client as mqtt
import time

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPICS = ["data/temperature", "data/humidity"]


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✅ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"📡 Subscribed to: {topic}")
    else:
        print(f"❌ Failed to connect, return code: {rc}")


def on_message(client, userdata, msg):
    """Callback when message is received"""
    try:
        print(f"\n📨 Received on topic: {msg.topic}")
        print(f"📄 Raw payload: {msg.payload.decode()}")

        # Try to parse JSON
        data = json.loads(msg.payload.decode())
        print(f"🔍 Parsed JSON: {json.dumps(data, indent=2)}")

        # Check if it has the expected fields
        if msg.topic == "data/temperature":
            if "temperature" in data and "timestamp" in data:
                print(
                    f"✅ Valid temperature data: {data['temperature']}°C at {data['timestamp']}")
            else:
                print(f"❌ Missing required fields in temperature data")

        elif msg.topic == "data/humidity":
            if "humidity" in data and "timestamp" in data:
                print(
                    f"✅ Valid humidity data: {data['humidity']}% at {data['timestamp']}")
            else:
                print(f"❌ Missing required fields in humidity data")

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")


def main():
    print("🚀 Testing MQTT Data Reception...")
    print("=" * 50)

    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Connect to broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        print("🔄 Starting message loop...")
        print("Press Ctrl+C to stop...")

        # Start the loop
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n⏹️  Stopping MQTT test...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()
        print("✅ Disconnected from MQTT broker")


if __name__ == "__main__":
    main()
