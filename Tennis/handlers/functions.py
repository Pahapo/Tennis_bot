from datetime import datetime
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram import F, Router
from config.config import CHANNEL, CHANNEL_ID, CHANNEL, ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_start as kb

from config.db import session
from models.User import User

router = Router()


adm_start_t = "<b>Привет Хозяин!</b> 👋\n\nПротестируй весь мой функционал, чтобы я работал исправно! 👇"
m_edit_start_t = "Мы рады приветствовать тебя в команде администраторов нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основные задачи:</b>\n\n✅ Распределение игроков по парам;\n✅ Анализ дивизиона для игроков;\n✅ Выдача банов\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Мир – Новости</b>"
edit_start_t = "Мы рады приветствовать тебя в команде администраторов нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основная задача:</b>\n\n✅ Создание и контроль турниров\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Минск Мир – Новости</b>"
all_players_start_t = "<b>Увлекаешься теннисом?</b> Давай расскажу, чем я 🤖 буду полезен тебе в ЖК \"Минск Мир\" 👇\n\n✅ Регистрирация на турнир;\n✅ Поиск соперников;\n✅ Бронирование корта;\n✅ Приобретение инвентаря\n\n💎 Для начала <b><a href='https://t.me/minskmir_news'>подпишитесь на канал</a>!</b> ⚡️ Здесь ты найдёшь актуальные новости, анонсы ярких мероприятий и обзоры заведений в Минск Мире!\n\n🙋‍♂️ Поддержка @sup_MM"


async def save_user(user_id, user_name, user_link): # Сохранение пользователей в список для рассылки

    user = session.query(User).filter_by(tg_user_id = user_id).first()
    if not user:
        print(f"Новый пользователь нажал /start")
        new_user = User(tg_user_id = user_id, name_user = user_name, link = user_link)
        session.add(new_user)  # Добавляем объект в сессию
        session.commit() # Сохраняем изменения (фиксируем транзакцию)



async def check_subscription(user_id: int, bot) -> bool: # Проверяет, подписан ли пользователь на канал
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False
    

    
async def check_subscription_message(callback: CallbackQuery):
    user_name = callback.from_user.full_name if callback.from_user.username else callback.from_user.username
    await callback.message.answer(f"<b>{user_name}</b>, даю слово, я 🤖 буду помогать тебе до последнего вздоха, но для продолжения <b>подпишись на наш канал</b> 👇", parse_mode=ParseMode.HTML, reply_markup=kb.builder)


async def check_ban_user(user_id):
    user = session.query(User).filter_by(tg_user_id = user_id).first()
    if user.ban_status:
        end_date = datetime.strptime(user.end_date_ban, "%d.%m.%Y")

        if datetime.today() > end_date:
            user.end_date_ban = None
            user.ban_status = None
            session.commit() # Сохраняем изменения (фиксируем транзакцию)


@router.callback_query(F.data == 'start_message')
async def start_message(callback: CallbackQuery, bot):
    await callback.answer('')

    user_name = callback.from_user.full_name if callback.from_user.username else callback.from_user.username
    user_id = callback.from_user.id

    options = LinkPreviewOptions(
        url=CHANNEL,
        prefer_small_media=True
    )

    if user_id in ADMINS:
        await callback.message.answer(adm_start_t, parse_mode=ParseMode.HTML, reply_markup=kb.main_admin_btn)
    elif user_id in MAIN_EDITOR:
        await callback.message.edit_text(f"<b>Уважаемый {user_name}!</b> 👋\n\n{m_edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.main_edit_btn)
    elif user_id in EDITOR:
        await callback.message.edit_text(f"<b>Уважаемый {user_name}!</b> 👋\n\n{edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.edit_btn)
    else:
        await callback.message.edit_text(f"<b>Привет {user_name}!</b> 👋\n\n{all_players_start_t}", link_preview_options=options, parse_mode=ParseMode.HTML, reply_markup=kb.main_btn)

async def output_edits_list():
    edits = session.query(User).filter(User.tg_user_id.in_(EDITOR)).all() # Получаем список User с указанным free_time
    edit_list = ''
    for edit in edits:
        edit_list += f"\n🙋‍♂️ <a href='{edit.link}'>{edit.name_user}</a>"
    return edit_list