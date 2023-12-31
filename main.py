import json
import time
import asyncio
import threading
import daemon
import telebot
import datetime
import validators
from telebot import types


flagFastAnswer = True
flagBanner = True

def NewConfig():
    fileConfig = open('json/config.json')

    fileConfig = json.load(fileConfig)
    return fileConfig

filePhrase = ""

def LoadPhrase():
    global filePhrase
    filePhrase = open('json/phrase.json')
    filePhrase = json.load(filePhrase)

fileAdministration = ""
def LoadAdministrationList():
    global fileAdministration
    fileAdministration = open('json/administration.json')
    fileAdministration = json.load(fileAdministration)

fileBanwords = ""
def LoadBanwords():
    global fileBanwords
    fileBanwords = open('json/banwords.json')
    fileBanwords = json.load(fileBanwords)

fileMailing = ""
def LoadMailing():
    global fileMailing
    fileMailing = open('json/mailing.json')
    fileMailing = json.load(fileMailing)

fileAdmname = ""
def LoadAdmname():
    global fileAdmname
    fileAdmname = open('json/admname.json')
    fileAdmname = json.load(fileAdmname)

def mailingFormating(fileMailing):
    formating = ""
    if fileMailing["status"] == True:
        formating+= "Рассылка активна\n\n"
        formating+= "<b>Содержание рассылки:</b>\n"
        formating+= fileMailing["text"]
        formating+= fileMailing["date"]
    else:
        formating+= "Рассылка неактивна"
    return formating

def addPhrase(filePhrase, phraseKey, phraseArray):

    filePhrase.update({
        phraseKey: phraseArray
    })
    
    with open("json/phrase.json", "w", encoding='utf-8') as write_file:
        json.dump(filePhrase, write_file, ensure_ascii=False)

def phraseFormating(filePhrase):
    formatingPhrase = "Список ответов и фраз:\n\n"
    for key, value in filePhrase.items():
        formatingPhrase+="<b>Быстрый ответ:</b>\n" + key + "\n<b>Фразы связанные с ответом:</b>\n"
        for v in value:
            formatingPhrase+=v + ", "
        formatingPhrase+="\n\n"
    return formatingPhrase

def banwordsFormating(fileBanwords):
    formatingPhrase = "Список триггеров:\n\n"
    formatingPhrase += "<b>Список триггеров для мута:</b>\n"
    for value in fileBanwords["mute"]:
        formatingPhrase+= value + ", "
    formatingPhrase += "\n\n <b>Список триггеров для бана:</b>\n"
    for value in fileBanwords["ban"]:
        formatingPhrase+= value + ", "
    return formatingPhrase
    

def admlistFormating(fileAdmname):
    formating = "Список администрации(Имя-айди):\n"
    for key, value in fileAdmname.items():
        formating+=value + " - " + key + "\n"
    return formating

config = NewConfig()
bot = telebot.TeleBot(config["apiToken"], parse_mode=None)
print("Start")


main_markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
main_markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
main_item1=types.KeyboardButton("Быстрые ответы")
main_item2=types.KeyboardButton("Рассылка")
main_item3=types.KeyboardButton("Админ-панель")
main_item4=types.KeyboardButton("Банлист")
main_markup.row(main_item1, main_item2)
main_markup.row(main_item3, main_item4)

@bot.message_handler(commands=['admin'])
def admin_button_message(message):
    if message.chat.type == "private":
        LoadAdministrationList()
        if str(message.from_user.id) in fileAdministration["admins"] or str(message.from_user.id) in fileAdministration["owner"]:
            bot.send_message(message.from_user.id, "Вход в панель администратора", reply_markup=main_markup)


@bot.message_handler(commands=["id"])
def get_id_message(message):
    if message.chat.type == "private":
        bot.send_message(message.from_user.id, str(message.from_user.id))

@bot.message_handler(content_types=['text'])
def phrase_add_message(message):

    global flagFastAnswer
    global flagBanner
    #Быстрые ответы
    if flagFastAnswer == True:
        if message.chat.type == "group" or message.chat.type == "supergroup":
            for key, value in filePhrase.items():
                for v in value:
                    if str.lower(v) in str.lower(message.text):
                            bot.send_message(message.chat.id, key)
                            break
    
    #Банлист
    if flagBanner == True:
        global fileBanwords
        if message.chat.type == "group" or message.chat.type == "supergroup":
            if validators.url(message.text):
                bot.delete_message(message.chat.id, message.message_id)
            if str.lower(message.text) in fileBanwords["mute"]:
                bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + 246060))
                bot.delete_message(message.chat.id, message.message_id)
            if str.lower(message.text) in fileBanwords["ban"]:
                bot.kick_chat_member(message.chat.id, message.from_user.id, until_date=864000000)
                bot.delete_message(message.chat.id, message.message_id)
        



    if message.chat.type != "private":
        return

    #Администраторские команды
    LoadAdministrationList()
    if str(message.from_user.id) in fileAdministration["admins"] or str(message.from_user.id) in fileAdministration["owner"]:
        
        #Быстрые ответы
        if message.text == "Быстрые ответы":
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1=types.KeyboardButton("Добавить ответ")
            item2=types.KeyboardButton("Список ответов")
            item3=types.KeyboardButton("Удалить ответ")
            item4=types.KeyboardButton("Вкл/Выкл ответы")
            item6=types.KeyboardButton("Назад")
            markup.row(item1, item2)
            markup.row(item3, item4)
            markup.add(item6)
            bot.send_message(message.from_user.id,"Вход в меню быстрые ответы", reply_markup=markup)

        #Банлист
        if message.text == "Банлист":
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1=types.KeyboardButton("Добавить мут триггер")
            item2=types.KeyboardButton("Добавить бан триггер")
            item3=types.KeyboardButton("Список триггеров")
            item4=types.KeyboardButton("Удалить триггер")
            item5=types.KeyboardButton("Вкл/Выкл банлист")
            item7=types.KeyboardButton("Назад")
            markup.row(item1, item2)
            markup.row(item3, item4)
            markup.row(item5, item7)
            bot.send_message(message.from_user.id,"Вход в меню банлиста", reply_markup=markup)

        #Рассылка
        if message.text == "Рассылка":
            LoadMailing()
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1=types.KeyboardButton("Создать рассылку")
            item6=types.KeyboardButton("Мгновенная рассылка")
            item2=types.KeyboardButton("Изменить содержание рассылки")
            item3=types.KeyboardButton("Изменить дату рассылки")
            item4=types.KeyboardButton("Отменить рассылку")
            item5=types.KeyboardButton("Назад")
            markup.row(item1, item6)
            markup.row(item2, item3)
            markup.add(item4, item5)
            bot.send_message(message.from_user.id, mailingFormating(fileMailing=fileMailing), parse_mode='HTML', reply_markup=markup)

        #Админ-панель
        if message.text == "Админ-панель":
            if str(message.from_user.id) in fileAdministration["owner"]:
                markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1=types.KeyboardButton("Добавить администратора")
                item2=types.KeyboardButton("Добавить owner администратора")
                item3=types.KeyboardButton("Список администраторов")
                item4=types.KeyboardButton("Удалить администратора")
                item5=types.KeyboardButton("Назад")
                item6=types.KeyboardButton("Изменить текст заглушки")
                markup.row(item1, item2)
                markup.row(item3, item4)
                markup.row(item6, item5)
                bot.send_message(message.from_user.id,"Меню owner", reply_markup=markup)
            else:
                bot.send_message(message.from_user.id, "Недостаточно прав")

    if str(message.from_user.id) in fileAdministration["admins"] or str(message.from_user.id) in fileAdministration["owner"]:
        if message.text == "Назад":
            bot.send_message(message.from_user.id, "Панель администратора", reply_markup=main_markup)
        #Быстрые ответы
        if message.text == "Вкл/Выкл ответы":
            flagFastAnswer = not flagFastAnswer
            if flagFastAnswer == True:
                bot.send_message(message.from_user.id, "Ответы включены")
            else:
                bot.send_message(message.from_user.id, "Ответы выключены")
        if message.text == "Добавить ответ":
            bot.send_message(message.from_user.id, "Введите ответ")
            bot.register_next_step_handler(message, get_phrase_key)
        elif message.text == "Список ответов":
            LoadPhrase()
            bot.send_message(message.from_user.id, phraseFormating(filePhrase), parse_mode='HTML')
        elif message.text == "Удалить ответ":
            bot.send_message(message.from_user.id, "Напишите какой быстрый ответ нужно удалить(Полностью)")
            bot.register_next_step_handler(message, pop_phrase_key)


        #Банлист
        if message.text == "Вкл/Выкл банлист":
            flagBanner = not flagBanner
            if flagBanner == True:
                bot.send_message(message.from_user.id, "Банлист включен")
            else:
                bot.send_message(message.from_user.id, "Банлист выключен")
        elif message.text == "Добавить мут триггер":
            bot.send_message(message.from_user.id, "Напишите триггер")
            bot.register_next_step_handler(message, add_trigger_mute)
        elif message.text == "Добавить бан триггер":
            bot.send_message(message.from_user.id, "Напишите триггер")
            bot.register_next_step_handler(message, add_trigger_ban)
        elif message.text == "Удалить триггер":
            bot.send_message(message.from_user.id, "Введите какой триггер удалить")
            bot.register_next_step_handler(message, pop_trigger)
        elif message.text == "Список триггеров":
            LoadBanwords()
            bot.send_message(message.from_user.id, banwordsFormating(fileBanwords), parse_mode='HTML')
    
        #Рассылка
        elif message.text == "Отменить рассылку":
            fileMailing["status"] = False
            with open("json/mailing.json", "w", encoding='utf-8') as write_file:
                json.dump(fileMailing, write_file, ensure_ascii=False)
            bot.send_message(message.from_user.id, "Рассылка отменена")
        elif message.text == "Создать рассылку":
            bot.send_message(message.from_user.id, "Введите дату рассылки в формате (День-Месяц-Год-Час-Минута) также месяца и дни писать без использования 0(Пример: 7 = Июль)")
            bot.register_next_step_handler(message, add_dateMailing)
    
        elif message.text == "Изменить содержимое рассылки":
            bot.send_message(message.from_user.id, "Напишите новый текст для рассылки")
            bot.register_next_step_handler(message, edit_textMailing)
        elif message.text == "Мгновенная рассылка":
            bot.send_message(message.from_user.id, "Введите текст рассылки")
            bot.register_next_step_handler(message, fastMailing)

        #Админ-панель
        if str(message.from_user.id) in fileAdministration["owner"]:
            if message.text == "Добавить администратора":
                bot.send_message(message.from_user.id, "Введите telegram_id Администратора")
                bot.register_next_step_handler(message, add_adm_id)
            if message.text == "Добавить owner администратора":
                bot.send_message(message.from_user.id, "Введите telegram_id Администратора")
                bot.register_next_step_handler(message, add_own_id)
            if message.text == "Список администраторов":
                LoadAdmname()
                bot.send_message(message.from_user.id, admlistFormating(fileAdmname))
            if message.text == "Удалить администратора":
                bot.send_message(message.from_user.id, "Введите айди администратора, которого нужно удалить")
                bot.register_next_step_handler(message, pop_adm)
            if message.text == "Изменить текст заглушки":
                bot.send_message(message.from_user.id, "Введите текст заглушки")
                bot.register_next_step_handler(message, edit_spam_message)

    else:
        bot.send_message(message.from_user.id, config["plug"])

#Быстрые ответы
def pop_phrase_key(message):
    del filePhrase[message.text]
    del fileFormating[message.text]
    with open("json/phrase.json", "w", encoding='utf-8') as write_file:
        json.dump(filePhrase, write_file, ensure_ascii=False)
    with open("json/formating.json", "w", encoding='utf-8') as write_file:
        json.dump(fileFormating, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Фраза удалена")

def get_phrase_key(message):
    global temp_phraseKey
    global fileFormating
    temp_phraseKey = message.text
    bot.send_message(message.from_user.id, "Введите через запятую с пробелом фразы")
    bot.register_next_step_handler(message, get_phrase_value)

def get_phrase_value(message):
    temp_phraseValue = message.text
    global filePhrase
    addPhrase(filePhrase,temp_phraseKey, temp_phraseValue.split(", "))
    bot.send_message(message.from_user.id, "Фраза добавлена")

#Банлист

def add_trigger_mute(message):
    fileBanwords["mute"].append(str.lower(message.text))
    with open("json/banwords.json", "w", encoding='utf-8') as write_file:
        json.dump(fileBanwords, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Мут триггер добавлен")

def add_trigger_ban(message):
    fileBanwords["ban"].append(str.lower(message.text))
    with open("json/banwords.json", "w", encoding='utf-8') as write_file:
        json.dump(fileBanwords, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Бан триггер добавлен")

def pop_trigger(message):
    try:
        fileBanwords["mute"].remove(str.lower(message.text))
    except ValueError:
        fileBanwords["ban"].remove(str.lower(message.text))
    with open("json/banwords.json", "w", encoding='utf-8') as write_file:
        json.dump(fileBanwords, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Триггер удалён")


#Рассылка

def add_dateMailing(message):
    global dateMailing
    dateMailing = message.text
    bot.send_message(message.from_user.id, "Введите текст рассылки")
    bot.register_next_step_handler(message, add_textMailing)

def add_textMailing(message):
    textMailing = message.text
    fileMailing["date"] = dateMailing
    fileMailing["text"] = textMailing
    fileMailing["status"] = True
    with open("json/mailing.json", "w", encoding='utf-8') as write_file:
                json.dump(fileMailing, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Рассылка создана\n")
    t = threading.Thread(target=startMailingDaemon)
    t.daemon = True
    t.start()

def edit_textMailing(message):
    fileMailing["text"] = message.text
    with open("json/mailing.json", "w", encoding='utf-8') as write_file:
        json.dump(fileMailing, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Рассылка изменена")

def edit_textMailing(message):
    fileMailing["date"] = message.text
    with open("json/mailing.json", "w", encoding='utf-8') as write_file:
        json.dump(fileMailing, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Рассылка изменена")

def fastMailing(message):
    for chatid in config["chatId"]:
        bot.send_message(int(chatid), message.text)
    bot.send_message(message.from_user.id, "Рассылка отправлена")


#Админ панель

def edit_spam_message(message):
    config["plug"] = message.text
    with open("json/config.json", "w", encoding="utf-8") as write_file:
        json.dump(config, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Изменено")

admID = ""
def add_adm_id(message):
    if str.lower(message.text) == "Назад":
        return
    global admID
    admID = message.text
    bot.send_message(message.from_user.id, "Введите имя администратора")
    bot.register_next_step_handler(message, add_adm_name)

admName = ""
def add_adm_name(message):
    if str.lower(message.text) == "Назад":
        return
    global fileAdmname
    admName = str(message.text)
    fileAdministration["admins"].append(str(admID))
    fileAdmname.update({
        str(admID): admName
    })
    with open("json/administration.json", "w", encoding='utf-8') as write_file:
        json.dump(fileAdministration, write_file, ensure_ascii=False)
    with open("json/admname.json", "w", encoding='utf-8') as write_file:
        json.dump(fileAdmname, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Администратор добавлен")


ownID = ""
def add_own_id(message):
    if str.lower(message.text) == "Назад":
        return
    global ownID
    ownID = message.text
    bot.send_message(message.from_user.id, "Введите имя администратора")
    if str.lower(message.text) == "Назад":
        return
    bot.register_next_step_handler(message, add_own_name)

ownName = ""
def add_own_name(message):
    if str.lower(message.text) == "Назад":
        return
    global fileAdmname
    ownName = str(message.text)
    fileAdministration["owner"].append(str(ownID))
    fileAdmname.update({
        str(ownID): ownName
    })
    with open("json/administration.json", "w", encoding='utf-8') as write_file:
        json.dump(fileAdministration, write_file, ensure_ascii=False)
    with open("json/admname.json", "w", encoding='utf-8') as write_file:
        json.dump(fileAdmname, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Овнер добавлен")


def pop_adm(message):
    global fileAdmname
    global fileAdministration
    fileAdministration["admins"].remove(message.text)
    del fileAdmname[message.text]
    with open("json/administration.json", "w", encoding='utf-8') as write_file:
        json.dump(fileAdministration, write_file, ensure_ascii=False)
    with open("json/admname.json", "w", encoding='utf-8') as write_file:
        json.dump(fileAdmname, write_file, ensure_ascii=False)
    bot.send_message(message.from_user.id, "Администратор удален")

#Асинхронная функция сверки времени с временем рассылки с интервалом в 15 секунд
async def mailing_infinity():
    LoadMailing()
    while fileMailing["status"] == True:
        dateMailing = fileMailing["date"].split("-")
        nowDate = datetime.datetime.now()
        if str(nowDate.day) == dateMailing[0] and str(nowDate.month) == dateMailing[1] and str(nowDate.year) == dateMailing[2] and str(nowDate.hour) == dateMailing[3] and str(nowDate.minute) == dateMailing[4]:
            for chatid in config["chatId"]:
                bot.send_message(int(chatid), fileMailing["text"])
            fileMailing["status"] = False
            with open("json/mailing.json", "w", encoding='utf-8') as write_file:
                json.dump(fileMailing, write_file, ensure_ascii=False)
        time.sleep(15)

async def start_gorutine_mailing():
    task = asyncio.create_task(mailing_infinity())
    await task

LoadPhrase()
LoadAdministrationList()
LoadBanwords()
LoadMailing()
LoadAdmname()

def startMailingDaemon():
    if fileMailing["status"] == True:
        asyncio.run(start_gorutine_mailing())

t = threading.Thread(target=startMailingDaemon)
t.daemon = True
t.start()

bot.infinity_polling()


