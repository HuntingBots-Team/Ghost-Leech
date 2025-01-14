from asyncio import sleep

from nekozee.filters import command
from nekozee.handlers import MessageHandler

from tghbot import bot
from tghbot.helper.telegram_helper.bot_commands import BotCommands
from tghbot.helper.telegram_helper.filters import CustomFilters
from tghbot.helper.telegram_helper.message_utils import (
    edit_message,
    send_message
)

delete = set()


async def delete_leech(client, message):
    args = message.text.split()
    if len(args) > 1:
        link = args[1]
    elif reply_to := message.reply_to_message:
        link = reply_to.text.strip()
    else:
        link = ""
    if not link.startswith("https://t.me/"):
        msg = "Send telegram message link along with command or by replying to the link by command"
        return await send_message(
            message,
            msg
        )
    msg = f"Okay deleting all replies with {link}"
    link = link.split("/")
    message_id = int(link[-1])
    if message_id in delete:
        msg = "Already deleting in progress"
        return await send_message(
            message,
            msg
        )
    chat_id = link[-2]
    if chat_id.isdigit():
        chat_id = f"-100{chat_id}"
        chat_id = int(chat_id)
    reply_message = await send_message(
        message,
        msg
    )
    await deleting(
        client,
        chat_id,
        message_id,
        reply_message
    )

async def deleting(client, chat_id, message_id, message):
    delete.add(message_id)
    try:
        msg = await client.get_messages(
            chat_id,
            message_id,
            replies = -1
        )
        replies_ids = []
        while msg:
            await sleep(0)
            replies_ids.append(msg.id)
            if msg.media_group_id:
                media_group = await msg.get_media_group()
                media_ids = []
                for media in media_group:
                    media_ids.append(media.id)
                    msg = media.reply_to_message
                    if not msg:
                        msg = await client.get_messages(
                            chat_id,
                            media.reply_to_message_id,
                            replies=-1
                        )
                replies_ids.extend(media_ids)
            else:
                msg = msg.reply_to_message
        replies_ids = list(set(replies_ids))
        total_ids = len(replies_ids)
        replies_ids = [
            replies_ids[i * 100:(i + 1) * 100]
            for i in range((total_ids + 100 - 1) // 100 )
        ]
        deleted = 0
        for each100 in replies_ids:
            deleted += await client.delete_messages(
                chat_id,
                each100
            )
            if len(each100) > 100:
                await sleep(1)
            await edit_message(
                message,
                f"{deleted}/{total_ids} message deleted"
            )
    except Exception as e:
        await edit_message(message, str(e))
    delete.remove(message_id)

bot.add_handler( # type: ignore
    MessageHandler(
        delete_leech,
        filters=command(
            f"leech{BotCommands.DeleteCommand}",
            case_sensitive=True
        ) & CustomFilters.sudo
    )
)
