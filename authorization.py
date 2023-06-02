import sqlite3
from datetime import datetime, timedelta
from flask import Flask
from flask import jsonify, request
from passlib.hash import pbkdf2_sha256 as sha256
import for_help

app = Flask(__name__)
conn = sqlite3.connect('database/authorization.db', check_same_thread=False)
cursor = conn.cursor()


# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register():
    # Должны получить json с 4 полями - username, email, password, role
    # При недостаточном количестве данных возвращаем ошибку с кодом 400
    # При некорректном email возвращаем ошибку с кодом 400
    # При повторной регистрации(поля email и username - уникальные) возвращаем ошибку с кодом 400
    # При полностью корректном запросе возвращаем сообщение об успешной регистрации с кодом 200
    data = request.get_json()
    print(f"{register.__name__}: Получена информация: {data}")
    try:
        username = data['username']
        email = data['email']
        password = data['password']
        role = data['role']
    except Exception:
        print(f"{register.__name__}: Недостаточно информации: {data}")
        return jsonify(message='Not enough information in request!'), 400
    if not for_help.is_valid_email(email):
        return jsonify(message='Not valid email address!'), 400
    password_hash = sha256.hash(password)
    try:
        cursor.execute('INSERT INTO user (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                       (username, email, password_hash, role))
        conn.commit()
        print(f"{register.__name__}: Успешная регистрация: {data}")
        return jsonify(message='Successful registration'), 200
    except sqlite3.IntegrityError:
        return jsonify(message='Name or email already exists!'), 400


# Вход пользователя в систему (авторизация)
@app.route('/login', methods=['POST'])
def login():
    # Должны получить json с 2 полями - email, password
    # При недостаточном количестве данных возвращаем ошибку с кодом 400
    # При неверной комбинации выводим сообщение о неуспешной авторизации с кодом 401
    # При полностью корректном запросе возвращаем сообщение об успешном входе с кодом 200
    print(f"{login.__name__}: Авторизация!")
    data = request.get_json()
    try:
        email = data['email']
        password = data['password']
    except Exception:
        print(f"{login.__name__}: Недостаточно информации: {data}")
        return jsonify(message='Not enough information in request!'), 400

    cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user and sha256.verify(password, user[3]):
        session_token = for_help.generate_session_token()
        expires_at = datetime.now() + timedelta(days=1)
        cursor.execute('INSERT INTO session (user_id, session_token, expires_at) VALUES (?, ?, ?)',
                       (user[0], session_token, expires_at))
        conn.commit()
        print(f"{login.__name__}: Успешная авторизация: {data}")
        return jsonify(message='Login successful', session_token=session_token), 200
    else:
        return jsonify(message='Invalid email or password'), 401


# Предоставление информации о пользователе
@app.route('/user', methods=['GET'])
def get_user_info():
    # Должны получить header Authorization с токеном
    # При неверном токене возвращаем информацию об ошибке и код 401
    # При верном токене возвращаем информацию о пользователе в виде json файла и код 200
    print(f"{get_user_info.__name__}: Получение информации о пользователе!")
    token = request.headers.get('Authorization')
    user_info = get_user_info_from_token(token)
    if user_info is None:
        return jsonify({'error': 'Invalid token'}), 401
    return jsonify(user_info), 200


# Вспомогательная функция для предоставления информации о пользователе
def get_user_info_from_token(token: str) -> dict or None:
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.role
        FROM user u
        INNER JOIN session s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
    ''', (token,))
    result = cursor.fetchone()
    if result is None:
        return None
    user_info = {
        'id': result[0],
        'username': result[1],
        'email': result[2],
        'role': result[3]
    }
    return user_info
