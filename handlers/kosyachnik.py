from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from messages import ZERO_PARTICIPANTS, WINNER_MSG, PROCESS_STARTING_MSG
from storage import storage
from utils import check_time, choose_random_winner, format_participants_list


async def kosyachnik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ The main function. Displays a list of members of the effective chat who have registered and randomly chooses one of them as Kosyachnik and displays as well.
        If it hasn't been 24 hours since the last call for this function or no one in this chat had registered - displays a corresponding message. """
    chat_id = update.message.chat.id
    username = update.effective_user.username or ''
    user_id = int(update.effective_user.id)
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    name = (first_name + ' ' + last_name) if last_name else first_name

    if not await storage.check_participants_exist(chat_id):  # If no users registered, do not find one
        await context.bot.send_message(chat_id=chat_id, text=ZERO_PARTICIPANTS)
        return

    await storage.update_user_row(target_user_id=user_id, new_username=username, new_name=name)

    if not await storage.check_time_row_exists(chat_id=chat_id):
        winner_id, winner_name = await choose_random_winner(chat_id)
        participants_text = await format_participants_list(chat_id)
        winner_text = WINNER_MSG.format(winner=winner_name)

        await context.bot.send_message(chat_id=chat_id, text=participants_text)
        await context.bot.send_message(chat_id=chat_id, text=PROCESS_STARTING_MSG)
        await context.bot.send_message(chat_id=chat_id, text=winner_text, parse_mode=ParseMode.HTML)

        await storage.create_time_file(chat_id=chat_id, winner_id=winner_id)
        return

    delta, wait_text = await check_time(update)

    if delta.days == 0:
        await context.bot.send_message(chat_id=chat_id, text=wait_text, parse_mode=ParseMode.HTML)
        return

    elif delta.days > 0:
        winner_id, winner_name = await choose_random_winner(chat_id)
        participants_text = await format_participants_list(chat_id)
        winner_text = WINNER_MSG.format(winner=winner_name)

        await context.bot.send_message(chat_id=chat_id, text=participants_text)
        await context.bot.send_message(chat_id=chat_id, text=PROCESS_STARTING_MSG)
        await context.bot.send_message(chat_id=chat_id, text=winner_text, parse_mode=ParseMode.HTML)

        await storage.create_time_file(chat_id=chat_id, winner_id=winner_id)
