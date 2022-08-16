import csv
from pathlib import Path


from messages import PREFIX_DIRTY, PREFIX_SIMPLE, PREFIX_GENERAL, PREFIX_LORD

API_link = 'https://api.telegram.org/bot5431088637:AAF5c6G5TrsbMK5jzd-mf-5FdoRzFbYfRPc'
CHAT_ID = -769270882


class Storage:
    headers = ['id', 'username', 'score']

    def __init__(self, storage_file_name: str):
        self.storage_file_name = f'database/{storage_file_name}.csv'
        path = Path(f'database/{storage_file_name}.csv')

        if not path.exists():
            with path.open('w+', newline='') as database:  # Create storage if does not exist and add headers. Just open storage otherwise
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

    async def add_row(self, user_id: int, username: str):

        # list_of_participants.append(f'{user_id},{username}')

        with open(self.storage_file_name, mode='a') as database:
            file = database.write(f'{user_id},{username},{0}\n')

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

    async def increment_row(self, rows_list: list, winner_username: str):

        with open(self.storage_file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            for i in rows_list:
                if i[1] == winner_username:
                    i[2] = int(i[2]) + 1
                writer.writerow(i)
