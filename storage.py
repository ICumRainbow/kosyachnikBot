from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import ClassVar

import pymysql

import config
from queries import SELECT_USER_ID_QUERY, SELECT_ID_QUERY, INSERT_USER_QUERY, SELECT_GROUP_QUERY, INSERT_GROUP_QUERY, INSERT_SCORE_QUERY, SELECT_STATS_QUERY, SELECT_FETCH_STATS_QUERY, \
    SELECT_USER_QUERY, \
    SELECT_CHAT_ID_QUERY, UPDATE_SCORE_QUERY, SELECT_LAST_TIME_NOT_NULL_QUERY, UPDATE_LAST_TIME_QUERY, SELECT_LAST_TIME_QUERY, SELECT_LAST_WINNER_QUERY, UPDATE_USER_ROW_QUERY

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
MAX_ATTEMPTS = 10


class Storage:
    def __init__(self):
        self.info_file_path = Path('info.txt')
        self._connection = None
        self.start_time = None

    async def _get_connection(self):
        """ Returns working connection either by reusing an existing one, or by creating a new one. """
        if self._connection is None:
            self._connection = pymysql.connect(
                host=config.host,
                port=3306,
                user=config.user,
                password=config.password,
                database=config.db_name,
                cursorclass=pymysql.cursors.DictCursor,
            )
            self.start_time = datetime.now(tz=timezone.utc)
            return self._connection

        now = datetime.now(tz=timezone.utc)
        delta = now - self.start_time
        self.start_time = now

        if delta > timedelta(seconds=60):
            self._connection.ping(reconnect=True)

        return self._connection

    def check_info_msg_exists(self) -> bool:
        """ Returns True if the file with info message exists. False otherwise. """
        return self.info_file_path.exists()

    def retrieve_info_message(self) -> str:
        """ Returns text from the file with info message. """
        with open(self.info_file_path, encoding='utf8') as f:
            info_text = f.read()

        return info_text

    async def check_user_registered(self, chat_id: int, user_id: int) -> bool:
        """ Returns True if the user is registered in the group. False otherwise. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            return bool(cursor.execute(SELECT_USER_ID_QUERY, (chat_id, user_id)))

    async def add_user(self, chat_id: int, user_id: int, username: str, name: str) -> None:
        """ Adds user's id, name, username and chat's id to every table this data is not present in. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:

            if not cursor.execute(SELECT_ID_QUERY, user_id):
                cursor.execute(INSERT_USER_QUERY, (user_id, username, name))

            if not cursor.execute(SELECT_GROUP_QUERY, (chat_id,)):
                cursor.execute(INSERT_GROUP_QUERY, (chat_id,))

            cursor.execute(INSERT_SCORE_QUERY, (chat_id, user_id))

            connection.commit()

    async def check_stats_exist(self, chat_id) -> bool:
        """ Returns True if there are any stats available for this chat_id. False otherwise. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            result = cursor.execute(SELECT_STATS_QUERY, chat_id)

        return bool(result)

    async def retrieve_participants_list(self, chat_id) -> tuple:
        """ Returns a list of all users registered in this chat. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_FETCH_STATS_QUERY, chat_id)
            participants_list = cursor.fetchall()

        return participants_list

    async def retrieve_user_data(self, user_id) -> dict:
        """ Returns a dict with name and username of the user, which are available in the database. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_USER_QUERY, user_id)
            user_data = cursor.fetchone()

        return user_data

    async def check_participants_exist(self, chat_id) -> bool:
        """ Returns True if there are users registered in group with this chat_id. False otherwise. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            participants_exist = cursor.execute(SELECT_CHAT_ID_QUERY, chat_id)

        return bool(participants_exist)

    async def increment_row(self, chat_id, winner_id: int) -> None:
        """ Increments score of user who was chosen as kosyachnik. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(UPDATE_SCORE_QUERY, (chat_id, winner_id))
            connection.commit()

    async def check_time_row_exists(self, chat_id) -> bool:
        """ Returns True if the Kosyachnik function was ever called in this chat. False otherwise. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            result = cursor.execute(SELECT_LAST_TIME_NOT_NULL_QUERY, chat_id)

        return bool(result)

    async def update_last_search_time(self, chat_id: int, winner_id: int) -> None:
        """ Either creates or updates last time of calling the Kosyachnik function. """
        connection = await self._get_connection()

        now = datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S:%f')

        row = (current_time, winner_id, chat_id)

        with connection.cursor() as cursor:
            cursor.execute(UPDATE_LAST_TIME_QUERY, row)
            connection.commit()

    async def retrieve_time(self, chat_id: int) -> str:
        """ Returns last time the Kosyachnik function was called in this chat as string. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_LAST_TIME_QUERY, chat_id)
            rows = cursor.fetchone()
        return str(rows['last_time'])

    async def retrieve_last_winner(self, chat_id: int) -> str:
        """ Returns a string with this chat's last winner's name and username. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_LAST_WINNER_QUERY, chat_id)
            rows = cursor.fetchone()

        return str(rows['winner_username'] or rows['winner_name'])

    async def update_user_row(self, target_user_id: int, new_username: str, new_name: str) -> None:
        """ Updates user's name and username if it doesn't match the data in database. """
        connection = await self._get_connection()

        user = await self.retrieve_user_data(target_user_id)
        if user['username'] != new_username or user['name'] != new_name:
            users_row = (new_username, new_name, target_user_id)
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_USER_ROW_QUERY, users_row)
                connection.commit()


storage = Storage()
