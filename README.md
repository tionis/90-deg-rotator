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
