# VS Code Configuration for ImageRotator

This directory contains VS Code-specific configuration files to streamline development and deployment of the maubot plugin.

## Available Tasks

Access these through **Terminal > Run Task...** or use the Command Palette (`Ctrl+Shift+P`) and search for "Tasks: Run Task":

### Build & Deployment Tasks
- **Build & Upload Plugin** ⭐ (Default build task) - Builds and uploads in one step
- **Build Plugin** - Only builds the .mbp file
- **Upload Plugin** - Only uploads existing .mbp file
- **Deploy Plugin (with Instance ID)** - Full deployment including instance update
- **Setup Dependencies** - Install required dependencies

### Authentication Tasks
- **mbc Login** - Log into maubot instance for deployment
- **mbc Auth (Bot Account)** - Authenticate Matrix bot account for encryption support

### Management Tasks
- **Check Plugin Status** - Quick status overview
- **Project Health Check** - Comprehensive project health check (builds, versions, git, server)
- **List Plugins & Instances** - Detailed plugin/instance information
- **Enable Instance** - Enable a specific instance
- **Disable Instance** - Disable a specific instance

## Keyboard Shortcuts

- `Ctrl+Shift+B` - **Build & Upload Plugin** (quick build and upload)
- `Ctrl+Shift+D` - **Deploy Plugin** (full deployment with instance update)
- `Ctrl+Shift+S` - **Check Plugin Status** (quick status check)

## Launch Configurations

Access these through **Run and Debug** view (`Ctrl+Shift+D`):

- **Build & Upload Plugin** - Run deployment script with debugging
- **Deploy Plugin (Interactive)** - Full deployment with instance ID prompt
- **Check Plugin Status** - Check status with debugging
- **List Plugins & Instances** - List all with debugging
- **Run Tests** - Execute pytest with debugging

## Usage Tips

### Quick Build & Upload
1. Press `Ctrl+Shift+B` or run "Build & Upload Plugin" task
2. Check output for success/failure

### First-Time Setup
1. Run "Setup Dependencies" task to install local mbc CLI
2. Run "mbc Login" task to authenticate with maubot server
3. Run "mbc Auth (Bot Account)" task for encryption support
4. Press `Ctrl+Shift+B` to build and upload

### Full Deployment
1. Press `Ctrl+Shift+D` or run "Deploy Plugin" task
2. Enter your instance ID when prompted
3. Plugin will be built, uploaded, and instance updated

### Status Checking
1. Press `Ctrl+Shift+S` or run "Check Plugin Status" task
2. View current plugin and instance status

## Environment Setup

The configuration assumes:
- Python virtual environment at `./.venv/`
- UV package manager (recommended) or pip
- Configured `mbc` (maubot-cli) for uploads
- Maubot helper script authentication

## File Structure

```
.vscode/
├── tasks.json          # Task definitions for build/deploy
├── launch.json         # Debug/run configurations  
├── settings.json       # Python and project settings
├── keybindings.json    # Custom keyboard shortcuts
└── README.md          # This file
```

## Troubleshooting

### "Command not found" errors
- Ensure scripts are executable: `chmod +x deploy.py maubot_helper.py`
- Check that mbc is installed and configured
- Verify virtual environment is activated

### Permission errors
- Check file permissions on scripts
- Ensure maubot server is accessible
- Verify authentication tokens

### Task not appearing
- Reload VS Code window (`Ctrl+Shift+P` > "Developer: Reload Window")
- Check tasks.json syntax with JSON validator
