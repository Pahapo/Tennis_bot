import re
from datetime import datetime

def validate_age(age: str) -> bool:
    """Проверяет, что возраст — положительное целое число."""
    return age.isdigit() and int(age) >= 6 and int(age) <=100

def validate_datetime(text: str) -> bool:
    """Проверяет, что дата соответствует формату HH:MM DD.MM.YYYY и является реальной."""
    pattern = r'^(?:[01]\d|2[0-3]):[0-5]\d \d{2}\.\d{2}\.\d{4}$'
    
    if not re.match(pattern, text):
        return False  # Формат неверный
    
    try:
        parsed_date = datetime.strptime(text, "%H:%M %d.%m.%Y")
        return parsed_date > datetime.now()  # Дата должна быть будущей
        # datetime.strptime(text, "%H:%M %d.%m.%Y")
        # return True  # Дата корректна
    except ValueError:
        return False  # Дата невозможная (например, 32 мая)
    
def validate_name(name: str) -> bool:
    """Проверяет, что текст не превышает 64 символов."""
    return len(name) <= 64

def validate_comment(comment: str) -> bool:
    """Проверяет, что текст не превышает 300 символов."""
    return len(comment) <= 300

def validate_start(text: str) -> bool:
    """Проверяет, что текст не равен /start."""
    return text != '/start'

def validate_date(text: str) -> bool:
    """Проверяет, что дата соответствует формату DD.MM.YYYY и является реальной."""
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    
    if not text:
        return False  # Пустая строка

    if not re.match(pattern, text):
        return False  # Формат неверный
    
    try:
        parsed_date = datetime.strptime(text, "%d.%m.%Y")
        return parsed_date > datetime.now()  # Дата должна быть будущей
    except ValueError:
        return False  # Дата невозможная (например, 32 мая)
    
def validate_isdigit(number: str) -> bool:
    """Проверяет на - положительное целое число."""
    return number.isdigit()

def validate_score(score: str) -> bool:
    """Проверяет, что комментарий не превышает 11 символов."""
    return len(score) <= 30

def contains_link(text: str) -> bool:
    """Проверяет, что комментарий не содержит ссылок."""
    return not 'http' in text

def auto_format_score(text: str) -> str:
    """Заменяет дефисы между цифрами на двоеточие."""
    return re.sub(r'(?<!\d)(\d{1,2})-(\d{1,2})(?!\d)', r'\1:\2', text)

def is_valid_score_format(text: str) -> bool:
    """Проверяет строгое соответствие формату: 2 или 3 пары X:Y, разделённые пробелами."""
    pattern_two = r'^\d{1,2}:\d{1,2} \d{1,2}:\d{1,2}$'
    pattern_three = r'^\d{1,2}:\d{1,2} \d{1,2}:\d{1,2} \d{1,2}:\d{1,2}$'
    return re.fullmatch(pattern_two, text) or re.fullmatch(pattern_three, text)
