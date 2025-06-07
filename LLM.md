# NinetyDegreeRotator - Matrix Bot Plugin

**Type**: Python maubot plugin that rotates images 90° counter-clockwise when commanded

## Current Functionality
- **Command-based**: Only responds to `/rotate` or `/r` commands sent as replies to image messages
- **Encryption support**: Handles both encrypted and unencrypted Matrix images
- **Auto-join**: Automatically joins rooms when invited (configurable)

## Key Files
- `NinetyDegreeRotator/__init__.py` - Main plugin code
- `maubot.yaml` - Plugin metadata
- `maubot-dev.py` - Build/deploy automation
- `maubot-api.py` - Instance management

## Development Commands
```bash
# Build and upload in one step
./maubot-dev.py build-upload

# Full deployment with instance update
./maubot-dev.py deploy -i <instance-id>

# Instance management
./maubot-api.py status
./maubot-api.py update <instance-id> dev.tionis.maubot.NinetyDegreeRotator
```

## Architecture
- Event handler for text messages looking for `/rotate` or `/r` commands
- Validates command is a reply to an image message
- Downloads → Decrypts (if needed) → Rotates → Uploads → Responds
- Uses mautrix built-in decryption with manual fallback

## Implementation Notes
- Prevents self-processing: `if evt.sender == self.client.mxid: return`
- Command detection: `body.startswith('/rotate') or body.startswith('/r')`
- Reply validation: Checks `evt.content.relates_to.in_reply_to.event_id`
- Encryption detection: `isinstance(evt.content, EncryptedMessageEventContent)`
- Image rotation: Pillow with 90° counter-clockwise transform

## Configuration
```yaml
# Instance configuration
autojoin: true  # Auto-join rooms when invited
```

## Dependencies (UV managed)
- maubot>=0.4.0
- Pillow>=9.0.0 
- cryptography>=3.0.0
