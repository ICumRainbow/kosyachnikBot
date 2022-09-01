import sys

from telegram import Update
from telegram.ext import ContextTypes

from messages import KOSYACHNIK_STATS, PREFIX_TERMINATION, PREFIX_CEO, PREFIX_SLACKER, PREFIX_SIMPLE, NO_STATS
from storage import storage


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Displays current statistics for the effective chat if there are registered users present.
        Displays a NO_STATS message otherwise. """
    chat_id = update.message.chat.id
    user_id = int(update.effective_user.id)
    username = update.effective_user.username or ''
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name

    name = (first_name + ' ' + last_name) if last_name else first_name
    rows_exist = await storage.check_stats_exist(chat_id=chat_id)

    if not rows_exist:  # Check if there is any users registered in this chat and display a no_stats message is there isn't
        await context.bot.send_message(chat_id=chat_id, text=NO_STATS)
        return

    if await storage.check_user_registered(chat_id=chat_id, user_id=user_id):
        await storage.update_user_row(target_user_id=user_id, new_username=username, new_name=name)

    prefixes = {
        1: PREFIX_SIMPLE,
        5: PREFIX_SLACKER,
        10: PREFIX_CEO,
        sys.maxsize: PREFIX_TERMINATION
    }

    kosyachnik_stats = []

    participants_list = await storage.retrieve_participants_list(chat_id)
    for row in participants_list:
        score = row['score']
        for key in prefixes.keys():
            if score < key:
                prefix = prefixes[key]
                break
        else:
            prefix = ''

        name = row['username'] or row['name']
        kosyachnik_str = f'{name} - {prefix}'

        kosyachnik_stats.append(kosyachnik_str)

    kosyachnik_stats = '\n'.join(kosyachnik_stats)

    kosyachnik_stats_message = KOSYACHNIK_STATS.format(kosyachnik_statistics=kosyachnik_stats)

    await context.bot.send_message(chat_id=chat_id, text=kosyachnik_stats_message)
