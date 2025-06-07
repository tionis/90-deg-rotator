#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "requests>=2.25.0",
# ]
# ///
"""
Maubot management helper script with improved CLI interface
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests

# ANSI color codes for better output formatting
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def colored(text: str, color: str) -> str:
    """Add color to text if stdout is a terminal"""
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.RESET}"
    return text

def status_icon(enabled: bool, started: bool) -> str:
    """Get a status icon based on enabled/started state"""
    if enabled and started:
        return colored("●", Colors.GREEN)  # Running
    elif enabled and not started:
        return colored("◐", Colors.YELLOW)  # Enabled but not started
    else:
        return colored("○", Colors.RED)  # Disabled

def print_separator(title: str = "", char: str = "─"):
    """Print a separator line with optional title"""
    width = 80
    if title:
        title_formatted = f" {colored(title, Colors.BOLD + Colors.CYAN)} "
        padding = (width - len(title) - 2) // 2
        print(char * padding + title_formatted + char * padding)
    else:
        print(char * width)

def print_table_row(col1: str, col2: str, col3: str, col4: str, col5: str = "", width1: int = 20, width2: int = 30, width3: int = 10, width4: int = 10, width5: int = 8):
    """Print a formatted table row"""
    print(f"{col1:<{width1}} {col2:<{width2}} {col3:<{width3}} {col4:<{width4}} {col5:<{width5}}")

def print_error(message: str):
    """Print an error message"""
    print(f"{colored('ERROR:', Colors.RED + Colors.BOLD)} {message}", file=sys.stderr)

def print_success(message: str):
    """Print a success message"""
    print(f"{colored('SUCCESS:', Colors.GREEN + Colors.BOLD)} {message}")

def print_info(message: str):
    """Print an info message"""
    print(f"{colored('INFO:', Colors.BLUE + Colors.BOLD)} {message}")


def get_maubot_token():
    """Get the maubot access token from config"""
    config_path = Path.home() / ".config" / "maubot-cli.json"
    if not config_path.exists():
        print_error(f"Config file not found at {config_path}")
        return None

    try:
        with open(config_path) as f:
            config = json.load(f)
            default_server = config.get("default_server")
            if default_server and default_server in config.get("servers", {}):
                return config["servers"][default_server]
    except Exception as e:
        print_error(f"Error reading config: {e}")
    return None


def list_plugins_formatted(base_url="https://conduit-test.fs-info.de", output_json=False):
    """List all plugins in a YAML-like formatted way"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get plugins
        response = requests.get(f"{base_url}/_matrix/maubot/v1/plugins", headers=headers)
        if response.status_code != 200:
            print_error(f"Failed to list plugins: {response.status_code} {response.text}")
            return

        plugins = response.json()
        
        # Get instances  
        response = requests.get(f"{base_url}/_matrix/maubot/v1/instances", headers=headers)
        if response.status_code != 200:
            print_error(f"Failed to list instances: {response.status_code} {response.text}")
            return

        instances = response.json()

        if output_json:
            result = {
                "plugins": plugins,
                "instances": instances
            }
            print(json.dumps(result, indent=2))
            return

        # Count active plugins and instances
        active_plugins = [p for p in plugins if len(p.get('instances', [])) > 0] if isinstance(plugins, list) else []
        total_instances = len(instances) if isinstance(instances, list) else 0
        running_instances = 0
        if isinstance(instances, list):
            running_instances = sum(1 for inst in instances if inst.get('enabled', False) and inst.get('started', False))

        # Header with summary
        print(colored("maubot status:", Colors.BOLD + Colors.CYAN))
        print(f"  {colored('plugins:', Colors.BLUE)} {len(plugins) if isinstance(plugins, list) else 0} total, {len(active_plugins)} active")
        print(f"  {colored('instances:', Colors.BLUE)} {total_instances} total, {running_instances} running")
        print()

        # Display instances in YAML-like format
        if isinstance(instances, list) and instances:
            print(colored("instances:", Colors.BOLD + Colors.YELLOW))
            for instance_info in instances:
                instance_id = instance_info.get("id", "Unknown")
                enabled = instance_info.get("enabled", False)
                started = instance_info.get("started", False)
                plugin_type = instance_info.get("type", "Unknown")
                primary_user = instance_info.get("primary_user", "Unknown")
                has_database = instance_info.get("database", False)
                
                # Status determination
                if enabled and started:
                    status = colored("running", Colors.GREEN)
                    status_icon = colored("●", Colors.GREEN)
                elif enabled and not started:
                    status = colored("stopped", Colors.YELLOW)
                    status_icon = colored("◐", Colors.YELLOW)
                else:
                    status = colored("disabled", Colors.RED)
                    status_icon = colored("○", Colors.RED)
                
                # Extract user name from full user ID for cleaner display
                user_display = primary_user.split('@')[1].split(':')[0] if '@' in primary_user else primary_user
                
                print(f"  {status_icon} {colored(instance_id + ':', Colors.CYAN)}")
                print(f"    {colored('plugin:', Colors.BLUE)} {colored(plugin_type, Colors.MAGENTA)}")
                print(f"    {colored('status:', Colors.BLUE)} {status}")
                print(f"    {colored('user:', Colors.BLUE)} {colored(user_display, Colors.WHITE)}")
                if has_database:
                    db_engine = instance_info.get("database_engine", "unknown")
                    print(f"    {colored('database:', Colors.BLUE)} {colored(db_engine, Colors.GREEN)}")
                print()
        else:
            print(colored("instances:", Colors.BOLD + Colors.YELLOW))
            print(f"  {colored('none found', Colors.YELLOW)}")
            print()

        # Display available plugins
        if isinstance(plugins, list) and plugins:
            print(colored("available plugins:", Colors.BOLD + Colors.CYAN))
            # Group by active/inactive
            active_plugins = [p for p in plugins if len(p.get('instances', [])) > 0]
            inactive_plugins = [p for p in plugins if len(p.get('instances', [])) == 0]
            
            if active_plugins:
                    print(f"  {colored('active:', Colors.GREEN)}")
                    for plugin in active_plugins:
                        plugin_id = plugin.get('id', 'Unknown')
                        version = plugin.get('version', 'Unknown')
                        instance_count = len(plugin.get('instances', []))
                        instance_text = f"{instance_count} instance" + ("s" if instance_count != 1 else "")
                        print(f"    - {colored(plugin_id, Colors.CYAN)} {colored(f'v{version}', Colors.WHITE)} ({colored(instance_text, Colors.YELLOW)})")
                    print()
            
            if inactive_plugins:
                print(f"  {colored('available:', Colors.BLUE)}")
                for plugin in inactive_plugins[:10]:  # Limit to first 10 to avoid clutter
                    plugin_id = plugin.get('id', 'Unknown')
                    version = plugin.get('version', 'Unknown')
                    print(f"    - {colored(plugin_id, Colors.CYAN)} {colored(f'v{version}', Colors.WHITE)}")
                
                if len(inactive_plugins) > 10:
                    remaining = len(inactive_plugins) - 10
                    print(f"    {colored(f'... and {remaining} more', Colors.YELLOW)}")
                print()

    except Exception as e:
        print_error(f"Error: {e}")


def delete_instance(instance_id, base_url="https://conduit-test.fs-info.de"):
    """Delete a plugin instance"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code == 200:
            print_success(f"Successfully deleted instance: {colored(instance_id, Colors.YELLOW)}")
        else:
            print_error(f"Failed to delete instance {instance_id}: {response.status_code} {response.text}")
    except Exception as e:
        print_error(f"Error deleting instance: {e}")


def disable_instance(instance_id, base_url="https://conduit-test.fs-info.de"):
    """Disable a plugin instance"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        # First get the current instance config
        response = requests.get(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code != 200:
            print_error(f"Failed to get instance {instance_id}: {response.status_code} {response.text}")
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
            print_success(f"Successfully disabled instance: {colored(instance_id, Colors.YELLOW)}")
        else:
            print_error(f"Failed to disable instance {instance_id}: {response.status_code} {response.text}")
    except Exception as e:
        print_error(f"Error disabling instance: {e}")


def enable_instance(instance_id, base_url="https://conduit-test.fs-info.de"):
    """Enable a plugin instance"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        # First get the current instance config
        response = requests.get(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code != 200:
            print_error(f"Failed to get instance {instance_id}: {response.status_code} {response.text}")
            return

        instance_data = response.json()
        instance_data["enabled"] = True

        # Update the instance to enable it
        response = requests.put(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}",
            headers=headers,
            json=instance_data,
        )
        if response.status_code == 200:
            print_success(f"Successfully enabled instance: {colored(instance_id, Colors.YELLOW)}")
        else:
            print_error(f"Failed to enable instance {instance_id}: {response.status_code} {response.text}")
    except Exception as e:
        print_error(f"Error enabling instance: {e}")


def list_instances_detailed(base_url="https://conduit-test.fs-info.de", output_json=False):
    """List all instances with detailed YAML-like information"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{base_url}/_matrix/maubot/v1/instances", headers=headers)
        if response.status_code != 200:
            print_error(f"Failed to list instances: {response.status_code} {response.text}")
            return

        instances = response.json()
        
        if output_json:
            print(json.dumps(instances, indent=2))
            return

        if not isinstance(instances, list) or not instances:
            print(colored("instances:", Colors.BOLD + Colors.YELLOW))
            print(f"  {colored('none found', Colors.YELLOW)}")
            return

        print(colored("instance details:", Colors.BOLD + Colors.CYAN))
        print()
        
        for instance_info in instances:
            instance_id = instance_info.get("id", "Unknown")
            enabled = instance_info.get("enabled", False)
            started = instance_info.get("started", False)
            plugin_type = instance_info.get("type", "Unknown")
            primary_user = instance_info.get("primary_user", "Unknown")
            has_database = instance_info.get("database", False)
            db_interface = instance_info.get("database_interface", "None")
            db_engine = instance_info.get("database_engine", "None")
            
            # Status determination
            if enabled and started:
                status = colored("running", Colors.GREEN)
                status_icon = colored("●", Colors.GREEN)
            elif enabled and not started:
                status = colored("stopped", Colors.YELLOW)
                status_icon = colored("◐", Colors.YELLOW)
            else:
                status = colored("disabled", Colors.RED)
                status_icon = colored("○", Colors.RED)
            
            # Extract clean user name
            user_display = primary_user.split('@')[1].split(':')[0] if '@' in primary_user else primary_user
            user_server = primary_user.split(':')[1] if ':' in primary_user else ""
            
            print(f"{status_icon} {colored(instance_id + ':', Colors.BOLD + Colors.CYAN)}")
            print(f"  {colored('plugin:', Colors.BLUE)} {colored(plugin_type, Colors.MAGENTA)}")
            print(f"  {colored('status:', Colors.BLUE)} {status}")
            print(f"  {colored('user:', Colors.BLUE)} {colored(user_display, Colors.WHITE)}{colored('@' + user_server if user_server else '', Colors.YELLOW)}")
            
            if has_database:
                print(f"  {colored('database:', Colors.BLUE)}")
                print(f"    {colored('engine:', Colors.BLUE)} {colored(db_engine, Colors.GREEN)}")
                if db_interface and db_interface != "None":
                    print(f"    {colored('interface:', Colors.BLUE)} {colored(db_interface, Colors.GREEN)}")
            else:
                print(f"  {colored('database:', Colors.BLUE)} {colored('none', Colors.YELLOW)}")
            
            # Show configuration info
            config = instance_info.get("config", "")
            if config and config.strip():
                config_lines = len(config.strip().split('\n'))
                print(f"  {colored('config:', Colors.BLUE)} {colored(f'{config_lines} lines', Colors.CYAN)}")
            else:
                print(f"  {colored('config:', Colors.BLUE)} {colored('empty', Colors.YELLOW)}")
            
            print()

    except Exception as e:
        print_error(f"Error: {e}")


def update_instance_plugin(
    instance_id, new_plugin_type, base_url="https://conduit-test.fs-info.de"
):
    """Update an instance to use a different plugin type"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        # First get the current instance config
        response = requests.get(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code != 200:
            print_error(f"Failed to get instance {instance_id}: {response.status_code} {response.text}")
            return

        instance_data = response.json()
        old_type = instance_data.get('type')
        print_info(f"Current instance type: {colored(old_type, Colors.CYAN)}")

        # Update the plugin type
        instance_data["type"] = new_plugin_type

        # Update the instance
        response = requests.put(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}",
            headers=headers,
            json=instance_data,
        )
        if response.status_code == 200:
            print_success(f"Successfully updated instance {colored(instance_id, Colors.YELLOW)} from {colored(old_type, Colors.CYAN)} to {colored(new_plugin_type, Colors.CYAN)}")
        else:
            print_error(f"Failed to update instance {instance_id}: {response.status_code} {response.text}")
    except Exception as e:
        print_error(f"Error updating instance: {e}")


def quick_status(base_url="https://conduit-test.fs-info.de"):
    """Show a quick one-line status summary"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get instances
        response = requests.get(f"{base_url}/_matrix/maubot/v1/instances", headers=headers)
        if response.status_code != 200:
            print_error(f"Failed to get status: {response.status_code}")
            return

        instances = response.json()
        
        if not isinstance(instances, list):
            print(colored("no instances found", Colors.YELLOW))
            return

        total = len(instances)
        running = sum(1 for inst in instances if inst.get('enabled', False) and inst.get('started', False))
        stopped = sum(1 for inst in instances if inst.get('enabled', False) and not inst.get('started', False))
        disabled = sum(1 for inst in instances if not inst.get('enabled', False))

        status_parts = []
        if running > 0:
            status_parts.append(colored(f"{running} running", Colors.GREEN))
        if stopped > 0:
            status_parts.append(colored(f"{stopped} stopped", Colors.YELLOW))
        if disabled > 0:
            status_parts.append(colored(f"{disabled} disabled", Colors.RED))

        print(f"maubot: {' • '.join(status_parts)} ({total} total)")

    except Exception as e:
        print_error(f"Error: {e}")


def get_instance_config(instance_id, base_url="https://conduit-test.fs-info.de", output_json=False):
    """Get the configuration of a specific instance"""
    token = get_maubot_token()
    if not token:
        print_error("Could not get access token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{base_url}/_matrix/maubot/v1/instance/{instance_id}", headers=headers
        )
        if response.status_code != 200:
            print_error(f"Failed to get instance {instance_id}: {response.status_code} {response.text}")
            return

        instance_data = response.json()
        
        if output_json:
            print(json.dumps(instance_data, indent=2))
            return

        print(colored(f"config for {instance_id}:", Colors.BOLD + Colors.CYAN))
        print()
        
        config = instance_data.get("config", "")
        if config and config.strip():
            # Add syntax highlighting for YAML-like config
            for line in config.strip().split('\n'):
                if ':' in line and not line.strip().startswith('#'):
                    key, value = line.split(':', 1)
                    print(f"{colored(key + ':', Colors.BLUE)}{value}")
                elif line.strip().startswith('#'):
                    print(colored(line, Colors.YELLOW))
                else:
                    print(line)
        else:
            print(colored("  no configuration found", Colors.YELLOW))

    except Exception as e:
        print_error(f"Error getting instance config: {e}")


def main():
    """Main CLI interface with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Maubot Helper - Manage maubot plugins and instances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                            # Quick status overview
  %(prog)s list                              # List all plugins and instances
  %(prog)s instances                         # List instances in detailed view
  %(prog)s config myinstance                 # Show configuration for instance
  %(prog)s enable myinstance                 # Enable an instance
  %(prog)s disable myinstance                # Disable an instance  
  %(prog)s delete myinstance                 # Delete an instance
  %(prog)s update myinstance new.plugin.id  # Update instance plugin type
  %(prog)s list --json                       # Output as JSON
        """
    )
    
    parser.add_argument(
        "--base-url", 
        default="https://conduit-test.fs-info.de",
        help="Maubot server base URL (default: %(default)s)"
    )
    
    parser.add_argument(
        "--json", 
        action="store_true",
        help="Output data as JSON instead of formatted text"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all plugins and instances")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show quick status summary")
    
    # Instances command  
    instances_parser = subparsers.add_parser("instances", help="List instances with detailed information")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration for an instance")
    config_parser.add_argument("instance_id", help="Instance ID to show config for")
    
    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable an instance")
    enable_parser.add_argument("instance_id", help="Instance ID to enable")
    
    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable an instance")
    disable_parser.add_argument("instance_id", help="Instance ID to disable")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an instance")
    delete_parser.add_argument("instance_id", help="Instance ID to delete")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update instance plugin type")
    update_parser.add_argument("instance_id", help="Instance ID to update")
    update_parser.add_argument("plugin_type", help="New plugin type to use")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == "list":
        list_plugins_formatted(args.base_url, getattr(args, 'json', False))
    elif args.command == "status":
        quick_status(args.base_url)
    elif args.command == "instances":
        list_instances_detailed(args.base_url, args.json)
    elif args.command == "config":
        get_instance_config(args.instance_id, args.base_url, args.json)
    elif args.command == "enable":
        enable_instance(args.instance_id, args.base_url)
    elif args.command == "disable":
        disable_instance(args.instance_id, args.base_url)
    elif args.command == "delete":
        delete_parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
        if not getattr(args, 'confirm', False):
            response = input(f"Are you sure you want to delete instance '{args.instance_id}'? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        delete_instance(args.instance_id, args.base_url)
    elif args.command == "update":
        update_instance_plugin(args.instance_id, args.plugin_type, args.base_url)


if __name__ == "__main__":
    main()
