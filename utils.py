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

    time_dict['hours'] = determine_suffix(h, (' hours, ', ' hour,', ' hours, '))
    time_dict['minutes'] = determine_suffix(m, (' minutes, ', ' minute, ', ' minutes, '))
    time_dict['seconds'] = determine_suffix(s, (' seconds', ' second', ' seconds'))
    time = ''
    for keys in time_dict:
        time = time + time_dict[keys]

    return time


verbose_format_time(1, 31, 21)


async def time_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    storage = Storage()

    now = datetime.now()
    last_time = datetime.strptime(await storage.retrieve_time(chat_id=chat_id), '%Y-%m-%d %H:%M:%S')
    winner_name = await storage.retrieve_last_winner(chat_id=chat_id)
    delta = last_time - now + timedelta(days=1)
    minutes, seconds = divmod(delta.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    verbose_format_time(hours, minutes, seconds)
    time_string = verbose_format_time(hours, minutes, seconds)
    wait_text = WAIT_MSG.format(time=time_string, winner_name=winner_name)

    return delta, wait_text, winner_name


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

# MORSE_CODE = {'A': '.-', 'B': '-...',
#               'C': '-.-.', 'D': '-..', 'E': '.',
#               'F': '..-.', 'G': '--.', 'H': '....',
#               'I': '..', 'J': '.---', 'K': '-.-',
#               'L': '.-..', 'M': '--', 'N': '-.',
#               'O': '---', 'P': '.--.', 'Q': '--.-',
#               'R': '.-.', 'S': '...', 'T': '-',
#               'U': '..-', 'V': '...-', 'W': '.--',
#               'X': '-..-', 'Y': '-.--', 'Z': '--..',
#               '1': '.----', '2': '..---', '3': '...--',
#               '4': '....-', '5': '.....', '6': '-....',
#               '7': '--...', '8': '---..', '9': '----.',
#               '0': '-----', ', ': '--..--', '.': '.-.-.-',
#               '?': '..--..', '/': '-..-.', '-': '-....-',
#               '(': '-.--.', ')': '-.--.-'}


# def decode_morse(morse_code):
    # morse_code = list(morse_code)
    # string = ''
    morse_list = []
    # for inx, val in enumerate(morse_code):
    #     if val != ' ':
    #         string = string + val
    #     elif val == ' ' and morse_code[inx+1] != ' ':
    #         morse_list.append(string)
    #         string = ''
    #         continue
    #     else:
    #         morse_list.append(val)
    #
    # print(morse_list)
#     morse_code = morse_code.split('   ')
#     for i in morse_code:
#         i = i.split()
#         morse_list.append(i)
#     print(morse_list)
#     for items in morse_list:
#         for item in items:
#             item = MORSE_CODE[item]
#             print(item)
# decode_morse('.... . -.--   .--- ..- -.. .')



# def is_isogram(string:str):
#     string = string.lower()
#     cache = set()
#     for i in string:
#         if i in cache:
#             return False
#         cache.add(i)
#     return True
