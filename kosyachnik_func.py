from random import choice

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from messages import PROCESS_STARTING_MSG, PARTICIPANTS_LIST, WINNER_MSG
from storage import storage


async def kosyachnik_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    rows_list = await storage.retrieve_rows_list(chat_id=chat_id)
    list_of_participants = []
    for i in rows_list:
        list_of_participants.append(i['name'])
    list_of_participants = ', '.join(list_of_participants)
    participants_text = PARTICIPANTS_LIST.format(list_of_participants=list_of_participants)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=participants_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=PROCESS_STARTING_MSG)

    winner = choice(rows_list)

    winner_name, winner_id = winner['username'] or winner['name'], winner['id']

    winner_text = WINNER_MSG.format(winner=winner_name)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=winner_text, parse_mode=ParseMode.HTML)

    await storage.increment_row(chat_id, winner_id)

    return winner_name, winner_id
