import csv
from pathlib import Path
from datetime import datetime

from messages import PREFIX_DIRTY, PREFIX_SIMPLE, PREFIX_GENERAL, PREFIX_LORD

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
CHAT_ID = -769270882


class Storage:
    headers = ['id', 'username', 'name', 'score']

    def __init__(self, storage_file_name: int):
        self.storage_file_name = f'database/{storage_file_name}.csv'
        self.storage_time_file_name = f'database/{storage_file_name}-time.txt'
        path = Path(f'database/{storage_file_name}.csv')

        if not path.exists():
            with open(self.storage_file_name, 'w+',
                           newline='') as database:  # Create storage if does not exist and add headers. Just open storage otherwise
                writer = csv.DictWriter(database, fieldnames=self.headers)
                writer.writeheader()

    def start_msg_exists(self):
        path_start = Path('start.txt')
        return path_start.exists()

    def start_message(self):

        with open('start.txt', encoding='utf8') as f:
            start = f.read()
            return start

    def check_row_existance(self, user_id: int):
        with open(self.storage_file_name, 'r') as list_of_participants_file:
            user_in_db = str(user_id) in list_of_participants_file.read()
            return user_in_db

    async def add_row(self, user_id: int, username: str, name: str):

        # list_of_participants.append(f'{user_id},{username}')

        with open(self.storage_file_name, mode='a') as database:
            file = database.write(f'{user_id},{username},{name},{0}\n')

        # print(list_of_participants)
        # with open('database/database.csv', mode='r') as database:
        #     print(database.readlines())
        # list_of_participants.append(username)

    def rows_exist(self) -> bool:
        with open(self.storage_file_name) as f:
            reader = csv.reader(f)
            data = list(reader)
        return len(data) > 1

    def rows_list(self) -> list:
        with open(self.storage_file_name) as f:
            reader = csv.reader(f)
            data = list(reader)
        return data

    async def increment_row(self, rows_list: list, winner_id: int):

        with open(self.storage_file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            for i in rows_list:
                if i[0] == winner_id:
                    i[3] = int(i[3]) + 1
                writer.writerow(i)

    def time_file_exists(self):
        path = Path(self.storage_time_file_name)
        return path.exists()

    def create_time_file(self):

        with open(f'{self.storage_time_file_name}', 'w') as timefile:
            now = datetime.now()
            current_time = now.strftime('%Y-%m-%d %H:%M:%S:%f')
            # current_time_list = current_time.split()
            # print(current_time_list)
            # print(split)
            writer = timefile.write(current_time)

    def time_file_read(self):
        with open(f'{self.storage_time_file_name}') as timefile:
            time_file_reader = timefile.read()
            print(time_file_reader)
            # time_file_list = list(time_file_reader)[0]
        return time_file_reader

    async def overwrite_row(self, rows_list: list, user_id: int, username: str, name: str):
        user_id = str(user_id)
        with open(self.storage_file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            for i in rows_list:
                if i[0] == user_id and (username != i[1] or name != i[2]):
                    i[1] = username
                    i[2] = name
                writer.writerow(i)
