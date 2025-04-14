from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import F, Router
from sqlalchemy import func

import keywords.kw_tournament as kb
import handlers.btn_tournaments as bt
import handlers.functions as f

from config.db import session
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.User import User

router = Router()


@router.callback_query(F.data == 'edit_tournament')
async def tournament_edit(callback: CallbackQuery):
    await callback.answer('')  # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await callback.message.answer(f"<b>Тут происходит редактирование турниров</b>\n\n• Если необходимо изменить карточку уже существующего турнира, создай <b>новый с таким же названием</b>! Турнир отредактируется\n\nВыбери нужное 👇", parse_mode=ParseMode.HTML, reply_markup=kb.edit_tournament)
    

@router.callback_query(F.data == 'tournament_info')
async def tournament_info(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await f.check_ban_user(callback.from_user.id) # проверка на бан

    if bt.get_list_tournaments() == []:
        await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но в данный момент нет ни одного доступного турнира...', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    else: 
        await callback.message.answer(f"<b>Тут отображаются доступные турниры, в которых можно принять участие</b>\n\nДоступные турниры 👇", parse_mode=ParseMode.HTML, reply_markup=kb.tournament_info)
    

@router.callback_query(F.data.in_(bt.get_list_tournaments())) 
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('')      

    user_id = call.from_user.id
    selected_tournament = call.data  # Получаем название выбранного турнира
    await state.update_data(selected_tournament = selected_tournament)  # Сохраняем user_id в состояние

    # Получаем турнир
    tournament_data = session.query(Tournament).filter(Tournament.name_tournament==selected_tournament).first()
    # Запрос "зареган ли юзер на выбранный им турнир?"
    user_in_tournament = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user_id, TournamentPlayers.id_tournament == tournament_data.tournament_id).all()
    # Запрос для подсчёта количества игроков
    player_count = session.query(func.count()).filter(TournamentPlayers.id_tournament == tournament_data.tournament_id).scalar()

    user = session.query(User).filter_by(tg_user_id = user_id).first()

    if int(player_count) >= int(tournament_data.quantity_person):            
        await call.message.answer(f'<b>Мест больше нет</b> 🥲\n\nНам жаль, но на турнир уже записаться нельзя...\nПроверь другие доступные турниры или дождись нового 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user_in_tournament:
        await call.message.answer(f'<b>Вы уже участвуете в турнире!</b> ✅\n\nОжидайте завершения регистрации других участников', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user.ban_status == True:
        await call.message.answer(f'<b>🚫 Вы не можете участвовать в турнире из-за бана</b> 🥲\n\nНам жаль, но на этот турнир записаться нельзя...\nБан будет снят {user.end_date_ban} 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    else:
        await call.message.answer(f"📋 <b>Регламент:</b>\n\n<b>1. ГРУППОВАЯ СТАДИЯ</b>\n<b><i>Количество групп:</i></b>\n- 4 группы по 4 игрока\n\n<b>Формирование групп:</b>\n- Распределение по группам производится посредством жеребьевки\n- Участники разбиваются на 4 корзины по 4 человека, исходя из уровня игры\n- В каждой группе оказывается по 4 игрока, каждый из которых из разных корзин\n\n<b><i>Формат матчей в группе:</i></b>\nСхема матчей: Каждый с каждым 🤺🎾\nФормат матча: Трехсетовый\n\nЕсли после двух сетов результат равный (1-1), третий сет играется в формате супертайбрейка:\nИгра до 10 очков (минимальный перевес для победы – 2 очка)\nЕсли потребуется считать геймы для определения лучшего по дополнительным показателям, супертайбрейк засчитывается как 1 гейм\n\n<b><i>Выход в плей-офф:</i></b>\nДва лучших игрока из каждой группы переходят в следующий этап\n\n<b>2. ПЛЕЙ-ОФФ</b>\n<b><i>Четвертьфиналы:</i></b>\nПосле завершения групповой стадии проводится жеребьевка четвертьфинала.Занявшие первые места в группах играют с занявшими вторые\n\n<b><i>Полуфиналы:</i></b>\nПроводится дополнительная жеребьевка полуфинала.\nУчастники из одной группы разводятся до финала\n\n<b><i>Формат матчей в плей-офф:</i></b>\nФинал и матч за третье место:\nПолноценные трехсетовые матчи 🥇🥈🥉\n\nЧетвертьфиналы и полуфиналы:\nФормат определяется по договоренности между соперниками:\n- Либо полноценные трехсетовики.\n- Либо замена 3-го сета супертайбрейком (до 10 с разницей в 2 очка).\n- Если договоренность не достигнута, применяется супертайбрейк\n\n<b>3.  ОГРАНИЧЕНИЕ ПО ВРЕМЕНИ</b> ⏰\nТурнир ограничен по времени – 3 недели с момента старта.\nИгры, не сыгранные в этот период, будут рассматриваться в индивидуальном порядке\n\n<b>4. ТУРНИРНЫЙ ВЗНОС</b> 💰\n {tournament_data.price} бел.руб.", parse_mode=ParseMode.HTML, reply_markup=kb.reglament)

# После прохождения турнира добавлять в карточку игрока название турнира, как история (код выше)