import time
import sqlite3 as sq
import telebot as tel
from telebot import types as t

bot = tel.TeleBot('YOUR_API_TOKEN')

#Создание бд бота
def create_table():
    with sq.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Users(
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        balance_pumpkin INTEGER,
                        price_per_click INTEGER
                    )''')
        con.commit()


#Проверка существования юзера
def user_exists(username):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Users WHERE username=?", (username,))
        result = cur.fetchone()
        return result is not None


#Обработчик начала общения с ботом юзера
@bot.message_handler(commands=['start'])
def start(message):
    global username,user_id
    markup_start=t.ReplyKeyboardMarkup(row_width=1)
    play=t.KeyboardButton(text='Играть')
    support=t.KeyboardButton(text='Позвать техсаппорта')
    help=t.KeyboardButton(text='Помощь по командам')
    markup_start.add(help,support,play)
    create_table()
    user_id = message.from_user.id
    username = message.from_user.username
    balance_pumpkin=0
    if user_exists(username):
        bot.send_message(message.chat.id, "Здравствуй,"+username+",выбери действие",reply_markup=markup_start)
    else:
        with sq.connect('users.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Users(user_id,username,balance_pumpkin,price_per_click) VALUES(?,?,?,10)", (user_id,username,balance_pumpkin))
            con.commit()
            bot.send_message(message.chat.id, f"Привет, {username}! Ты добавлен в базу данных.")
            

#Обработчики просьбы о помощи от юзера
@bot.message_handler(commands=['support'])
def support_frim_command(message):
    bot.send_message(message.chat.id,f"Здравствуй,"+username+",свяжись пожалуйста с разработчиком по твоему вопросу @Oleg9770")

@bot.message_handler(func=lambda message:message.text=='Позвать техсаппорта')
def support_from_button(message):
    bot.send_message(message.chat.id,f"Здравствуй,"+username+",свяжись пожалуйста с разработчиком по твоему вопросу @Oleg9770")


#Обработчики просьбы юзера показать список комманд
@bot.message_handler(commands=['help'])
def help_from_command(message):
    bot.send_message(message.chat.id,'Здравствуй,'+username+',вот список команд')
    bot.send_message(message.chat.id,'/help-Помощь по командам')
    bot.send_message(message.chat.id,'/support-Связаться с разработчиком')
    bot.send_message(message.chat.id,'/start-Перезапуск бота')
    bot.send_message(message.chat.id,'/play-Запуск игры')

@bot.message_handler(func=lambda message:message.text=='Помощь по командам')
def help_from_button(message):
     bot.send_message(message.chat.id,'Здравствуй,'+username+',вот список команд')
     bot.send_message(message.chat.id,'/help-Помощь по командам')
     bot.send_message(message.chat.id,'/support-Связаться с разработчиком')
     bot.send_message(message.chat.id,'/start-Перезапуск бота')
     bot.send_message(message.chat.id,'/play-Запуск игры')


#Обработчики начала игры
@bot.message_handler(commands=['play'])
def start_play_for_command(message):
    markup_for_start_play=t.ReplyKeyboardMarkup(row_width=1)
    start_play_button=t.KeyboardButton(text='Нажми на меня')
    markup_for_start_play.add(start_play_button)
    bot.send_message(message.chat.id,'Нажми на кнопку для старта игры',reply_markup=markup_for_start_play)

#Сам функционал игры
@bot.message_handler(func=lambda message:message.text=='Играть')
def start_play_from_button(message):
    markup_start_play_from_button=t.ReplyKeyboardMarkup(row_width=1)
    button_play=t.KeyboardButton(text='Клик')
    markup_start_play_from_button.add(button_play)
    bot.send_message(message.chat.id,'Нажми кнопку для пополнения баланса и начала игры, что бы выйти из этого режима нужно будет написать /start',reply_markup=markup_start_play_from_button)


#Обработчик клика по кнопке "Клик" т.е обновления баланса юзера
@bot.message_handler(func=lambda message:message.text=='Клик')
def reaction_for_click_button(message):
    #Переменная содержащая цифру на которую будет пополнятся баланс если юзер без улучшений
    global price_per_click
    price_per_click=10
    #Удаление лишней клавиатуры для удобства
    markup_removes=t.ReplyKeyboardRemove(selective=False)
    #Создание другой клавиатуры
    markup_button_clicker=t.ReplyKeyboardMarkup(row_width=2)
    button_clicker=t.KeyboardButton(text='Клик')
    markup_button_clicker.add(button_clicker)
    user_id = message.from_user.id
    conn = sq.connect('users.db')
    cursor = conn.cursor()
    #Обновление баланса юзера в базе данных
    cursor.execute('UPDATE Users SET balance_pumpkin = balance_pumpkin+? WHERE user_id = ?', (price_per_click,user_id,))
    bot.send_message(user_id, f"Твой баланс пополнен на,{price_per_click}",reply_markup=markup_removes)

    #Показ баланса юзера
    
    cursor.execute('SELECT balance_pumpkin FROM Users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    balance = result[0] if result else 0
    bot.send_message(user_id, f"Твой текущий баланс: {balance}",reply_markup=markup_button_clicker)
    conn.commit()
    conn.close()

#Обработка просьбы о переводе от юзера
def pay_command(message):
    if len(message.text.split()) != 3:
        bot.send_message(message.chat.id, "Используйте /pay <ник> <сумма>")
        return

    sender_username = message.from_user.username
    recipient_username = message.text.split()[1]
    transfer_amount = int(message.text.split()[2])

    if sender_username == recipient_username:
        bot.send_message(message.chat.id, "Вы не можете перевести средства самому себе")
        return

    sender_balance = get_user_balance(sender_username)

    if sender_balance <= 0:
        bot.send_message(message.chat.id, "У вас нет средств для перевода")
        return
    elif sender_balance < transfer_amount:
        transfer_amount = sender_balance  

    if user_exists(recipient_username):
        decrease_balance(sender_username, transfer_amount)
        increase_balance(recipient_username, transfer_amount)

        send_notification(sender_username, recipient_username, transfer_amount)

        bot.send_message(
            message.chat.id,
            f"Средства успешно переведены пользователю {recipient_username}"
        )
    else:
        bot.send_message(message.chat.id, "Пользователь не найден. Попробуйте еще раз")
@bot.message_handler(commands=['pay'])
def pay_command(message):
    if len(message.text.split()) != 3:
        bot.send_message(message.chat.id, "Используйте /pay <ник> <сумма>")
        return

    sender_username = message.from_user.username
    recipient_username = message.text.split()[1]
    transfer_amount = int(message.text.split()[2])

    if sender_username == recipient_username:
        bot.send_message(message.chat.id, "Вы не можете перевести средства самому себе")
        return

    sender_balance = get_user_balance(sender_username)

    if sender_balance <= 0:
        bot.send_message(message.chat.id, "У вас нет средств для перевода")
        return
    elif sender_balance < transfer_amount:
        transfer_amount = sender_balance  # Переводим всю доступную сумму

    if user_exists(recipient_username):
        decrease_balance(sender_username, transfer_amount)
        increase_balance(recipient_username, transfer_amount)

        send_notification(sender_username, recipient_username, transfer_amount)

        bot.send_message(
            message.chat.id,
            f"Средства успешно переведены пользователю {recipient_username}"
        )
    else:
        bot.send_message(message.chat.id, "Пользователь не найден. Попробуйте еще раз")

def send_notification(sender, recipient, amount):
    recipient_id = get_user_id(recipient)
    if recipient_id:
        bot.send_message(recipient_id, f"Вам было отправлено {amount} от пользователя {sender}")

def get_user_id(username):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        cur.execute("SELECT user_id FROM Users WHERE username = ?", (username,))
        result = cur.fetchone()
        if result:
            return result[0]
    return None

def decrease_balance(username, amount):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        cur.execute("UPDATE Users SET balance_pumpkin = balance_pumpkin - ? WHERE username = ?", (amount, username))
        con.commit()

def increase_balance(username, amount):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        cur.execute("UPDATE Users SET balance_pumpkin = balance_pumpkin + ? WHERE username = ?", (amount, username))
        con.commit()

def get_user_balance(username):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        cur.execute("SELECT balance FROM Users WHERE username = ?", (username,))
        result = cur.fetchone()
        return result[0] if result else 0
    

bot.polling()

