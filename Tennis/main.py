import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo
import handlers.functions as f
import handlers.match_app as ma
from config.router import router
from config.config import TOKEN, WEBAPP_URL
from webapp.server import start_webapp

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем роутер
dp.include_router(router)

# Запуск бота
async def main():
    asyncio.create_task(f.check_players(bot))  # Запускаем трекер игроков без дивизиона
    asyncio.create_task(ma.match_scheduler(bot))  # Напоминания об играх и запрос счёта
    await start_webapp(bot)  # Запускаем Mini App (веб-сервер)

    if WEBAPP_URL:
        # Кнопка "Приложение" слева от поля ввода сообщения
        await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text='Приложение', web_app=WebAppInfo(url=WEBAPP_URL)))

    await dp.start_polling(bot) # start_polling обращается к серверу телеграмм и спрашивает не пришло ли какое-то сообщение

# Завершение бота
async def shutdown(bot: Bot):
    await bot.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot finished!')