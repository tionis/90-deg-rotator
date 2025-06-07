# Project Information

**NinetyDegreeRotator** - Matrix Maubot Plugin for automatic image rotation

## Overview
- **Type**: Python maubot plugin  
- **Function**: Rotates images 90° counter-clockwise in Matrix rooms
- **Features**: Encryption support, auto-join, robust error handling

## Architecture
- Main class: `NinetyDegreeRotator` in `NinetyDegreeRotator/__init__.py`
- Event handlers for room invites and image messages
- Image processing: Download → Decrypt → Rotate → Upload → Reply
- Encryption: mautrix built-in with manual fallback

## Development
- **Dependencies**: UV-managed with `requirements-dev.txt`
- **Build+Upload**: `python deploy.py build-upload` → automatic server reload verification
- **Deploy**: `python deploy.py deploy -i <instance>`
- **Config**: `autojoin: true` in instance settings

## File Structure
```
NinetyDegreeRotator/__init__.py  # Main plugin code
maubot.yaml                      # Plugin metadata  
deploy.py                        # Build/deploy script
maubot_helper.py                 # Instance management
requirements-dev.txt             # Dependencies
pyproject.toml                   # Modern Python config
```
## Key Implementation Details

### Encryption Detection
```python
is_encrypted = "file" in content and "url" in content["file"]
```

### Main Event Handler
```python
@event.on(EventType.ROOM_MESSAGE)
async def on_message(self, evt: MaubotMessageEvent) -> None:
    if evt.content.msgtype == MessageType.IMAGE:
        # Download → Decrypt → Rotate → Upload → Reply
```

### Development Commands
```bash
# Setup
./deploy.py setup

# Build & Deploy
./deploy.py build-upload  # Build and upload in one step (recommended)
./deploy.py build         # Build only
./deploy.py upload        # Upload only
./deploy.py deploy -i <instance>

# Management
./maubot_helper.py list-detailed
./status.py
```


### Updating Versions
1. Update `version` in `maubot.yaml`
2. Update `__version__` in `NinetyDegreeRotator/__init__.py`
3. Update documentation if needed
4. Build and test
5. Deploy with `deploy.py`

## 🚀 Deployment Targets

### Development
- **Server**: `conduit-test.fs-info.de`
- **Instance**: `rotatorv2`
- **User**: `@rotator:conduit-test.fs-info.de`

### Production Considerations
- Monitor resource usage (image processing can be intensive)
- Configure appropriate room permissions
- Set up logging and monitoring
- Consider rate limiting for busy rooms

## 📚 Technical Dependencies

### Python Packages (UV Managed)
```txt
# Core maubot framework
maubot>=0.4.0

# Image processing
Pillow>=9.0.0

# Encryption support
cryptography>=3.0.0

# HTTP client (usually provided by maubot)
aiohttp>=3.8.0
```

### System Dependencies
- Python 3.8+
- Matrix server access
- Sufficient memory for image processing
- Write permissions for temporary files

## 🔍 Code Patterns

### Event Handler Pattern
```python
@event.on(EventType.ROOM_MESSAGE)
async def on_message(self, evt: MessageEvent) -> None:
    if evt.content.msgtype != MessageType.IMAGE:
        return
    # Process image...
```

### Error Handling Pattern
```python
try:
    # Operation that might fail
    result = await risky_operation()
except Exception as e:
    self.log.error(f"Operation failed: {e}")
    await evt.reply("Error processing image")
    return
```

### Encryption Detection Pattern
```python
is_encrypted = (
    isinstance(evt.content, ImageMessageEventContent) 
    and hasattr(evt.content, 'file') 
    and evt.content.file is not None
)
```

## 🎛️ Configuration Options

### Plugin-Level (`maubot.yaml`)
- Dependencies
- Module structure
- Main class definition
- Version information

### Instance-Level (maubot web UI)
- `autojoin`: Boolean to enable/disable auto-joining rooms
- Future: rotation angles, image filters, etc.

### Environment-Level
- MBC configuration in `~/.config/maubot-cli.json`
- Python environment and UV setup
- Matrix server credentials

---

**For LLM Context**: This project uses modern Python practices with UV for dependency management, follows maubot plugin conventions, handles Matrix encryption robustly, and includes comprehensive tooling for development and deployment.

## Recent Fixes

### Encrypted File URL Issue (FIXED)
**Problem:** Bot was always returning "Could not find image URL in encrypted file" when processing encrypted images.

**Root Cause:** The code was trying to access the MXC URL from `evt.content.url` for encrypted files, but encrypted files store their URL in the `EncryptedFile` structure at `evt.content.file.url`.

**Solution:** Changed line 55 in `__init__.py` from:
```python
mxc_url = evt.content.url
enc_info: EncryptedFile = evt.content.file
```
to:
```python
enc_info: EncryptedFile = evt.content.file
mxc_url = enc_info.url
```

**Research:** Based on mautrix-python source code analysis, the `EncryptedFile` dataclass (defined in `mautrix/types/event/message.py`) has the following structure:
```python
@dataclass
class EncryptedFile(SerializableAttrs):
    key: JSONWebKey
    iv: str
    hashes: Dict[str, str]
    url: Optional[ContentURI] = None
    version: str = attr.ib(default="v2", metadata={"json": "v"})
```

The URL for encrypted files is stored within the `EncryptedFile` object, not at the top level of the event content.
