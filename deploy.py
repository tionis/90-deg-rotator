#!/usr/bin/env python3
"""
Deployment script for NinetyDegreeRotator maubot plugin

This script automates the build, upload, and deployment process.
Uses UV for dependency management when available.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"📋 {description}")
    print(f"   Running: {command}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"   ✅ Success")
        if result.stdout:
            print(f"   📄 Output: {result.stdout.strip()}")
    else:
        print(f"   ❌ Failed with exit code {result.returncode}")
        if result.stderr:
            print(f"   ⚠️  Error: {result.stderr.strip()}")
        return False

    return True


def check_uv_available():
    """Check if UV is available and recommend its use"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ UV available: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("⚠️  UV not found. Consider installing for faster dependency management:")
    print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
    return False


def setup_dependencies():
    """Setup project dependencies using UV if available, otherwise pip"""
    if check_uv_available():
        print("🔧 Setting up dependencies with UV...")
        commands = [
            "uv venv --allow-existing",
            "uv pip install -r requirements-dev.txt",
            "uv pip install maubot",  # Try with UV first
        ]
    else:
        print("🔧 Setting up dependencies with pip...")
        commands = [
            "python3 -m venv .venv --clear",
            ".venv/bin/pip install -r requirements-dev.txt",
            ".venv/bin/pip install maubot",
        ]

    for cmd in commands:
        # Skip maubot installation if already available
        if "maubot" in cmd and check_mbc_available():
            print("   ⏭️  Skipping maubot install - already available")
            continue

        result = run_command(cmd, f"Running: {cmd}")

        # For maubot install failures, continue anyway (it might be available system-wide)
        if not result and "maubot" in cmd:
            print("   ⚠️  maubot install failed, checking if mbc is available...")
            if check_mbc_available():
                print("   ✅ mbc is available system-wide, continuing...")
                continue
            else:
                print("   ❌ mbc not available. Install maubot manually with:")
                print("       pip install --user maubot")
                return False
        elif not result:
            return False

    return True


def check_mbc_available():
    """Check if mbc (maubot-cli) is available"""
    try:
        result = subprocess.run(["mbc", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_current_plugin_version():
    """Extract current plugin version from maubot.yaml"""
    try:
        with open("maubot.yaml", "r") as f:
            content = f.read()
            for line in content.split("\n"):
                if line.startswith("id:"):
                    return line.split(":")[-1].strip()
    except Exception as e:
        print(f"⚠️  Could not determine plugin version: {e}")
    return None


def build_plugin():
    """Build the maubot plugin"""
    return run_command("mbc build", "Building maubot plugin")


def upload_plugin():
    """Upload the plugin to maubot server"""
    plugin_version = get_current_plugin_version()
    if not plugin_version:
        print("❌ Could not determine plugin version")
        return False

    plugin_file = f"{plugin_version}-v0.2.0.mbp"

    if not os.path.exists(plugin_file):
        print(f"❌ Plugin file {plugin_file} not found")
        return False

    return run_command(f"mbc upload {plugin_file}", "Uploading plugin to maubot server")


def update_instance(instance_id):
    """Update a maubot instance to use the new plugin version"""
    plugin_version = get_current_plugin_version()
    if not plugin_version:
        print("❌ Could not determine plugin version")
        return False

    return run_command(
        f"./maubot_helper.py update {instance_id} {plugin_version}",
        f"Updating instance {instance_id} to use {plugin_version}",
    )


def move_to_builds():
    """Move built plugin to builds directory"""
    plugin_version = get_current_plugin_version()
    if not plugin_version:
        return False

    plugin_file = f"{plugin_version}-v0.2.0.mbp"

    if os.path.exists(plugin_file):
        os.makedirs("builds", exist_ok=True)
        return run_command(f"mv {plugin_file} builds/", "Moving plugin to builds directory")
    return True


def deploy_full(instance_id):
    """Complete deployment process"""
    print("🚀 Starting full deployment process")
    print("=" * 50)

    steps = [
        ("build", lambda: build_plugin()),
        ("upload", lambda: upload_plugin()),
        ("organize", lambda: move_to_builds()),
    ]

    if instance_id:
        steps.append(("update", lambda: update_instance(instance_id)))

    for step_name, step_func in steps:
        print(f"\n📍 Step: {step_name}")
        if not step_func():
            print(f"❌ Deployment failed at step: {step_name}")
            return False
        print(f"✅ Step {step_name} completed")

    print("\n🎉 Deployment completed successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Deploy NinetyDegreeRotator maubot plugin")
    parser.add_argument(
        "action", choices=["setup", "build", "upload", "deploy"], help="Action to perform"
    )
    parser.add_argument("-i", "--instance", help="Instance ID to update (for deploy action)")

    args = parser.parse_args()

    # Ensure we're in the right directory
    if not os.path.exists("maubot.yaml"):
        print("❌ maubot.yaml not found. Please run from the plugin root directory.")
        sys.exit(1)

    success = False

    if args.action == "setup":
        success = setup_dependencies()
    elif args.action == "build":
        success = build_plugin() and move_to_builds()
    elif args.action == "upload":
        success = upload_plugin()
    elif args.action == "deploy":
        if not args.instance:
            print("❌ Instance ID required for deploy action. Use -i <instance_id>")
            sys.exit(1)
        success = deploy_full(args.instance)

    if success:
        print("✅ Operation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
