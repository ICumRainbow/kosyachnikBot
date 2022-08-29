from time import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from timeit import default_timer

import pymysql
from telegram.ext import ContextTypes

from config import host, user, db_name, password
from messages import ERROR_MSG

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
MAX_ATTEMPTS = 10


class Storage:

    def __init__(self):
        self.path_start = Path('start.txt')
        self._connection = None
        self.start_time = None

    async def _get_connection(self):
        """ Returns working connection either by reusing an existing one, or by creating a new one """
        # if attempt > MAX_ATTEMPTS:
        #     await context.bot.send_message(chat_id=-719794843, text=ERROR_MSG)
        # print('getting connection')
        if self._connection is None:
            self._connection = pymysql.connect(
                host=host,
                port=3306,
                user=user,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor,
            )
            self.start_time = datetime.now(tz=timezone.utc)
            return self._connection
        now = datetime.now(tz=timezone.utc)
        delta = now - self.start_time
        # print(delta.seconds)
        if delta > timedelta(seconds=60):
            start = default_timer()
            self._connection.ping(reconnect=True)
            print(f'Time taken: {default_timer() - start}s')

        self.start_time = now
        return self._connection

    def start_msg_exists(self) -> bool:
        return self.path_start.exists()

    def start_message(self):
        with open(self.path_start, encoding='utf8') as f:
            start_text = f.read()
            return start_text

    async def check_registered(self, chat_id: int, user_id: int):
        chat_and_user_id = (chat_id, user_id)
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            select_query = 'select user_id from scores where chat_id=%s and user_id=%s'
            return cursor.execute(select_query, chat_and_user_id)

    async def add_row(self, chat_id: int, user_id: int, username: str, name: str):

        connection = await self._get_connection()

        row_users = (user_id, username, name)
        row_groups = (chat_id,)
        row_scores = (chat_id, user_id)

        with connection.cursor() as cursor:
            check_users_query = "SELECT id, username, name from users where id=%s"
            add_row_users_query = "INSERT INTO users VALUES(%s,%s,%s)"
            check_groups_query = "SELECT id from contest_groups where id=%s"
            add_row_groups_query = "INSERT INTO contest_groups(id) VALUES(%s)"
            add_row_scores_query = "INSERT INTO scores(chat_id,user_id) VALUES(%s,%s)"

            if not cursor.execute(check_users_query, user_id):
                cursor.execute(add_row_users_query, row_users)

            if not cursor.execute(check_groups_query, row_groups):
                cursor.execute(add_row_groups_query, row_groups)

            cursor.execute(add_row_scores_query, row_scores)

            connection.commit()

    async def rows_exist(self, chat_id) -> bool:

        connection = await self._get_connection()
        with connection.cursor() as cursor:
            rows_exist_query = 'SELECT IFNULL(users.username, users.name) AS "name" ' \
                               'FROM scores ' \
                               'JOIN users ON scores.chat_id=%s AND scores.user_id=users.id;'
            result = cursor.execute(rows_exist_query, chat_id)
            connection.commit()
            return result

    async def retrieve_rows_list(self, chat_id) -> list:
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            select_query = 'SELECT users.username AS "username", users.name AS "name", users.id AS "id", scores.score as "score" ' \
                           'FROM scores ' \
                           'JOIN users ON scores.chat_id=%s AND scores.user_id=users.id;'
            cursor.execute(select_query, chat_id)
            participants_list = cursor.fetchall()
            connection.commit()
            return participants_list

    async def check_user_data(self, user_id):
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            check_user_query = 'SELECT username, name from users WHERE id=%s'
            cursor.execute(check_user_query, user_id)
            user_data = cursor.fetchone()
            connection.commit()
            return user_data

    async def check_participants(self, chat_id):
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            check_participants_query = 'SELECT chat_id FROM scores WHERE chat_id=%s'
            participants_exist = cursor.execute(check_participants_query, chat_id)
            # print(participants_exist)
        return participants_exist

    async def increment_row(self, chat_id, winner_id: int):

        connection = await self._get_connection()

        row = (chat_id, winner_id)
        with connection.cursor() as cursor:
            increment_score_query = 'UPDATE scores SET score = score + 1 WHERE chat_id = %s AND user_id =%s'
            cursor.execute(increment_score_query, row)
            connection.commit()

    async def time_row_exists(self, chat_id):
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            check_time_file_query = 'SELECT last_time FROM contest_groups WHERE id=%s and last_time IS NOT NULL'
            result = cursor.execute(check_time_file_query, chat_id)
            # connection.commit()
            # print(result)
            return result

    async def truncate(self):
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            truncate_users = 'TRUNCATE TABLE users'
            truncate_scores = 'TRUNCATE TABLE scores'
            truncate_contest_groups = 'TRUNCATE TABLE contest_groups'
            cursor.execute(truncate_users)
            cursor.execute(truncate_scores)
            cursor.execute(truncate_contest_groups)
            connection.commit()

    async def create_time_file(self, chat_id: int, winner_id: int):
        connection = await self._get_connection()
        now = datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S:%f')

        row = (current_time, winner_id, chat_id)
        with connection.cursor() as cursor:
            create_time_file_query = "UPDATE contest_groups SET last_time=%s, winner_id=%s WHERE id=%s"
            cursor.execute(create_time_file_query, row)
            connection.commit()

    async def retrieve_time(self, chat_id: int):
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            time_file_read_query = 'SELECT last_time FROM contest_groups WHERE id=%s'
            cursor.execute(time_file_read_query, chat_id)
            rows = cursor.fetchone()
            connection.commit()
        return str(rows['last_time'])

    async def retrieve_last_winner(self, chat_id: int):
        connection = await self._get_connection()
        with connection.cursor() as cursor:
            time_file_read_query = 'SELECT users.username AS "winner_username", users.name AS "winner_name", users.id AS "id" ' \
                                   'FROM contest_groups ' \
                                   'JOIN users ON contest_groups.id=%s AND contest_groups.winner_id=users.id;'
            cursor.execute(time_file_read_query, chat_id)
            rows = cursor.fetchone()
            connection.commit()
        return str(rows['winner_username'] or rows['winner_name'])

    async def overwrite_row(self, target_user_id: int, new_username: str, new_name: str):
        connection = await self._get_connection()
        user = await self.check_user_data(target_user_id)
        if user['username'] != new_username or user['name'] != new_name:
            users_row = (new_username, new_name, target_user_id)
            with connection.cursor() as cursor:
                overwrite_rows_query = "UPDATE users SET username=%s, name=%s WHERE id=%s"
                cursor.execute(overwrite_rows_query, users_row)
                connection.commit()


storage = Storage()
