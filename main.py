import logging
import os
import pymysql
from config import host, user, db_name, password

try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print('Success!')

    # try:
        # cursor = connection.cursor()

        # create table
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE 'users'(id int"

except Exception as ex:
    print('FAIL')
    print(ex)

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from messages import PREFIX_SIMPLE, PREFIX_DIRTY, PREFIX_LORD, PREFIX_GENERAL, ALREADY_IN, \
    DEFAULT_START_MSG, ZERO_PIDORS, NO_STATS, PIDOR_STATS, JOINED_MSG
from pidor_func import pidor_func
from utils import time_func
from storage import Storage

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

    text = storage.start_message() if storage.start_msg_exists() else DEFAULT_START_MSG
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)

    # Add new row (when registered)
    username = update.effective_user.username or ''
    user_id = int(update.effective_user.id)
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    print(first_name)
    name = (first_name + ' ' + last_name) if last_name else first_name

    if not storage.check_row_existance(user_id=user_id, chat_id=chat_id):
        joined_text = JOINED_MSG.format(name=username or name)
        await storage.add_row(chat_id, user_id, username, name)
        await context.bot.send_message(chat_id=chat_id, text=joined_text)
    else:
        await storage.overwrite_row(target_user_id=user_id, new_username=username, new_name=name)
        await context.bot.send_message(chat_id=chat_id, text=ALREADY_IN)


scoreboard = {}


async def pidor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)

    if not storage.check_participants(chat_id):  # If no users registered, do not find one
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ZERO_PIDORS)
        return

    if not storage.time_file_exists(chat_id=chat_id):
        await pidor_func(update, context)
        storage.create_time_file(chat_id=chat_id)
        return

    delta, wait_text = time_func(update, context)

    if delta.days == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=wait_text)
    else:
        await pidor_func(update, context)
        storage.create_time_file(chat_id=chat_id)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)
    rows_exist = storage.rows_exist(chat_id=chat_id)
    if not rows_exist:
        await context.bot.send_message(chat_id=chat_id, text=NO_STATS)
        return

    pidor_statistics = []
    rows_list = storage.rows_list(chat_id)
    print(rows_list)
    for row in rows_list:
        score = row['score']
        if score < 5:
            prefix = PREFIX_SIMPLE
        elif score < 10:
            prefix = PREFIX_DIRTY
        elif score < 20:
            prefix = PREFIX_LORD
        else:
            prefix = PREFIX_GENERAL
        name = row['username'] or row['name']
        pidor_str = f'{name} - {prefix}'

        pidor_statistics.append(pidor_str)

    pidor_statistics = '\n'.join(pidor_statistics)
    pidor_stats_text = PIDOR_STATS.format(pidor_statistics=pidor_statistics)
    await context.bot.send_message(chat_id=chat_id, text=pidor_stats_text)


PORT = int(os.environ.get('PORT', '8443'))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    handlers = [
        CommandHandler('start', start),
        CommandHandler('register', register),
        CommandHandler('pidor', pidor),
        CommandHandler('stats', stats)
    ]

    application.add_handlers(handlers)

    # application.run_polling()


application.run_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN,
                        webhook_url='https://pidor-checker-bot.herokuapp.com/' + TOKEN
                        )
