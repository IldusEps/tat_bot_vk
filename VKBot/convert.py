import re

def remove_vk_formatting(text: str) -> str:
    """
    Удаляет всё форматирование VK из текста
    
    Удаляет:
    - **жирный**
    - *курсив*
    - __подчеркнутый__
    - ~~зачеркнутый~~
    - [[моноширинный]]
    - [текст|ссылка]
    - === заголовок ===
    - == заголовок ==
    - = заголовок =
    - * пункт списка
    - --- разделитель
    """
    if not text:
        return text
    
    # Удаляем ссылки [текст|url] -> текст
    text = re.sub(r'\[(.*?)\|.*?\]', r'\1', text)
    
    # Удаляем заголовки
    text = re.sub(r'===\s*(.*?)\s*===', r'\1', text)
    text = re.sub(r'==\s*(.*?)\s*==', r'\1', text)
    text = re.sub(r'=\s*(.*?)\s*=', r'\1', text)
    
    # Удаляем форматирование
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)      # Жирный
    text = re.sub(r'\*(.*?)\*', r'\1', text)          # Курсив
    text = re.sub(r'__(.*?)__', r'\1', text)          # Подчеркнутый
    text = re.sub(r'~~(.*?)~~', r'\1', text)          # Зачеркнутый
    text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)      # Моноширинный
    
    # Удаляем маркеры списков
    text = re.sub(r'^\*\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Удаляем разделители
    text = re.sub(r'^---$', '', text, flags=re.MULTILINE)
    
    # Очистка лишних пробелов
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

def simple_markdown_to_vk(markdown_text: str) -> str:
    """
    Упрощенная конвертация Markdown в VK Wiki
    
    Поддерживает:
    - Жирный: **текст** -> **текст**
    - Курсив: *текст* -> *текст*
    - Зачеркнутый: ~~текст~~ -> ~~текст~~
    - Ссылки: [текст](url) -> [текст|url]
    - Заголовки: # H1 -> === H1 ===
    """
    text = markdown_text
    
    # Заголовки
    text = re.sub(r'^# (.*?)$', r'=== \1 ===', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'== \1 ==', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'= \1 =', text, flags=re.MULTILINE)
    
    # Форматирование
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'***\1***', text)  # Жирный+курсив
    text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)        # Жирный
    text = re.sub(r'__(.*?)__', r'**\1**', text)            # Жирный
    text = re.sub(r'\*(.*?)\*', r'*\1*', text)              # Курсив
    text = re.sub(r'_(.*?)_', r'*\1*', text)                # Курсив
    text = re.sub(r'~~(.*?)~~', r'~~\1~~', text)            # Зачеркнутый
    
    # Ссылки
    def replace_link(match):
        return f"[{match.group(1)}|{match.group(2)}]"
    text = re.sub(r'\[(.*?)\]\((.*?)\)', replace_link, text)
    
    return text

def html_to_vk(html_text: str) -> str:
    """
    Расширенная конвертация с обработкой вложенных тегов
    """
    text = html_text
    
    # Обрабатываем вложенные теги (жирный+курсив)
    text = re.sub(r'<b><i>(.*?)</i></b>', r'***\1***', text)
    text = re.sub(r'<i><b>(.*?)</b></i>', r'***\1***', text)
    
    # Обрабатываем каждый тип
    conversions = [
        # Заголовки
        (r'<h1>(.*?)</h1>', r'=== \1 ==='),
        (r'<h2>(.*?)</h2>', r'== \1 =='),
        (r'<h3>(.*?)</h3>', r'= \1 ='),
        
        # Форматирование
        (r'<b>(.*?)</b>', r'**\1**'),
        (r'<strong>(.*?)</strong>', r'**\1**'),
        (r'<i>(.*?)</i>', r'*\1*'),
        (r'<em>(.*?)</em>', r'*\1*'),
        (r'<u>(.*?)</u>', r'__\1__'),
        (r'<s>(.*?)</s>', r'~~\1~~'),
        (r'<strike>(.*?)</strike>', r'~~\1~~'),
        (r'<del>(.*?)</del>', r'~~\1~~'),
        (r'<code>(.*?)</code>', r'[[\1]]'),
        
        # Ссылки
        (r'<a href="(.*?)">(.*?)</a>', lambda m: f"[{m.group(2)}|{m.group(1)}]"),
        
        # Структура
        (r'<p>(.*?)</p>', r'\1\n'),
        (r'<br\s*/?>', '\n'),
        (r'<hr\s*/?>', '---'),
    ]
    
    for pattern, replacement in conversions:
        if callable(replacement):
            text = re.sub(pattern, replacement, text, flags=re.DOTALL)
        else:
            text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    
    # Списки
    def process_list(match, is_ordered=False):
        items = re.findall(r'<li>(.*?)</li>', match.group(0), re.DOTALL)
        result = []
        for i, item in enumerate(items, 1):
            if is_ordered:
                result.append(f"{i}. {item.strip()}")
            else:
                result.append(f"* {item.strip()}")
        return '\n'.join(result)
    
    text = re.sub(r'<ol>(.*?)</ol>', lambda m: process_list(m, True), text, flags=re.DOTALL)
    text = re.sub(r'<ul>(.*?)</ul>', lambda m: process_list(m, False), text, flags=re.DOTALL)
    
    # Удаляем все оставшиеся теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Очистка
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text