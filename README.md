# NinetyDegreeRotator Maubot Plugin

A maubot plugin that automatically rotates images 90 degrees counter-clockwise when sent to Matrix rooms. Supports both encrypted and unencrypted images with auto-join functionality.

## Features

- Rotates all sent images 90 degrees counter-clockwise
- Handles encrypted and unencrypted Matrix images
- Auto-joins rooms when invited (configurable)
- Comprehensive error handling and logging

## Quick Start

### Prerequisites
- Running maubot server with `mbc` CLI configured
- Python 3.8+ with UV or pip

### Installation

```bash
# Setup environment
python deploy.py setup

# Build and deploy
python deploy.py build
python deploy.py deploy -i your-instance-id

# Setup project
git clone <repository-url>
cd 90-deg-rotator
python3 deploy.py setup  # Sets up UV environment and dependencies
```

For detailed UV setup instructions, see [docs/UV_SETUP.md](docs/UV_SETUP.md).

### Dependencies

The plugin requires the following Python packages (managed by UV):
- `maubot` - Matrix bot framework
- `Pillow` - Image processing library
- `cryptography` - For encrypted image decryption
- `aiohttp` - Async HTTP client

Development dependencies include linting, testing, and type-checking tools.

### Build and Deploy

1. **Setup development environment**:
   ```bash
   git clone <repository-url>
   cd 90-deg-rotator
   python3 deploy.py setup  # Sets up UV and dependencies
   ```

2. **Build the plugin**:
   ```bash
   mbc build
   # or use the deploy script
   python3 deploy.py build
   ```

3. **Upload to maubot server**:
   ```bash
   mbc upload builds/dev.tionis.maubot.NinetyDegreeRotator-v0.2.0.mbp
   # or use the deploy script
   python3 deploy.py upload
   ```

4. **Create and configure an instance**:
   - Access your maubot web interface
   - Create a new instance using the uploaded plugin
   - Configure auto-join settings if desired

### Quick Deploy with Helper Script

Use the included management helper for easier deployment:

```bash
# Complete setup (UV + dependencies)
python3 deploy.py setup

# Update existing instance to latest version
python3 maubot_helper.py update-plugin <instance_id> dev.tionis.maubot.NinetyDegreeRotator

# Full deployment (build + upload + update)
python3 deploy.py deploy -i <instance_id>

# List all instances
python3 maubot_helper.py list-detailed

# Disable an instance
python3 maubot_helper.py disable <instance_id>
```

## ⚙️ Configuration

The plugin supports the following configuration options in your maubot instance:

```yaml
# Whether to automatically join rooms when invited
autojoin: true
```

## Configuration

Edit your maubot instance configuration:

```yaml
autojoin: true  # Auto-join rooms when invited
```

## Management Commands

```bash
# List instances
python maubot_helper.py list-detailed

# Update instance
python maubot_helper.py update-plugin <instance-id> <plugin-id>

# Check status
python status.py
```

## Development

```bash
# Format code
python -m black . && python -m isort .

# Build
python deploy.py build

# Deploy
python deploy.py deploy -i <instance-id>
```

## License

MIT License - see [LICENSE](LICENSE) file.
