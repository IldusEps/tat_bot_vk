from ast import match_case
from datetime import date, datetime
from prettytable import PrettyTable, TableStyle
from functools import lru_cache

from database import connect

connection, cursor = connect.get_connection_cursor()

# SET


# Проверка необходимости добавления нового дня в базу данных
@lru_cache(maxsize=1)
def check_day(day):
    cursor.execute(
        'SELECT count FROM analytics_days WHERE day = DATE(NOW())')
    res = cursor.fetchall()
    if res == []:
        cursor.execute(
            'INSERT INTO analytics_days (count, day) VALUES(0, DATE(NOW()))')
        connection.commit()
    return True


def add_analytics(word_id):
    cursor.execute(
        'SELECT count FROM analytics WHERE word_id = %s', (word_id,))
    res1 = cursor.fetchall()
    if res1 == []:
        cursor.execute(
            'INSERT INTO analytics (word_id) VALUES(%s)', (word_id,))
        connection.commit()
    else:
        cursor.execute(
            'UPDATE analytics SET count = count + 1 WHERE word_id = %s', (word_id,))
        connection.commit()

    if check_day(date.today()):
        cursor.execute(
            'UPDATE analytics_days SET count = count + 1 WHERE day = DATE(NOW())')
        connection.commit()


# GET
def get_count_users():
    cursor.execute('SELECT COUNT(*) FROM users_vk')
    count = cursor.fetchone()

    return str(count[0]) if count != [] else "0"


@lru_cache(maxsize=4)
def statistics_query(word: bool = False):
    if word:
        cursor.execute(
            'SELECT w.word, count FROM analytics as analt JOIN Words2 as w ON analt.word_id = w.id ORDER BY analt.count DESC LIMIT 30')
        words = cursor.fetchall()
        return words
    else:
        cursor.execute(
            'SELECT count FROM analytics_days WHERE day = DATE(NOW())')
        count_day = cursor.fetchall()
        count_day = str(count_day[0][0]) if count_day != [] else "0"

        cursor.execute('SELECT COUNT(*) FROM users_vk')
        count_users = cursor.fetchone()
        count_users = str(count_users[0]) if count_users != [] else "0"

        cursor.execute(
            # LIMIT 20 OFFSET %s', (start,))
            'SELECT username, count, last_time, user_id FROM users_vk ORDER BY last_time DESC')
        users = cursor.fetchall()

        return count_day, count_users, users


def get_statistics(view=0):  # start=0,
    count_day, count_users, users = statistics_query()

    match view:
        case 0:
            return count_day, count_users
        case 1:
            rows = []
            head_row = ["<b>username</b>",
                        "<u><b>Кол-во слов</b></u>", "<b>Последний вход</b>", "id"]
            rows.append(" - ".join(head_row))
            for user in users:
                username = user[0]
                if not (isinstance(user[0], str)):
                    username = "id_" + user[3]
                else:
                    username = "@" + username
                rows.append(
                    f"{username} - <u>{user[1]}</u> - {user[2].strftime("%d.%B.%Y %H:%M")} - {user[3]}")

            return "\n".join(rows)

        case 2:
            users_table = PrettyTable()
            users_table.set_style(TableStyle.MSWORD_FRIENDLY)
            users_table.field_names = [
                "username", "Кол-во слов", "Последний вход"]
            for user in users:
                users_table.add_row(
                    [f"@{user[0]}", user[1], user[2].strftime("%d.%m.%Y %H:%M")])

            return users_table.get_string()

        case 3:
            words = statistics_query(True)
            words_table = PrettyTable()
            words_table.set_style(TableStyle.MSWORD_FRIENDLY)
            words_table.field_names = ["Слово", "Кол-во раз"]
            for word in words:
                words_table.add_row([word[0], word[1]])

            return words_table.get_string()
