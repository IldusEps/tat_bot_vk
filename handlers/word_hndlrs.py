from random import randint
import re

from keyboards import *
from database import user, analytics, word_db
import log

logging = log.get_logger("base")


def register_commands(bot):
    @bot.callback_query_handler(func=lambda call: re.match(r"^[А-ЯЁёа-яҗңһүәөҖҢҺҮӘӨ \-\|]+$", call.data))
    def word_get_callback(call):
        get_word(bot, call)
        bot.answer_callback_query(callback_query_id=call.id)

    @bot.callback_query_handler(func=lambda call: re.match(r"^Search_", call.data))
    def search_III_callback(call):
        search_III(call, bot)
        bot.answer_callback_query(callback_query_id=call.id)

# utils


def send_word(bot, words, user_id, lang, word=""):
    """ Отправка слов """
    # keyboard = mainKeyboard(user_id)
    if len(words) > 0:
        translation, buttons = word_db.translation_replace(
            words[0]["translation"])
        logging.info(
            "%s - %s... user: %s" % (words[0]["word"], translation[0:20].replace("\n", ""), str(user_id),))
        # if len(buttons) > 0:
        #     inl_keyboard = types.InlineKeyboardMarkup()
        #     for b in buttons:
        #         inl_keyboard.add(
        #             types.InlineKeyboardButton(b, callback_data=b))
        # inl_keyboard if len(buttons) > 0 else

        translation = re.sub(
            r"<\/?[^uiba\/]*?>|<\/?[^a\/](.*?(?<=a))>", "", translation)
        word_id = f"(id=[{words[0]["id"]}](http://217.114.6.216:3001/?id={words[0]["id"]}))" if user_id in ADMINS else ""
        mess = f"Перевел  <u>{"с татарского🟢" if not (lang) else "с русского🇷🇺"}</u>\n<b>{words[0]["word"]}</b> {word_id}\n{translation}"
        if len(mess) < 4096:
            bot.send_message( user_id, mess)#, keyboard=keyboard, parse_mode='HTML')
        else:
            matches = re.finditer(
                r"[\s\S]{1,3900}(\n|$)", mess, re.MULTILINE)
            for matchNum, match in enumerate(matches):
                if matchNum != 0:
                    bot.send_message( 
                        user_id, f"<blockquote expandable>{match.group(0)}</blockquote>")#, keyboard=keyboard, parse_mode='HTML')
                else:
                    bot.send_message(
                        user_id, match.group(0))#, keyboard=keyboard, parse_mode='HTML')
        if len(words) > 1:
            perhaps_words = ""
            # inl_keyboard = NewInlineKeyboard()
            # for i, w in enumerate(words[1:]):
            #     perhaps_words += f"<b>{w["word"]}</b>" + \
            #         (", " if i != len(words) - 2 else " ")
            #     inl_keyboard.add(types.InlineKeyboardButton(
            #         w["word"], callback_data=w["word"]))
            # bot.send_message(user_id, f"Возможно вы имели ввиду: {perhaps_words}",
            #                  keyboard=inl_keyboard, parse_mode='HTML')
    else:
        # inl_keyboard = NewInlineKeyboard()
        # if word != "":
            # inl_keyboard.add(types.InlineKeyboardButton(
            #     "Найти похожее", callback_data="Search_" + word))
            # inl_keyboard.add(types.InlineKeyboardButton(
            #     "Сменить язык и найти", callback_data="Change_lang_" + word))
        bot.send_message(user_id,
                         f"*Слово не найдено!*\nВводите слово в *именительном падеже, первом лице*.\nПопробуйте сменить язык.\n\nЯзык: {"с татарского🟢" if not (lang) else "с русского🇷🇺"}", )
        #keyboard=inl_keyboard, parse_mode="Markdown")

# handlers


def get_word(bot, message, random=False):
    word = message.text
    user_id = message.user_id
    lang = user.get_lang(bot, message)

    username = "id_" + str(user_id)

    if random or (re.match(r"^[А-ЯЁёа-яҗңһүәөҖҢҺҮӘӨ \-\|]+$", word.lower()) and len(word.lower()) < 50):
        if random:
            # Если ищем случайное слово
            word_id = randint(0, word_db.get_count_word(lang))
            words = word_db.get_by_id(lang, user_id, word_id)
        else:
            words = word_db.get_word(word, user_id,  lang)

        send_word(bot, words, user_id, lang, word)

        admin_message = f"Пользователь {username} ищет слово {"с татарского🟢" if not (lang) else "с русского🇷🇺"}: \n{word}\nКол-во найденных слов: {len(words)}"
    else:
        logging.info("Ошибка ввода user: %s" % (str(user_id),))

        admin_message = f"Пользователь {username} ищет слово: \n{word}\nОшибка ввода"
        bot.send_message(user_id, "Ошибка при вводе слова. Вводите слова кириллицей. Либо вы превысили кол-во символов", keyboard=mainKeyboard(message))

    bot.send_message(bot, '215001844', admin_message)#, disable_notification=True)
    try:
        bot.send_message(407764903, admin_message)
                     #,                         disable_notification=True)
    except:
        pass


def search_III(call, bot):
    message = call.message
    user_id = message.user_id
    lang = user.get_lang(bot, message)

    words = word_db.get_word(
        re.sub(r"Search_", "", call.data), user_id,  lang, True)
    send_word(bot, words, user_id, lang)
