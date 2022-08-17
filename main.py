import logging
import os
import pprint
import telegram
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater
from random import choice
from messages import PREFIX_SIMPLE, PREFIX_DIRTY, PREFIX_LORD, PREFIX_GENERAL, WINNER_MSG, ALREADY_IN, \
    DEFAULT_START_MSG, ZERO_PIDORS, PROCESS_STARTING_MSG, NO_STATS, PARTICIPANTS_LIST, PIDOR_STATS, JOINED_MSG
from storage import Storage
import asyncio

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
CHAT_ID = -769270882

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
TOKEN = '5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'


# pip install -r requirements.txt

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    global storage
    storage = Storage(chat_id)
    if storage.start_msg_exists():
        await context.bot.send_message(chat_id=update.effective_chat.id, text=storage.start_message())
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=DEFAULT_START_MSG)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    register_message = telegram.Update(update_id=update.effective_user)
    # Add new row (when registered)
    global username, user_id
    username = register_message["update_id"]["username"]
    user_id = int(register_message['update_id']['id'])

    storage = Storage(chat_id)
    if not storage.check_row_existance(user_id=user_id):
        joined_text = JOINED_MSG.format(username=username)
        await storage.add_row(user_id, username)
        await context.bot.send_message(chat_id=chat_id, text=joined_text)
    else:
        await context.bot.send_message(chat_id=chat_id, text=ALREADY_IN)
        await context.bot.send_message(chat_id=chat_id, text='этот бот использует вебхуки, мазафака! WebPudge')


scoreboard = {}


async def pidor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)

    if storage.rows_list()[1:]:
        list_of_participants = []
        for i in storage.rows_list()[1:]:
            list_of_participants.append(i[1])
        list_of_participants = ', '.join(list_of_participants)
        participants_text = PARTICIPANTS_LIST.format(list_of_participants=list_of_participants)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=participants_text)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=PROCESS_STARTING_MSG)

        winner = choice(storage.rows_list()[1:])
        winner_username = winner[1]
        winner_text = WINNER_MSG.format(winner_username=winner_username)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=winner_text, parse_mode=ParseMode.HTML)

        await storage.increment_row(storage.rows_list(), winner_username)

    else:
        # raise ValueError('No rows in database')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ZERO_PIDORS)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)
    if storage.rows_exist():
        pidor_statistics = []
        for user_id, username, score in storage.rows_list()[1:]:
            if not score.isnumeric():
                continue

            score = int(score)
            if score < 5:
                prefix = PREFIX_SIMPLE
            elif score < 10:
                prefix = PREFIX_DIRTY
            elif score < 20:
                prefix = PREFIX_LORD
            else:
                prefix = PREFIX_GENERAL

            pidor_str = f'{username} - {prefix}'
            pidor_statistics.append(pidor_str)
        pidor_statistics = '\n'.join(pidor_statistics)
        pidor_stats_text = PIDOR_STATS.format(pidor_statistics=pidor_statistics)
        await context.bot.send_message(chat_id=chat_id, text=pidor_stats_text)
    else:
        await context.bot.send_message(chat_id=chat_id, text=NO_STATS)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '8443'))

    application = ApplicationBuilder().token(TOKEN).build()
    # updater = Updater(TOKEN, use_context=True)
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    pidor_handler = CommandHandler('pidor', pidor)
    stats_handler = CommandHandler('stats', stats)
    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.add_handler(pidor_handler)
    application.add_handler(stats_handler)

    application.run_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN,
                            webhook_url='https://pidor-checker-bot.herokuapp.com/' + TOKEN
                            )
