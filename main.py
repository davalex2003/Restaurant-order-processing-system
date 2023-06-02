import authorization
import orders_processing
import for_help

# Создание баз данных
for_help.create_database_authorization()
for_help.create_database_order_processing()

if __name__ == '__main__':
    # orders_processing.app.run(host="127.0.0.1", port=5000)  # запуск сервиса работы с сервисом заказов
    authorization.app.run(host="127.0.0.1", port=5000)  # запуск сервиса авторизации
