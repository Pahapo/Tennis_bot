import json
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import F, Router

import handlers.keywords as kb
import handlers.functions as f

router = Router()

message_text_send = ''


@router.callback_query(F.data == 'contestant')
async def contestant(callback: CallbackQuery, bot):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    if await f.check_subscription(callback.from_user.id, bot):
        await callback.message.answer(f"<b>Тут ты можешь найти соперника</b> 🙋‍♂️ по уровню игры, возрасту и даже по истории сыгранных турниров\n\nСоздай свою карточку, чтобы другие игроки могли найти тебя 👇\n\n<i>Фильтрация станет доступна в новой версии</i>", parse_mode=ParseMode.HTML, reply_markup=kb.players)
    else:
        await f.check_subscription_message(callback)



@router.callback_query(F.data == 'search_contestant')
async def search_contestant(callback: CallbackQuery, state:FSMContext):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    try:
        # Читаем существующие данные из файла
        with open("players_data.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует, создаем пустой список
        users_data = []

    count_users = 0

    for user in users_data:
        for key, data in user.items():
            if int(key) == user_id: # Все кроме меня
                continue
            count_users += 1

    if count_users > 0:
        await callback.message.answer(f"Список доступных соперников 👇", parse_mode=ParseMode.HTML)
    
        options = LinkPreviewOptions(
            is_disabled=True
        )

        list_players = ''
        num = 1

        data = await state.get_data()
        user_id = data.get("user_id") # взяли из состояния, которое записалось при /start

        for user in users_data:
            for key, data in user.items():
                if int(key) == user_id: # Все кроме меня
                    continue
                else:
                    data_players_text = []
                    for key, value in data.items():
                        if key == 'Имя':
                            if value:
                                data_players_text.append(f'🙋‍♂️ <b>{value.upper()}</b>\n') # Добавить вывод рейтинга в скобках возле имени
                        elif key == 'Ссылка':
                            if value:
                                data_players_text.append(f'{key}: <tg-spoiler>{value}</tg-spoiler>')
                        elif key == 'Предпочтительное время игры':
                            if value:
                                data_players_text.append(f'{key}: <blockquote>{value}</blockquote>')
                        else:
                            if key != 'Наличие бана':
                                if value:
                                    data_players_text.append(f'{key}: {value}')

                    list_players += f"\n\n{'\n'.join(data_players_text)}"
                    num += 1
            

        await callback.message.answer(f"{list_players}", parse_mode=ParseMode.HTML, link_preview_options=options, reply_markup=kb.players_data)
    else:
        await callback.message.answer(f"Нам жаль, но список 📂 доступных соперников пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.players_data)
    


