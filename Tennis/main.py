import asyncio
from aiogram import Bot, Dispatcher
import handlers.functions as f
from config.router import router
from config.config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем роутер
dp.include_router(router)

# Запуск бота
async def main():
    # asyncio.create_task(f.check_players(bot))  # Запускаем трекер игроков без дивизиона   # ВКЛЮЧИТЬ ПОСЛЕ ТЕСТИРОВАНИЯ ! ! ! ! ! !
    await dp.start_polling(bot) # start_polling обращается к серверу телеграмм и спрашивает не пришло ли какое-то сообщение


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot finished!')