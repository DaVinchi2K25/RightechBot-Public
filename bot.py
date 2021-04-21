import json
from multiprocessing.dummy import Process
from time import sleep

import telebot
import requests
from headers import headers

bot = telebot.TeleBot('');


def start_process():
    p1 = Process(target=send_msg, args=())
    p1.start()


def send_msg():
    last_msg_time = 0
    while True:
        contents = json.loads(
            requests.get("http://sandbox.rightech.io/api/v1/messages",
                         headers=headers).text)
        requests.delete("http://sandbox.rightech.io/api/v1/messages/clear", headers=headers)
        objects = json.loads(requests.get("http://sandbox.rightech.io/api/v1/objects/",
                                          headers=headers).text)
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
    if message.text == "/start":
        open('members.txt', 'a').write(str(message.from_user.id) + '\n')
        bot.send_message(message.from_user.id, "Бот активирован, все сообщения с платформы Rightech IoT будут "
                                               "пересылаться сюда, приятного использования")
    elif message.text == "/stop":
        members_w = ''
        members = open('members.txt', 'r').readlines()
        for member in members:
            if member.replace('\n', '') != str(message.from_user.id):
                members_w += member.replace('\n', '') + '\n'
        open('members.txt', 'w').write(members_w)
        bot.send_message(message.from_user.id, "Бот деактивирован")
    else:
        bot.send_message(message.from_user.id,
                         'Чтобы активировать бота напишите /start,\n чтобы деактивировать бота напишите /stop.')


start_process()
bot.polling(none_stop=False)
