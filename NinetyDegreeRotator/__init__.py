from io import BytesIO
from typing import Type

from maubot import MessageEvent, Plugin
from maubot.handlers import event
from mautrix.types import EncryptedFile, EventType, MessageType, RelatesTo
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from mautrix.crypto.attachments import decrypt_attachment
from mautrix.errors import DecryptionError
from PIL import Image


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("autojoin")


class NinetyDegreeRotator(Plugin):
    """
    A Matrix bot that rotates images by 90 degrees when commanded.
    Usage: Reply to an image with !rotate or !r to rotate it.
    """

    async def start(self) -> None:
        await super().start()
        self.log.info("NinetyDegreeRotator plugin started.")

    @event.on(EventType.ROOM_MEMBER)
    async def on_invite(self, evt: MessageEvent) -> None:
        if evt.content.membership == "invite" and evt.state_key == self.client.mxid:
            if self.config["autojoin"]:
                await evt.client.join_room(evt.room_id)

    @event.on(EventType.ROOM_MESSAGE)
    async def on_message(self, evt: MessageEvent) -> None:
        # Ignore messages from the bot itself to prevent loops
        if evt.sender == self.client.mxid:
            return
            
        # Only process text messages that contain rotate commands
        if evt.content.msgtype != MessageType.TEXT:
            return
            
        # Check if the message is a rotate command
        body = (evt.content.body or "").strip().lower()
        if not (body.startswith('!rotate') or body.startswith('!r')):
            return

        self.log.info(f"Processing rotate command: {evt.event_id}")
        
        # Ensure this is a reply to another message
        if not hasattr(evt.content, 'relates_to') or not evt.content.relates_to or not hasattr(evt.content.relates_to, 'in_reply_to'):
            await evt.respond("Please reply to an image message with !rotate or !r to rotate it.")
            return
            
        # Get the message being replied to
        reply_to_id = evt.content.relates_to.in_reply_to.event_id
        try:
            replied_msg = await evt.client.get_event(evt.room_id, reply_to_id)
        except Exception as e:
            self.log.error(f"Failed to get replied message: {e}")
            await evt.respond("Could not find the message you're replying to.")
            return
            
        # Ensure the replied message is an image
        if replied_msg.content.msgtype != MessageType.IMAGE:
            await evt.respond("Please reply to an image message to rotate it.")
            return

        try:
            image_bytes = None
            filename = replied_msg.content.body or "image"

            # Check if it's an encrypted file
            if hasattr(replied_msg.content, "file") and replied_msg.content.file:
                # Encrypted file
                enc_info: EncryptedFile = replied_msg.content.file
                mxc_url = enc_info.url

                if not mxc_url:
                    await evt.respond("Could not find image URL in encrypted file.")
                    return

                try:
                    # Download and decrypt the encrypted file
                    encrypted_bytes = await evt.client.download_media(mxc_url)
                    
                    # Decrypt using the metadata from the event
                    image_bytes = decrypt_attachment(
                        ciphertext=encrypted_bytes,
                        key=enc_info.key.key,
                        hash=enc_info.hashes["sha256"],
                        iv=enc_info.iv
                    )

                except DecryptionError as e:
                    self.log.error(f"Decryption failed for {filename}: {e}")
                    await evt.respond(f"Could not decrypt the encrypted image: {str(e)}")
                    return
                except Exception as e:
                    self.log.error(f"Unexpected error during decryption: {e}")
                    await evt.respond(f"Unexpected error while decrypting image: {str(e)}")
                    return

            elif replied_msg.content.url:
                # Unencrypted file
                mxc_url = replied_msg.content.url
                image_bytes = await evt.client.download_media(mxc_url)

            else:
                await evt.respond("Could not find image URL.")
                return

            if not image_bytes:
                await evt.respond("Failed to download image data.")
                return

            # Process the image
            img = Image.open(BytesIO(image_bytes))
            rotated_img = img.rotate(-90, expand=True)  # Rotate 90 degrees counter-clockwise

            # Convert back to bytes
            output_buffer = BytesIO()
            img_format = img.format or "PNG"
            rotated_img.save(output_buffer, format=img_format)
            output_buffer.seek(0)
            
            # Get the size before uploading (which may close the buffer)
            rotated_image_size = len(output_buffer.getvalue())
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
                    "msgtype": MessageType.IMAGE.value,
                    "body": f"rotated_{filename}",
                    "url": rotated_image_mxc,
                    "info": {
                        "mimetype": f"image/{img_format.lower()}",
                        "w": rotated_img.width,
                        "h": rotated_img.height,
                        "size": rotated_image_size,
                    },
                }
            )

        except Exception as e:
            self.log.error(f"Error processing image: {e}", exc_info=True)
            await evt.respond(f"Sorry, I couldn't process that image: {str(e)}")

    async def stop(self) -> None:
        pass