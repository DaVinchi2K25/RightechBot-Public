import json
from multiprocessing.dummy import Process
from time import sleep

import telebot
import requests
from headers import headers  # получение из файла headers.py заголовков для работы с API Rightech IoT

bot = telebot.TeleBot('1781434104:AAHH-jK64eMbNmW72_f_Fln77xNz0-VeCzA')  # инициализация бота с токеном


def start_process():
    p1 = Process(target=send_msg, args=())
    p1.start()


def send_msg():
    last_msg_time = 0
    while True:
        contents = json.loads(
            requests.get("http://sandbox.rightech.io/api/v1/messages",
                         headers=headers).text) # получение списка сообщений
        requests.delete("http://sandbox.rightech.io/api/v1/messages/clear", headers=headers) # очистка списка сообщений
        objects = json.loads(requests.get("http://sandbox.rightech.io/api/v1/objects/",
                                          headers=headers).text) # получение списка объектов
        if contents:
            if last_msg_time != int(contents[0]['time']):
                last_msg_time = int(contents[0]['time'])
                for message in contents:
                    for object in objects:
                        if object['_id'] == message['id']:
                            s_msg = object['name'] + "\n"
                    if message['importance'] == 'critical':
                        s_msg += "!<b>Критическое</b>!"
                    elif message['importance'] == 'important':
                        s_msg += "<b>Важное</b>"
                    else:
                        s_msg += "<b>Информационное</b>"
                    s_msg += "\n" + message['message-body']
                    members = open('members.txt')
                    while True:
                        user = members.readline()
                        if not user: break
                        bot.send_message(user, s_msg, parse_mode="HTML")
        sleep(1)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    elif message.text == "/start":
        open('members.txt', 'a').write(str(message.from_user.id) + '\n')
        bot.send_message(message.from_user.id, "Бот активирован, все сообщения с платформы Rightech IoT будут "
                                               "пересылаться сюда, приятного использования")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


start_process()
bot.polling(none_stop=False)
