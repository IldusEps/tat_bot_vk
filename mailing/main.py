import os
import requests
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import sys
import html

# Загружаем переменные окружения
load_dotenv()

# Глобальные переменные для подключения к БД
_connection = None
_cursor = None


def get_connection_cursor():
    global _connection, _cursor
    if not _connection:
        try:
            _connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE", "words")
            )
            print("✓ Подключение к БД установлено")
        except Error as e:
            print(f"✗ Ошибка подключения к БД: {e}")
            sys.exit(1)

    if not _cursor:
        _cursor = _connection.cursor(dictionary=True)

    return _connection, _cursor


def get_users_from_db():
    """Получаем всех пользователей из БД"""
    connection, cursor = get_connection_cursor()

    try:
        # Используем таблицу users_vk и столбец user_id
        query = "SELECT user_id FROM users_vk WHERE user_id IS NOT NULL"
        cursor.execute(query)
        users = cursor.fetchall()
        return users
    except Error as e:
        print(f"✗ Ошибка при получении пользователей: {e}")
        return []


def send_telegram_message(chat_id, text, photo_path=None, parse_mode=None):
    """Отправляем сообщение через Telegram Bot API"""
    bot_token = os.getenv("TELEGRAM_API")

    if not bot_token:
        print("✗ Ошибка: TELEGRAM_API не установлен")
        return False

    # Если parse_mode не указан, спрашиваем пользователя
    if parse_mode is None:
        parse_mode = os.getenv("DEFAULT_PARSE_MODE", "HTML")

    if photo_path:
        # Отправка сообщения с фото
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

        try:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': chat_id,
                    'caption': text,
                }

                # Добавляем parse_mode только если он указан и не равен 'None'
                if parse_mode and parse_mode.lower() != 'none':
                    data['parse_mode'] = parse_mode

                response = requests.post(url, files=files, data=data)
        except FileNotFoundError:
            print(f"✗ Файл {photo_path} не найден. Отправляем только текст.")
            return send_telegram_message(chat_id, text, parse_mode=parse_mode)
    else:
        # Отправка только текстового сообщения
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
        }

        # Добавляем parse_mode только если он указан и не равен 'None'
        if parse_mode and parse_mode.lower() != 'none':
            data['parse_mode'] = parse_mode

        response = requests.post(url, data=data)

    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            return True
        else:
            error_desc = result.get('description', 'Неизвестная ошибка')
            print(
                f"✗ Ошибка при отправке пользователю {chat_id}: {error_desc}")

            # Проверяем, не связана ли ошибка с HTML тегами
            if "can't parse entities" in error_desc.lower():
                print(
                    f"  Подсказка: возможно, проблема с HTML тегами. Проверьте синтаксис.")

            return False
    else:
        print(
            f"✗ HTTP ошибка {response.status_code} для пользователя {chat_id}")
        return False


def send_broadcast_message(message_text, photo_path=None, parse_mode=None):
    """Отправляем рассылку всем пользователям"""
    users = get_users_from_db()

    if not users:
        print("✗ Нет пользователей для рассылки")
        return

    total_users = len(users)
    print(f"\n📊 Начинаем рассылку для {total_users} пользователей...")
    print(
        f"📝 Режим разметки: {parse_mode if parse_mode else 'без форматирования'}")

    successful_sends = 0
    failed_sends = 0

    for i, user in enumerate(users, 1):
        chat_id = user.get('user_id')
        if chat_id:
            print(f"\r🔄 Отправка {i}/{total_users}...", end="", flush=True)

            if send_telegram_message(chat_id, message_text, photo_path, parse_mode):
                successful_sends += 1
            else:
                failed_sends += 1

    print(f"\n\n✅ Рассылка завершена!")
    print(f"   ✓ Успешно отправлено: {successful_sends}")
    print(f"   ✗ Не удалось отправить: {failed_sends}")

    if failed_sends > 0:
        print(f"\n💡 Рекомендации:")
        print(f"   - Проверьте валидность user_id в базе данных")
        print(f"   - Убедитесь, что бот не был заблокирован пользователями")
        print(f"   - Проверьте синтаксис HTML тегов (если используется форматирование)")


def get_multiline_input():
    """Функция для ввода многострочного текста"""
    print("\n" + "="*60)
    print("📝 ВВОД ТЕКСТА РАССЫЛКИ")
    print("="*60)
    print("Вводите текст построчно. Поддерживается HTML разметка.")
    print("Примеры HTML тегов:")
    print("  <b>жирный</b> <i>курсив</i> <u>подчеркнутый</u>")
    print("  <code>моноширинный</code> <a href='url'>ссылка</a>")
    print("\nВведите 'END' на отдельной строке для завершения ввода.")
    print("="*60)

    lines = []
    line_number = 1

    while True:
        try:
            prompt = f"{line_number:3d} | " if line_number > 1 else ""
            line = input(prompt)

            if line.strip() == 'END':
                break

            lines.append(line)
            line_number += 1

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\n✗ Ввод прерван пользователем")
            return None

    if not lines:
        print("✗ Текст не введен")
        return None

    return '\n'.join(lines)


def validate_html_tags(text):
    """Проверяем баланс HTML тегов"""
    stack = []
    i = 0
    while i < len(text):
        if text[i] == '<':
            # Нашли открывающий тег
            if i + 1 < len(text) and text[i + 1] == '/':
                # Закрывающий тег
                i += 2
                start = i
                while i < len(text) and text[i] != '>':
                    i += 1
                if i < len(text):
                    tag = text[start:i].strip()
                    if stack and stack[-1] == tag:
                        stack.pop()
                    else:
                        return False, f"Непарный закрывающий тег </{tag}>"
            else:
                # Открывающий тег
                i += 1
                start = i
                while i < len(text) and text[i] != '>' and text[i] != ' ':
                    i += 1
                if i < len(text):
                    tag = text[start:i].strip()
                    stack.append(tag)
        i += 1

    if stack:
        return False, f"Незакрытые теги: {', '.join(f'<{tag}>' for tag in stack)}"

    return True, "OK"


def preview_message(text, parse_mode):
    """Предварительный просмотр сообщения"""
    print("\n" + "="*60)
    print("👁‍🗨 ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР")
    print("="*60)

    if parse_mode == 'HTML':
        # Показываем текст с HTML тегами
        print("📋 Форматированный текст (HTML):")
        print("-" * 40)
        print(text)
        print("-" * 40)

        # Показываем текст без тегов для сравнения
        print("\n📋 Текст без тегов:")
        print("-" * 40)
        # Простая замена тегов (не полный HTML парсер)
        clean_text = text.replace('<b>', '').replace('</b>', '')
        clean_text = clean_text.replace('<i>', '').replace('</i>', '')
        clean_text = clean_text.replace('<u>', '').replace('</u>', '')
        clean_text = clean_text.replace('<code>', '').replace('</code>', '')
        clean_text = clean_text.replace('<pre>', '').replace('</pre>', '')
        # Удаляем ссылки, но оставляем текст
        import re
        clean_text = re.sub(r'<a[^>]*>', '', clean_text)
        clean_text = clean_text.replace('</a>', '')
        print(clean_text)
        print("-" * 40)

        # Проверяем HTML теги
        is_valid, message = validate_html_tags(text)
        if is_valid:
            print(f"\n✅ HTML теги корректны")
        else:
            print(f"\n⚠️  Внимание: {message}")
            print("   Telegram может не отправить сообщение с ошибками в тегах")

    else:
        print("📋 Текст сообщения:")
        print("-" * 40)
        print(text)
        print("-" * 40)


def main():
    """Основная функция скрипта"""
    print("="*60)
    print("🤖 TELEGRAM РАССЫЛОЧНЫЙ БОТ")
    print("="*60)

    # Получаем текст сообщения (многострочный)
    message_text = get_multiline_input()

    if not message_text or message_text.strip() == '':
        print("✗ Текст сообщения не может быть пустым")
        return

    # Выбираем режим разметки
    print("\n" + "="*60)
    print("🎨 ВЫБОР РЕЖИМА РАЗМЕТКИ")
    print("="*60)
    print("1. HTML - поддерживает теги: <b>, <i>, <u>, <code>, <a href='...'>")
    print("2. Без форматирования - простой текст")
    print("3. Отменить рассылку")

    mode_choice = input("\nВыберите режим (1-3): ").strip()

    if mode_choice == '3':
        print("✗ Рассылка отменена")
        return
    elif mode_choice == '1':
        parse_mode = 'HTML'
    else:
        parse_mode = None

    # Предварительный просмотр
    preview_message(message_text, parse_mode)

    # Спрашиваем про изображение
    print("\n" + "="*60)
    print("🖼 ДОБАВЛЕНИЕ ИЗОБРАЖЕНИЯ")
    print("="*60)
    use_photo = input("\nДобавить изображение? (y/n): ").strip().lower()
    photo_path = None

    if use_photo == 'y':
        photo_path = input("Введите путь к файлу изображения: ").strip()
        if not os.path.exists(photo_path):
            print(f"✗ Файл {photo_path} не существует")
            confirm = input(
                "Продолжить без изображения? (y/n): ").strip().lower()
            if confirm != 'y':
                print("✗ Рассылка отменена")
                return
            photo_path = None
        else:
            print(f"✓ Изображение найдено: {photo_path}")

    # Получаем количество пользователей
    users = get_users_from_db()
    user_count = len(users) if users else 0

    # Финальное подтверждение
    print("\n" + "="*60)
    print("✅ ПОДТВЕРЖДЕНИЕ РАССЫЛКИ")
    print("="*60)
    print(f"📝 Длина текста: {len(message_text)} символов")
    print(f"👥 Получателей: {user_count}")
    print(f"🎨 Форматирование: {'HTML' if parse_mode else 'нет'}")
    print(f"🖼 Изображение: {'да' if photo_path else 'нет'}")
    print("="*60)

    confirm = input("\n🚀 Начать рассылку? (y/n): ").strip().lower()

    if confirm == 'y':
        print("\n" + "="*60)
        print("🚀 ЗАПУСК РАССЫЛКИ")
        print("="*60)
        send_broadcast_message(message_text, photo_path, parse_mode)
    else:
        print("✗ Рассылка отменена")


def cleanup():
    """Очистка ресурсов при завершении"""
    global _connection, _cursor
    if _cursor:
        _cursor.close()
    if _connection:
        _connection.close()
        print("\n✓ Соединение с БД закрыто")


if __name__ == "__main__":
    try:
        # Проверяем наличие .env файла
        if not os.path.exists('.env'):
            print("✗ Файл .env не найден!")
            print("\nСоздайте файл .env со следующим содержимым:")
            print("="*60)
            print("""# MySQL settings
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=words

# Telegram Bot Token
TELEGRAM_API=your_bot_token_here

# Optional: default parse mode (HTML, Markdown, or None)
# DEFAULT_PARSE_MODE=HTML""")
            print("="*60)
            sys.exit(1)

        # Проверяем обязательные переменные
        required_vars = ['MYSQL_HOST', 'MYSQL_USER',
                         'MYSQL_PASSWORD', 'TELEGRAM_API']
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(
                f"✗ Отсутствуют обязательные переменные в .env: {', '.join(missing_vars)}")
            sys.exit(1)

        main()

    except KeyboardInterrupt:
        print("\n\n✗ Программа прервана пользователем")
    except Exception as e:
        print(f"\n✗ Неожиданная ошибка: {e}")
    finally:
        cleanup()
