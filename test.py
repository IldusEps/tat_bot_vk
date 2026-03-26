
import re

from database import connect
from database.utils import *
import log

logging = log.get_logger("base")
connection, cursor = connect.get_connection_cursor()


def get_word(word, lang=0, search_III=False):
    # logging.info("print %s | user:%s" % (word, str(user_id),))

    res = []
    data_base = dbName(lang)
    not_sort = False
    # word = word.lower()

    def search_I_level():
        # Простой поиск
        nonlocal res
        cursor.execute(
            f'SELECT tr, order_, word, id FROM {data_base} WHERE word LIKE %s ORDER BY CHAR_LENGTH(word) ASC LIMIT 4', (word, ))
        res = cursor.fetchall()
        logging.info("[]" + word if len(res) == 0 else (
            "len: " + str(len(res)) + " " + res[0][2]))

    def search_II_level():
        # Поиск методом генерации всех возможных слов заменой некоторых букв
        nonlocal res, not_sort
        if len(res) > 0:
            not_sort = True

        replacements = [
            ["э", "ә"],
            ["о", "ө"],
            ["у",  "ү"],
            ["ж", "җ"],
            ["н", "ң"],
            ["х", "һ"],
            ["ә", "а"],
            ["э", "а"],
            ["а", "ә"],
            ["е", "ә"],
            ["г", "гъ"],
            ["г", "гь"],
            ["к", "къ"],
            ["к", "кь"],
            ["м", "мъ"],
            ["м", "мь"],
            ["н", "нъ"],
            ["н", "нь"],
            ["ы", "о"],
            ["у", "о"]
        ]
        add_words = []
        # Генерация всех возможных вариантов слов с помощью замены букв на похожие буквы
        for letter in replacements:
            if letter[0] in word:
                add_words.append(word.replace(letter[0], letter[1]))
                match = re.finditer(letter[0], word)
                for m in match:
                    new_word = word[0:m.start()] + "_" + word[m.start() + 1:]
                    for letter1 in replacements:
                        if letter1[0] in new_word:
                            add_words.append(word[0:m.start()].replace(
                                letter1[0], letter1[1]) + letter[1] + word[m.start() + 1:].replace(letter1[0], letter1[1]))

        # Генерация добавочной строчки SQL из сгенерированных выше слов
        add_word_SQL = ""
        if len(add_words) > 0:
            for add_word in add_words:
                add_word_SQL += "or word LIKE '%s' " % (add_word + "%")

        cursor.execute(
            f'SELECT tr, order_, word, id FROM {data_base} WHERE word LIKE %s {add_word_SQL} ORDER BY CASE WHEN word LIKE %s THEN 0 ELSE 1 END ASC, CHAR_LENGTH(word) ASC LIMIT 4', (word, word, ))
        new_res = cursor.fetchall()
        if res != []:
            res = res + new_res
            if not (not_sort):
                res = sorted(res, key=lambda x: len(x[2]))
        else:
            res = new_res
        logging.info(f"[]" + word if len(res) ==
                     0 else ("len: " + str(len(res)) + " " + res[0][2]))

    def search_III_level():
        nonlocal res
        where = []
        without_vowels = word
        count = []

        # Раскладываем слово на слоги с пропусками. Ввида:  тапок - т_п, а_о, п_к
        for [e, s] in enumerate(word):
            if e != 0 and e != len(word) - 1:
                new_word = ("%" if e != 0 else "") + word[e-1:e] + "_" + word[e+1:e+2] + \
                    ("%" if len(word) > 3 else "")
                count.append(f'IF(word LIKE "{new_word}", 1, 0)')
                count.append(
                    f'IF(word LIKE "{new_word.replace("_", "__")}", 0.5, 0)')
                if e == 1:
                    where.append(
                        'word LIKE "' + new_word + '"' + ' or word LIKE "' + new_word.replace("_", "__") + '"')
                else:
                    where.append(' or word LIKE "' + new_word + '"' +
                                 ' or word LIKE "' + new_word.replace("_", "__") + '"')
                # Генерируем слово без гласных. Ввида: тапок - т_п_к
                if s in vowels and s not in {"ы", "е", "я", "и"}:
                    without_vowels = without_vowels[:e] + \
                        "%" + without_vowels[e+1:]
        where.append(' or word LIKE "' + without_vowels + '"')

        cursor.execute(
            'SELECT tr, order_, word, id, (' + "+".join(count) + ') as count1 FROM `' + data_base + '` WHERE CHAR_LENGTH(word) < ' + str(len(word) + 3) + ' and (' + "".join(
                where) + ') ORDER BY CASE WHEN word LIKE %s THEN 0 ELSE 1 END ASC, count1 DESC, char_length(word) ASC LIMIT 4',
            (without_vowels, ))
        res_ = cursor.fetchall()

        if res != []:
            word_len = len(word)
            res = res + res_
            if not (not_sort):
                res = sorted(res, key=lambda x: abs(word_len - len(x[2])))
        else:
            res = res_

        logging.info("[]" + word if len(res) == 0 else (
            "len: " + str(len(res)) + " " + res[0][2]))

    search_I_level()
    if len(res) < 3 and len(word) > 2:
        if lang == 0:
            search_II_level()
        if (len(res) < 3 and len(word) > 3) and search_III:  # or lang == 1:
            search_III_level()

    if res == []:
        return []

    # analytics.add_analytics(res[0][3])

    temp = []
    new_res = []
    for val in res:
        if val[2] not in temp:
            temp.append(val[2])
            new_res.append(val)

    data = []
    for r in new_res:
        data.append({
            "translation": r[0],
            "order": r[1],
            "word": r[2]
        })
    return data


try:
    while True:
        get_word(input('слово'))

except KeyboardInterrupt:
    pass
