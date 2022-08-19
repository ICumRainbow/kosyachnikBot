from random import choice
from storage import Storage
import telegram
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from messages import PROCESS_STARTING_MSG, PARTICIPANTS_LIST, WINNER_MSG_USERNAME, WINNER_MSG_NAME


async def pidor_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)
    register_message = telegram.Update(update_id=update.effective_user)
    username = register_message["update_id"]["username"]
    list_of_participants = []
    for i in storage.rows_list()[1:]:
        if username:
            list_of_participants.append(i[1])
        else:
            list_of_participants.append(i[2])
    list_of_participants = ', '.join(list_of_participants)
    participants_text = PARTICIPANTS_LIST.format(list_of_participants=list_of_participants)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=participants_text)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=PROCESS_STARTING_MSG)

    winner = choice(storage.rows_list()[1:])
    winner_id = winner[0]
    winner_username = winner[1]
    winner_name = winner[2]
    winner_text_username = WINNER_MSG_USERNAME.format(winner_username=winner_username)
    winner_text_name = WINNER_MSG_NAME.format(winner_name=winner_name)
    if winner_username != 'None':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=winner_text_username,
                                       parse_mode=ParseMode.HTML)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=winner_text_name,
                                       parse_mode=ParseMode.HTML)

    await storage.increment_row(storage.rows_list(), winner_id)


