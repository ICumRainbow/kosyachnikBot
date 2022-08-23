import csv
from pathlib import Path
from datetime import datetime
import pymysql
from pprint import pprint

from config import host, user, db_name, password

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
CHAT_ID = -769270882


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

    # try:
        # cursor = connection.cursor()

        # create table
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE 'users'(id int"

except Exception as ex:
    print('FAIL')
    print(ex)




class Storage:
    headers = ['id', 'username', 'name', 'score']

    def __init__(self, storage_file_name: int):
        self.storage_file_name = f'database/{storage_file_name}.csv'
        self.storage_time_file_name = f'database/{storage_file_name}-time.txt'
        path = Path(self.storage_file_name)

        if not path.exists():
            self._create_storage_file()

    def _create_storage_file(self):
        """ Create storage if it does not exist and add headers. Just open storage otherwise """
        with open(self.storage_file_name, 'w', newline='') as database:
            writer = csv.DictWriter(database, fieldnames=self.headers)
            writer.writeheader()

    def start_msg_exists(self) -> bool:
        path_start = Path('start.txt')
        return path_start.exists()

    def start_message(self):
        with open('start.txt', encoding='utf8') as f:
            start = f.read()
            return start

    def check_row_existance(self, chat_id: int, user_id: int):
        # with open(self.storage_file_name, 'r') as list_of_participants_file:
        #     user_in_db = str(user_id) in list_of_participants_file.read()
        #     return user_in_db
        with connection.cursor() as cursor:
            select_query = 'select * from users'
            cursor.execute(select_query)
            participants_list = cursor.fetchall()
            for i in participants_list:
                if chat_id in i.values() and user_id in i.values():
                    return True

    async def add_row(self, chat_id: int, user_id: int, username: str, name: str):

        # list_of_participants.append(f'{user_id},{username}')
        #coding: utf-8
        # with open(self.storage_file_name, mode='a', encoding='utf-8') as database:
        #     database.write(f'{user_id},{username},{name},0\n')
        row = (chat_id, user_id, username, name, 0)
        with connection.cursor() as cursor:
            add_row_query = "INSERT INTO `users` VALUES(%s,%s,%s,%s, %s)"
            cursor.execute(add_row_query, row)
            connection.commit()
        # print(list_of_participants)
        # with open('database/database.csv', mode='r') as database:
        #     print(database.readlines())
        # list_of_participants.append(username)

    def rows_exist(self, chat_id) -> bool:
        with connection.cursor() as cursor:
            rows_exist_query = 'SELECT * FROM users WHERE chat_id=%s'

            result = cursor.execute(rows_exist_query, chat_id)
            connection.commit()
            return result

    def rows_list(self, chat_id) -> list:
        # with open(self.storage_file_name) as f:
        #     reader = csv.reader(f)
        #     data = list(reader)
        # return data
        with connection.cursor() as cursor:
            select_query = 'select * from users where chat_id=%s'
            cursor.execute(select_query, chat_id)
            participants_list = cursor.fetchall()
            connection.commit()
            return participants_list

    def check_participants(self, chat_id):
        with connection.cursor() as cursor:
            check_participants_query = 'SELECT * FROM users WHERE chat_id=%s'

            return cursor.execute(check_participants_query, chat_id)

    async def increment_row(self, chat_id, winner_id: int):


            # for chat_id, user_id, username, name, score in rows_list:
                # if user_id == winner_id:
                #     score = int(score) + 1
            row = (chat_id, winner_id)
            with connection.cursor() as cursor:
                increment_score_query = 'UPDATE `users` SET score = score + 1 WHERE chat_id = %s AND user_id =%s'
                cursor.execute(increment_score_query, row)
                connection.commit()


    def time_file_exists(self, chat_id):

        with connection.cursor() as cursor:
            check_participants_query = 'SELECT * FROM time_db WHERE chat_id=%s'

            result = cursor.execute(check_participants_query, chat_id)
            connection.commit()
            return result
    def truncate(self):
        with connection.cursor() as cursor:
            truncate_users = 'TRUNCATE TABLE users'
            truncate_time = 'TRUNCATE TABLE time_db'

            cursor.execute(truncate_time)
            cursor.execute(truncate_users)
            connection.commit()
    def create_time_file(self, chat_id: int):
        now = datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S:%f')

        # with open(self.storage_time_file_name, 'w') as timefile:
        #     # current_time_list = current_time.split()
        #     # print(current_time_list)
        #     # print(split)
        #     timefile.write(current_time)
        row = (chat_id, current_time)
        with connection.cursor() as cursor:
            create_time_file_query = "INSERT INTO `time_db` VALUES(%s, %s)"
            cursor.execute(create_time_file_query, row)
            connection.commit()


    def time_file_read(self, chat_id):
        with connection.cursor() as cursor:
            time_file_read_query = 'SELECT last_time FROM time_db WHERE chat_id=%s'
            cursor.execute(time_file_read_query, chat_id)
            rows = cursor.fetchone()
            connection.commit()
        return str(rows['last_time'])

    async def overwrite_row(self, target_user_id: int, new_username: str, new_name: str):
        row2overwrite = (new_username, new_name, target_user_id)
        with connection.cursor() as cursor:
            add_row_query = "UPDATE `users` SET username=%s, name=%s WHERE user_id=%s"
            cursor.execute(add_row_query, row2overwrite)
            connection.commit()