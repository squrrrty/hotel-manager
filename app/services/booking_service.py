from ..extensions import db
from ..models import Booking, Room, Guest
from sqlalchemy import and_


def is_room_available(room_id, check_in, check_out, exclude_booking_id=None):
    """
    Проверяет, свободен ли номер на указанные даты.
    Логика пересечения: (начало1 < конец2) И (конец1 > начало2)
    """
    q = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status.in_(["created", "confirmed", "checked_in"]),
        and_(Booking.check_in < check_out, Booking.check_out > check_in),
    )
    if exclude_booking_id:
        q = q.filter(Booking.id != exclude_booking_id)
    
    return q.first() is None


def create_booking(guest_id, room_id, check_in, check_out, user_id):
    if check_out <= check_in:
        raise ValueError("Дата выезда должна быть позже даты заезда")
        
    # Блокируем строку номера до commit: параллельные заявки проверяются по очереди.
    room = Room.query.filter_by(id=room_id).with_for_update().first()
    if room is None or db.session.get(Guest, guest_id) is None:
        raise ValueError("Выберите существующего гостя и номер")
    if room.status == "repair":
        raise ValueError("Номер на ремонте: бронирование недоступно")
    if not is_room_available(room_id, check_in, check_out):
        raise ValueError("Этот номер уже занят на выбранные даты")

    booking = Booking(
        guest_id=guest_id,
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        status="created",
        created_by=user_id,
    )
    db.session.add(booking)
    db.session.commit()
    return booking
