from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from datetime import datetime
import pytz
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
import asyncio
from threading import Thread
from aiogram import Bot
import os
from config.config import TOKEN, DATABASE_URL

# Инициализация Flask приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Секретный ключ
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Подключение к базе данных
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

# Инициализация бота
bot = Bot(token=TOKEN)

@app.route('/')
def home():
    """Главная страница"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        # Используем text() для SQL запросов
        user = db.execute(
            text("SELECT * FROM users WHERE tg_user_id = :id"),
            {"id": user_id}
        ).fetchone()
        
        if user:
            session['user_id'] = user_id
            session['user_name'] = user.name_user
            return redirect(url_for('home'))
        return render_template('login.html', error="Пользователь не найден")
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    return redirect(url_for('login'))

# переделал запрос и поигрался немного со страницей ! ! !

@app.route('/tournaments')
def tournaments():
    """Список турниров"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tournaments = db.execute(text("""
        SELECT * FROM tournament 
        WHERE STR_TO_DATE(end_tournament, '%d.%m.%Y') >= CURDATE()
        ORDER BY STR_TO_DATE(start_tournament, '%d.%m.%Y')

    """)).fetchall()
    
    return render_template('tournaments.html', tournaments=tournaments)

@app.route('/booking')
def booking():
    """Бронирования пользователя"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    bookings = db.execute(text("""
        SELECT * FROM matches 
        WHERE id_tg_user = :user_id 
        AND (date_booking IS NOT NULL OR date_without_booking IS NOT NULL)
        ORDER BY COALESCE(date_booking, date_without_booking)
    """), {"user_id": session['user_id']}).fetchall()
    
    return render_template('booking.html', bookings=bookings)

@app.route('/profile')
def profile():
    """Профиль пользователя"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.execute(
        text("SELECT * FROM users WHERE tg_user_id = :id"),
        {"id": session['user_id']}
    ).fetchone()
    
    tournaments = db.execute(text("""
        SELECT t.name_tournament, t.start_tournament 
        FROM tournament_players tp
        JOIN tournament t ON tp.id_tournament = t.tournament_id
        WHERE tp.id_tg_user = :user_id
    """), {"user_id": session['user_id']}).fetchall()
    
    return render_template('profile.html', user=user, tournaments=tournaments)

@app.route('/api/matches')
def get_matches():
    """API для получения списка матчей"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    matches = db.execute(text("""
        SELECT m.*, u.name_user, u.link 
        FROM matches m
        JOIN users u ON m.id_tg_user = u.tg_user_id
        WHERE m.player_1 IS NULL AND m.player_2 IS NULL
        AND u.tg_user_id != :user_id
        ORDER BY COALESCE(m.date_booking, m.date_without_booking)
    """), {"user_id": session['user_id']}).fetchall()
    
    return jsonify([dict(match) for match in matches])

def run_bot(dp):  # принимаем dp как аргумент
    asyncio.run(dp.start_polling(bot))


if __name__ == '__main__':
    from config.config import dp  # импорт только при запуске
    # Создаем необходимые папки
    os.makedirs('web/static/css', exist_ok=True)
    os.makedirs('web/static/js', exist_ok=True)
    os.makedirs('web/templates', exist_ok=True)
    
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask
    app.run(host='0.0.0.0', port=5000, debug=True)