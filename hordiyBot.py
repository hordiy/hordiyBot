import telebot
from telebot import types
import config
import datetime

greeting = ['здравствуй', 'привет', 'ку', 'здорово']
now = datetime.datetime.now()

bot = telebot.TeleBot(config.token)

@bot.message_handler(content_types=['text'])
def sendHello(message):

    if message.text.lower() in greeting and 6 <= now.hour < 12:
        bot.send_message(message.chat.id, 'Доброе утро, {}!'.format(message.chat.first_name))

    elif message.text.lower() in greeting and 12 <= now.hour < 17:
        bot.send_message(message.chat.id, 'Добрый день, {}!'.format(message.chat.first_name))

    elif message.text.lower() in greeting and 17 <= now.hour < 23:
        bot.send_message(message.chat.id, 'Добрый вечер, {}!'.format(message.chat.first_name))
    else:
        searchInfo(message)

def searchInfo(message):
    if message.text.lower() == 'поиск':
        keyboard = types.InlineKeyboardMarkup()
        url_google = types.InlineKeyboardButton(text='Перейти на "Google".', url='https://www.google.com/')
        url_youtube = types.InlineKeyboardButton(text='Перейти на "Youtube".', url='https://www.youtube.com/')
        keyboard.add(url_google, url_youtube)
        bot.send_message(message.chat.id, 'Нажми на одну из кнопок и перейди по ссылке.', reply_markup=keyboard)

if __name__ == "__main__":
    bot.polling(none_stop=True)
