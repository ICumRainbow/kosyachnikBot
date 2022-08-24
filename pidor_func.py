from random import choice

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from messages import PROCESS_STARTING_MSG, PARTICIPANTS_LIST, WINNER_MSG
from storage import Storage


async def pidor_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage()
    rows_list = await storage.retrieve_rows_list(chat_id=chat_id)
    list_of_participants = []
    for i in rows_list:
        if i['chat_id'] == chat_id:
            list_of_participants.append(i['username'] or i['name'])
            print('#' * 20)
    list_of_participants = ', '.join(list_of_participants)
    participants_text = PARTICIPANTS_LIST.format(list_of_participants=list_of_participants)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=participants_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=PROCESS_STARTING_MSG)

    winner = choice(rows_list)

    _, winner_id, winner_username, winner_name, _ = winner.values()

    winner_text = WINNER_MSG.format(winner=winner_username or winner_name)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=winner_text, parse_mode=ParseMode.HTML)

    await storage.increment_row(chat_id, winner_id)

    winner_name = winner_username or winner_name
    return winner_name
