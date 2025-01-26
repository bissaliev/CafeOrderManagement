# CafeOrderManagement | Веб-приложение для управления заказами в кафе.

Веб-приложение на Django для управления заказами в кафе. Приложение позволяет добавлять, удалять, искать, изменять и отображать заказы.

# Описание

**CafeOrderManagement** — это система управления заказами в кафе. Пользователи могут:

-   Просмотр всех заказов, с отображением их `ID`, номера стола, списка позиций блюд, общей стоимости и статуса.
-   Создание заказа: Пользователь вводит номер стола, список блюд и их количество. Система автоматически добавляет заказ с уникальным `ID`, рассчитанной стоимостью и статусом `в ожидании`.;
-   Возможность редактирования заказа (номер столика, добавление или удаление блюд)
-   Удаление заказа по `ID`.
-   Поиска заказов по номеру стола.
-   Фильтрация списка заказов по статусу
-   Изменение статуса заказа: Пользователь выбирает заказ по `ID` и изменяет его статус (`в ожидании`, `готово`, `оплачено`).
-   Расчет выручки за смену: Отдельная страница выводит расчет выручки для заказов со статусом “оплачено” за определенный период(Сегодня, неделя, месяц, все время).
-   Просмотр меню блюд

# API

Проект дополнительно предоставляет API для работы с заказами:

-   Просмотр заказов
-   Просмотр заказа по ID
-   Создание заказа
-   Редактирование заказа по ID
-   Изменение статуса заказа по ID
-   Удаление заказа по ID
-   Просмотр меню

## Документация API

Полная документация доступна по адресу:

Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/

Redoc: http://127.0.0.1:8000/api/schema/redoc/

# Технологии

-   `Python 3.12`
-   `Django 5.1`
-   `Django REST Framework`
-   `Django-filter`
-   `SQLite`
-   `Unittest`

## Установка и запуск

1. Клонируйте репозиторий:

    ```bash
    git clone git@github.com:bissaliev/CafeOrderManagement.git
    cd CafeOrderManagement/
    ```

2. Cоздать и активировать виртуальное окружение:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Установить зависимости из файла `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

4. Перейти в директорию `cafe/` и выполните миграции:

    ```bash
    python3 manage.py migrate
    ```

5. Загрузите фикстуры:

    ```bash
    python3 manage.py loaddata fixtures/dishes.json
    python3 manage.py loaddata fixtures/orders.json
    python3 manage.py loaddata fixtures/order_items.json
    ```

6. Запустите сервер-разработчика:

    ```bash
    python3 manage.py runserver
    ```

## Тестирование

Тесты написаны на библиотеке unittest. Тесты проекта находятся в директории `tests/`.
Чтобы запустить тесты выполните команду:

```bash
python3 manage.py test tests
```

### **Разработчик проекта**

[**Биссалиев Олег**](https://github.com/bissaliev)
