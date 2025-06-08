# NinetyDegreeRotator Maubot Plugin

A maubot plugin that rotates images 90 degrees counter-clockwise when commanded in Matrix rooms. Responds to `!rotate` or `!r` commands sent as replies to image messages.

## Features

- 🔄 Rotates images 90 degrees counter-clockwise 
- 💬 Command: `!rotate` or `!r` as reply to images
- 🔐 Supports encrypted and unencrypted images
- 🤖 Auto-joins rooms when invited

## Quick Start

```bash
# Setup and authenticate
./maubot-dev.py setup
.venv/bin/python -m maubot.cli login --server "https://conduit-test.fs-info.de"

# Build and deploy
./maubot-dev.py build-upload
```

**Usage:** Reply to any image with `!rotate` or `!r`

## Configuration

Configure your bot instance through the maubot web interface. The plugin supports comprehensive configuration options including:

- Custom rotation commands and angles
- Image processing limits and supported formats  
- Customizable response messages
- Auto-join room behavior

For all available configuration options and their default values, see [`base-config.yaml`](base-config.yaml).

## Management

```bash
# Status and health check
./maubot-dev.py status

# Instance management
./maubot-api.py status
./maubot-api.py list
./maubot-api.py instances
./maubot-api.py enable <instance-id>
./maubot-api.py disable <instance-id>
```

## Troubleshooting

- **Plugin not responding:** Check `./maubot-api.py instances` and bot permissions
- **Encryption issues:** Test with unencrypted images first, check logs
- **Auto-join not working:** Verify `autojoin: true` in configuration
- **Build failures:** Run `./maubot-dev.py status` to check setup

## License
AGPL-3.0