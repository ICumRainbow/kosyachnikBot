from datetime import datetime, timedelta
from typing import Tuple

from telegram import Update
from telegram.ext import ContextTypes

from messages import WAIT_MSG
from storage import Storage


def verbose_format_time(h, m, s) -> str:
    time_dict = {}

    def determine_suffix(val: int, words: Tuple[str, str, str]):

        if 1 < val % 10 < 5 and (val < 10 or val > 20):
            return str(val) + words[0]
        elif val % 10 == 1 and (val > 11 or val < 10):
            return str(val) + words[1]
        elif val == 0:
            return ''
        else:
            return str(val) + words[2]

    time_dict['hours'] = determine_suffix(h, (' часа, ', ' час,', ' часов, '))
    time_dict['minutes'] = determine_suffix(m, (' минуты, ', ' минута, ', ' минут, '))
    time_dict['seconds'] = determine_suffix(s, (' секунды', ' секунда', ' секунд'))
    time = ''
    for keys in time_dict:
        time = time + time_dict[keys]

    return time


verbose_format_time(1, 31, 21)


def time_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage(chat_id)

    now = datetime.now()
    last_time = datetime.strptime(storage.time_file_read(chat_id=chat_id), '%Y-%m-%d %H:%M:%S')
    delta = last_time - now + timedelta(days=1)
    minutes, seconds = divmod(delta.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    verbose_format_time(hours, minutes, seconds)
    time_string = verbose_format_time(hours, minutes, seconds)
    wait_text = WAIT_MSG.format(time=time_string)

    return delta, wait_text
