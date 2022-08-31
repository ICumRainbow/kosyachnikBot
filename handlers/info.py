from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from messages import DEFAULT_START_MSG
from storage import storage


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Provides info on bot commands if there is a file with info text. Displays default text otherwise. """
    text = storage.retrieve_info_message() if storage.check_info_msg_exists() else DEFAULT_START_MSG
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)
