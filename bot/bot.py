import os
import time
import utils
import telebot
from db import Connect
from multiprocessing import Process

bot = telebot.TeleBot(os.environ.get('token'))


@bot.message_handler(commands=['start'])
def start(message):
    response = utils.collect()
    if response.get('error'):
        return bot.send_message(chat_id=message.chat.id, text='Error: {}'.format(response['error']))
    text = '\n'.join([f'{i}: {j}%' for i, j in response.items()])
    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=['users'], func=lambda m: m.chat.id == 0)
def get_all_users(message):
    conn = Connect()
    users = conn.get_users()
    conn.close_connection()
    bot.send_message(chat_id=message.chat.id, text='\n'.join(map(str, users)))


@bot.message_handler(commands=['add'], func=lambda m: m.chat.id == 538729400)
def add_user(message):
    user_data = message.text.split(maxsplit=1)
    if len(user_data) == 2 and user_data[1].isdigit():
        conn = Connect()
        conn.insert_user(int(user_data[1]))
        conn.close_connection()
        bot.send_message(chat_id=message.chat.id, text='Пользователь добавлен')


@bot.message_handler(commands=['delete'], func=lambda m: m.chat.id == 538729400)
def delete_user(message):
    user_data = message.text.split(maxsplit=1)
    if len(user_data) == 2 and user_data[1].isdigit():
        conn = Connect()
        conn.delete_user(int(user_data[1]))
        conn.close_connection()
        bot.send_message(chat_id=message.chat.id, text='Пользователь удалён')


@bot.message_handler(commands=['step'], func=lambda m: m.chat.id == 538729400)
def change_step(message):
    conn = Connect()
    user_data = message.text.split(maxsplit=1)
    if len(user_data) == 2 and user_data[1].isdigit():
        conn.set_step(user_data[1])
        bot.send_message(chat_id=message.chat.id, text='Шаг изменён')
    conn.close_connection()


@bot.message_handler(commands=['proc'], func=lambda m: m.chat.id == 538729400)
def change_percentage(message):
    conn = Connect()
    user_data = message.text.split(maxsplit=1)
    if len(user_data) == 2 and user_data[1].isdigit():
        conn.set_percentage(user_data[1])
        bot.send_message(chat_id=message.chat.id, text='Процент изменён')
    conn.close_connection()


def notify(message):
    conn = Connect()
    users = conn.get_users()
    conn.close_connection()
    for i in users:
        bot.send_message(chat_id=i, text=message)
        time.sleep(0.5)


if __name__ == '__main__':
    worker = Process(target=utils.run_collecting)
    worker.start()
    bot.polling(none_stop=True, timeout=1000)
