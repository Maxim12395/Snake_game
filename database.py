from pathlib import Path
import hashlib

from kivy.storage.jsonstore import JsonStore
from os.path import join
from kivy.app import App
import os
import sqlite3
from kivy.utils import platform

DB_NAME = 'snake_game.db'

def init_db():
    if platform == 'android':
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), DB_NAME)
    else:
        db_path = DB_NAME

    # Проверяем, существует ли файл БД
    first_run = not os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if first_run:
        # Создаем таблицы только при первом запуске
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            high_score INTEGER DEFAULT 0,
            speed TEXT DEFAULT 'Средне',
            sound INTEGER DEFAULT 1,
            theme TEXT DEFAULT 'Светлая'
        )''')
        conn.commit()

    conn.close()

def create_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            return True
        except sqlite3.IntegrityError:
            return False

def validate_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return c.fetchone() is not None

def get_user_settings(username):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT speed, sound, theme FROM users WHERE username=?", (username,))
        return c.fetchone()

def update_user_settings(username, speed, sound, theme):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE users SET speed=?, sound=?, theme=? WHERE username=?",
                     (speed, sound, theme, username))

def update_score(username, score):
    """Обновляет рекорд пользователя, если новый счет больше текущего рекорда"""
    with sqlite3.connect(DB_NAME) as conn:
        # Сначала получаем текущий рекорд
        c = conn.cursor()
        c.execute("SELECT high_score FROM users WHERE username=?", (username,))
        result = c.fetchone()
        if result:
            current_high_score = result[0]
            if score > current_high_score:
                conn.execute("UPDATE users SET high_score=? WHERE username=?", (score, username))
                conn.commit()
                return True
        return False

def get_or_create_profile(username):
    """Создает профиль пользователя, если его нет, или возвращает существующий"""
    with sqlite3.connect(DB_NAME) as conn:
        try:
            # Пытаемся создать пользователя с пустым паролем (если он еще не существует)
            conn.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, '')", (username,))
            conn.commit()
            return True
        except:
            return False

def get_top_players(limit=10):
    """Возвращает список топ игроков с их рекордами"""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT username, high_score FROM users WHERE high_score > 0 ORDER BY high_score DESC LIMIT ?",
                  (limit,))
        return c.fetchall()

def get_player_score(username):
    """Возвращает счет игрока по имени"""
    if platform == 'android':
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), 'snake_game.db')
    else:
        db_path = 'snake_game.db'

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute("SELECT score FROM profiles WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_player_rank(username):
    """Возвращает позицию игрока в рейтинге"""
    if platform == 'android':
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), 'snake_game.db')
    else:
        db_path = 'snake_game.db'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) + 1 
        FROM profiles 
        WHERE score > (SELECT score FROM profiles WHERE username=?)
    """, (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

#Безопасное хранение паролей
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                         (username, hash_password(password)))
            return True
        except sqlite3.IntegrityError:
            return False

def validate_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.execute("SELECT password FROM users WHERE username=?", (username,))
        result = c.fetchone()
        if result:
            stored_hash = result[0]
            return stored_hash == hash_password(password)
        return False

