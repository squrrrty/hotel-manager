from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Booking, Guest, Room
from ..services.booking_service import create_booking

bookings_bp = Blueprint("bookings", __name__)


@bookings_bp.route("/")
@login_required
def list_bookings():
    query = Booking.query
    status = request.args.get('status', '')
    if status in ['created', 'confirmed', 'checked_in', 'checked_out', 'cancelled']:
        query = query.filter_by(status=status)
    bookings = query.order_by(Booking.check_in.desc()).all()
    return render_template("bookings/list.html", bookings=bookings)


@bookings_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    guests = Guest.query.order_by(Guest.full_name).all()
    rooms = Room.query.order_by(Room.number).all()

    if request.method == "POST":
        try:
            guest_id = int(request.form.get("guest_id"))
            room_id = int(request.form.get("room_id"))
            check_in = datetime.strptime(request.form.get("check_in"), "%Y-%m-%d").date()
            check_out = datetime.strptime(request.form.get("check_out"), "%Y-%m-%d").date()

            create_booking(guest_id, room_id, check_in, check_out, current_user.id)
            
            flash("Бронирование успешно создано!", "success")
            return redirect(url_for("bookings.list_bookings"))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception as e:
            db.session.rollback()
            flash("Ошибка при создании брони. Проверьте введенные данные.", "danger")

    return render_template("bookings/form.html", guests=guests, rooms=rooms)


@bookings_bp.route("/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.status not in ['created', 'confirmed']:
        flash("Эту бронь нельзя отменить", "danger")
    else:
        booking.status = 'cancelled'
        db.session.commit()
        flash("Бронь отменена", "success")
    return redirect(url_for("bookings.list_bookings"))
@bookings_bp.route("/<int:booking_id>/check-in", methods=["POST"])
@login_required
def check_in(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    
    if booking.status != 'confirmed' and booking.status != 'created':
        flash("Этого гостя нельзя заселить (бронь отменена или завершена)", "danger")
        return redirect(url_for("bookings.list_bookings"))

    Room.query.filter_by(id=booking.room_id).with_for_update().one()
    if booking.room.status != 'free' or Booking.query.filter(
        Booking.room_id == booking.room_id, Booking.status == 'checked_in'
    ).first():
        db.session.rollback()
        flash("Номер не готов к заселению: проверьте занятость, уборку или ремонт", "danger")
        return redirect(url_for("bookings.list_bookings"))
    if not booking.check_in <= date.today() < booking.check_out:
        db.session.rollback()
        flash("Заселение доступно только в даты проживания", "danger")
        return redirect(url_for("bookings.list_bookings"))

    booking.status = 'checked_in'
    booking.room.status = 'occupied'  # Меняем статус номера на "Занят"
    db.session.commit()
    
    flash(f"Гость {booking.guest.full_name} заселен в номер {booking.room.number}", "success")
    return redirect(url_for("bookings.list_bookings"))


@bookings_bp.route("/<int:booking_id>/check-out", methods=["POST"])
@login_required
def check_out(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    
    if booking.status != 'checked_in':
        flash("Этот гость еще не заселен", "danger")
        return redirect(url_for("bookings.list_bookings"))

    booking.status = 'checked_out'
    booking.room.status = 'cleaning'  # Номер уходит на уборку
    db.session.commit()
    
    flash(f"Гость {booking.guest.full_name} выехал. Номер {booking.room.number} отправлен на уборку.", "info")
    return redirect(url_for("bookings.list_bookings"))
