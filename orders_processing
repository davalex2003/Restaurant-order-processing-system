import sqlite3
import time

from flask import Flask
from flask import jsonify, request

app = Flask(__name__)
database = sqlite3.connect('database/orders.db', check_same_thread=False)
cursor = database.cursor()


# Создание заказов
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Никакой информации не поступило!'}), 400
    print(f"{create_order.__name__}: Получена информация: {data}")
    if 'user_id' not in data or 'dishes' not in data or 'special_requests' not in data:
        print(f"{create_order.__name__}: Недостаточно информации!")
        return jsonify({'error': 'Неверная информация!'}), 400
    user_id = data['user_id']
    database_users = sqlite3.connect('database/authorization.db', check_same_thread=False)
    cursor_user = database_users.cursor()
    cursor_user.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    user = cursor_user.fetchone()
    database_users.close()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    dishes = data['dishes']
    special_requests = data['special_requests']
    for dish in dishes:
        dish_id = dish['dish_id']
        quantity = dish['quantity']
        cursor.execute("SELECT COUNT(*) FROM dish WHERE id = ?", (dish_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            return jsonify({'error': 'Блюдо не найдено!'}), 404
        cursor.execute("SELECT quantity FROM dish WHERE id = ?", (dish_id,))
        available_quantity = cursor.fetchone()[0]
        if quantity > available_quantity:
            print(f"{create_order.__name__}: Заказу недостаточно блюд на складе!")
            return jsonify({'error': 'Не хватает {}!'.format(dish_id)}), 400
    cursor.execute("INSERT INTO order_table (user_id, special_requests, status) VALUES (?, ?, ?)",
                   (user_id, special_requests, 'pending'))
    order_id = cursor.lastrowid
    for dish in dishes:
        dish_id = dish['dish_id']
        quantity = dish['quantity']
        price = dish['price']
        cursor.execute("INSERT INTO order_dish (order_id, dish_id, quantity, price) VALUES (?, ?, ?, ?)",
                       (order_id, dish_id, quantity, price))
        cursor.execute("UPDATE dish SET quantity = quantity - ? WHERE id = ?", (quantity, dish_id))
        database.commit()
        cursor.execute("SELECT quantity FROM dish WHERE id = ?", (dish_id,))
        if cursor.fetchone()[0] <= 0:
            cursor.execute("UPDATE dish SET is_available = 'False' WHERE id = ?", (dish_id,))
    database.commit()
    print(f"{create_order.__name__}: Успешное создание заказа!")
    return jsonify({'message': 'Заказ создан успешно!'}), 201


# Обработка заказов
@app.route('/orders/process', methods=['POST'])
def process_orders():
    cursor.execute("SELECT * FROM order_table WHERE status = ?", ('pending',))
    orders = cursor.fetchall()
    print(f"{process_orders.__name__}: Начинаю обработку заказов!")
    for order in orders:
        time.sleep(2)
        order_id = order[0]
        print(f"{process_orders.__name__}: Выполнил заказ c id {order_id}!")
        cursor.execute("UPDATE order_table SET status = ? WHERE id = ?", ('completed', order_id))
    database.commit()
    print(f"{process_orders.__name__}: Выполнил заказы!")
    return jsonify({'message': 'Заказы выполнены успешно!'}), 200


# Предоставление информации о заказе
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    cursor.execute("SELECT * FROM order_table WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    if not order:
        return jsonify({'error': 'Заказ не найден'}), 404
    return jsonify({
        'order_id': order[0],
        'user_id': order[1],
        'status': order[2],
        'special_requests': order[3]})


# Управление блюдами
@app.route('/dishes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_dishes():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No data from user!'}), 400
    print(f"{manage_dishes.__name__}: Получена информация: {data}")
    if 'user_id' not in data:
        print(f"{manage_dishes.__name__}: Нет информации о пользователе!")
        return jsonify({'error': 'Неверная информация!'}), 400
    user_id = data['user_id']
    db_users = sqlite3.connect('database/authorization.db', check_same_thread=False)
    cursor_user = db_users.cursor()
    cursor_user.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    user = cursor_user.fetchone()
    if user is None:
        return jsonify({'error': 'Пользователь не найден!'}), 404
    user_role = user[4]
    db_users.close()
    if user_role != 'manager':
        return jsonify({'error': 'Вы не манагер('}), 403
    if request.method == 'GET':
        dish_id = data['id']
        cursor.execute("SELECT * FROM dish WHERE id = ?", (dish_id,))
        dish = cursor.fetchone()
        if dish is None or not dish[5] or dish[4] <= 0:
            return jsonify({'error': 'Блюдо не найдено или закончилось!'}), 404
        return jsonify({'dish': dish}), 200
    elif request.method == 'POST':
        if 'name' not in data or 'description' not in data or 'price' not in data or 'quantity' not in data or 'is_available' not in data:
            print(f"{manage_dishes.__name__}: Недостаточно информации!")
            return jsonify({'error': 'Блюдо создаётся не так('}), 400
        dish_data = request.json
        cursor.execute("INSERT INTO dish (name, description, price, quantity, is_available) VALUES (?, ?, ?, ?, ?)",
                       (dish_data['name'], dish_data['description'], dish_data['price'], dish_data['quantity'],
                        dish_data['is_available']))
        database.commit()
        return jsonify({'message': 'Блюдо успешно создано!'}), 201

    elif request.method == 'PUT':
        if 'name' not in data or 'description' not in data or 'price' not in data or 'quantity' not in data or 'is_available' not in data:
            print(f"{manage_dishes.__name__}: Недостаточно информации!")
            return jsonify({'error': 'Блюдо изменяется не так('}), 400
        dish_id = request.json['id']
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        quantity = request.json['quantity']
        is_available = request.json['is_available']
        query = "UPDATE dish SET name=?, description=?, price=?, quantity=?, is_available=? WHERE id=?"
        cursor.execute(query, (name, description, price, quantity, is_available, dish_id))
        database.commit()
        return jsonify({'message': 'Блюдо успешно изменено'}), 200
    elif request.method == 'DELETE':
        dish_id = request.json['id']
        cursor.execute("SELECT * FROM dish WHERE id = ?", (dish_id,))
        dish = cursor.fetchone()
        if dish is None:
            return jsonify({'error': 'Блюдо не найдено'}), 404
        query = "DELETE FROM dish WHERE id=?"
        cursor.execute(query, (dish_id,))
        database.commit()
        return jsonify({'message': 'Блюдо успешно удалено'}), 200


# Предоставление меню
@app.route('/menu', methods=['GET'])
def get_menu():
    print(f"{get_menu.__name__}: Получаем информацию о меню!")
    query = "SELECT * FROM dish WHERE is_available = 'True'"
    cursor.execute(query)
    dishes = cursor.fetchall()
    menu = []
    for dish in dishes:
        dish_dict = {
            'id': dish[0],
            'name': dish[1],
            'description': dish[2],
            'price': float(dish[3]),
            'quantity': dish[4],
            'is_available': bool(dish[5]),
            'created_at': str(dish[6]),
            'updated_at': str(dish[7])
        }
        menu.append(dish_dict)
    return jsonify({'menu': menu}), 200
