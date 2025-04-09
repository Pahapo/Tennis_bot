import asyncio
from aiogram import Bot, Dispatcher
from router import router  # Импортируем основной роутер
from config import TOKEN

# from db import db_connection, cursor
# def add_news(nameperson, age):
#     query = "INSERT INTO test (nameperson, age) VALUES (%s, %s)"
#     cursor.execute(query, (nameperson, age))
#     db_connection.commit()
#     print("User добавлен!")


bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем роутер
dp.include_router(router)

# Запуск бота
async def main():
    # add_news("Lera", 22)
    await dp.start_polling(bot) # start_polling обращается к серверу телеграмм и спрашивает не пришло ли какое-то сообщение


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot finished!')
 