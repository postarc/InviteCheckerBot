## -*- coding: utf-8 -*-
#pip install pytelegrambotapi

import telebot
import sqlite3 as sql
import os.path

#basefile='userdata'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "userdata.db")
con = sql.connect(db_path, check_same_thread=False)
bot = telebot.TeleBot('1647077261:AAHQhT-gplqWr7SDDod_CwjPyKhSQPK795Q')

with con:
   cur = con.cursor()
   cur.execute("CREATE TABLE IF NOT EXISTS database (userid INTEGER, firstname STRING, lastname STRING, username STRING, invite INTEGER)")
   #userid=int(input("UserId: "))
   #name=input("Name: ")
   #surname=input("Surname: ")
   #invite=int(input("Invite: "))
   #cur.execute(f"INSERT INTO book(userid,name,surname,invite) VALUES ('{userid}', '{name}', '{surname}', '{invite}')")

@bot.message_handler(content_types=['text'])

def get_text_messages(message):
   message_arr=message.text.split(" ")
   if message_arr[0] == "/help":
      bot.send_message(message.from_user.id, "/list - список всех пользователей\n"
                                             "/check userid - проверить пользователя\n"
                                             "/check - узнать свой id\n"
                                             "форвард сообщения - узнать id автора сообщения\n\n"
                                             "Если аккаунт закрыт настройками приватности,"
                                             " можно узнать id в специализированных ботах,"
                                             " например @username_to_id_bot по username" )
   elif message_arr[0] == "/check":
      if len(message_arr) == 1:
         bot.send_message(message.from_user.id, f'Ваш id: {message.from_user.id}')
      else:
         if message_arr[1].isdigit():
            cur.execute("SELECT * FROM database WHERE userid=?", (message_arr[1],))
            rows = cur.fetchall()
            if rows:
               for row in rows:
                  bot.send_message(message.from_user.id, f'Найден!\nUserid: {row[0]}\nFirstname: {row[1]}\n'
                                                         f'Lastname: {row[2]}\nUsername: {row[3]}\n'
                                                         f'Invites: {row[4]}')
            else:
               bot.send_message(message.from_user.id,'Пользователь не найден.')
         else:
            bot.send_message(message.from_user.id, "Неверно введен id")
   elif message_arr[0] == "/adduser":
      if len(message_arr) == 6:
         if message_arr[1].isdigit() and message_arr[5].isdigit():
            #and message_arr[6].isdigit()
            cur.execute("SELECT * FROM database WHERE userid=?", (message_arr[1],))
            rows = cur.fetchall()
            if not rows:
               cur.execute(f"INSERT INTO database VALUES ('{message_arr[1]}','{message_arr[2]}','{message_arr[3]}','{message_arr[4]}','{message_arr[5]}')")
               con.commit()
               bot.send_message(message.from_user.id, "OK")
            else:
               bot.send_message(message.from_user.id, "EXSIST")
   elif message_arr[0] == "/change":
      if len(message_arr) == 3:
         if message_arr[1].isdigit() and message_arr[2].isdigit():
            cur.execute("UPDATE database SET invite = ? WHERE userid = ?", (message_arr[2], message_arr[1],))
            con.commit()
            bot.send_message(message.from_user.id, "CHANGED")
   elif message_arr[0] == "/list":
      cur.execute("SELECT * FROM database")
      rows = cur.fetchall()
      if rows:
         for row in rows:
            bot.send_message(message.from_user.id, f'Userid: {row[0]}\nFirstname: {row[1]}\n'
                                                   f'Lastname: {row[2]}\nUsername: {row[3]}\n'
                                                   f'Invites: {row[4]}')
   else:
      if message.forward_from or message.forward_sender_name:
         if message.forward_from:
            user=message.forward_from
            print(user.id)
            bot.send_message(message.from_user.id, f'Userid: {user.id}\nFirstname: {user.first_name}\n'
                                                   f'Lastname: {user.last_name}\n'
                                                   f'Username: {user.username}')
            cur.execute("SELECT * FROM database WHERE userid=?", (user.id,))
            rows = cur.fetchall()
            if rows:
               for row in rows:
                  bot.send_message(message.from_user.id,f'Испорчено инвайтов: {row[4]}')
            else:
                  bot.send_message(message.from_user.id,"Пользователь не обнаружен в базе данных")
         else:
            bot.send_message(message.from_user.id, "Обнаружен форвард, но аккаунт скрыт настройками приватности")
      else:
         bot.send_message(message.from_user.id, "Команда не найдена. Для помощи введите /help.")
try:
   bot.polling(none_stop=True, interval=0)
except KeyboardInterrupt:
   con.commit()
   cur.close()
   exit (0)
