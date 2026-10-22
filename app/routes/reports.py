from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required

from ..models import Room, Booking, Guest

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
@login_required
def dashboard():
    # Статистика по номерам
    total_rooms = Room.query.count()
    occupied_rooms = Room.query.filter_by(status='occupied').count()
    free_rooms = Room.query.filter_by(status='free').count()
    cleaning_rooms = Room.query.filter_by(status='cleaning').count()

    # Статистика по броням и гостям
    active_bookings = Booking.query.filter(
        Booking.status.in_(['created', 'confirmed', 'checked_in'])
    ).count()
    total_guests = Guest.query.count()
    
    # Последние 5 броней для наглядности
    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()

    context = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'free_rooms': free_rooms,
        'cleaning_rooms': cleaning_rooms,
        'active_bookings': active_bookings,
        'total_guests': total_guests,
        'recent_bookings': recent_bookings,
        'today': date.today(),
        'repair_rooms': Room.query.filter_by(status='repair').count(),
        'arrivals': Booking.query.filter(Booking.check_in == date.today(), Booking.status.in_(['created', 'confirmed'])).all(),
        'departures': Booking.query.filter(Booking.check_out == date.today(), Booking.status == 'checked_in').all(),
    }
    
    return render_template("reports/dashboard.html", **context)
