from telegram import Update
from telegram.ext import ContextTypes

from messages import JOINED_MSG, ALREADY_IN
from storage import storage


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Registers a user if not already present in the database and displays a corresponding message. Displays an ALREADY_IN message otherwise. """
    chat_id = update.message.chat.id
    username = update.effective_user.username or ''
    user_id = int(update.effective_user.id)
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name

    name = (first_name + ' ' + last_name) if last_name else first_name

    if not await storage.check_user_registered(chat_id=chat_id, user_id=user_id):
        join_text = JOINED_MSG.format(name=name)
        await storage.add_user(chat_id, user_id, username, name)
        await context.bot.send_message(chat_id=chat_id, text=join_text)
    else:
        await storage.update_user_row(target_user_id=user_id, new_username=username, new_name=name)
        await context.bot.send_message(chat_id=chat_id, text=ALREADY_IN)