from asyncio import sleep
from pathlib import Path
from datetime import datetime

import pymysql
from telegram import Update
from telegram.ext import ContextTypes

from config import host, user, db_name, password
from messages import ERROR_MSG

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
MAX_ATTEMPTS = 10

class Storage:
    headers = ['id', 'username', 'name', 'score']

    def __init__(self):
        self.path_start = Path('start.txt')
        # self.storage_file_name = f'database/{storage_file_name}.csv'
        # self.storage_time_file_name = f'database/{storage_file_name}-time.txt'
        # path = Path(self.storage_file_name)
        # if not path.exists():
        #     self._create_storage_file()

    # def _create_storage_file(self):
    #     """ Create storage if it does not exist and add headers. Just open storage otherwise """
    #     with open(self.storage_file_name, 'w', newline='') as database:
    #         writer = csv.DictWriter(database, fieldnames=self.headers)
    #         writer.writeheader()

    async def connect(self, attempt=0, update=Update, context= ContextTypes.DEFAULT_TYPE):
        if attempt > MAX_ATTEMPTS:
            await context.bot.send_message(chat_id=-719794843, text=ERROR_MSG)
        try:
            connection = pymysql.connect(
                host=host,
                port=3306,
                user=user,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            print('Success!')
            return connection
        except pymysql.OperationalError as ex:
            print(ex)
            await sleep(1)
            print('retrying...')
            return self.connect(attempt + 1)

    def start_msg_exists(self) -> bool:
        return self.path_start.exists()

    def start_message(self):
        with open(self.path_start, encoding='utf8') as f:
            start_text = f.read()
            return start_text

    def check_row_existance(self, chat_id: int, user_id: int):
        connection = self.connect()
        with connection.cursor() as cursor:
            select_query = 'select * from users'
            cursor.execute(select_query)
            participants_list = cursor.fetchall()
            for i in participants_list:
                if chat_id in i.values() and user_id in i.values():
                    return True

    async def add_row(self, chat_id: int, user_id: int, username: str, name: str):

        row = (chat_id, user_id, username, name, 0)
        connection = self.connect()
        with connection.cursor() as cursor:
            add_row_query = "INSERT INTO users VALUES(%s,%s,%s,%s, %s)"
            cursor.execute(add_row_query, row)
            connection.commit()

    def rows_exist(self, chat_id) -> bool:
        connection = self.connect()
        with connection.cursor() as cursor:
            rows_exist_query = 'SELECT * FROM users WHERE chat_id=%s'
            result = cursor.execute(rows_exist_query, chat_id)
            connection.commit()
            return result

    def retrieve_rows_list(self, chat_id) -> list:
        # with open(self.storage_file_name) as f:
        #     reader = csv.reader(f)
        #     data = list(reader)
        # return data
        connection = self.connect()
        with connection.cursor() as cursor:
            select_query = 'select * from users where chat_id=%s'
            cursor.execute(select_query, chat_id)
            participants_list = cursor.fetchall()
            connection.commit()
            return participants_list

    def check_participants(self, chat_id):
        connection = self.connect()
        with connection.cursor() as cursor:
            check_participants_query = 'SELECT * FROM users WHERE chat_id=%s'
            participants_exist = cursor.execute(check_participants_query, chat_id)
        return participants_exist

    async def increment_row(self, chat_id, winner_id: int):

        # for chat_id, user_id, username, name, score in rows_list:
        # if user_id == winner_id:
        #     score = int(score) + 1
        row = (chat_id, winner_id)
        connection = self.connect()
        with connection.cursor() as cursor:
            increment_score_query = 'UPDATE users SET score = score + 1 WHERE chat_id = %s AND user_id =%s'
            cursor.execute(increment_score_query, row)
            connection.commit()

    def time_row_exists(self, chat_id):
        connection = self.connect()
        with connection.cursor() as cursor:
            check_time_file_query = 'SELECT * FROM contest_groups WHERE chat_id=%s'
            result = cursor.execute(check_time_file_query, chat_id)
            connection.commit()

            return result

    def truncate(self):
        connection = self.connect()
        with connection.cursor() as cursor:
            truncate_users = 'TRUNCATE TABLE users'
            truncate_time = 'TRUNCATE TABLE contest_groups'
            cursor.execute(truncate_time)
            cursor.execute(truncate_users)
            connection.commit()

    def create_time_file(self, chat_id: int, winner_name):
        now = datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S:%f')

        row = (chat_id, current_time, winner_name)
        connection = self.connect()
        with connection.cursor() as cursor:
            create_time_file_query = "INSERT INTO contest_groups VALUES(%s, %s, %s)"
            cursor.execute(create_time_file_query, row)
            connection.commit()

    def time_file_read(self, chat_id):
        connection = self.connect()
        with connection.cursor() as cursor:
            time_file_read_query = 'SELECT last_time FROM contest_groups WHERE chat_id=%s'
            cursor.execute(time_file_read_query, chat_id)
            rows = cursor.fetchone()
            connection.commit()
        return str(rows['last_time'])

    async def overwrite_row(self, target_user_id: int, new_username: str, new_name: str):
        connection = self.connect()
        row2overwrite = (new_username, new_name, target_user_id)
        with connection.cursor() as cursor:
            add_row_query = "UPDATE users SET username=%s, name=%s WHERE user_id=%s"
            cursor.execute(add_row_query, row2overwrite)
            connection.commit()
