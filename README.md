# NinetyDegreeRotator Maubot Plugin

A maubot plugin that rotates images 90 degrees counter-clockwise when commanded in Matrix rooms. Responds to `/rotate` or `/r` commands sent as replies to image messages. Supports both encrypted and unencrypted images with auto-join functionality.
This is mainly meant as a template and experiment.  

## Features

- 🔄 Rotates images 90 degrees counter-clockwise when commanded
- 💬 Command-based: responds to `/rotate` or `/r` replies to images
- 🔐 Handles encrypted and unencrypted Matrix images
- 🤖 Auto-joins rooms when invited (configurable)
- 📝 Comprehensive error handling and logging

## Quick Start

### Prerequisites
- Running maubot server with `mbc` CLI configured
- Python 3.8+ with uv (recommended) or pip
- For maubot_helper.py: uv will automatically install `requests` dependency

### 🚀 Quick Deploy

```bash
# 1. Build and deploy in one command
./deploy.py deploy -i your-instance-id

# 2. Or step by step:
./deploy.py build-upload  # Build and upload in one step (recommended)
# OR separate steps:
./deploy.py build         # Build plugin only
./deploy.py upload        # Upload to server only
./maubot_helper.py update your-instance-id dev.tionis.maubot.NinetyDegreeRotator
```

### ✅ Verify Installation

1. Check instance is running: `./maubot_helper.py status`
2. Send an image to a room with the bot
3. Reply to that image with `/rotate` or `/r`
4. Verify rotated image is returned
5. Check logs for any errors

## Configuration

Edit your maubot instance configuration in the maubot web interface:

```yaml
# Example configuration for 90 Degree Rotator Plugin
# Whether to automatically join rooms when the bot is invited
# Default: true
autojoin: true

# Note: Additional configuration options may be added in future versions
# such as:
# - rotation_angle: 90  # degrees to rotate (90, 180, 270)
# - max_file_size: 10485760  # maximum file size to process (10MB)
# - allowed_formats: ["jpg", "jpeg", "png", "gif"]  # supported formats
```

## Management Commands

The `maubot_helper.py` script now uses uv for dependency management and can be run directly:

```bash
# Quick status overview
./maubot_helper.py status

# List all plugins and instances
./maubot_helper.py list

# Detailed instance information
./maubot_helper.py instances

# Show instance configuration
./maubot_helper.py config <instance-id>

# Instance management
./maubot_helper.py enable <instance-id>
./maubot_helper.py disable <instance-id>
./maubot_helper.py delete <instance-id>

# Update instance plugin type
./maubot_helper.py update <instance-id> <new-plugin-id>

# JSON output for any command
./maubot_helper.py list --json

# Check deployment status
./status.py
```

**Note:** The script can also be run with `python maubot_helper.py` if uv is not available.

## 🐛 Troubleshooting

### Plugin not responding
- Check instance is enabled and started: `./maubot_helper.py instances`
- Verify bot has proper room permissions
- Check maubot server logs

### Encryption issues
- Check logs for decryption method used
- Verify cryptography dependencies installed
- Test with unencrypted images first

### Auto-join not working
- Verify `autojoin: true` in configuration
- Check bot has permission to join rooms
- Monitor logs for invitation events

### Build Failures
```bash
# Check mbc configuration
mbc auth

# Verify maubot.yaml syntax
cat maubot.yaml

# Check for Python syntax errors
python3 -m py_compile NinetyDegreeRotator/__init__.py
```

## Development

### Architecture

The plugin implements a three-tier encryption approach:
1. **Primary**: `mautrix.crypto.attachments.decrypt_attachment`
2. **Fallback**: Manual AES-CTR decryption  
3. **Graceful**: Error messaging when unavailable

### Plugin Class Structure

```python
class NinetyDegreeRotator(Plugin):
    PLUGIN_VERSION = "v20250607_I"  # Version tracking
    
    async def start(self) -> None:
        # Plugin initialization
        
    @event.on(EventType.ROOM_MEMBER)
    async def on_invite(self, evt: MessageEvent) -> None:
        # Handle room invitations for auto-join
        
    @event.on(EventType.ROOM_MESSAGE) 
    async def on_message(self, evt: MessageEvent) -> None:
        # Process image messages and perform rotation
```

### Code Standards

#### Naming Conventions
- Plugin versions: `v20250607_X` (date + letter)
- Plugin IDs: `dev.tionis.maubot.90degrotatorVX`
- Class names: PascalCase
- Method names: snake_case
- Constants: UPPER_SNAKE_CASE

#### Logging Standards
```python
# Use descriptive log messages
self.log.info(f"Processing image event: {evt.event_id}")
self.log.error(f"Failed to decrypt image: {error}", exc_info=True)

# Include version in key operations
self.log.info(f"on_message ({self.PLUGIN_VERSION}) received event...")
```

#### Error Handling
```python
try:
    # Operation
    result = await some_operation()
except SpecificError as e:
    self.log.error(f"Specific error: {e}")
    await evt.respond(f"User-friendly error message")
    return
except Exception as e:
    self.log.error(f"Unexpected error: {e}", exc_info=True)
    await evt.respond("Generic error message")
    return
```

### Building & Testing

```bash
# Format code
python3 -m black . && python3 -m isort .

# Build and upload in one step (recommended)
./deploy.py build-upload

# OR separate steps:
./deploy.py build     # Build plugin only
./deploy.py upload    # Upload plugin only

# Update instance
./maubot_helper.py update <instance-id> dev.tionis.maubot.NinetyDegreeRotator

# Full deploy with helper script
./deploy.py deploy -i <instance-id>

# Check deployment status
./status.py
```

### Manual Testing Checklist
- [ ] Unencrypted image rotation
- [ ] Encrypted image rotation (E2EE room)
- [ ] Auto-join functionality
- [ ] Error handling (invalid images, network issues)
- [ ] Plugin startup/shutdown
- [ ] Configuration changes

### Version Management

#### Plugin ID Evolution
Each major change gets a new plugin ID to avoid conflicts:
- V1-V7: Development iterations
- V8: Added cryptography dependency
- V9: Implemented mautrix decryption 
- V10: Added fallback decryption

#### Version Numbering
- Plugin version: Incremented for each change (V1, V2, V3...)
- Code version: Date-based with letter suffix (v20250607_A, v20250607_B...)
- Semantic version: Standard semver in maubot.yaml (0.1.0, 0.2.0...)

### Encryption Details

Matrix uses:
- **Olm**: 1:1 encryption protocol
- **Megolm**: Group encryption protocol
- **JWK**: JSON Web Key format for encryption keys
- **AES-CTR**: Symmetric encryption algorithm

### Important Event Types
- `m.room.message`: Regular messages (including images)
- `m.room.member`: Membership changes (invites, joins, leaves)
- `m.room.encrypted`: Encrypted message content

## License

MIT License - see [LICENSE](LICENSE) file.
