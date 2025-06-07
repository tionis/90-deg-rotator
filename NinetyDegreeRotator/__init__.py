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
                    # Download the raw encrypted bytes
                    download_url = self.client.api.get_download_url(mxc_url)
                    async with self.http.get(download_url) as resp:
                        encrypted_bytes = await resp.read()

                    # Decrypt using the metadata from the event
                    image_bytes = decrypt_attachment(
                        ciphertext=encrypted_bytes,
                        key=enc_info.key.key,
                        iv=enc_info.iv,
                        hash=enc_info.hashes["sha256"]
                    )
                    self.log.info(f"Successfully decrypted {len(image_bytes)} bytes")

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
