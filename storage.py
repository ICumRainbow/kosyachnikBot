from pathlib import Path
from datetime import datetime, timedelta, timezone

# import pymysql
import psycopg2
from psycopg2.extras import DictCursor
import config
from queries import SELECT_USER_ID_QUERY, SELECT_ID_QUERY, INSERT_USER_QUERY, SELECT_GROUP_QUERY, INSERT_GROUP_QUERY, INSERT_SCORE_QUERY, SELECT_STATS_QUERY, SELECT_FETCH_STATS_QUERY, \
    SELECT_USER_QUERY, \
    SELECT_CHAT_ID_QUERY, UPDATE_SCORE_QUERY, SELECT_LAST_TIME_NOT_NULL_QUERY, UPDATE_LAST_TIME_QUERY, SELECT_LAST_TIME_QUERY, SELECT_LAST_WINNER_QUERY, UPDATE_USER_ROW_QUERY

# API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
MAX_ATTEMPTS = 10


class Storage:
    def __init__(self):
        self.info_file_path = Path('info.txt')
        self._connection = None
        self.start_time = None

    async def _get_connection(self):
        """ Returns working connection either by reusing an existing one, or by creating a new one. """
        if self._connection is None:
            # When rerunning the bot shortly afterwards the command was executed, it raises Too Many Connections error
            self._connection = psycopg2.connect(
                host=config.host,
                port=5432,
                user=config.user,
                password=config.password,
                database=config.db_name,
                cursor_factory=DictCursor,
            )
            self.start_time = datetime.now(tz=timezone.utc)
            return self._connection
        now = datetime.now(tz=timezone.utc)
        delta = now - self.start_time
        self.start_time = now

        # if delta > timedelta(seconds=60):
            # try:
            # Somehow if we use ping(reconnect=True) it raises Too Many Connections error, if we remove reconnect=True, everything seems to be working good
            # self._connection.ping()
            # except psycopg2 as err:
            #     return self._connection

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
            query_user_registered = cursor.execute(SELECT_USER_ID_QUERY, (chat_id, user_id))
            user_registered = cursor.fetchall()
            return bool(user_registered)

    async def add_user(self, chat_id: int, user_id: int, username: str, name: str) -> None:
        """ Adds user's id, name, username and chat's id to every table this data is not present in. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            query_user = cursor.execute(SELECT_ID_QUERY, [user_id])
            user_exists = cursor.fetchall()
            if not user_exists:
                cursor.execute(INSERT_USER_QUERY, (user_id, username, name))
            await storage.update_user_row(target_user_id=user_id, new_username=username, new_name=name)
            query_group = cursor.execute(SELECT_GROUP_QUERY, (chat_id,))
            group_exists = cursor.fetchall()
            if not group_exists:
                cursor.execute(INSERT_GROUP_QUERY, (chat_id,))

            cursor.execute(INSERT_SCORE_QUERY, (chat_id, user_id))

            connection.commit()

    async def check_stats_exist(self, chat_id) -> bool:
        """ Returns True if there are any stats available for this chat_id. False otherwise. """
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            query = cursor.execute(SELECT_STATS_QUERY, [chat_id])
            result = cursor.fetchone()[0]

        return bool(result)

    async def retrieve_participants_list(self, chat_id) -> list:
        """ Returns a list of all users registered in this chat. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_FETCH_STATS_QUERY, [chat_id])
            participants_list = cursor.fetchall()

        return participants_list

    async def retrieve_user_data(self, user_id) -> dict:
        """ Returns a dict with name and username of the user, which are available in the database. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_USER_QUERY, [user_id])
            user_data = cursor.fetchone()

        return user_data

    async def check_participants_exist(self, chat_id) -> bool:
        """ Returns True if there are users registered in group with this chat_id. False otherwise. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            participants_exist = cursor.execute(SELECT_CHAT_ID_QUERY, [chat_id])
            result = cursor.fetchall()

        return bool(result)

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
            query = cursor.execute(SELECT_LAST_TIME_NOT_NULL_QUERY, [chat_id])
            result = cursor.fetchall()

        return bool(result)

    async def update_last_search_time(self, chat_id: int, winner_id: int) -> None:
        """ Either creates or updates last time of calling the Kosyachnik function. """
        connection = await self._get_connection()

        # time_zone = pytz.timezone('Asia/Samarkand')
        now = datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S')

        row = (current_time, winner_id, chat_id)

        with connection.cursor() as cursor:
            cursor.execute(UPDATE_LAST_TIME_QUERY, row)
            connection.commit()

    async def retrieve_time(self, chat_id: int) -> str:
        """ Returns last time the Kosyachnik function was called in this chat as string. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_LAST_TIME_QUERY, [chat_id])
            rows = cursor.fetchone()
        return str(rows[0])

    async def retrieve_last_winner(self, chat_id: int) -> str:
        """ Returns a string with this chat's last winner's name and username. """
        connection = await self._get_connection()

        with connection.cursor() as cursor:
            cursor.execute(SELECT_LAST_WINNER_QUERY, [chat_id])
            rows = cursor.fetchone()
        # Returns username if exists, name otherwise.
        return rows[0] or rows[1]

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
