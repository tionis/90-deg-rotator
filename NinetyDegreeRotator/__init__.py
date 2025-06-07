from io import BytesIO
from typing import Type

from maubot import MessageEvent, Plugin
from maubot.handlers import event
from mautrix.types import EncryptedFile, EventType, ImageInfo, MessageType, RoomID
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from PIL import Image

# Try to import cryptography and decryption functions
try:
    from mautrix.crypto.attachments import EncryptionError, decrypt_attachment

    CRYPTO_AVAILABLE = True
    DECRYPT_METHOD = "mautrix"
except ImportError:
    try:
        # Fallback to manual decryption if mautrix crypto isn't available
        import base64
        import hashlib

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        CRYPTO_AVAILABLE = True
        DECRYPT_METHOD = "manual"
    except ImportError:
        CRYPTO_AVAILABLE = False
        DECRYPT_METHOD = "none"


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("autojoin")


class NinetyDegreeRotator(Plugin):
    PLUGIN_VERSION = "v0.2.0"  # Updated version identifier

    async def start(self) -> None:
        await super().start()
        self.log.info(f"NinetyDegreeRotator plugin {self.PLUGIN_VERSION} started.")
        self.log.info(f"Cryptography available: {CRYPTO_AVAILABLE}, method: {DECRYPT_METHOD}")

    @event.on(EventType.ROOM_MEMBER)
    async def on_invite(self, evt: MessageEvent) -> None:
        if evt.content.membership == "invite" and evt.state_key == self.client.mxid:
            if self.config["autojoin"]:
                await evt.client.join_room(evt.room_id)

    @event.on(EventType.ROOM_MESSAGE)
    async def on_message(self, evt: MessageEvent) -> None:
        # Log basic message details
        self.log.info(
            f"on_message ({self.PLUGIN_VERSION}) received event: {evt.event_id}, type: {evt.type}, msgtype: {evt.content.msgtype}"
        )

        # Only process image messages
        if evt.content.msgtype != MessageType.IMAGE:
            return

        self.log.info(f"Processing image event: {evt.event_id}")

        try:
            # Handle both encrypted and unencrypted images
            image_bytes = None
            filename = evt.content.body or "image"

            if hasattr(evt.content, "file") and evt.content.file:
                # This is an encrypted file
                self.log.info("Detected encrypted file")
                self.log.info(
                    f"Cryptography available: {CRYPTO_AVAILABLE}, method: {DECRYPT_METHOD}"
                )
                mxc_url = evt.content.file.url

                if not mxc_url:
                    await evt.respond("Could not find image URL in encrypted file.")
                    return

                if not CRYPTO_AVAILABLE:
                    self.log.info("Sending cryptography unavailable message")
                    await evt.respond(
                        "Sorry, cryptography module is not available on this server. Cannot decrypt encrypted images."
                    )
                    return

                # Download encrypted data
                encrypted_bytes = await evt.client.download_media(mxc_url)

                # Try different decryption methods
                try:
                    if DECRYPT_METHOD == "mautrix":
                        # Use mautrix built-in decryption
                        image_bytes = decrypt_attachment(encrypted_bytes, evt.content.file)
                        self.log.info(
                            "Successfully decrypted image using mautrix.crypto.attachments.decrypt_attachment"
                        )
                    elif DECRYPT_METHOD == "manual":
                        # Use manual decryption
                        file_info = evt.content.file
                        if hasattr(file_info, "key") and hasattr(file_info, "iv"):
                            # Extract decryption parameters from JWK format
                            key_jwk = file_info.key
                            if hasattr(key_jwk, "k"):
                                # Add padding if needed for base64 decoding
                                key_b64 = key_jwk.k
                                key_b64 += "=" * (4 - len(key_b64) % 4) if len(key_b64) % 4 else ""
                                key_data = base64.b64decode(key_b64)
                            else:
                                raise ValueError("Missing key data in JWK")

                            # Decode IV
                            iv_b64 = file_info.iv
                            iv_b64 += "=" * (4 - len(iv_b64) % 4) if len(iv_b64) % 4 else ""
                            iv_data = base64.b64decode(iv_b64)

                            self.log.info(f"Key length: {len(key_data)}, IV length: {len(iv_data)}")

                            # Decrypt using AES-CTR
                            cipher = Cipher(
                                algorithms.AES(key_data),
                                modes.CTR(iv_data),
                                backend=default_backend(),
                            )
                            decryptor = cipher.decryptor()
                            image_bytes = decryptor.update(encrypted_bytes) + decryptor.finalize()

                            # Verify hash if available
                            if hasattr(file_info, "hashes") and hasattr(file_info.hashes, "sha256"):
                                expected_hash = base64.b64decode(
                                    file_info.hashes.sha256
                                    + "=" * (4 - len(file_info.hashes.sha256) % 4)
                                    if len(file_info.hashes.sha256) % 4
                                    else file_info.hashes.sha256
                                )
                                actual_hash = hashlib.sha256(image_bytes).digest()
                                if expected_hash != actual_hash:
                                    self.log.warning("Hash verification failed for decrypted file")
                                else:
                                    self.log.info("Hash verification successful")

                            self.log.info("Successfully decrypted image using manual decryption")
                        else:
                            raise ValueError("Missing encryption parameters for encrypted file")
                    else:
                        raise ValueError("No decryption method available")

                except (
                    EncryptionError if DECRYPT_METHOD == "mautrix" else Exception
                ) as decrypt_error:
                    self.log.error(f"Failed to decrypt image: {decrypt_error}")
                    await evt.respond(
                        f"Could not decrypt the encrypted image: {str(decrypt_error)}"
                    )
                    return
                except Exception as decrypt_error:
                    self.log.error(
                        f"Unexpected error during decryption: {decrypt_error}", exc_info=True
                    )
                    await evt.respond(
                        f"Unexpected error while decrypting image: {str(decrypt_error)}"
                    )
                    return

            elif evt.content.url:
                # This is an unencrypted file
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
