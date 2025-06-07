#!/usr/bin/env python3
"""
Deployment script for NinetyDegreeRotator maubot plugin

This script automates the build, upload, and deployment process.
Uses UV for dependency management when available.
"""

import argparse
import json
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
            "uv sync --dev",  # Install all dependencies including dev and main
        ]
    else:
        print("🔧 Setting up dependencies with pip...")
        commands = [
            "python3 -m venv .venv",
            ".venv/bin/pip install -e .[dev]",  # Install all dependencies including maubot
        ]

    for cmd in commands:
        # Skip if dependencies are already available
        if ("sync" in cmd or "install -e" in cmd) and check_mbc_available():
            print("   ⏭️  Skipping dependency install - mbc already available in virtual environment")
            continue

        result = run_command(cmd, f"Running: {cmd}")

        # For dependency install failures, check if we can proceed
        if not result:
            if "sync" in cmd or "install -e" in cmd:
                print("   ⚠️  Dependency install failed, checking if mbc is available...")
                if check_mbc_available():
                    print("   ✅ mbc is available, continuing...")
                    continue
                else:
                    print("   ❌ mbc not available. Dependencies not properly installed.")
                    print("       Try running: uv sync --dev  (or pip install -e .[dev])")
                    return False
            else:
                return False

    return True


def check_mbc_available():
    """Check if mbc (maubot-cli) is available in the virtual environment"""
    # First try the virtual environment using python -m
    venv_python = Path(".venv/bin/python")
    if venv_python.exists():
        try:
            result = subprocess.run([str(venv_python), "-m", "maubot.cli", "--help"], 
                                    capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            pass
    
    # Fallback to system-wide mbc
    try:
        result = subprocess.run(["mbc", "--help"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_mbc_command():
    """Get the appropriate mbc command (prefer virtual environment)"""
    venv_python = Path(".venv/bin/python")
    if venv_python.exists():
        try:
            result = subprocess.run([str(venv_python), "-m", "maubot.cli", "--help"], 
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return f"{venv_python} -m maubot.cli"
        except (subprocess.TimeoutExpired, Exception):
            pass
    return "mbc"


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


def build_and_upload():
    """Build and upload the plugin in one step, with reload verification"""
    print("🚀 Building and uploading plugin...")
    
    # Step 1: Build
    if not build_plugin():
        return False
    
    # Step 2: Upload
    if not upload_plugin():
        return False
    
    # Step 3: Verify server reload
    if not verify_plugin_reload():
        print("⚠️  Warning: Could not verify plugin reload, but upload succeeded")
    
    # Step 4: Move to builds
    return move_to_builds()


def verify_plugin_reload():
    """Check if the maubot server successfully reloaded the plugin"""
    plugin_id = get_current_plugin_version()
    if not plugin_id:
        return False
    
    print("🔍 Verifying plugin reload on server...")
    
    try:
        # Use maubot-api to check if plugin is loaded
        result = subprocess.run(
            ["./maubot-api.py", "list", "--json"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            
            # Check if our plugin ID exists in the plugins list
            if 'plugins' in data:
                for plugin in data['plugins']:
                    if plugin.get('id') == plugin_id:
                        print(f"   ✅ Plugin {plugin_id} successfully loaded on server")
                        return True
            
            print(f"   ❌ Plugin {plugin_id} not found in server plugin list")
            return False
            
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"   ⚠️  Could not verify reload: {e}")
        return False
    
    return False


def build_plugin():
    """Build the maubot plugin"""
    mbc_cmd = get_mbc_command()
    return run_command(f"{mbc_cmd} build", "Building maubot plugin")


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

    mbc_cmd = get_mbc_command()
    return run_command(f"{mbc_cmd} upload {plugin_file}", "Uploading plugin to maubot server")


def update_instance(instance_id):
    """Update a maubot instance to use the new plugin version"""
    plugin_version = get_current_plugin_version()
    if not plugin_version:
        print("❌ Could not determine plugin version")
        return False

    return run_command(
        f"./maubot-api.py update {instance_id} {plugin_version}",
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
        ("build-upload", lambda: build_and_upload()),
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


# Status checking functions (merged from status.py)
def check_plugin_version():
    """Check current plugin version"""
    print("\n🏷️  Checking plugin version...")

    try:
        with open("maubot.yaml", "r") as f:
            content = f.read()
            for line in content.split("\n"):
                if line.startswith("id:"):
                    plugin_id = line.split(":")[-1].strip()
                    print(f"✅ Plugin ID: {plugin_id}")
                elif line.startswith("version:"):
                    version = line.split(":")[-1].strip()
                    print(f"✅ Plugin Version: {version}")
    except Exception as e:
        print(f"❌ Could not read plugin version: {e}")
        return False

    # Check code version
    try:
        with open("NinetyDegreeRotator/__init__.py", "r") as f:
            content = f.read()
            for line in content.split("\n"):
                if "PLUGIN_VERSION" in line and "=" in line:
                    code_version = line.split("=")[-1].strip().strip("\"'")
                    print(f"✅ Code Version: {code_version}")
                    break
    except Exception as e:
        print(f"❌ Could not read code version: {e}")
        return False

    return True


def check_builds():
    """Check available builds"""
    print("\n🔨 Checking builds...")

    builds_dir = Path("builds")
    if builds_dir.exists():
        builds = list(builds_dir.glob("*.mbp"))
        if builds:
            print(f"✅ Found {len(builds)} build(s):")
            for build in sorted(builds):
                print(f"   📦 {build.name}")
        else:
            print("⚠️  No builds found in builds/ directory")
    else:
        print("❌ builds/ directory not found")


def check_mbc_availability_detailed():
    """Check if mbc is available for building (detailed version)"""
    print("\n🔧 Checking mbc availability...")

    # First try virtual environment
    venv_python = Path(".venv/bin/python")
    if venv_python.exists():
        try:
            result = subprocess.run([str(venv_python), "-m", "maubot.cli", "--help"], 
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ mbc available in virtual environment (.venv/bin/python -m maubot.cli)")
                return True
        except (subprocess.TimeoutExpired, Exception):
            pass

    # Try system-wide mbc
    try:
        result = subprocess.run(["mbc", "--help"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ mbc command available for building")
        else:
            print("⚠️  mbc may have issues - check installation")
    except FileNotFoundError:
        print("❌ mbc command not found - install with: pip install maubot")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  mbc command timed out")
    
    return True  # Don't fail the overall check since mbc might work for building


def check_git_status():
    """Check git repository status"""
    print("\n📝 Checking git status...")

    if os.path.exists(".git"):
        try:
            # Check if there are uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10
            )
            if result.stdout.strip():
                print("⚠️  Uncommitted changes detected:")
                print(result.stdout)
            else:
                print("✅ Working directory clean")

            # Check current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                print(f"✅ Current branch: {branch}")
        except FileNotFoundError:
            print("❌ git command not found")
        except subprocess.TimeoutExpired:
            print("⚠️  git command timed out - repository may be in bad state")
    else:
        print("⚠️  Not a git repository")


def check_server_status():
    """Check maubot server status using helper script"""
    print("\n🌐 Checking server status...")

    try:
        result = subprocess.run(
            ["./maubot-api.py", "status"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Server status:")
            print(f"   {result.stdout.strip()}")
        else:
            print("⚠️  Could not get server status:")
            print(f"   {result.stderr.strip()}")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"⚠️  Could not check server status: {e}")
        return False
    
    return True


def run_status_check():
    """Run comprehensive project health check"""
    print("🏥 90 Degree Rotator - Project Health Check")
    print("=" * 50)

    checks = [
        check_plugin_version,
        check_builds,
        check_mbc_availability_detailed,
        check_git_status,
        check_server_status,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append(False)
        print()  # Empty line between checks

    # Summary
    print("📊 Summary")
    print("-" * 20)
    passed = sum(1 for r in results if r is not False)
    total = len(results)

    if passed == total:
        print("🎉 All checks passed! Project is in good health.")
    else:
        print(f"⚠️  {passed}/{total} checks passed. Some issues need attention.")

    print("\n💡 Quick commands:")
    print("   Build:       ./maubot-dev.py build")
    print("   Build+Upload: ./maubot-dev.py build-upload")
    print("   Upload:      ./maubot-dev.py upload")
    print("   Deploy:      ./maubot-dev.py deploy -i <instance-id>")
    print("   Status:      ./maubot-api.py status")
    
    return passed == total


def main():
    parser = argparse.ArgumentParser(description="Deploy NinetyDegreeRotator maubot plugin")
    parser.add_argument(
        "action", 
        choices=["setup", "build", "upload", "build-upload", "deploy", "status"], 
        help="Action to perform"
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
    elif args.action == "build-upload":
        success = build_and_upload()
    elif args.action == "deploy":
        if not args.instance:
            print("❌ Instance ID required for deploy action. Use -i <instance_id>")
            sys.exit(1)
        success = deploy_full(args.instance)
    elif args.action == "status":
        success = run_status_check()

    if success:
        print("✅ Operation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
