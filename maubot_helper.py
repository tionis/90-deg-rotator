#!/usr/bin/env python3
"""
Maubot management helper script
"""

import json
import os
from pathlib import Path

import requests


def get_maubot_token():
    """Get the maubot access token from config"""
    config_path = Path.home() / ".config" / "maubot-cli.json"
    if not config_path.exists():
        print(f"Config file not found at {config_path}")
        return None

    try:
        with open(config_path) as f:
            config = json.load(f)
            default_server = config.get("default_server")
            if default_server and default_server in config.get("servers", {}):
                return config["servers"][default_server]
    except Exception as e:
        print(f"Error reading config: {e}")
    return None


def list_plugins(base_url="https://conduit-test.fs-info.de"):
    """List all plugins on the maubot server"""
    token = get_maubot_token()
    if not token:
        print("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # List plugins
        response = requests.get(f"{base_url}/_matrix/maubot/v1/plugins", headers=headers)
        if response.status_code == 200:
            plugins = response.json()
            print("Available plugins:")
            if isinstance(plugins, list):
                for plugin in plugins:
                    print(f"  - {plugin}")
            elif isinstance(plugins, dict):
                for plugin_id, plugin_info in plugins.items():
                    print(f"  - {plugin_id}: {plugin_info}")
        else:
            print(f"Failed to list plugins: {response.status_code} {response.text}")

        # List instances
        response = requests.get(f"{base_url}/_matrix/maubot/v1/instances", headers=headers)
        if response.status_code == 200:
            instances = response.json()
            print("\nActive instances:")
            if isinstance(instances, list):
                for instance in instances:
                    print(f"  - {instance}")
            elif isinstance(instances, dict):
                for instance_id, instance_info in instances.items():
                    print(f"  - {instance_id}: {instance_info}")
        else:
            print(f"Failed to list instances: {response.status_code} {response.text}")

    except Exception as e:
        print(f"Error: {e}")


def delete_instance(instance_id, base_url="https://conduit-test.fs-info.de"):
    """Delete a plugin instance"""
    token = get_maubot_token()
    if not token:
        print("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code == 200:
            print(f"Successfully deleted instance: {instance_id}")
        else:
            print(
                f"Failed to delete instance {instance_id}: {response.status_code} {response.text}"
            )
    except Exception as e:
        print(f"Error deleting instance: {e}")


def disable_instance(instance_id, base_url="https://conduit-test.fs-info.de"):
    """Disable a plugin instance"""
    token = get_maubot_token()
    if not token:
        print("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        # First get the current instance config
        response = requests.get(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code != 200:
            print(f"Failed to get instance {instance_id}: {response.status_code} {response.text}")
            return

        instance_data = response.json()
        instance_data["enabled"] = False

        # Update the instance to disable it
        response = requests.put(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}",
            headers=headers,
            json=instance_data,
        )
        if response.status_code == 200:
            print(f"Successfully disabled instance: {instance_id}")
        else:
            print(
                f"Failed to disable instance {instance_id}: {response.status_code} {response.text}"
            )
    except Exception as e:
        print(f"Error disabling instance: {e}")


def list_all_instances(base_url="https://conduit-test.fs-info.de"):
    """List all instances in more detail"""
    token = get_maubot_token()
    if not token:
        print("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{base_url}/_matrix/maubot/v1/instances", headers=headers)
        if response.status_code == 200:
            instances = response.json()
            print("All instances:")
            if isinstance(instances, list):
                for instance in instances:
                    print(f"  - {instance}")
            elif isinstance(instances, dict):
                for instance_id, instance_info in instances.items():
                    enabled = instance_info.get("enabled", "unknown")
                    started = instance_info.get("started", "unknown")
                    plugin_type = instance_info.get("type", "unknown")
                    print(f"  - ID: {instance_id}")
                    print(f"    Type: {plugin_type}")
                    print(f"    Enabled: {enabled}")
                    print(f"    Started: {started}")
                    print()
        else:
            print(f"Failed to list instances: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error: {e}")


def update_instance_plugin(
    instance_id, new_plugin_type, base_url="https://conduit-test.fs-info.de"
):
    """Update an instance to use a different plugin type"""
    token = get_maubot_token()
    if not token:
        print("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        # First get the current instance config
        response = requests.get(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code != 200:
            print(f"Failed to get instance {instance_id}: {response.status_code} {response.text}")
            return

        instance_data = response.json()
        print(f"Current instance type: {instance_data.get('type')}")

        # Update the plugin type
        instance_data["type"] = new_plugin_type

        # Update the instance
        response = requests.put(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}",
            headers=headers,
            json=instance_data,
        )
        if response.status_code == 200:
            print(f"Successfully updated instance {instance_id} to use plugin {new_plugin_type}")
        else:
            print(
                f"Failed to update instance {instance_id}: {response.status_code} {response.text}"
            )
    except Exception as e:
        print(f"Error updating instance: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "list":
            list_plugins()
        elif command == "list-detailed":
            list_all_instances()
        elif command == "disable" and len(sys.argv) > 2:
            disable_instance(sys.argv[2])
        elif command == "delete" and len(sys.argv) > 2:
            delete_instance(sys.argv[2])
        elif command == "update-plugin" and len(sys.argv) > 3:
            update_instance_plugin(sys.argv[2], sys.argv[3])
        else:
            print(
                "Usage: python maubot_helper.py [list|list-detailed|disable <instance_id>|delete <instance_id>|update-plugin <instance_id> <new_plugin_type>]"
            )
    else:
        list_plugins()
