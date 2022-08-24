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


async def time_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage()

    now = datetime.now()
    last_time, winner_name = datetime.strptime(await storage.time_file_read(chat_id=chat_id), '%Y-%m-%d %H:%M:%S')
    delta = last_time - now + timedelta(days=1)
    minutes, seconds = divmod(delta.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    verbose_format_time(hours, minutes, seconds)
    time_string = verbose_format_time(hours, minutes, seconds)
    wait_text = WAIT_MSG.format(time=time_string, winner_name=winner_name)

    return delta, wait_text


# def compare_versions(version1: str, version2: str):
#     if '.' in version1:
#         version1 = version1.split('.')
#     if '.' in version2:
#         version2 = version2.split('.')
#     else:
#         version2 =
#     if len(version1) == len(version2):
#         for num1, num2 in zip(version1, version2):
#             if num1 != num2:
#                 return (num1 > num2)
#         return True
#     else:
#         v1 = 1
#         v2 = 1
#         version_1st = []
#         version_2nd = []
#         for number in version1:
#             number = int(number)
#             number = number * v1
#             version_1st.append(number)
#             v1 **= 2
#         for number in version2:
#             number = int(number)
#             number = number * v2
#             version_2nd.append(number)
#             v2 **= 2
#             print(version_2nd)
#         return sum(version_1st) > sum(version_2nd)
#
#
# compare_versions("10.4", "11")

