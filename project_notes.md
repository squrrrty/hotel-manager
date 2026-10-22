# 📌 Паспорт проекта: HotelManager (Система управления гостиницей)

Этот файл содержит краткое описание архитектуры, стека и текущего функционала проекта. Предназначен для быстрого погружения в контекст (например, для ИИ-ассистента или нового разработчика).

## 1. Технологический стек
* **Язык:** Python 3.14+
* **Фреймворк:** Flask (с использованием паттерна Application Factory и Blueprints)
* **База данных:** PostgreSQL 18
* **ORM:** SQLAlchemy + Flask-Migrate (Alembic)
* **Аутентификация:** Flask-Login (пароли хешируются через Werkzeug)
* **Frontend:** HTML5, Jinja2 (шаблонизатор), Bootstrap 5 (через CDN), Vanilla JS.
* **Окружение:** Виртуальное окружение `.venv`, конфигурация через `.env` (python-dotenv).

## 2. Структура проекта
* `app/` — основной пакет приложения
  * `__init__.py` — фабрика приложений `create_app()`, регистрация Blueprints.
  * `config.py` — класс конфигурации, чтение `.env`.
  * `extensions.py` — инициализация `db`, `migrate`, `login_manager`.
  * `models/` — модели SQLAlchemy (User, Role, Room, RoomCategory, Guest, Booking).
  * `routes/` — контроллеры (Blueprints): `auth.py`, `main.py`, `rooms.py`, `guests.py`, `bookings.py`, `reports.py`.
  * `services/booking_service.py` — бизнес-логика бронирования (защита от пересечения дат).
  * `templates/` — HTML-шаблоны (Jinja2) с наследованием от `base.html`.
  * `static/` — CSS (кастомные стили) и JS.
* `run.py` — точка входа для запуска сервера.
* `seed.py` — скрипт для первичного заполнения БД (роли, admin, номера, тестовые данные).

## 3. Схема базы данных (Основные сущности)
* `Role` (id, name)
* `User` (id, username, password_hash, full_name, role_id) — связан с Role.
* `RoomCategory` (id, name, capacity, base_price)
* `Room` (id, number, category_id, floor, status) — статусы: free, occupied, cleaning, repair.
* `Guest` (id, full_name, passport, phone, email)
* `Booking` (id, guest_id, room_id, check_in, check_out, status, created_by) — статусы: created, confirmed, checked_in, checked_out, cancelled.

## 4. Ключевая бизнес-логика
* **Защита от двойного бронирования:** В `app/services/booking_service.py` функция `is_room_available()` проверяет пересечение дат `(check_in < new_check_out) AND (check_out > new_check_in)`. Отмененные брони не учитываются.
* **Жизненный цикл (Check-in / Check-out):** 
  * При Check-in статус брони меняется на `checked_in`, а статус номера — на `occupied`.
  * При Check-out статус брони — `checked_out`, а номер переходит в `cleaning` (на уборку).
* **Удаление:** Запрещено удалять номера и гостей, если у них есть привязанные брони (защита внешних ключей).

## 5. Текущий статус (MVP готов)
Реализовано: Авторизация, Дашборд (статистика), CRUD для Номеров и Гостей, Создание/Отмена броней с проверкой дат, Заезд/Выезд.
Роли (пока без строгого ограничения прав на уровне декораторов): admin (полный доступ).

## 6. Как запустить
1. Активировать venv: `.\.venv\Scripts\Activate.ps1`
2. Применить миграции: `flask db upgrade`
3. Запустить: `python run.py`
4. Адрес: `http://127.0.0.1:5000` (Логин: `admin`, Пароль: `admin123`).

## 7. Что планируется улучшить (Roadmap для ИИ)
1. **UI/UX:** Переход на Tailwind CSS или кастомная тема Bootstrap. Замена CRUD-страниц на модальные окна (SPA-стиль). Добавление графиков Chart.js на дашборд.
2. **Функционал:** Добавление модуля «Услуги» (привязка доп. услуг к брони), модуля «Платежи» (учет оплат), создание публичной страницы онлайн-бронирования без авторизации.

## 8. Обновление 22.10.2026

Добавлены подбор номеров по датам, ориентировочная стоимость, завершение уборки, поиск гостей и фильтр броней. UI обновлён в рамках Bootstrap. Стек и схема БД сохранены. Актуальный запуск — README.md, объяснение — CODE_GUIDE.md, результаты — TEST_REPORT.md. Раздел 7 выше — исходный roadmap, а не список реализованных модулей.
