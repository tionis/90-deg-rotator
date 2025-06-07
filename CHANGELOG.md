# Changelog

## [Unreleased]

### Encrypted File URL Fix - 2025-06-07
- **FIXED:** Bot returning "Could not find image URL in encrypted file" for all encrypted images
- **Issue:** Code was accessing `evt.content.url` instead of `evt.content.file.url` for encrypted files
- **Solution:** Updated encrypted file URL handling to properly access the URL from the EncryptedFile structure
- **Research:** Based on mautrix-python source code analysis of EncryptedFile dataclass structure
- Plugin deployed and ready for testing with encrypted images

### Build System Improvements - 2025-06-07
- Added combined `build-upload` command for one-step deployment
- Implemented server reload verification after plugin upload
- Enhanced deployment workflow with automatic plugin organizing
- Updated documentation to reflect new build commands

### Repository Cleanup - 2025-06-07
- Removed shell-specific scripts (fish helpers) for shell-agnostic approach
- Consolidated documentation into main README
- Removed redundant files (QUICKSTART.md, docs/, pre-commit configs)
- Moved test files to proper tests/ directory
- Simplified project structure and reduced complexity

## [0.2.0] - 2025-06-07

### V11 - Current Version
- Renamed to `NinetyDegreeRotator` with semantic versioning
- Modern Python development with UV support
- Enhanced deployment scripts with setup command
- Comprehensive project documentation for LLMs

## [0.1.0] - 2025-06-07

### V10 - Previous Version  
- Robust encryption support with fallback methods
- Auto-detection of decryption capabilities
- Improved error handling and logging

---

## Development History

### V9 (v20250607_H) - 2025-06-07

#### Added
- Initial implementation of `mautrix.crypto.attachments.decrypt_attachment`
- Cleaner approach to encrypted image handling

#### Issues
- Import failures on servers without mautrix.crypto module
- Led to development of V10 with fallback methods

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV9`
- Code Version: `v20250607_H`

### V8 (v20250607_G) - 2025-06-07

#### Added
- Cryptography dependency to maubot.yaml
- Enhanced URL detection for encrypted files
- Graceful cryptography import handling

#### Changed
- Improved encrypted file detection logic
- Added `CRYPTO_AVAILABLE` flag for runtime checks

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV8`
- Code Version: `v20250607_G`

### V7 (v20250607_F) - 2025-06-07

#### Fixed
- Ghost handler issues through server restart
- Duplicate event processing problems

#### Changed
- Clean single-handler operation confirmed

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV7`
- Code Version: `v20250607_F`

### V6 (v20250607_E) - 2025-06-07

#### Added
- Comprehensive error handling and logging
- Version tracking in log messages

#### Fixed
- Various runtime issues and edge cases

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV6`
- Code Version: `v20250607_E`

### V5 (v20250607_D) - 2025-06-07

#### Added
- Enhanced URL detection for encrypted files
- Support for `evt.content.file.url` vs `evt.content.url`

#### Fixed
- Encrypted file URL resolution issues

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV5`
- Code Version: `v20250607_D`

### V4 (v20250607_C) - 2025-06-07

#### Fixed
- EventType.ROOM_INVITE error resolution
- Changed to EventType.ROOM_MEMBER with membership="invite" check

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV4`
- Code Version: `v20250607_C`

### V3 (v20250607_B) - 2025-06-07

#### Added
- Auto-join functionality for room invitations
- EventType.ROOM_MEMBER event handling

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV3`
- Code Version: `v20250607_B`

### V2 (v20250607_A) - 2025-06-07

#### Added
- Basic image rotation functionality
- PIL image processing capabilities
- Support for unencrypted images

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90degrotatorV2`
- Code Version: `v20250607_A`

### V1 - 2025-06-07

#### Added
- Initial plugin structure
- Basic maubot plugin framework setup
- Initial configuration setup

#### Technical Details
- Plugin ID: `dev.tionis.maubot.90-deg-rotator`
- Basic functionality implementation

---

## Technical Evolution

### Plugin ID Changes
- V1: `dev.tionis.maubot.90-deg-rotator`
- V2-V10: `dev.tionis.maubot.90degrotatorVX`

### Major Milestones
1. **V1-V3**: Basic functionality and auto-join
2. **V4-V6**: Error handling and encrypted image support
3. **V7**: Ghost handler resolution
4. **V8**: Cryptography dependency management
5. **V9-V10**: Robust decryption implementation

### Encryption Implementation Evolution
1. **V1-V7**: Manual Matrix AES-CTR decryption
2. **V8**: Added cryptography dependency
3. **V9**: Attempted mautrix built-in decryption
4. **V10**: Hybrid approach with fallback methods

---

## Development Tools Evolution

### Management Scripts
- **maubot-api.py**: Added in V8 development
  - Functions: list, delete, disable, update instances
  - API integration for maubot management
  - Streamlined development workflow

### Build Process
- **V1-V7**: Manual mbc commands
- **V8+**: Structured build and upload process
- **V10**: Organized archive and builds directories

---

## Future Roadmap

### Possible Improvements
- [ ] Unit tests implementation
- [ ] Configuration validation
- [ ] Better error recovery

---

**Maintained by**: tionis  
**Project Start**: June 7, 2025  
**Current Version**: V10 (0.1.0)
