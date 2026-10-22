from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Booking, Room, Guest
from app.services.booking_service import create_booking, is_room_available


def test_authentication(app):
    client = app.test_client()
    assert client.get('/rooms/').status_code == 302
    response = client.post('/login', data={'username': 'admin', 'password': 'wrong'})
    assert 'Неверный логин' in response.text
    assert client.get('/bookings/').status_code == 302


@pytest.mark.parametrize('path', ['/reports/', '/rooms/', '/guests/', '/bookings/',
                                 '/rooms/new', '/guests/new', '/bookings/new',
                                 '/rooms/1/edit', '/guests/1/edit'])
def test_pages_render(client, path):
    assert client.get(path).status_code == 200


def test_overlap_and_adjacent_dates(app):
    start = date.today()
    booking = create_booking(1, 1, start, start + timedelta(days=3), 1)
    assert booking.nights == 3
    assert booking.estimated_total == Decimal('4501.50')
    assert not is_room_available(1, start + timedelta(days=1), start + timedelta(days=4))
    assert is_room_available(1, start + timedelta(days=3), start + timedelta(days=5))
    assert is_room_available(1, start - timedelta(days=2), start)
    with pytest.raises(ValueError, match='уже занят'):
        create_booking(1, 1, start, start + timedelta(days=2), 1)
    db.session.rollback()
    booking.status = 'cancelled'
    db.session.commit()
    assert is_room_available(1, start, start + timedelta(days=3))


def test_invalid_dates_and_repair(client, booking_data):
    invalid = dict(booking_data, check_out=booking_data['check_in'])
    assert 'позже даты заезда' in client.post('/bookings/new', data=invalid).text
    response = client.post('/bookings/new', data=dict(booking_data, room_id=2))
    assert 'на ремонте' in response.text
    assert Booking.query.count() == 0


def test_availability_filter(client, booking_data):
    client.post('/bookings/new', data=booking_data)
    response = client.get('/rooms/', query_string={
        'check_in': booking_data['check_in'], 'check_out': booking_data['check_out']})
    assert 'Найдено номеров: 0' in response.text
    adjacent = date.fromisoformat(booking_data['check_out'])
    response = client.get('/rooms/', query_string={
        'check_in': adjacent.isoformat(), 'check_out': (adjacent + timedelta(days=1)).isoformat()})
    assert 'Найдено номеров: 1' in response.text
    response = client.get('/rooms/?check_in=bad')
    assert 'Укажите обе даты' in response.text
    assert 'Найдено номеров: 0' in response.text


def test_stay_and_cleaning_cycle(client, booking_data):
    client.post('/bookings/new', data=booking_data)
    client.post('/bookings/1/check-in')
    assert db.session.get(Room, 1).status == 'occupied'
    assert db.session.get(Booking, 1).status == 'checked_in'
    client.post('/bookings/1/cancel')
    assert db.session.get(Booking, 1).status == 'checked_in'
    client.post('/rooms/1/ready')
    assert db.session.get(Room, 1).status == 'occupied'
    client.post('/bookings/1/check-out')
    assert db.session.get(Room, 1).status == 'cleaning'
    client.post('/rooms/1/ready')
    assert db.session.get(Room, 1).status == 'free'
    assert db.session.get(Booking, 1).status == 'checked_out'


def test_unready_room_and_future_checkin(client, booking_data):
    client.post('/bookings/new', data=booking_data)
    room = db.session.get(Room, 1)
    room.status = 'cleaning'
    db.session.commit()
    response = client.post('/bookings/1/check-in', follow_redirects=True)
    assert 'не готов' in response.text
    assert db.session.get(Booking, 1).status == 'created'
    client.post('/rooms/1/ready')
    booking = db.session.get(Booking, 1)
    booking.check_in += timedelta(days=1)
    booking.check_out += timedelta(days=1)
    db.session.commit()
    response = client.post('/bookings/1/check-in', follow_redirects=True)
    assert 'только в даты проживания' in response.text


def test_linked_records_cannot_be_deleted(client, booking_data):
    client.post('/bookings/new', data=booking_data)
    assert 'есть связанные брони' in client.post('/rooms/1/delete', follow_redirects=True).text
    assert 'есть брони' in client.post('/guests/1/delete', follow_redirects=True).text
    assert db.session.get(Room, 1) and db.session.get(Guest, 1)


def test_guest_search_and_booking_filter(client, booking_data):
    assert 'Тестовый гость' in client.get('/guests/?q=992900').text
    assert 'Найдено гостей: 0' in client.get('/guests/?q=отсутствует').text
    client.post('/bookings/new', data=booking_data)
    assert 'Найдено броней: 1' in client.get('/bookings/?status=created').text
    assert 'Найдено броней: 0' in client.get('/bookings/?status=cancelled').text


def test_invalid_guest_and_form_retention(client, booking_data):
    response = client.post('/bookings/new', data=dict(booking_data, guest_id=999))
    assert 'существующего гостя' in response.text
    assert f'value="{booking_data["check_in"]}"' in response.text
    assert Booking.query.count() == 0


def test_room_status_cannot_bypass_booking(client):
    response = client.post('/rooms/1/edit', data={
        'number': '101', 'category_id': 1, 'floor': 1, 'status': 'occupied'})
    assert 'через заезд и выезд' in response.text
    assert db.session.get(Room, 1).status == 'free'
