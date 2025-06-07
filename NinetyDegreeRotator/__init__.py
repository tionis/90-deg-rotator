from io import BytesIO
from typing import Type

from maubot import MessageEvent, Plugin
from maubot.handlers import event
from mautrix.types import EncryptedFile, EventType, ImageInfo, MessageType
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from mautrix.crypto.attachments import decrypt_attachment
from PIL import Image

# Handle different versions of mautrix crypto
try:
    from mautrix.crypto.attachments import EncryptionError
except ImportError:
    # Fallback for older versions that don't export EncryptionError
    class EncryptionError(Exception):
        pass


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("autojoin")


class NinetyDegreeRotator(Plugin):
    PLUGIN_VERSION = "v0.2.0"

    async def start(self) -> None:
        await super().start()
        self.log.info(f"NinetyDegreeRotator plugin {self.PLUGIN_VERSION} started.")

    @event.on(EventType.ROOM_MEMBER)
    async def on_invite(self, evt: MessageEvent) -> None:
        if evt.content.membership == "invite" and evt.state_key == self.client.mxid:
            if self.config["autojoin"]:
                await evt.client.join_room(evt.room_id)

    @event.on(EventType.ROOM_MESSAGE)
    async def on_message(self, evt: MessageEvent) -> None:
        # Only process image messages
        if evt.content.msgtype != MessageType.IMAGE:
            return
        
        # Logging whole event for debugging for now TODO remove this
        print(evt)

        self.log.info(f"Processing image event: {evt.event_id}")

        try:
            image_bytes = None
            filename = evt.content.body or "image"

            # Check if it's an encrypted file
            if hasattr(evt.content, "file") and evt.content.file:
                # Encrypted file
                self.log.info("Detected encrypted file")
                enc_info: EncryptedFile = evt.content.file
                mxc_url = enc_info.url

                if not mxc_url:
                    await evt.respond("Could not find image URL in encrypted file.")
                    return

                try:
                    # Use the client's built-in download method for encrypted files
                    self.log.info(f"Downloading encrypted media from: {mxc_url}")
                    encrypted_bytes = await evt.client.download_media(mxc_url)
                    self.log.info(f"Downloaded {len(encrypted_bytes)} bytes of encrypted data")
                    
                    self.log.info(f"Downloaded {len(encrypted_bytes)} bytes of encrypted data")
                    self.log.info(f"Expected hash (base64): {enc_info.hashes['sha256']}")
                    self.log.info(f"Key length: {len(enc_info.key.key)} chars")
                    self.log.info(f"IV: {enc_info.iv}")
                    
                    # Calculate actual hash of downloaded data for comparison
                    import hashlib
                    import base64
                    actual_hash = hashlib.sha256(encrypted_bytes).digest()
                    actual_hash_b64 = base64.b64encode(actual_hash).decode()
                    
                    self.log.info("Starting hash processing...")
                    
                    # Check if the hash from Matrix is already bytes or base64 string
                    hash_from_matrix = enc_info.hashes["sha256"]
                    self.log.info(f"Hash from matrix: {hash_from_matrix}")
                    self.log.info(f"Hash from matrix type: {type(hash_from_matrix)}")
                    
                    try:
                        if isinstance(hash_from_matrix, str):
                            # It's a base64 string, decode it
                            self.log.info("Attempting to decode hash as base64 string...")
                            hash_str = hash_from_matrix
                            # Add padding if needed
                            missing_padding = len(hash_str) % 4
                            if missing_padding:
                                hash_str += '=' * (4 - missing_padding)
                            self.log.info(f"Hash with padding: '{hash_str}'")
                            expected_hash_bytes = base64.b64decode(hash_str)
                            expected_hash_b64 = hash_from_matrix
                        else:
                            # It's already bytes
                            self.log.info("Hash is already bytes...")
                            expected_hash_bytes = hash_from_matrix
                            expected_hash_b64 = base64.b64encode(hash_from_matrix).decode()
                        self.log.info("Hash processing successful!")
                    except Exception as hash_error:
                        self.log.error(f"Hash decoding failed: {hash_error}")
                        # Try URL-safe base64 for hash too
                        try:
                            expected_hash_bytes = base64.urlsafe_b64decode(hash_from_matrix + '===')
                            expected_hash_b64 = hash_from_matrix
                            self.log.info("Hash decoded with URL-safe base64!")
                        except Exception as hash_error2:
                            self.log.error(f"URL-safe hash decoding also failed: {hash_error2}")
                            raise hash_error
                    
                    self.log.info(f"Actual SHA-256 (b64): {actual_hash_b64}")
                    self.log.info(f"Expected SHA-256 (b64): {expected_hash_b64}")
                    self.log.info(f"Hash match: {actual_hash == expected_hash_bytes}")
                    self.log.info(f"Hash type: {type(hash_from_matrix)}")
                    self.log.info(f"IV type: {type(enc_info.iv)}")
                    self.log.info(f"Key type: {type(enc_info.key.key)}")
                    
                    # Log first few bytes of encrypted data for debugging
                    self.log.info(f"First 32 bytes: {encrypted_bytes[:32].hex()}")
                    
                    self.log.info("Starting decryption parameter processing...")
                    
                    # Handle IV decoding more carefully
                    self.log.info(f"Raw IV value: '{enc_info.iv}'")
                    self.log.info(f"Raw IV repr: {repr(enc_info.iv)}")
                    try:
                        if isinstance(enc_info.iv, str):
                            # Try different padding approaches
                            iv_str = enc_info.iv
                            # Add padding if needed
                            missing_padding = len(iv_str) % 4
                            if missing_padding:
                                iv_str += '=' * (4 - missing_padding)
                            self.log.info(f"IV with padding: '{iv_str}'")
                            iv_bytes = base64.b64decode(iv_str)
                        else:
                            iv_bytes = enc_info.iv
                        self.log.info(f"IV bytes length: {len(iv_bytes)}")
                        self.log.info(f"IV hex: {iv_bytes.hex()}")
                    except Exception as iv_error:
                        self.log.error(f"IV decoding error: {iv_error}")
                        # Try alternative approaches
                        try:
                            # Try URL-safe base64
                            iv_bytes = base64.urlsafe_b64decode(enc_info.iv + '===')
                            self.log.info(f"IV decoded with urlsafe: {iv_bytes.hex()}")
                        except Exception as iv_error2:
                            self.log.error(f"URL-safe IV decoding error: {iv_error2}")
                            # Last resort: treat as already bytes or encode as UTF-8
                            if isinstance(enc_info.iv, bytes):
                                iv_bytes = enc_info.iv
                            else:
                                iv_bytes = enc_info.iv.encode('utf-8')[:16]  # AES block size
                            self.log.info(f"Fallback IV bytes: {iv_bytes.hex()}")
                    
                    # Handle key decoding with similar approach
                    self.log.info(f"Raw key value: '{enc_info.key.key}'")
                    try:
                        if isinstance(enc_info.key.key, str):
                            key_str = enc_info.key.key
                            # Add padding if needed
                            missing_padding = len(key_str) % 4
                            if missing_padding:
                                key_str += '=' * (4 - missing_padding)
                            key_bytes = base64.b64decode(key_str)
                        else:
                            key_bytes = enc_info.key.key
                        self.log.info(f"Key bytes length: {len(key_bytes)}")
                    except Exception as key_error:
                        self.log.error(f"Key decoding error: {key_error}")
                        # Try URL-safe base64 for key too
                        try:
                            if isinstance(enc_info.key.key, str):
                                key_bytes = base64.urlsafe_b64decode(enc_info.key.key + '===')
                            else:
                                key_bytes = enc_info.key.key
                        except Exception as key_urlsafe_error:
                            self.log.error(f"URL-safe key decoding also failed: {key_urlsafe_error}")
                            # Final fallback - if it's a string, encode it, otherwise use as-is
                            if isinstance(enc_info.key.key, str):
                                key_bytes = enc_info.key.key.encode('utf-8')
                            else:
                                key_bytes = enc_info.key.key
                    
                    self.log.info("About to call decrypt_attachment with:")
                    self.log.info(f"  - ciphertext length: {len(encrypted_bytes)}")
                    self.log.info(f"  - key length: {len(key_bytes)}")
                    self.log.info(f"  - hash length: {len(expected_hash_bytes)}")
                    self.log.info(f"  - iv length: {len(iv_bytes)}")
                    
                    # Decrypt using the metadata from the event
                    try:
                        image_bytes = decrypt_attachment(
                            ciphertext=encrypted_bytes,
                            key=key_bytes,
                            hash=expected_hash_bytes,
                            iv=iv_bytes
                        )
                        self.log.info(f"Successfully decrypted {len(image_bytes)} bytes")
                    except Exception as decrypt_error:
                        self.log.error(f"decrypt_attachment failed: {decrypt_error}")
                        self.log.error(f"Error type: {type(decrypt_error)}")
                        raise decrypt_error

                except EncryptionError as e:
                    self.log.error(f"Decryption failed for {filename}: {e}")
                    await evt.respond(f"Could not decrypt the encrypted image: {str(e)}")
                    return
                except Exception as e:
                    self.log.error(f"Unexpected error during decryption: {e}")
                    await evt.respond(f"Unexpected error while decrypting image: {str(e)}")
                    return

            elif evt.content.url:
                # Unencrypted file
                self.log.info("Detected unencrypted file")
                mxc_url = evt.content.url
                image_bytes = await evt.client.download_media(mxc_url)

            else:
                await evt.respond("Could not find image URL.")
                return

            if not image_bytes:
                await evt.respond("Failed to download image data.")
                return

            # Process the image
            self.log.info(f"Processing image with {len(image_bytes)} bytes")
            img = Image.open(BytesIO(image_bytes))
            rotated_img = img.rotate(-90, expand=True)  # Rotate 90 degrees counter-clockwise

            # Convert back to bytes
            output_buffer = BytesIO()
            img_format = img.format or "PNG"
            rotated_img.save(output_buffer, format=img_format)
            output_buffer.seek(0)

            # Upload the rotated image
            rotated_image_mxc = await evt.client.upload_media(
                output_buffer,
                mime_type=f"image/{img_format.lower()}",
                filename=f"rotated_{filename}",
            )

            # Send the rotated image
            await evt.respond(
                content={
                    "msgtype": MessageType.IMAGE,
                    "body": f"rotated_{filename}",
                    "url": rotated_image_mxc,
                    "info": ImageInfo(
                        mimetype=f"image/{img_format.lower()}",
                        width=rotated_img.width,
                        height=rotated_img.height,
                        size=len(output_buffer.getvalue()),
                    ),
                }
            )

            self.log.info(f"Successfully rotated and sent image: {evt.event_id}")

        except Exception as e:
            self.log.error(f"Error processing image: {e}", exc_info=True)
            await evt.respond(f"Sorry, I couldn't process that image: {str(e)}")

    async def stop(self) -> None:
        pass

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config
