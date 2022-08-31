import logging
import os

from telegram.ext import ApplicationBuilder, CommandHandler

from handlers.info import info
from handlers.kosyachnik import kosyachnik
from handlers.register import register
from handlers.stats import stats

PORT = int(os.environ.get('PORT', '8443'))
TOKEN = '5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    handlers = [
        CommandHandler('info', info),
        CommandHandler('register', register),
        CommandHandler('kosyachnik', kosyachnik),
        CommandHandler('stats', stats)
    ]

    application.add_handlers(handlers)

    # application.run_polling()

    application.run_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN,
                            webhook_url='https://pidor-checker-bot.herokuapp.com/' + TOKEN
                            )
