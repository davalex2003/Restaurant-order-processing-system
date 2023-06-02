import re
import secrets
import sqlite3


# Создаем базу данных для работы с авторизацией
def create_database_authorization() -> None:
    print("Создание базы данных для регистрации и авторизации.")
    conn = sqlite3.connect(r'database/authorization.db')
    try:
        cursor = conn.cursor()
        # Создаем таблицу "user"
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(10) NOT NULL CHECK (role IN ('customer', 'chef', 'manager')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        # Создаем таблицу "session"
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token VARCHAR(255),
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user(id)
                )
            ''')
        # Сохранение изменений и закрытие соединения
        conn.commit()
    except Exception as error:
        print(f"Создание базы данных произошло с ошибкой: {error}.")
    finally:
        conn.close()


# Создаем базу данных для работы с заказами
def create_database_order_processing() -> None:
    print("Создание базы данных для заказов.")
    conn = sqlite3.connect("database/orders.db")
    try:
        cursor = conn.cursor()
        # Создаем таблицу "dish"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                quantity INT NOT NULL,
                is_available BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Создаем таблицу "order_table"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT NOT NULL,
                status VARCHAR(50) NOT NULL,
                special_requests TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        ''')
        # Создаем таблицу "order_dish"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_dish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INT NOT NULL,
                dish_id INT NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES order_table(id),
                FOREIGN KEY (dish_id) REFERENCES dish(id)
            )
        ''')
        # Сохранение изменений и закрытие соединения
        conn.commit()
    except Exception as error:
        print(f"Создание базы данных №2 произошло с ошибкой: {error}.")
    finally:
        conn.close()


# Генерируем токен сессии
def generate_session_token() -> str:
    token = secrets.token_hex(16)
    return token


# Проверка на валидность email
def is_valid_email(email: str) -> bool:
    pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"
    if re.match(pattern, email) is not None:
        return True
    else:
        return False
