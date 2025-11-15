#Github.com/mrinvisible7

import asyncio, time, os
import logging

from pyrogram.enums import ParseMode, MessageMediaType

from .. import Bot, bot
from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot, video_metadata

from pyrogram import Client, filters
from pyrogram.errors import (
    ChannelBanned,
    ChannelInvalid,
    ChannelPrivate,
    ChatIdInvalid,
    ChatInvalid,
    FloodWait,
)

from telethon import events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.INFO)
logging.getLogger("telethon").setLevel(logging.INFO)


def thumbnail(sender):
    return f"{sender}.jpg" if os.path.exists(f"{sender}.jpg") else None


# safe helpers for editing/deleting messages (no exceptions, no spam)
async def safe_edit(client, chat_id, message_id, text, **kwargs):
    """
    Edit a message if message_id is not None. Ignore errors.
    """
    if not message_id:
        return None
    try:
        return await client.edit_message_text(chat_id, message_id, text, **kwargs)
    except Exception as e:
        logger.info(f"safe_edit skipped: {e}")
        return None


async def safe_delete(message_obj):
    """
    Delete a message object if it's not None. Ignore errors.
    Accepts either a message object or None.
    """
    if not message_obj:
        return None
    try:
        # message_obj may be a message or contain id attribute
        if hasattr(message_obj, "delete"):
            await message_obj.delete()
        else:
            # some libraries return different types - try common delete
            await message_obj.delete()
    except Exception as e:
        logger.info(f"safe_delete skipped: {e}")
        return None


async def check(userbot, client, link):
    logging.info(link)
    msg_id = 0
    try:
        msg_id = int(link.split("/")[-1])
    except ValueError:
        if "?single" not in link:
            return False, "**Invalid Link!**"
        link_ = link.split("?single")[0]
        msg_id = int(link_.split("/")[-1])
    if "t.me/c/" in link:
        try:
            chat = int("-100" + str(link.split("/")[-2]))
            await userbot.get_messages(chat, msg_id)
            return True, None
        except ValueError:
            return False, "**Invalid Link!**"
        except Exception as e:
            logging.info(e)
            return False, "Have you joined the channel?"
    else:
        try:
            chat = str(link.split("/")[-2])
            await client.get_messages(chat, msg_id)
            return True, None
        except Exception as e:
            logging.info(e)
            return False, "Maybe bot is banned from the chat, or your link is invalid!"


async def get_msg(userbot, client, sender, edit_id, msg_link, i, file_n):
    """
    Core message fetch/download/upload function.
    edit_id may be None — in that case we skip edit_message_text calls.
    """
    edit = None
    chat = ""
    msg_id = int(i)
    if msg_id == -1:
        # try to notify if edit_id exists
        if edit_id:
            await safe_edit(client, sender, edit_id, "**Invalid Link!**")
        return None

    if "t.me/c/" in msg_link or "t.me/b/" in msg_link:

        if "t.me/b" not in msg_link:
            chat = int("-100" + str(msg_link.split("/")[-2]))
        else:
            chat = int(msg_link.split("/")[-2])
        file = ""
        try:
            msg = await userbot.get_messages(chat_id=chat, message_ids=msg_id)
            logging.info(msg)

            # service message -> remove edit (if any) and skip
            if msg.service is not None:
                await safe_delete(edit)
                return None

            if getattr(msg, "empty", None) is not None:
                await safe_delete(edit)
                return None

            # If web page or plain text -> send content, skip cloning/edit flow
            if msg.media and msg.media == MessageMediaType.WEB_PAGE:
                a = b = True
                # do not create or edit the "Cloning." message; just send content
                if msg.text and getattr(msg.text, "html", ""):
                    if (
                        "--" in msg.text.html
                        or "**" in msg.text.html
                        or "__" in msg.text.html
                        or "~~" in msg.text.html
                        or "||" in msg.text.html
                        or "```" in msg.text.html
                        or "`" in msg.text.html
                    ):
                        await client.send_message(sender, msg.text.html, parse_mode=ParseMode.HTML)
                        a = False
                if msg.text and getattr(msg.text, "markdown", ""):
                    if (
                        "<b>" in msg.text.markdown
                        or "<i>" in msg.text.markdown
                        or "<em>" in msg.text.markdown
                        or "<u>" in msg.text.markdown
                        or "<s>" in msg.text.markdown
                        or "<spoiler>" in msg.text.markdown
                        or "<a href=" in msg.text.markdown
                        or "<pre" in msg.text.markdown
                        or "<code>" in msg.text.markdown
                        or "<emoji" in msg.text.markdown
                    ):
                        await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                        b = False
                if a and b and getattr(msg.text, "markdown", None):
                    await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                await safe_delete(edit)
                return None

            if not msg.media and getattr(msg, "text", None):
                a = b = True
                # do not create an intermediate "Cloning." message — just send content
                if getattr(msg.text, "html", "") and (
                    "--" in msg.text.html
                    or "**" in msg.text.html
                    or "__" in msg.text.html
                    or "~~" in msg.text.html
                    or "||" in msg.text.html
                    or "```" in msg.text.html
                    or "`" in msg.text.html
                ):
                    await client.send_message(sender, msg.text.html, parse_mode=ParseMode.HTML)
                    a = False
                if getattr(msg.text, "markdown", "") and (
                    "<b>" in msg.text.markdown
                    or "<i>" in msg.text.markdown
                    or "<em>" in msg.text.markdown
                    or "<u>" in msg.text.markdown
                    or "<s>" in msg.text.markdown
                    or "<spoiler>" in msg.text.markdown
                    or "<a href=" in msg.text.markdown
                    or "<pre" in msg.text.markdown
                    or "<code>" in msg.text.markdown
                    or "<emoji" in msg.text.markdown
                ):
                    await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                    b = False
                if a and b and getattr(msg.text, "markdown", None):
                    await client.send_message(sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)

                await safe_delete(edit)
                return None

            if msg.media == MessageMediaType.POLL:
                # polls cannot be saved
                if edit_id:
                    await safe_edit(client, sender, edit_id, "poll media cant be saved")
                return

            # If we reach here, we will download media
            # Do not create a "Cloning." message; use safe_edit only if edit_id provided
            if edit_id:
                edit = await safe_edit(client, sender, edit_id, "Trying to Download.")

            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    "**DOWNLOADING:**\n**bot made by Mr. Invisible**",
                    edit,
                    time.time(),
                ),
            )
            path = file
            await safe_delete(edit)

            upm = await client.send_message(sender, "Preparing to Upload!")

            caption = str(file)
            if getattr(msg, "caption", None) is not None:
                caption = msg.caption

            ext = str(file).split(".")[-1].lower()
            if ext in ["mkv", "mp4", "webm", "mpe4", "mpeg"]:
                if ext in ["webm", "mkv", "mpe4", "mpeg"]:
                    path = str(file).split(".")[0] + ".mp4"
                    try:
                        os.rename(file, path)
                        file = path
                    except Exception as e:
                        logger.info(e)
                data = video_metadata(file)
                duration = data.get("duration")
                wi = data.get("width")
                hi = data.get("height")
                logging.info(data)

                if file_n != "":
                    if "." in file_n:
                        path = f"/app/downloads/{file_n}"
                    else:
                        path = f"/app/downloads/{file_n}." + ext
                    os.rename(file, path)
                    file = path
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception as e:
                    logging.info(e)
                    thumb_path = None
                caption = msg.caption if getattr(msg, "caption", None) is not None else os.path.basename(file)
                await client.send_video(
                    chat_id=sender,
                    video=path,
                    caption=caption,
                    supports_streaming=True,
                    duration=duration,
                    height=hi,
                    width=wi,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        "**UPLOADING:**\n**bot made by Mr. Sumit**",
                        upm,
                        time.time(),
                    ),
                )

            elif ext in ["jpg", "jpeg", "png", "webp"]:
                if file_n != "":
                    if "." in file_n:
                        path = f"/app/downloads/{file_n}"
                    else:
                        path = f"/app/downloads/{file_n}." + ext
                    os.rename(file, path)
                    file = path

                caption = msg.caption if getattr(msg, "caption", None) is not None else os.path.basename(file)
                # update the "Preparing..." message text instead of creating new ones
                try:
                    await upm.edit("Uploading photo.")
                except Exception:
                    pass

                await bot.send_file(sender, path, caption=caption)

            else:
                if file_n != "":
                    if "." in file_n:
                        path = f"/app/downloads/{file_n}"
                    else:
                        path = f"/app/downloads/{file_n}." + ext
                    os.rename(file, path)
                    file = path
                thumb_path = thumbnail(sender)
                caption = msg.caption if getattr(msg, "caption", None) is not None else os.path.basename(file)
                await client.send_document(
                    sender,
                    path,
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        "**UPLOADING:**\n**bot made by Mr. Invisible**",
                        upm,
                        time.time(),
                    ),
                )

            try:
                os.remove(file)
            except Exception:
                pass

            try:
                await upm.delete()
            except Exception:
                pass

            return None

        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid) as e:
            logger.info(e)
            if edit_id:
                await safe_edit(client, sender, edit_id, "Bot is not in that channel/ group \n send the invite link so that bot can join the channel ")
            return None
        except Exception as e:
            logger.info(e)
            # ensure any in-progress messages are cleared
            try:
                await safe_delete(edit)
            except Exception:
                pass
            return None
    else:
        # Public chat — do not create 'Cloning.' message; just copy message
        # edit_id may be None; skip edit if not present
        if edit_id:
            await safe_edit(client, sender, edit_id, "Cloning.")
        chat = msg_link.split("/")[-2]
        try:
            await client.copy_message(int(sender), chat, msg_id)
        except Exception as e:
            logger.info(e)
        if edit_id:
            await safe_delete(edit)
        return None


async def get_bulk_msg(userbot, client, sender, msg_link, i):
    """
    Replaces the previous 'Processing!' message with a dummy object
    so we don't spam the chat. We still pass an edit_id (None) so that
    get_msg knows not to attempt edits unless provided.
    """
    class Dummy:
        id = None

    x = Dummy()
    file_name = ""
    await get_msg(userbot, client, sender, x.id, msg_link, i, file_name)
