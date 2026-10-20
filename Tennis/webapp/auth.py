import hmac
import hashlib
import json
import time
from urllib.parse import parse_qsl
from config.config import TOKEN

MAX_AGE_SECONDS = 86400  # Данные от Telegram действительны 24 часа


# Проверка подписи initData (https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)
def check_init_data(init_data: str):
    if not init_data:
        return None

    data = dict(parse_qsl(init_data))
    received_hash = data.pop('hash', None)

    if received_hash == None:
        return None

    # Собираем строку для проверки: все поля, кроме hash, по алфавиту, каждое с новой строки
    lines = []
    for key in sorted(data.keys()):
        lines.append(f"{key}={data[key]}")
    data_check_string = "\n".join(lines)

    secret_key = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None  # Подпись не совпала — данные подделаны

    auth_date = int(data.get('auth_date', '0'))
    if time.time() - auth_date > MAX_AGE_SECONDS:
        return None  # Данные устарели

    if 'user' not in data:
        return None

    return json.loads(data['user'])  # {'id': ..., 'first_name': ..., 'username': ..., 'photo_url': ...}


# Получение пользователя Telegram из запроса Mini App (None, если запрос не из Telegram)
def get_tg_user(request):
    init_data = request.headers.get('X-Init-Data', '')
    return check_init_data(init_data)
