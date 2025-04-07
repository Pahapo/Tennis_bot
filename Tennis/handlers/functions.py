import json
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, LinkPreviewOptions, InlineKeyboardButton
from aiogram import F, Router

from config import CHANNEL, CHANNEL_ID, ADMINS, MAIN_EDITOR, EDITOR

import handlers.keywords as kb

router = Router()


adm_start_t = "<b>Привет Хозяин!</b> 👋\n\nПротестируй весь мой функционал, чтобы я работал исправно! 👇"
m_edit_start_t = "Мы рады приветствовать тебя в команде администраторов нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основные задачи:</b>\n\n✅ Распределение игроков по парам;\n✅ Установка рейтинга игрокам;\n✅ Выдача банов\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Мир – Новости</b>"
edit_start_t = "Мы рады приветствовать тебя в команде администраторов нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основная задача:</b>\n\n✅ Создание и контроль турниров\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Минск Мир – Новости</b>"
all_players_start_t = "<b>Увлекаешься теннисом?</b> Давай расскажу, чем я 🤖 буду полезен тебе в ЖК \"Минск Мир\". Я помогу с 👇\n\n• Регистрирацией на турнир;\n• Поиском соперника;\n• Бронированием корта;\n• Приобретением инвентаря\n\n💎 Для начала <b><a href='https://t.me/minskmir_news'>подпишитесь на канал</a>!</b> ⚡️ Здесь ты найдёшь актуальные новости, анонсы ярких мероприятий и обзоры заведений в Минск Мире!\n\n🙋‍♂️ Поддержка @sup_MM"


async def save_user(user_id): # Сохранение пользователей в список для рассылки
    try:
        # Читаем существующие данные из файла
        with open("users.json", "r", encoding="utf-8") as file:
            users = json.load(file)
    except FileNotFoundError:
        # Если файл не существует, создаем пустой список
        users = []

    # Проверяем, есть ли пользователь уже в списке
    if not any(user == user_id for user in users):
        users.append(user_id)  # Добавляем нового пользователя
        with open("users.json", "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)



async def check_subscription(user_id: int, bot) -> bool: # Проверяет, подписан ли пользователь на канал
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False
    

    
async def check_subscription_message(callback: CallbackQuery):
    user_name = callback.from_user.full_name if callback.from_user.username else callback.from_user.username
    await callback.message.answer(f"<b>{user_name}</b>, даю слово, я 🤖 буду помогать тебе до последнего вздоха, но для продолжения <b>подпишись на наш канал</b> 👇", parse_mode=ParseMode.HTML, reply_markup=kb.builder)



@router.callback_query(F.data == 'start_message')
async def start_message(callback: CallbackQuery, bot):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

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
