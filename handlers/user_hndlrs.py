from email import message
import re

from handlers import word_hndlrs
from keyboards import *
from database import user, analytics, word_db
import log

logging = log.get_logger("base")


def register_commands(bot):
    def start_message(message):
        start(bot, message)

    # @bot.callback_query_handler(func=lambda call: re.match(r"Change_lang_", call.data))
    # def change_lang_callback(call):
    #     message = call.message
    #     lang, state = user.get_lang(bot, message, 1)
    #     user_id = message.user_id
    #     change_lang(bot, lang, user_id)

    #     words = word_db.get_word(
    #         re.sub(r"Change_lang_", "", call.data), user_id,  not (lang))
    #     word_hndlrs.send_word(bot, words, user_id, not (lang))

    #     bot.answer_callback_query(callback_query_id=call.id)
    
    bot.register_command("начать", start_message)


# handlers
def start(bot,message):
    """ Ввод команды /start в боте """
    username = bot.get_user_name(message.user_id)
    lang = user.get_lang(bot, message, user_name = username)

    username = f"@{username}" if isinstance(username, str) else str(message.user_id)
    user.set_lang(True, message.user_id)

    count = analytics.get_count_users()
    admin_message = "Новый пользователь " + \
        username + "\nВсего пользователей: " + count
    if int(count) % 50 == 0:
        admin_message = "Поздравляю!!! 🎆\n" + count + \
            " пользователей\n\nНовый пользователь " + username

    bot.send_message(215001844, admin_message)
    try:
        bot.send_message(407764903, admin_message)
    except:
        pass

    word_hndlrs.get_word(bot, message)
    # bot.send_message(message.user_id, "Привет ✌️ \nЯ твой <b>личный словарь</b> с татарского на русский язык и наоборот\n\nСейчас у тебя включен <b>Язык</b>: \n   🟢<u>с татарского</u>  на русский\n\n<b>Напиши слово</b>, которое ты хочешь перевести!\n\nТакже ты можешь спрашивать у меня перевод в любом чате, просто введи <b>@tatarcha_translate_bot</b> *Свое слово*",keyboard=mainKeyboard(message), parse_mode="HTML")
    bot.send_message(message.user_id, "Подписывайтесь на наш <b>канал по изучению татарского языка https://t.me/jitmesh_chakrim</b>!", keyboard=mainKeyboard(message), parse_mode="HTML")


def change_lang(bot, lang, user_id):
    logging.info(
        "Смена языка %s| user: %s" % ("rus" if not (lang) else "tat", str(user_id),))

    user.set_lang(not (lang), user_id)

    bot.send_message(user_id, f"Язык: \n{'*с русского* на татарский' if not (lang) else '*с татарского* на русский'}",
                     keyboard=mainKeyboard(user_id), parse_mode='MarkdownV2')


def report(bot, user_id):
    logging.info("Сообщить о проблеме | user: %s" % (str(user_id),))

    bot.send_message(user_id, "Опишите свою проблему",
                     keyboard=ReportKeyboard)
    user.set_state(user_id, 1)


def report_step_2(bot, message):
    lang = user.get_lang(bot, message)
    user_id = message.user_id

    if message.text == "Назад":
        user.set_state(user_id, 0)

        logging.info("Назад | user: %s" % (str(user_id),))

        bot.send_message(
            user_id, f"Язык: \n{'*с русского* на татарский' if lang else '*с татарского* на русский'}", keyboard=mainKeyboard(message), parse_mode="Markdown")
    else:
        bot.send_message(
            user_id, "Ваше сообщение отправлено разработчику!\nОн ответит вам в ближайшее время.", keyboard=mainKeyboard(message))

        logging.info("Сообщил об ошибке: %s | user: %s" %
                     (message.text[0:30], str(user_id),))

        user.set_state(user_id, 0)

        bot.send_message(
            215001844, f"Пользователь @{bot.get_user_name(message.user_id)} отправил сообщение об ошибке\n\n{message.text}")
