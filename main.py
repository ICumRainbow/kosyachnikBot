import logging
import os
import sys

import pymysql
from telegram.constants import ParseMode

from config import host, user, db_name, password

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from messages import PREFIX_SIMPLE, PREFIX_SLACKER, PREFIX_CEO, PREFIX_TERMINATION, ALREADY_IN, \
    DEFAULT_START_MSG, ZERO_PARTICIPANTS, NO_STATS, KOSYACHNIK_STATS, JOINED_MSG
from kosyachnik_func import kosyachnik_func
from utils import time_func
from storage import Storage

# try:
#     connection = pymysql.connect(
#         host=host,
#         port=3306,
#         user=user,
#         password=password,
#         database=db_name,
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     print('Success!')
#
#
# except Exception as ex:
#     print('FAIL')
#     print(ex)

# connection.ping(reconnect=True)


API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
CHAT_ID = -769270882

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
TOKEN = '5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    storage = Storage()

    text = storage.start_message() if storage.start_msg_exists() else DEFAULT_START_MSG
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage()
    # storage.truncate()
    # Add new row (when registered)
    username = update.effective_user.username or ''
    user_id = int(update.effective_user.id)
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    name = (first_name + ' ' + last_name) if last_name else first_name

    if not await storage.check_row_existance(user_id=user_id, chat_id=chat_id):
        joined_text = JOINED_MSG.format(name=username or name)
        await storage.add_row(chat_id, user_id, username, name)
        await context.bot.send_message(chat_id=chat_id, text=joined_text)
    else:
        await storage.overwrite_row(target_user_id=user_id, new_username=username, new_name=name)
        await context.bot.send_message(chat_id=chat_id, text=ALREADY_IN)


# scoreboard = {}


async def kosyachnik_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage()

    if not await storage.check_participants(chat_id):  # If no users registered, do not find one
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ZERO_PARTICIPANTS)
        return

    if not await storage.time_row_exists(chat_id=chat_id):
        winner_name, winner_id = await kosyachnik_func(update, context)
        await storage.create_time_file(chat_id=chat_id, winner_name=winner_name, winner_id=winner_id)
        return

    delta, wait_text, winner_name = await time_func(update, context)

    if delta.days == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=wait_text)
    else:
        winner_name, winner_id = await kosyachnik_func(update, context)
        await storage.create_time_file(chat_id=chat_id, winner_name=winner_name, winner_id=winner_id)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage()
    rows_exist = await storage.rows_exist(chat_id=chat_id)
    if not rows_exist:
        await context.bot.send_message(chat_id=chat_id, text=NO_STATS)
        return


    prefixes = {
        5: PREFIX_SIMPLE,
        10: PREFIX_SLACKER,
        20: PREFIX_CEO,
        sys.maxsize: PREFIX_TERMINATION
    }

    kosyachnik_statistics = []
    rows_list = await storage.retrieve_rows_list(chat_id)
    for row in rows_list:
        score = row['score']
        for key in prefixes.keys():
            if score < key:
                prefix = prefixes[key]
                break
        # if score < 5:
        #     prefix = PREFIX_SIMPLE
        # elif score < 10:
        #     prefix = PREFIX_SLACKER
        # elif score < 20:
        #     prefix = PREFIX_CEO
        # else:
        #     prefix = PREFIX_TERMINATION
        name = row['username'] or row['name']
        kosyachnik_str = f'{name} - {prefix}'

        kosyachnik_statistics.append(kosyachnik_str)

    kosyachnik_statistics = '\n'.join(kosyachnik_statistics)
    kosyachnik_message = KOSYACHNIK_STATS.format(kosyachnik_statistics=kosyachnik_statistics)
    await context.bot.send_message(chat_id=chat_id, text=kosyachnik_message)


PORT = int(os.environ.get('PORT', '8443'))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    handlers = [
        CommandHandler('start', start),
        CommandHandler('register', register),
        CommandHandler('kosyachnik_search', kosyachnik_search),
        CommandHandler('stats', stats)
    ]

    application.add_handlers(handlers)

    # application.run_polling()

    application.run_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN,
                            webhook_url='https://pidor-checker-bot.herokuapp.com/' + TOKEN
                            )
