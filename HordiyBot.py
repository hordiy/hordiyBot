#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytz
import telebot
from telebot.apihelper import ApiException

import config

bot = telebot.TeleBot(config.TOKEN)

help_message_string_en = '''
This bot was developed to backup your data from groups in your private message with bot. 
1. You should add bot to group. 
2. The command /backup gives bot task to backup data. You will receive a message from bot and after that 
you will need to attach your data.
3. You will receive a backup in a private message (Attention, you can get backup if you have role Admin or Creator)
'''

help_message_string_ru = '''
Бот был разработан для резервного копирования ваших данных из групп в личном сообщении с ботом. 
1. Вам следует добавить бота в группу. 
2. Команда /backup дает задание боту для резервного копирования данных. Вы получите сообщение от бота и после этого вам нужно будет добавить ваши данные. 
3. Вы получите резервную копию в личном сообщении (Внимание, вы можете получить резервную копию, если у вас есть роль Админ или Создатель) '''


def message_lang(language_code, string_ru, string_en):
    if language_code == 'ru':
        return string_ru
    else:
        return string_en


@bot.message_handler(commands=['start'])
def start_message(message):
    msg = message_lang(message.from_user.language_code, help_message_string_ru, help_message_string_en)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['help'])
def help_message(message):
    msg = message_lang(message.from_user.language_code, help_message_string_ru, help_message_string_en)
    bot.send_message(message.chat.id, msg)


# BackUp Photo to private massage
@bot.message_handler(commands=['backup'])
def handle_docs_photo(message):
    msg_lang = message_lang(message.from_user.language_code, 'Добавьте ваши данные', 'Attach you data')
    msg = bot.send_message(message.chat.id, msg_lang)
    bot.register_next_step_handler(msg, forward_message_for_users)


@bot.message_handler(content_types=['text'])
def print_message(message):
    import datetime
    print("{time}: {first_name} {last_name} ==> {message}".format(first_name=message.from_user.first_name,
                                                                  last_name=message.from_user.last_name,
                                                                  message=message.text,
                                                                  time=datetime.datetime.now(
                                                                      pytz.timezone("Europe/Kiev"))))


def forward_message_for_users(message):
    members = bot.get_chat_administrators(message.chat.id)
    print(bot.get_chat_members_count(message.chat.id))
    for member in members:
        try:
            bot.forward_message(member.user.id, message.chat.id, message.message_id)
        except ApiException:
            continue


if __name__ == '__main__':
    bot.infinity_polling(True)
