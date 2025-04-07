import asyncio
from aiogram import Bot, Dispatcher
from router import router  # Импортируем основной роутер
from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем роутер
dp.include_router(router)

# Запуск бота
async def main():
    await dp.start_polling(bot) # start_polling обращается к серверу телеграмм и спрашивает не пришло ли какое-то сообщение

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot finished!')
 