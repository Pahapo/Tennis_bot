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
    

def validate_comment(comment: str) -> bool:
    """Проверяет, что комментарий не превышает 300 символов."""
    return len(comment) <= 300


def validate_date(text: str) -> bool:
    """Проверяет, что дата соответствует формату DD.MM.YYYY и является реальной."""
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    
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

