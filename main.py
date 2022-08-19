import logging
import os
from datetime import datetime

import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from messages import PREFIX_SIMPLE, PREFIX_DIRTY, PREFIX_LORD, PREFIX_GENERAL, ALREADY_IN, \
    DEFAULT_START_MSG, ZERO_PIDORS, NO_STATS, PIDOR_STATS, JOINED_MSG_USERNAME, \
    JOINED_MSG_NAME, WAIT_MSG
from pidor_func import pidor_func
from storage import Storage
from utils import suffix_function

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
CHAT_ID = -769270882

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
TOKEN = '5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)
    if storage.start_msg_exists():
        await context.bot.send_message(chat_id=update.effective_chat.id, text=storage.start_message())
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=DEFAULT_START_MSG)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    register_message = telegram.Update(update_id=update.effective_user)
    # Add new row (when registered)
    global username, user_id, name
    username = register_message["update_id"]["username"]
    user_id = int(register_message['update_id']['id'])
    first_name = register_message['update_id']['first_name']
    last_name = register_message['update_id']['last_name']
    if last_name:
        name = first_name + ' ' + last_name
    else:
        name = first_name

    storage = Storage(chat_id)
    if not storage.check_row_existance(user_id=user_id):
        joined_text_username = JOINED_MSG_USERNAME.format(username=username)
        joined_text_name = JOINED_MSG_NAME.format(name=name)
        await storage.add_row(user_id, username, name)
        if username:
            await context.bot.send_message(chat_id=chat_id, text=joined_text_username)
        else:
            await context.bot.send_message(chat_id=chat_id, text=joined_text_name)
    else:
        await storage.overwrite_row(storage.rows_list(), user_id=user_id, username=username, name=name)
        await context.bot.send_message(chat_id=chat_id, text=ALREADY_IN)


scoreboard = {}


async def pidor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)
    if storage.rows_list()[1:]:
        if not storage.time_file_exists():
            await pidor_func(update, context)
            storage.create_time_file()
        else:
            now = datetime.now()
            print(now)
            last_time = datetime.strptime(storage.time_file_read(), '%Y-%m-%d %H:%M:%S:%f')
            delta = now - last_time
            minutes, seconds = divmod(delta.seconds, 60)
            hours, minutes = divmod(minutes, 60)
            seconds = 59 - seconds
            minutes = 59 - minutes
            hours = 23 - hours

            wait_text = WAIT_MSG.format(hours=suffix_function(hours, minutes, seconds)[0],
                                        minutes=suffix_function(hours, minutes, seconds)[1],
                                        seconds=suffix_function(hours, minutes, seconds)[2])
            if delta.days == 0:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=wait_text)
            else:
                await pidor_func(update, context)
                storage.create_time_file()

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ZERO_PIDORS)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)
    if storage.rows_exist():
        pidor_statistics = []
        for user_id, username, name, score in storage.rows_list()[1:]:
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
            if username != 'None':
                pidor_str = f'{username} - {prefix}'
            else:
                pidor_str = f'{name} - {prefix}'
            pidor_statistics.append(pidor_str)
        pidor_statistics = '\n'.join(pidor_statistics)
        pidor_stats_text = PIDOR_STATS.format(pidor_statistics=pidor_statistics)
        await context.bot.send_message(chat_id=chat_id, text=pidor_stats_text)
    else:
        await context.bot.send_message(chat_id=chat_id, text=NO_STATS)


PORT = int(os.environ.get('PORT', '8443'))

application = ApplicationBuilder().token(TOKEN).build()
start_handler = CommandHandler('start', start)
register_handler = CommandHandler('register', register)
pidor_handler = CommandHandler('pidor', pidor)
stats_handler = CommandHandler('stats', stats)
application.add_handler(start_handler)
application.add_handler(register_handler)
application.add_handler(pidor_handler)
application.add_handler(stats_handler)
# application.run_polling()


application.run_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN,
                        webhook_url='https://pidor-checker-bot.herokuapp.com/' + TOKEN
                        )
