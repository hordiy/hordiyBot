#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random
import config
import telebot
from telebot import types
import requests
import re
import json
from bs4 import BeautifulSoup
import datetime
import pytz
import pyowm
from typing import List
import detection

bot = telebot.TeleBot(config.TOKEN)

# Class for parsing weather
class Weather:

	def __init__(self):
		self.owm = pyowm.OWM("a53a2754ece8267b620ebf100d39617f", language="ru")
		self.observation = self.owm.weather_at_place("Kharkiv")
		self.w = self.observation.get_weather()
		self.temp: float = self.w.get_temperature("celsius")["temp"]
	
	def weather(self, message: str) -> str:

		#place = input("City/Country: ")
		bot.send_message(message.chat.id, "В городе {} сейчас {}".format("Харьков", self.w.get_detailed_status()))
		bot.send_message(message.chat.id, "Температура в районе " + str(self.temp))
		
		if self.temp < 10:
			bot.send_message(message.chat.id, "Сейчас очень холодно, одевайся!")
		elif self.temp < 20:
			bot.send_message(message.chat.id, "Холодно, одевайся потеплее.")
		else:
			bot.send_message(message.chat.id, "Температура норм, надевай что угодно.")

# Class for select search 'google' or 'youtube'
class Search:

	def searchInfo(self, message: str) -> str:
		keyboard = types.InlineKeyboardMarkup()
		keyboard.row(
				types.InlineKeyboardButton(text='Перейти на "Google".', url='https://www.google.com/')
			)
		keyboard.row(
				types.InlineKeyboardButton(text='Перейти на "Youtube".', url='https://www.youtube.com/')
			)
		bot.send_message(message.chat.id, 'Нажми на одну из кнопок и перейди по ссылке.', reply_markup=keyboard)

# Class for parsing currency
class Currency:

	@staticmethod
	def load_exchange():  
	    return json.loads(requests.get(config.URL).text)  

	@staticmethod
	def get_exchange(ccy_key: int) -> bool:
		for exc in Currency.load_exchange():
			if ccy_key == exc['ccy']:
				return exc
		return False

	def get_exchanges(self, ccy_pattern):
		result = []
		ccy_pattern = re.escape(ccy_pattern) + '.*'
		for exc in Currency.load_exchange():
			if re.metch(ccy_pattern, exc['ccy'], re.IGNORECASE) is not None:
				result.append(exc)
		return result

	def exchange(self, message: str) -> str:
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
				telebot.types.InlineKeyboardButton('USD', callback_data='get-USD'),
				telebot.types.InlineKeyboardButton('EUR', callback_data='get-EUR'),
				telebot.types.InlineKeyboardButton('RUR', callback_data='get-RUR')
			)
		bot.send_message(message.chat.id, 'Выбери курс валют:', reply_markup=keyboard)

class Game:

	def __init__(self):
		self.figures: List[str] = ["камень", "бумага", "ножницы"]

	def generate_markup(self) -> str:
	    markup = types.ReplyKeyboardMarkup(row_width=3)
	    markup.row("Камень", "Бумага", "Ножницы")
	    return markup

	def generate_figure(self) -> int:
	    return random.sample(self.figures, 1)

	def define_winner(self, message: str) -> str:
		answer, reply = message.text.lower(), self.generate_figure()[0]
		status = self.figures.index(answer) - self.figures.index(reply)
		responses: List[str] = ['Ничья :d', 'Твоя победа :)', 'Твой проигрыш :(']
		bot.send_message(message.chat.id,
			'HordiyBot: ' + reply.title() + '\nvs \n' + message.from_user.first_name + ': ' +
			answer.title() + '\n' + responses[status])

# Main class with inheritance of other classes
class Main(Weather, Currency, Search, Game):
	
	def __init__(self):
		Weather.__init__(self)
		Game.__init__(self)
		self.GREETING: List[str] = ['здравствуй', 'привет', 'ку', 'здорово']
		self.now: int = datetime.datetime.now(pytz.timezone("Europe/Kiev"))

	def sayHello(self, message: str) -> str:
		if message.text.lower() in self.GREETING and 6 <= self.now.hour < 12:
			bot.send_message(message.chat.id, 'Доброе утро, {}'.format(message.from_user.first_name))
		elif message.text.lower() in self.GREETING and 12 <= self.now.hour < 17:
			bot.send_message(message.chat.id, 'Добрый день, {}'.format(message.from_user.first_name))
		elif message.text.lower() in self.GREETING and 17 <= self.now.hour < 23:
			bot.send_message(message.chat.id, 'Добрый вечер, {}'.format(message.from_user.first_name))
		else:
			bot.send_message(message.chat.id, 'Доброй ночи, {}'.format(message.from_user.first_name))			

# BackUp Photo to other group
@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message: str) -> str:
    try:
      
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
      
        bot.forward_message(-1001230103900, message.chat.id, message.message_id)
        bot.reply_to(message,"Фото добавлено")
         
        src= file_info.file_path;
        with open(src, 'wb') as new_file:
           new_file.write(downloaded_file)
        detection.face_recong(src)
        photo = open('image_with_boxes.jpg', 'rb')

        bot.send_photo(message.chat.id, photo)
    except Exception as e:
        bot.reply_to(message, e)
  

# Main method for text
@bot.message_handler(content_types=['text'])
def main(message: str) -> str:
	superMain = Main()
	print(message.chat.id)
	print("{time}: {first_name} {last_name} ==> {message}".format(first_name=message.from_user.first_name,  
														   last_name=message.from_user.last_name, 
														   message=message.text,
														   time=superMain.now))
	if message.text.lower() in superMain.GREETING:
		superMain.sayHello(message)
	elif message.text.lower() == 'курс':
		superMain.exchange(message)
	elif message.text.lower() == 'погода':
		superMain.weather(message)
	elif message.text.lower() == 'поиск':
		superMain.searchInfo(message)
	elif message.text.lower() == 'игра':
		bot.send_message(message.chat.id,
                     'Выбери одно из трех:',
                     reply_markup=superMain.generate_markup())
	elif message.text.lower() in superMain.figures:
		superMain.define_winner(message)		

# Method for query
@bot.callback_query_handler(func=lambda call: True)  
def iq_callback(query):  
    data = query.data  
    if data.startswith('get-'):  
        get_ex_callback(query)

def get_ex_callback(query):  
	    bot.answer_callback_query(query.id)  
	    send_exchange_result(query.message, query.data[4:])

def send_exchange_result(message: str, ex_code: int) -> str:  
    bot.send_chat_action(message.chat.id, 'typing')  
    ex = Currency.get_exchange(ex_code)  
    bot.send_message(  
        message.chat.id, serialize_ex(ex),  
	parse_mode='HTML'  
    )

def serialize_ex(ex_json, diff=None) -> str:  
	result = '<b>' + ex_json['base_ccy'] + ' -> ' + ex_json['ccy'] + ':</b>\n\n' + 'Buy: ' + ex_json['buy']  
	if diff:  
	    result += ' ' + serialize_exchange_diff(diff['buy_diff']) + '\n' + 'Sell: ' + ex_json['sale'] + ' ' + serialize_exchange_diff(diff['sale_diff']) + '\n'  
	else:  
	    result += '\nSell: ' + ex_json['sale'] + '\n'  
	return result


def serialize_exchange_diff(diff: int) -> str:  
    result = ''  
    if diff > 0:  
        result = '(' + str(diff) + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="↗️" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/72x72/2197.png">" src="https://s.w.org/images/core/emoji/72x72/2197.png">)'  
    elif diff < 0:  
        result = '(' + str(diff)[1:] + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="↘️" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/72x72/2198.png">" src="https://s.w.org/images/core/emoji/72x72/2198.png">)'  
    return result


if __name__ == '__main__':
	bot.infinity_polling(True)
	#bot.polling(none_stop=True) 	