import os
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config.config import BOT_USERNAME

import keywords.kw_any as ka
import keywords.kw_payment as kp
import keywords.kw_tournament as kb
import handlers.btn_referrals as rf
import handlers.validation as valid
import handlers.functions as f
import handlers.classes as cl

from config.db import session
from models.Referrals import Referrals
from models.Tournament import Tournament
from models.User import User


router = Router()


async def generate_referral_link(user_id: int):
    return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"



@router.callback_query(F.data == 'referral_system')
async def referral_system(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        user_id = callback.from_user.id

        user = session.query(User).filter(User.tg_user_id == user_id).first()

        if user:
            coins = ''
            if user.coins == None:
                coins = 0
            else:
                coins = user.coins
            refferal_link = await generate_referral_link(user_id)

            invite_text = "\nПрисоединяйся к нашему теннисному клубу 🎾 и участвуй в турнирах! 🏆"
            referral_system = rf.generate_share_referral_link(user_id, invite_text)

            if os.path.exists("Tennis/img/referral/referral.png"):  # Проверка, есть ли файл
                photo = FSInputFile("Tennis/img/referral/referral.png")  # Загружаем файл
                await callback.message.answer_photo(photo, caption=f'<b>📊 Ваша реферальная статистика</b>\n\n💰 <b>Монеты:</b> {coins}\n🔗 <b>Ваша ссылка:</b> <code>{refferal_link}</code>\n\n😎 Приглашайте друзей и получайте 100 монет за каждого приглашённого!', parse_mode=ParseMode.HTML, reply_markup=referral_system)
            else:
                await callback.message.answer(f'<b>📊 Ваша реферальная статистика</b>\n\n💰 <b>Монеты:</b> {coins}\n🔗 <b>Ваша ссылка:</b> <code>{refferal_link}</code>\n\n😎 Приглашайте друзей и получайте 100 монет за каждого приглашённого!', parse_mode=ParseMode.HTML, reply_markup=referral_system)
        else:
            await callback.message.answer(f'<b>Произошла ошибка загрузки страницы!</b>\n\n• Пожалуйста, свяжитесь с поддержкой бота! Их контакт есть в описании бота', parse_mode=ParseMode.HTML, reply_markup=ka.exit)
    else:
        await f.check_subscription_message(callback)



async def check_referral(args, user_id, bot):
    # Если есть реферальный код (например, /start ref_user_id)
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = int(args[1][4:])  # Извлекаем ID (ref_user_id → user_id)
        
        try:
            # Проверяем, новый ли это пользователь
            check_new_user = session.query(User).filter(User.tg_user_id == user_id).first()

            if not check_new_user:

                # Проверяем, что пользователь не пригласил сам себя
                if referrer_id != user_id:
                    referrer = session.query(Referrals).filter(Referrals.tg_users_id == referrer_id).first()
                    referrer_user = session.query(User).filter(User.tg_user_id == referrer_id).first()
                    coins = referrer_user.coins
                    
                    if referrer:
                        referrers_id_list = referrer.referrals.split(",")  # Разбиваем строку на список
                        
                        if user_id not in referrers_id_list:  # Проверяем, приглашал ли пользователь уже этого реферала                

                            referrer.referrals += f", {user_id}"
                            referrer.count += 1

                            # Увеличиваем баллы у реферрера
                            if referrer_user:
                                referrer_user.coins += 100
                                coins += 100

                            try:
                                session.commit()
                            except IntegrityError as e:
                                session.rollback()
                                if "unique constraint" in str(e).lower():
                                    print(f"Ошибка: дубликат данных (пользователь {user_id} или ссылка уже существуют)")
                                else:
                                    print(f"Неизвестная IntegrityError: {e}")
                            except OperationalError as e:
                                session.rollback()
                                print(f"Ошибка подключения к БД: {e}")
                            except DatabaseError as e:
                                session.rollback()
                                print(f"Общая ошибка БД: {e}")
                            except Exception as e:
                                session.rollback()
                                print(f"Ошибка в БД. Подробнее: {e}")
                        else:
                            return
                    else:
                        new_referrer = Referrals(tg_users_id = referrer_id, referrals = user_id, count = 1)
                        if new_referrer:
                            session.add(new_referrer)  # Добавляем объект в сессию

                        # Увеличиваем баллы у реферрера
                        if referrer_user:
                            referrer_user.coins = 100
                            coins = 100
                        
                        try:
                            session.commit()
                        except IntegrityError as e:
                            session.rollback()
                            if "unique constraint" in str(e).lower():
                                print(f"Ошибка: дубликат данных (пользователь {user_id} или ссылка уже существуют)")
                            else:
                                print(f"Неизвестная IntegrityError: {e}")
                        except OperationalError as e:
                            session.rollback()
                            print(f"Ошибка подключения к БД: {e}")
                        except DatabaseError as e:
                            session.rollback()
                            print(f"Общая ошибка БД: {e}")
                        except Exception as e:
                            session.rollback()
                            print(f"Ошибка в БД. Подробнее: {e}")
                    
                    # Оповещаем реферреру о новом реферале
                    message_text_send = f"<b>По Вашей ссылке зарегистрировался новый реферал! 🚀</b>\n\n🙋‍♂️ <b>Реферал:</b> {check_new_user.name_user}\n💰 <b>Монеты:</b> {coins}"

                    try:
                        await bot.send_message(chat_id=referrer_id, text=message_text_send, parse_mode="HTML", reply_markup=ka.exit)
                        print(f"Игроку с id {referrer_id} отпралено уведомление о новом реферале ({user_id})!")
                    except Exception as e:
                        print(f"❌ Игроку с id {referrer_id} НЕ было отпралено уведомление о новом реферале ({user_id}) из-за ошибки: {e}")
                    
                return
            return
        except Exception as e:
            print(f"Произошла ошибка при работе с рефералами. Подробнее: {e}")
    return


@router.callback_query(F.data == 'use_coins_q')
async def use_coins_q(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    data = await state.get_data()
    user_id = callback.from_user.id

    user = session.query(User).filter(User.tg_user_id == user_id).first()

    if user:
        remaining_coins = ''
        if user.coins == None:
            remaining_coins = 0
        else:
            if data.get("coins"):
                remaining_coins = user.coins - data.get("coins")
            else: 
                remaining_coins = user.coins

        await state.update_data(remaining_coins = remaining_coins)
        await callback.message.answer(f'<b>📊 Ваша реферальная статистика</b>\n\n💰 <b>Монеты:</b> {remaining_coins}\n\n<b>Хотите использовать монеты?</b>', parse_mode=ParseMode.HTML, reply_markup=kb.use_coins_q)
    else:
        await callback.message.answer(f'<b>Произошла ошибка загрузки страницы!</b>\n\n• Пожалуйста, свяжитесь с поддержкой бота! Их контакт есть в описании бота', parse_mode=ParseMode.HTML, reply_markup=ka.exit)


@router.callback_query(F.data == 'use_coins')
async def use_coins(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    await state.set_state(cl.UsedCoins.coins)
    await callback.message.answer('Введите количество монет, которое хотите использовать 👇')


@router.message(cl.UsedCoins.coins)
async def register_age(message: Message, state:FSMContext):
    coins = message.text

    # Проверяем, корректно ли введено количество монет
    if not valid.validate_isdigit(coins):
        await message.answer("⚠ Ошибка! Введите <b>целое положительное число</b>. Попробуйте снова 👇", parse_mode=ParseMode.HTML)
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова
    
    await state.set_state(None)

    data = await state.get_data()
    selected_tournament = data.get("selected_tournament")
    
    if int(coins) >= 300:
        if int(coins) <= data.get("remaining_coins"):

            tournament = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()

            sale = int(coins) / 100
            if sale < tournament.price * 0.5:

                await state.update_data(coins = int(coins))
                await message.answer(f'✅ <b>Монеты применены!\n\n😎 Стоимость участия уменьшена на {sale} бел.руб.</b>', parse_mode=ParseMode.HTML, reply_markup=kp.payment_with_coins)
            else:    
                await message.answer('<b>Вы не можете погасить больше 30% от взноса на турнир! 🥲</b>\n\n💰 Хотите использовать монеты?', parse_mode=ParseMode.HTML, reply_markup=kb.use_coins_q)
        else:
            await message.answer('<b>У Вас нет столько монет! 😅</b>\n\n💰 Хотите использовать монеты?', parse_mode=ParseMode.HTML, reply_markup=kb.use_coins_q)
    else:
        await message.answer('<b>Вы не можете применить монеты из-за проходного ограничения! 🥲</b>\n\n• Минимальное использование монет - 300\n\n💰 Хотите использовать монеты?', parse_mode=ParseMode.HTML, reply_markup=kb.use_coins_q)