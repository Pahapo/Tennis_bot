import json
from aiogram import F, Router
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode

import handlers.keywords as kb
import handlers.functions as f

router = Router()

message_text_send = ''

# Не отвечает, перепроверить!

@router.callback_query(F.data == 'tournament_lists')
async def search_contestant(callback: CallbackQuery):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    try:
        # Читаем существующие данные из файла
        with open("tournaments.json", "r", encoding="utf-8") as file:
            tournaments_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует, создаем пустой список
        tournaments_data = []

    if tournaments_data:
        await callback.message.answer(f"Список доступных турниров 👇", parse_mode=ParseMode.HTML)
    
        options = LinkPreviewOptions(
            is_disabled=True
        )

        list_tournaments = ''
        name_tournament = ''
        num = 1

        for tournament in tournaments_data:
            for key, data in tournament.items():
                    data_tournaments_text = []
                    for key, value in data.items():
                        if key == 'Название турнира':
                            name_tournament = value
                        else:
                            if value:
                                data_tournaments_text.append(f'{key}: {value}')

                    data = '\n'.join(data_tournaments_text)
                    list_tournaments += f"🏆 <b>Турнир {name_tournament.upper()}</b>\n\n{data}\n\n"
                    num += 1
            

        await callback.message.answer(f"{list_tournaments}", parse_mode=ParseMode.HTML, link_preview_options=options, reply_markup=kb.tournaments_data)
    else:
        await callback.message.answer(f"Нам жаль, но список 📂 турниров пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.tournaments_data)
    


