import os
from urllib import parse
import psycopg2


class Connect:
    def __init__(self):
        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def set_step(self, step):
        self.cursor.execute("UPDATE settings SET step = %s", (step,))

    def set_percentage(self, value):
        self.cursor.execute('UPDATE settings SET proc = %s', (value,))

    def insert_user(self, user_id):
        if user_id not in self.get_users():
            self.cursor.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))

    def delete_user(self, user_id):
        if user_id in self.get_users():
            self.cursor.execute("DELETE from users WHERE user_id = %s", (user_id,))

    def get_users(self):
        self.cursor.execute("SELECT * FROM users")
        result = self.cursor.fetchall()
        return [x[0] for x in result]

    def get_step(self):
        self.cursor.execute("SELECT step FROM settings")
        result = self.cursor.fetchall()
        return result[0][0]

    def get_percentage(self):
        self.cursor.execute("SELECT proc FROM settings")
        result = self.cursor.fetchall()
        return result[0][0]

    def close_connection(self):
        self.connection.close()
