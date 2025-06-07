#!/usr/bin/env python3
"""
Project status and health check script
"""

import json
import os
import subprocess
import sys
from pathlib import Path


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


def check_mbc_availability():
    """Check if mbc is available for building"""
    print("\n🔧 Checking mbc availability...")

    try:
        # Just check if mbc command exists using help command
        result = subprocess.run(["mbc", "--help"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ mbc command available for building")
        else:
            print("⚠️  mbc may have issues - check installation")
    except FileNotFoundError:
        print("❌ mbc command not found - install with: pip install maubot")
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


def main():
    """Run all status checks"""
    print("🏥 90 Degree Rotator - Project Health Check")
    print("=" * 50)

    checks = [
        check_plugin_version,
        check_builds,
        check_mbc_availability,
        check_git_status,
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
    print("   Build:       python deploy.py build")
    print("   Build+Upload: python deploy.py build-upload")
    print("   Upload:      python deploy.py upload")
    print("   Deploy:      python deploy.py deploy -i <instance-id>")
    print("   Status:      ./maubot_helper.py status")


if __name__ == "__main__":
    main()
