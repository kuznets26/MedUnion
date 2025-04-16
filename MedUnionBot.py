import telebot
from telebot import types
from enum import Enum

# State management for conversations
class UserState(Enum):
    IDLE = 0
    SEEKING_JOB = 1
    HIRING = 2

# Initialize bot and user states
import os

API_TG = os.getenv("API_TG")
bot = telebot.TeleBot(API_TG)
user_states = {}
user_data = {}

# Create main menu keyboard
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Ищу работу"))
    keyboard.add(types.KeyboardButton("Ищу сотрудника"))
    return keyboard

# --- ДЛЯ СОИСКАТЕЛЯ ---

def ask_specialization(message):
    user_id = message.from_user.id
    user_states[user_id] = UserState.SEEKING_JOB
    user_data[user_id] = {}
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Какая у вас специализация?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_experience)

def ask_experience(message):
    user_id = message.from_user.id
    user_data[user_id]['experience'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Меньше 1 года"), types.KeyboardButton("Больше 1 года"))
    markup.add(types.KeyboardButton("Больше трех лет"))
    bot.send_message(message.chat.id, "Какой у вас опыт?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_schedule)

def ask_schedule(message):
    user_id = message.from_user.id
    user_data[user_id]['specialization'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("5/2"), types.KeyboardButton("2/2"))
    markup.add(types.KeyboardButton("Посменно"))
    bot.send_message(message.chat.id, "Какой график работы вы предпочитаете?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_rate)

def ask_rate(message):
    user_id = message.from_user.id
    user_data[user_id]['schedule'] = message.text
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Какая минимальная ставка за смену вас интересует (напишите значение в рублях)?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_platform)

def ask_platform(message):
    user_id = message.from_user.id
    user_data[user_id]['rate'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    bot.send_message(message.chat.id, "Готовы ли вы работать через платформу?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_city_seeker)

def ask_city_seeker(message):
    user_id = message.from_user.id
    user_data[user_id]['rate'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Москва"), types.KeyboardButton("Санкт-Петербург"))
    markup.add(types.KeyboardButton("Новосибирск"), types.KeyboardButton("Екатеринбург"))
    markup.add(types.KeyboardButton("Казань"), types.KeyboardButton("Нижний Новгород"))
    bot.send_message(message.chat.id, "Из какого вы города?", reply_markup=markup)
    bot.register_next_step_handler(message, process_job_seeker_data)

def process_job_seeker_data(message):
    user_id = message.from_user.id
    user_data[user_id]['platform'] = message.text
    bot.send_message(message.chat.id, "Спасибо за информацию! Мы обработаем ваш запрос.", 
                     reply_markup=create_main_keyboard())
    user_states[user_id] = UserState.IDLE


# --- ДЛЯ РАБОТОДАТЕЛЯ ---

def ask_specialist_type(message):
    user_id = message.from_user.id
    user_states[user_id] = UserState.HIRING
    user_data[user_id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Медсестра"), types.KeyboardButton("Сиделка"))
    markup.add(types.KeyboardButton("Врач"))
    bot.send_message(message.chat.id, "Какой специалист вам нужен?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_work_schedule)

def ask_work_schedule(message):
    user_id = message.from_user.id
    user_data[user_id]['specialist_type'] = message.text
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Какой график работы предлагаете? (укажите смены и часы)", reply_markup=markup)
    bot.register_next_step_handler(message, ask_requirements)

def ask_requirements(message):
    user_id = message.from_user.id
    user_data[user_id]['work_schedule'] = message.text
    bot.send_message(message.chat.id, "Какие требования к опыту работы и сертификатам?")
    bot.register_next_step_handler(message, ask_commission)

def ask_commission(message):
    user_id = message.from_user.id
    user_data[user_id]['requirements'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    bot.send_message(message.chat.id, "Готовы ли вы платить комиссию за подбор специалиста?", reply_markup=markup)
    bot.register_next_step_handler(message, process_employer_data)

def process_employer_data(message):
    user_id = message.from_user.id
    user_data[user_id]['commission'] = message.text
    bot.send_message(message.chat.id, "Спасибо за информацию! Мы обработаем ваш запрос.",
                     reply_markup=create_main_keyboard())
    user_states[user_id] = UserState.IDLE


# --- ОБРАБОТКА СООБЩЕНИЙ ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Добрый день! Чем могу помочь?", reply_markup=create_main_keyboard())
    user_states[message.from_user.id] = UserState.IDLE

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    user_id = message.from_user.id

    if text == "ищу работу":
        ask_specialization(message)
    elif text == "ищу сотрудника":
        ask_specialist_type(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите вариант на клавиатуре.", reply_markup=create_main_keyboard())


import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet_job_seekers = client.open("MedUnion").worksheet("Job Seekers")
sheet_employers = client.open("MedUnion").worksheet("Employers")

def process_job_seeker_data(message):
    user_id = message.from_user.id
    user_data[user_id]['platform'] = message.text

    try:
        sheet_job_seekers.append_row([
            message.from_user.first_name,
            message.from_user.last_name,
            str(user_id),
            user_data[user_id].get('specialization', ''),
            user_data[user_id].get('experience', ''),
            user_data[user_id].get('schedule', ''),
            user_data[user_id].get('rate', ''),
            user_data[user_id].get('platform', ''),
            user_data[user_id].get('city', '')
        ])
        bot.send_message(message.chat.id, "Спасибо за информацию! Мы обработаем ваш запрос.",
                         reply_markup=create_main_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении в таблицу: {e}")
    
    user_states[user_id] = UserState.IDLE

def process_employer_data(message):
    user_id = message.from_user.id
    user_data[user_id]['commission'] = message.text

    try:
        sheet_employers.append_row([
            message.from_user.first_name,
            message.from_user.last_name,
            str(user_id),
            user_data[user_id].get('specialist_type', ''),
            user_data[user_id].get('work_schedule', ''),
            user_data[user_id].get('requirements', ''),
            user_data[user_id].get('commission', '')
        ])
        bot.send_message(message.chat.id, "Спасибо за информацию! Мы обработаем ваш запрос.",
                         reply_markup=create_main_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении в таблицу: {e}")
    
    user_states[user_id] = UserState.IDLE

if __name__ == '__main__':
    bot.polling(none_stop=True)
