import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage 
from telebot import types

# Инициализация бота
state_storage = StateMemoryStorage()
bot = telebot.TeleBot('YOUR_BOT_TOKEN', state_storage=state_storage)

# Состояния бота
class AdminStates(StatesGroup):
    waiting_for_action = State()
    waiting_for_user = State()
    waiting_for_time = State()

# Словарь для хранения администраторов
admins = {'admin_id_1', 'admin_id_2'} 

# Функция проверки на админа
def is_admin(user_id):
    return str(user_id) in admins

# Стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    if is_admin(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Забанить', 'Разбанить', 'Удалить сообщение', 'Закрепить сообщение')
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)
        bot.set_state(message.from_user.id, AdminStates.waiting_for_action, message.chat.id)
    else:
        bot.reply_to(message, 'У вас нет прав администратора')

# Обработка выбора действия
@bot.message_handler(state=AdminStates.waiting_for_action)
def handle_action(message):
    if message.text == 'Забанить':
        bot.send_message(message.chat.id, 'Укажите ID пользователя для бана:')
        bot.set_state(message.from_user.id, AdminStates.waiting_for_user, message.chat.id)
        
    elif message.text == 'Разбанить':
        bot.send_message(message.chat.id, 'Укажите ID пользователя для разбана:')
        bot.set_state(message.from_user.id, AdminStates.waiting_for_user, message.chat.id)
        
    elif message.text == 'Удалить сообщение':
        bot.send_message(message.chat.id, 'Ответьте на сообщение, которое нужно удалить')
        
    elif message.text == 'Закрепить сообщение':
        bot.send_message(message.chat.id, 'Ответьте на сообщение, которое нужно закрепить')

# Обработка бана/разбана
@bot.message_handler(state=AdminStates.waiting_for_user)
def handle_user_action(message):
    try:
        user_id = int(message.text)
        action = bot.get_state(message.from_user.id, message.chat.id)
        
        if action == 'Забанить':
            bot.ban_chat_member(message.chat.id, user_id)
            bot.send_message(message.chat.id, f'Пользователь {user_id} забанен')
        else:
            bot.unban_chat_member(message.chat.id, user_id)
            bot.send_message(message.chat.id, f'Пользователь {user_id} разбанен')
            
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {str(e)}')
    
    bot.delete_state(message.from_user.id, message.chat.id)

# Обработка удаления сообщений
@bot.message_handler(content_types=['text'], func=lambda message: message.reply_to_message)
def delete_message(message):
    if is_admin(message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.reply_to_message.message_id)
            bot.send_message(message.chat.id, 'Сообщение удалено')
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка при удалении: {str(e)}')

# Обработка закрепления сообщений  
@bot.message_handler(content_types=['text'], func=lambda message: message.reply_to_message)
def pin_message(message):
    if is_admin(message.from_user.id):
        try:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            bot.send_message(message.chat.id, 'Сообщение закреплено')
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка при закреплении: {str(e)}')

# Запуск бота
bot.polling(none_stop=True)