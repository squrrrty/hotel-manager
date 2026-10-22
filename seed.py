"""Начальное заполнение БД: роли, пользователь admin,
категории номеров и сами номера.

Запуск:
    python seed.py
"""

import os
from datetime import date

from app import create_app
from app.extensions import db
from app.models import Role, User, RoomCategory, Room, Guest, Booking


def seed():
    app = create_app()
    with app.app_context():
        production = app.config.get("PRODUCTION", False)
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "" if production else "admin123")
        if not User.query.filter_by(username=username).first() and production and len(password) < 12:
            raise ValueError("Задайте ADMIN_PASSWORD длиной не менее 12 символов")
        # ---------- Роли ----------
        if not Role.query.filter_by(name="admin").first():
            db.session.add_all(
                [
                    Role(name="admin"),     # администратор системы
                    Role(name="manager"),   # менеджер ресепшена
                    Role(name="maid"),      # горничная
                ]
            )
            db.session.commit()
            print("[+] Роли добавлены: admin, manager, maid")
        else:
            print("[=] Роли уже существуют — пропускаем")

        # ---------- Пользователь admin ----------
        admin_role = Role.query.filter_by(name="admin").first()
        if not User.query.filter_by(username=username).first():
            admin = User(
                username=username,
                full_name="Администратор системы",
                role_id=admin_role.id,
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print("[+] Администратор создан. Пароль взят из окружения или локальных демо-настроек.")
        else:
            print("[=] Пользователь admin уже существует — пропускаем")

        # ---------- Категории номеров ----------
        categories_data = [
            {"name": "Standard", "capacity": 2, "base_price": 1500},
            {"name": "Deluxe",   "capacity": 3, "base_price": 2500},
            {"name": "Suite",    "capacity": 4, "base_price": 4500},
        ]
        if RoomCategory.query.count() == 0:
            for c in categories_data:
                db.session.add(RoomCategory(**c))
            db.session.commit()
            print("[+] Категории номеров добавлены")
        else:
            print("[=] Категории уже есть — пропускаем")

        # ---------- Номера ----------
        standard = RoomCategory.query.filter_by(name="Standard").first()
        deluxe = RoomCategory.query.filter_by(name="Deluxe").first()
        suite = RoomCategory.query.filter_by(name="Suite").first()

        rooms_data = [
            {"number": "101", "category_id": standard.id, "floor": 1},
            {"number": "102", "category_id": standard.id, "floor": 1},
            {"number": "103", "category_id": standard.id, "floor": 1},
            {"number": "201", "category_id": deluxe.id,   "floor": 2},
            {"number": "202", "category_id": deluxe.id,   "floor": 2},
            {"number": "301", "category_id": suite.id,    "floor": 3},
        ]
        if Room.query.count() == 0:
            for r in rooms_data:
                db.session.add(Room(**r))
            db.session.commit()
            print("[+] Номера добавлены: 101, 102, 103, 201, 202, 301")
        else:
            print("[=] Номера уже есть — пропускаем")

        # На хостинге нужны роли, администратор и номера, без тестовых гостей и броней.
        if production:
            print("Готово. Начальные данные созданы без демонстрационных броней.")
            return

        # ---------- Тестовый гость и бронь ----------
        if Guest.query.count() == 0:
            guest = Guest(
                full_name="Иванов Иван Иванович",
                passport="1234 567890",
                phone="+992900000001",
                email="ivanov@example.com",
            )
            db.session.add(guest)
            db.session.commit()
            print("[+] Тестовый гость добавлен")
        else:
            guest = Guest.query.first()
            print("[=] Гости уже есть — пропускаем")

        if Booking.query.count() == 0:
            room101 = Room.query.filter_by(number="101").first()
            booking = Booking(
                guest_id=guest.id,
                room_id=room101.id,
                check_in=date(2026, 11, 1),
                check_out=date(2026, 11, 5),
                status="confirmed",
            )
            db.session.add(booking)
            db.session.commit()
            print("[+] Тестовая бронь добавлена (101, 01.11.2026–05.11.2026)")
        else:
            print("[=] Брони уже есть — пропускаем")

        print("\nГотово.")


if __name__ == "__main__":
    seed()
