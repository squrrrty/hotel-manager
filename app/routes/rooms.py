from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..extensions import db
from ..models import Room, RoomCategory, Booking

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/")
@login_required
def list_rooms():
    query = Room.query
    status = request.args.get("status", "")
    if status in ['free', 'occupied', 'cleaning', 'repair']:
        query = query.filter_by(status=status)
    start, end = request.args.get("check_in", ""), request.args.get("check_out", "")
    if start or end:
        try:
            check_in, check_out = date.fromisoformat(start), date.fromisoformat(end)
            if check_out <= check_in:
                raise ValueError
            # NOT EXISTS исключает номера с пересекающимися активными бронями.
            conflict = db.session.query(Booking.id).filter(
                Booking.room_id == Room.id,
                Booking.status.in_(['created', 'confirmed', 'checked_in']),
                Booking.check_in < check_out, Booking.check_out > check_in,
            ).exists()
            query = query.filter(~conflict, Room.status != 'repair')
        except ValueError:
            flash("Укажите обе даты: выезд должен быть позже заезда", "danger")
            query = query.filter(db.false())
    rooms = query.order_by(Room.number).all()
    return render_template("rooms/list.html", rooms=rooms)


@rooms_bp.route("/<int:room_id>/ready", methods=["POST"])
@login_required
def ready(room_id):
    room = db.get_or_404(Room, room_id)
    if room.status != 'cleaning':
        flash("Завершить уборку можно только для номера на уборке", "danger")
    else:
        room.status = 'free'
        db.session.commit()
        flash(f"Уборка номера {room.number} завершена. Номер готов к заезду.", "success")
    return redirect(url_for('rooms.list_rooms'))


@rooms_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_room():
    categories = RoomCategory.query.order_by(RoomCategory.name).all()

    if request.method == "POST":
        number = request.form.get("number", "").strip()
        category_id = request.form.get("category_id", type=int)
        floor = request.form.get("floor", type=int)
        status = request.form.get("status", "free")

        if not number or not category_id:
            flash("Заполните номер и категорию", "danger")
        elif status not in ['free', 'cleaning', 'repair'] or not db.session.get(RoomCategory, category_id):
            flash("Выберите корректную категорию и статус. Заселение выполняется через бронь.", "danger")
        elif Room.query.filter_by(number=number).first():
            flash(f"Номер {number} уже существует", "danger")
        else:
            room = Room(
                number=number,
                category_id=category_id,
                floor=floor,
                status=status,
            )
            db.session.add(room)
            db.session.commit()
            flash(f"Номер {number} добавлен", "success")
            return redirect(url_for("rooms.list_rooms"))

    return render_template("rooms/form.html", room=None, categories=categories)


@rooms_bp.route("/<int:room_id>/edit", methods=["GET", "POST"])
@login_required
def edit_room(room_id):
    room = db.get_or_404(Room, room_id)
    categories = RoomCategory.query.order_by(RoomCategory.name).all()

    if request.method == "POST":
        number = request.form.get("number", "").strip()
        category_id = request.form.get("category_id", type=int)
        floor = request.form.get("floor", type=int)
        status = request.form.get("status", "free")

        if not number or not category_id:
            flash("Заполните номер и категорию", "danger")
        elif status not in ['free', 'occupied', 'cleaning', 'repair'] or not db.session.get(RoomCategory, category_id):
            flash("Выберите корректную категорию и статус", "danger")
        elif (status == 'occupied') != bool(Booking.query.filter_by(room_id=room.id, status='checked_in').first()):
            flash("Занятость номера меняется через заезд и выезд в разделе броней", "danger")
        elif Room.query.filter(Room.number == number, Room.id != room.id).first():
            flash(f"Номер {number} уже существует", "danger")
        else:
            room.number = number
            room.category_id = category_id
            room.floor = floor
            room.status = status
            db.session.commit()
            flash("Изменения сохранены", "success")
            return redirect(url_for("rooms.list_rooms"))

    return render_template("rooms/form.html", room=room, categories=categories)


@rooms_bp.route("/<int:room_id>/delete", methods=["POST"])
@login_required
def delete_room(room_id):
    room = db.get_or_404(Room, room_id)
    if room.bookings:
        flash(f"Нельзя удалить номер {room.number}: есть связанные брони", "danger")
        return redirect(url_for("rooms.list_rooms"))

    db.session.delete(room)
    db.session.commit()
    flash(f"Номер {room.number} удалён", "success")
    return redirect(url_for("rooms.list_rooms"))
