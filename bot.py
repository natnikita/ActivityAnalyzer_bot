# -*- coding: utf-8 -*-

import telebot
from analytics import CourseAnalytics

# Токен вашего бота
TOKEN = '...'

# Создание экземпляра класса TeleBot
bot = telebot.TeleBot(TOKEN)

# Флаг для определения состояния бота (ожидание id курса или генерация отчета)
state = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет! Я бот для генерации отчетов по курсам. Чтобы сгенерировать отчет, используйте команду /generate_report")


@bot.message_handler(commands=['generate_report'])
def generate_report(message):
    state[message.chat.id] = 'waiting_for_course_id'
    bot.send_message(message.chat.id, "Введите id курса")


@bot.message_handler(commands=['end'])
def end(message):
    if message.chat.id in state:
        del state[message.chat.id]
    bot.send_message(message.chat.id, "Работа бота завершена")


@bot.message_handler(
    func=lambda message: message.chat.id in state and state[message.chat.id] == 'waiting_for_course_id')
def receive_course_id(message):
    course_id = message.text
    analytics = CourseAnalytics(course_id)
    analytics.to_html()
    report_path = analytics.get_report_path()
    with open(report_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    del state[message.chat.id]


# Запуск бота
bot.polling()
