"""Тесты работают в отдельной временной схеме PostgreSQL, без данных приложения."""
import os
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, text

from app import create_app
from app.extensions import db
from app.models import Role, User, RoomCategory, Room, Guest


@pytest.fixture
def app():
    url = os.environ.get('TEST_DATABASE_URL')
    if not url or not url.startswith('postgresql'):
        pytest.skip('Укажите TEST_DATABASE_URL для тестовой PostgreSQL')
    url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    schema = 'test_' + uuid.uuid4().hex
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA {schema}'))

    class TestConfig:
        TESTING = True
        CSRF_ENABLED = False
        SECRET_KEY = 'test-only'
        SQLALCHEMY_DATABASE_URI = url
        SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'options': f'-csearch_path={schema}'}}
        SQLALCHEMY_TRACK_MODIFICATIONS = False

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        role = Role(name='admin')
        category = RoomCategory(name='Standard', capacity=2, base_price='1500.50')
        db.session.add_all([role, category])
        db.session.flush()
        user = User(username='admin', full_name='Администратор', role_id=role.id)
        user.set_password('admin123')
        db.session.add_all([
            user, Guest(full_name='Тестовый гость', phone='+992900000001'),
            Room(number='101', category_id=category.id, status='free'),
            Room(number='102', category_id=category.id, status='repair'),
        ])
        db.session.commit()
        yield app
        db.session.remove()
        db.engine.dispose()
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA {schema} CASCADE'))
    engine.dispose()


@pytest.fixture
def client(app):
    client = app.test_client()
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    return client


@pytest.fixture
def booking_data():
    today = date.today()
    return {'guest_id': 1, 'room_id': 1, 'check_in': today.isoformat(),
            'check_out': (today + timedelta(days=3)).isoformat()}
