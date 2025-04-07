import json
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import F, Router

import handlers.keywords as kb
import handlers.btn_tournaments as bt


router = Router()



@router.callback_query(F.data == 'edit_tournament')
async def tournament_edit(callback: CallbackQuery):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await callback.message.answer(f"<b>Тут происходит редактирование турниров</b>\n\nЕсли необходимо изменить карточку уже существующего турнира, создай <b>новый с таким же именем</b>! Тогда он отредактируентся\n\nВыбери нужное 👇", parse_mode=ParseMode.HTML, reply_markup=kb.edit_tournament)
    

@router.callback_query(F.data == 'tournament_info')
async def tournament_info(callback: CallbackQuery):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    if bt.get_list_tournaments() == []:
        await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но в данный момент нет ни одного доступного турнира...', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    else: 
        await callback.message.answer(f"<b>Тут отображаются доступные турниры, в которых можно принять участие</b>\n\nДоступные турниры 👇", parse_mode=ParseMode.HTML, reply_markup=kb.tournament_info)
    

@router.callback_query(F.data.in_(bt.get_list_tournaments()))   # Переделать под автоматизацию как с кнопками, так и в этой функции (шапка + try -> for)
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать       

    user_id = call.from_user.id

    try:
        # Читаем существующие данные из файла
        with open("tournament1.json", "r", encoding="utf-8") as file: # исправить название под каждый турнир
            players_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        players_data = []
    
    try:
        # Читаем существующие данные из файла
        with open("tournaments.json", "r", encoding="utf-8") as file:
            tournaments_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        tournaments_data = []


    count_players = len(players_data) # количество участников в турнире
    max_count_players = ''
    participation_bool = False
    price = ''
    name_turnament = ''

    for player in players_data: # проверка на наличие игрока в регистрации на турнир
        for key in player.keys():
            if int(key) == user_id:
                participation_bool = True
                break

    for tournament in tournaments_data: # поиск максимального количества участников в турнире
        for key, data in tournament.items():
            if key in bt.get_list_tournaments():                              # ПРОВЕРИТЬ РАБОТУ

                await state.update_data(tournament_name = key)  # Сохраняем user_link в состояние
                name_turnament = key

                for key, value in data.items():
                    if key == 'Максимальное кол-во участников':
                        if value:
                            max_count_players = value
                    elif key == 'Стоимость участия':
                        price = value
                        break

    if int(count_players) >= int(max_count_players):            
        await call.message.answer(f'<b>Мест больше нет</b> 🥲\n\nНам жаль, но на турнир уже записаться нельзя...\nПроверь другие доступные турниры или дождись нового 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)

    elif participation_bool:
        await call.message.answer(f'<b>Вы уже участвуете в турнире!</b> ✅\n\nОжидайте завершения регистрации других участников', parse_mode=ParseMode.HTML, reply_markup=kb.exit)

    else:
        await call.message.answer(f"📋 <b>Регламент:</b>\n\n<b>1. ГРУППОВАЯ СТАДИЯ</b>\n<b><i>Количество групп:</i></b>\n- 4 группы по 4 игрока\n\n<b>Формирование групп:</b>\n- Распределение по группам производится посредством жеребьевки\n- Участники разбиваются на 4 корзины по 4 человека, исходя из уровня игры\n- В каждой группе оказывается по 4 игрока, каждый из которых из разных корзин\n\n<b><i>Формат матчей в группе:</i></b>\nСхема матчей: Каждый с каждым 🤺🎾\nФормат матча: Трехсетовый\n\nЕсли после двух сетов результат равный (1-1), третий сет играется в формате супертайбрейка:\nИгра до 10 очков (минимальный перевес для победы – 2 очка)\nЕсли потребуется считать геймы для определения лучшего по дополнительным показателям, супертайбрейк засчитывается как 1 гейм\n\n<b><i>Выход в плей-офф:</i></b>\nДва лучших игрока из каждой группы переходят в следующий этап\n\n<b>2. ПЛЕЙ-ОФФ</b>\n<b><i>Четвертьфиналы:</i></b>\nПосле завершения групповой стадии проводится жеребьевка четвертьфинала.Занявшие первые места в группах играют с занявшими вторые\n\n<b><i>Полуфиналы:</i></b>\nПроводится дополнительная жеребьевка полуфинала.\nУчастники из одной группы разводятся до финала\n\n<b><i>Формат матчей в плей-офф:</i></b>\nФинал и матч за третье место:\nПолноценные трехсетовые матчи 🥇🥈🥉\n\nЧетвертьфиналы и полуфиналы:\nФормат определяется по договоренности между соперниками:\n- Либо полноценные трехсетовики.\n- Либо замена 3-го сета супертайбрейком (до 10 с разницей в 2 очка).\n- Если договоренность не достигнута, применяется супертайбрейк\n\n<b>3.  ОГРАНИЧЕНИЕ ПО ВРЕМЕНИ</b> ⏰\nТурнир ограничен по времени – 3 недели с момента старта.\nИгры, не сыгранные в этот период, будут рассматриваться в индивидуальном порядке\n\n<b>4. ТУРНИРНЫЙ ВЗНОС</b> 💰\n {price} бел.руб.", parse_mode=ParseMode.HTML, reply_markup=kb.reglament)


    # Записываем словарь в список
    try:
        # Читаем существующие данные из файла
        with open("players_data.json", "r", encoding="utf-8") as file:
            players_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует, создаем пустой список
        players_data = []

    for i, user in enumerate(players_data):
        if str(user_id) in user:
            for data in players_data[i].value():
                for key, value in data.items():
                    if key == 'Участие в турнире':
                        if value == None:
                            value = name_turnament
                        else:
                            value.append(name_turnament)       # А ТОЧНО ЛИ ЭТО МАССИВ???    
                        break

    with open("players_data.json", "w", encoding="utf-8") as file:
        json.dump(players_data, file, ensure_ascii=False, indent=4)    


# После прохождения турнира добавлять в карточку игрока название турнира, как история (код выше)