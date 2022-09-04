from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from messages import NO_PARTICIPANTS, WINNER_MSG, PROCESS_STARTING_MSG
from storage import storage
from utils import check_time, choose_random_winner, format_participants_list, get_wait_text


async def _send_winner_messages(chat_id, context: ContextTypes.DEFAULT_TYPE):
    """ Send messages about search results into target group and update last search time """
    winner_id, winner_name = await choose_random_winner(chat_id)  # Retrieving randomly chosen winner's user id and name
    participants_text = await format_participants_list(chat_id)  # Retrieving formatted test for a message listing participants
    winner_text = WINNER_MSG.format(winner=winner_name)  # Formatting a message with the winner using winner's id and name retrieved above

    await context.bot.send_message(chat_id=chat_id, text=participants_text)
    await context.bot.send_message(chat_id=chat_id, text=PROCESS_STARTING_MSG)
    await context.bot.send_message(chat_id=chat_id, text=winner_text, parse_mode=ParseMode.HTML)

    await storage.update_last_search_time(chat_id=chat_id, winner_id=winner_id)  # Set current time as function's last time call


async def kosyachnik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ The main function. Displays a list of members of the effective chat who have registered and randomly chooses one of them as Kosyachnik and displays as well.
        If it hasn't been 24 hours since the last call for this function or no one in this chat had registered - displays a corresponding message. """

    chat_id = update.message.chat.id  # Get id of the chat where this handler was called
    user_id = int(update.effective_user.id)  # Get id of user who called this handler
    username = update.effective_user.username or ''
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    name = (first_name + ' ' + last_name) if last_name else first_name

    if not await storage.check_participants_exist(chat_id):  # If no users registered, do not find one
        await context.bot.send_message(chat_id=chat_id, text=NO_PARTICIPANTS)
        return

    if await storage.check_user_registered(chat_id=chat_id, user_id=user_id):
        await storage.update_user_row(target_user_id=user_id, new_username=username, new_name=name)  # If user is registered in any chat, update his username and name

    if not await storage.check_time_row_exists(chat_id=chat_id):  # If there is no last time of calling this handler - choose the winner
        await _send_winner_messages(chat_id, context)
        return

    delta = await check_time(update)  # Check if enough time passed since last call of this handler
    winner_name = await storage.retrieve_last_winner(chat_id=chat_id)  # Retrieve last winner's name for a message to wait
    wait_text = get_wait_text(delta, winner_name)  # Format wait message using data we retrieved above

    if delta.seconds == 0:  # If it wasn't a day since last handler call, display wait message
        await context.bot.send_message(chat_id=chat_id, text=wait_text, parse_mode=ParseMode.HTML)
        return

    elif delta.seconds > 1:  # If it was a day or more - choose the winner
        await _send_winner_messages(chat_id, context)
