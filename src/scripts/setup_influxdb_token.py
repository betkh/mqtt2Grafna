#!/usr/bin/env python3
"""
InfluxDB Token Setup Script
Helps create and configure InfluxDB tokens for the MQTT project
"""

import requests
import json
import os
import sys
from pathlib import Path

# Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_USERNAME = "admin"
INFLUXDB_PASSWORD = "adminpassword"
INFLUXDB_ORG = "myorg"
INFLUXDB_BUCKET = "weather_data"


def check_influxdb_running():
    """Check if InfluxDB is running"""
    try:
        response = requests.get(f"{INFLUXDB_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def login_to_influxdb():
    """Login to InfluxDB and get session cookie"""
    login_url = f"{INFLUXDB_URL}/api/v2/signin"
    login_data = {
        "username": INFLUXDB_USERNAME,
        "password": INFLUXDB_PASSWORD
    }

    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            return response.cookies
        else:
            print(f"Failed to login to InfluxDB: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to InfluxDB: {e}")
        return None


def get_org_id(cookies):
    """Get organization ID"""
    orgs_url = f"{INFLUXDB_URL}/api/v2/orgs"

    try:
        response = requests.get(orgs_url, cookies=cookies)
        if response.status_code == 200:
            orgs = response.json()["orgs"]
            for org in orgs:
                if org["name"] == INFLUXDB_ORG:
                    return org["id"]
        print(f"Organization '{INFLUXDB_ORG}' not found")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting organization: {e}")
        return None


def get_bucket_id(cookies, org_id):
    """Get bucket ID"""
    buckets_url = f"{INFLUXDB_URL}/api/v2/buckets?orgID={org_id}"

    try:
        response = requests.get(buckets_url, cookies=cookies)
        if response.status_code == 200:
            buckets = response.json()["buckets"]
            for bucket in buckets:
                if bucket["name"] == INFLUXDB_BUCKET:
                    return bucket["id"]
        print(f"Bucket '{INFLUXDB_BUCKET}' not found")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting bucket: {e}")
        return None


def create_token(cookies, org_id, bucket_id):
    """Create a new API token"""
    token_url = f"{INFLUXDB_URL}/api/v2/authorizations"

    token_data = {
        "orgID": org_id,
        "description": "Telegraf MQTT Data Collection",
        "permissions": [
            {
                "action": "read",
                "resource": {
                    "orgID": org_id,
                    "type": "orgs"
                }
            },
            {
                "action": "write",
                "resource": {
                    "orgID": org_id,
                    "type": "buckets",
                    "id": bucket_id
                }
            },
            {
                "action": "read",
                "resource": {
                    "orgID": org_id,
                    "type": "buckets",
                    "id": bucket_id
                }
            }
        ]
    }

    try:
        response = requests.post(token_url, json=token_data, cookies=cookies)
        if response.status_code == 201:
            token_info = response.json()
            return token_info["token"]
        else:
            print(f"Failed to create token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error creating token: {e}")
        return None


def update_telegraf_config(token):
    """Update telegraf.conf with the new token"""
    telegraf_conf_path = Path("telegraf/telegraf.conf")

    if not telegraf_conf_path.exists():
        print(f"Telegraf config file not found: {telegraf_conf_path}")
        return False

    try:
        # Read current config
        with open(telegraf_conf_path, 'r') as f:
            content = f.read()

        # Replace token line
        import re
        new_content = re.sub(
            r'token = ".*"',
            f'token = "{token}"',
            content
        )

        # Write updated config
        with open(telegraf_conf_path, 'w') as f:
            f.write(new_content)

        print(f"Updated {telegraf_conf_path} with new token")
        return True
    except Exception as e:
        print(f"Error updating telegraf config: {e}")
        return False


def main():
    """Main function"""
    print("InfluxDB Token Setup Script")
    print("=" * 40)

    # Check if InfluxDB is running
    print("1. Checking if InfluxDB is running...")
    if not check_influxdb_running():
        print("InfluxDB is not running. Please start the services first:")
        print("   docker-compose -p mqtt2grafna up -d")
        sys.exit(1)
    print("InfluxDB is running")

    # Login to InfluxDB
    print("\n2. Logging into InfluxDB...")
    cookies = login_to_influxdb()
    if not cookies:
        sys.exit(1)
    print("Successfully logged into InfluxDB")

    # Get organization ID
    print("\n3. Getting organization ID...")
    org_id = get_org_id(cookies)
    if not org_id:
        sys.exit(1)
    print(f"Found organization: {INFLUXDB_ORG} (ID: {org_id})")

    # Get bucket ID
    print("\n4. Getting bucket ID...")
    bucket_id = get_bucket_id(cookies, org_id)
    if not bucket_id:
        sys.exit(1)
    print(f"Found bucket: {INFLUXDB_BUCKET} (ID: {bucket_id})")

    # Create token
    print("\n5. Creating new API token...")
    token = create_token(cookies, org_id, bucket_id)
    if not token:
        sys.exit(1)
    print("Successfully created new API token")

    # Display token
    print(f"\nGenerated Token: {token}")
    print("\nIMPORTANT: Save this token securely! It won't be shown again.")

    # Update telegraf config
    print("\n6. Updating Telegraf configuration...")
    if update_telegraf_config(token):
        print("Telegraf configuration updated")
    else:
        print("Failed to update Telegraf configuration")
        print(
            f"Please manually update 'telegraf/telegraf.conf' with the token: {token}")

    # Instructions
    print("\nNext Steps:")
    print("1. Restart Telegraf to use the new token:")
    print("   docker-compose -p mqtt2grafna restart telegraf")
    print("\n2. Verify data collection is working:")
    print("   docker-compose -p mqtt2grafna logs telegraf")
    print("\n3. Check InfluxDB web interface:")
    print("   http://localhost:8086")
    print("\n4. For production, consider using environment variables:")
    print("   See README.md 'InfluxDB Token Management' section")


if __name__ == "__main__":
    main()
