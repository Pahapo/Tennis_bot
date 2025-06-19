
# # Этот код:
# # - автоматически создаёт чат (рекомендуется до 200 чатов рекомендуется на 1 акк) 
# # - приглашает пользователей
# # - пишет сообщение
# # - закрепляется сообщение (рекомендуется закреплять 1 сообщение раз в 5 минут)

# from telethon.sync import TelegramClient
# from telethon.tl.functions.messages import (
#     CreateChatRequest, 
#     AddChatUserRequest,
#     SendMessageRequest,
#     UpdatePinnedMessageRequest
# )
# from telethon.tl.types import InputPeerUser

# # Настройки
# api_id = 'ВАШ_API_ID'  # Замените
# api_hash = 'ВАШ_API_HASH'  # Замените
# phone = '+375XXXXXXXXX'  # Ваш номер

# # Данные для чата
# chat_title = "Теннис Минск | Дивизион 4.0"  # Название чата
# tournament_name = "Летний кубок 2024"       # Название турнира
# participants = ["username1", "username2"]   # Список участников

# # Шаблон сообщения (можно менять под каждый дивизион/турнир)
# message_template = """
# 🎾 Добро пожаловать в {chat_title}! 🎾

# Турнир: {tournament_name}  
# Формат: 2х2 (пары)  
# Дата: 15–20 июля 2024  

# Важно:  
# 1. Подтвердите участие до 10 июля.  
# 2. Взнос: 20 BYN с пары.  

# Вопросы? Пишите @администратор.  
# """

# with TelegramClient('session_name', api_id, api_hash) as client:
#     # Авторизация
#     client.connect()
#     if not client.is_user_authorized():
#         client.send_code_request(phone)
#         client.sign_in(phone, input('Введите код из Telegram: '))

#     # Создание чата
#     created_chat = client(CreateChatRequest(
#         users=participants,
#         title=chat_title
#     ))
#     chat_id = created_chat.chats[0].id
#     print(f"Чат создан: {chat_id}")

#     # Приглашение участников
#     for user in participants:
#         try:
#             client(AddChatUserRequest(
#                 chat_id=chat_id,
#                 user_id=user,
#                 fwd_limit=10
#             ))
#         except Exception as e:
#             print(f"Ошибка с {user}: {e}")

#     # Отправка сообщения
#     custom_message = message_template.format(
#         chat_title=chat_title,
#         tournament_name=tournament_name
#     )
#     sent_message = client(SendMessageRequest(
#         peer=chat_id,
#         message=custom_message,
#         no_webpage=True
#     ))
#     print("Сообщение отправлено.")

#     # Закрепление сообщения
#     client(UpdatePinnedMessageRequest(
#         peer=chat_id,
#         id=sent_message.id,
#         silent=True
#     ))
#     print("Сообщение закреплено.")