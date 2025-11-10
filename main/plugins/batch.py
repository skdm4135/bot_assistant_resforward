#Tg:@mister_invisiblebot/save_restricted
#Github. com/mrinvisible7

"""
Plugin for both public & private channels!
...................
"""
import logging
import time, os, asyncio

from .. import bot as Invix
from .. import userbot, Bot, AUTH, SUDO_USERS
from main.plugins.pyroplug import check, get_bulk_msg
from main.plugins.helpers import get_link, screenshot

from telethon import events, Button, errors
from telethon.tl.types import DocumentAttributeVideo

from pyrogram.errors import FloodWait

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("telethon").setLevel(logging.WARNING)

batch = []
ids = []

@Invix.on(events.NewMessage(incoming=True, from_users=SUDO_USERS, pattern='/batch'))
async def _batch(event):

    s = False
    if f'{event.sender_id}' in batch:
        return await event.reply("You've already started one batch, wait for it to complete!")

    async with Invix.conversation(event.chat_id) as conv:
        if not s:
            await conv.send_message(
                "Send me the message link you want to start saving from.",
                buttons=Button.force_reply()
            )
            try:
                link = await conv.get_reply()
                try:
                    _link = get_link(link.text)
                except Exception:
                    await conv.send_message("No link found.")
            except Exception as e:
                logger.info(e)
                return await conv.send_message("Timeout! No reply received.")

            await conv.send_message("Send me how many messages to clone.", buttons=Button.force_reply())
            try:
                _range = await conv.get_reply()
            except Exception as e:
                logger.info(e)
                return await conv.send_message("Timeout! No reply received.")

            try:
                value = int(_range.text)
                if value > 1000000:
                    return await conv.send_message("You can only get upto 100000 files.")
            except ValueError:
                return await conv.send_message("Range must be an integer!")

            for i in range(value):
                ids.append(i)

            s, r = await check(userbot, Bot, _link)
            if s != True:
                await conv.send_message(r)
                return

            batch.append(f'{event.sender_id}')
            cd = await conv.send_message(
                "**Batch process ongoing.**\n\nProcess completed: ",
                buttons=[[Button.inline("CANCEL❌", data="cancel")]]
            )

            co = await run_batch(userbot, Bot, event.sender_id, cd, _link)

            try:
                if co == -2:
                    await Bot.send_message(event.sender_id, "Batch successfully completed!")
                    await cd.edit(
                        f"**Batch process ongoing.**\n\nProcess completed: {value} \n\n✅ Batch successfully completed!"
                    )
            except:
                await Bot.send_message(event.sender_id, "ERROR!\nMaybe last message didn’t exist.")

            conv.cancel()
            ids.clear()
            batch.clear()


@Invix.on(events.callbackquery.CallbackQuery(data="cancel"))
async def cancel(event):
    ids.clear()


# ✅ ✅ ✅ FIXED VERSION WITH 7-SECOND DELAY ✅ ✅ ✅
async def run_batch(userbot, client, sender, countdown, link):

    for i in range(len(ids)):

        # ALWAYS WAIT 7 SECONDS AFTER EACH MESSAGE
        timer = 7

        try:
            count_down = f"**Batch process ongoing.**\n\nProcess completed: {i+1}"

            # Extract starting msg_id from link
            try:
                msg_id = int(link.split("/")[-1])
            except ValueError:
                if '?single' not in link:
                    return await client.send_message(sender, "**Invalid Link!**")
                link_ = link.split("?single")[0]
                msg_id = int(link_.split("/")[-1])

            integer = msg_id + int(ids[i])

            # Process next message
            await get_bulk_msg(userbot, client, sender, link, integer)

            # Timer Message
            protection = await client.send_message(
                sender,
                f"Sleeping for `{timer}` seconds to avoid FloodWait…"
            )

            await countdown.edit(
                count_down,
                buttons=[[Button.inline("CANCEL❌", data="cancel")]]
            )

            # ✅ FINAL FIXED DELAY
            await asyncio.sleep(timer)

            await protection.delete()

        except IndexError as ie:
            await client.send_message(sender, f"{i}  {ie}\n\n✅ Batch Ended!")
            await countdown.delete()
            break

        except FloodWait as fw:
            if int(fw.value) > 300:
                await client.send_message(sender, f'⚠️ FloodWait {fw.value}s — cancelling batch.')
                ids.clear()
                break
            else:
                fw_alert = await client.send_message(
                    sender,
                    f'⚠️ FloodWait: sleeping for {fw.value + 5} seconds…'
                )

                await asyncio.sleep(fw.value + 5)
                await fw_alert.delete()

                try:
                    await get_bulk_msg(userbot, client, sender, link, integer)
                except Exception as e:
                    logger.info(e)
                    if countdown.text != count_down:
                        await countdown.edit(
                            count_down,
                            buttons=[[Button.inline("CANCEL❌", data="cancel")]]
                        )

        except Exception as e:
            logger.info(e)
            await client.send_message(
                sender,
                f"⚠️ Error during cloning. Batch will continue.\n\n**Error:** {str(e)}"
            )

            if countdown.text != count_down:
                await countdown.edit(
                    count_down,
                    buttons=[[Button.inline("CANCEL❌", data="cancel")]]
                )

        n = i + 1
        if n == len(ids):
            return -2
