from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..extensions import db
from ..models import Guest

guests_bp = Blueprint("guests", __name__)


@guests_bp.route("/")
@login_required
def list_guests():
    search = request.args.get('q', '').strip()
    query = Guest.query
    if search:
        query = query.filter(db.or_(
            Guest.full_name.ilike(f'%{search}%'), Guest.phone.ilike(f'%{search}%'),
            Guest.email.ilike(f'%{search}%'),
        ))
    guests = query.order_by(Guest.full_name).all()
    return render_template("guests/list.html", guests=guests)


@guests_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_guest():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        passport = request.form.get("passport", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None

        if not full_name:
            flash("ФИО обязательно для заполнения", "danger")
        elif passport and Guest.query.filter_by(passport=passport).first():
            flash(f"Гость с паспортом {passport} уже существует", "danger")
        else:
            guest = Guest(full_name=full_name, passport=passport, phone=phone, email=email)
            db.session.add(guest)
            db.session.commit()
            flash("Гость добавлен", "success")
            return redirect(url_for("guests.list_guests"))

    return render_template("guests/form.html", guest=None)


@guests_bp.route("/<int:guest_id>/edit", methods=["GET", "POST"])
@login_required
def edit_guest(guest_id):
    guest = db.get_or_404(Guest, guest_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        passport = request.form.get("passport", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None

        if not full_name:
            flash("ФИО обязательно для заполнения", "danger")
        elif passport and Guest.query.filter(Guest.passport == passport, Guest.id != guest.id).first():
            flash(f"Гость с паспортом {passport} уже существует", "danger")
        else:
            guest.full_name = full_name
            guest.passport = passport
            guest.phone = phone
            guest.email = email
            db.session.commit()
            flash("Данные гостя обновлены", "success")
            return redirect(url_for("guests.list_guests"))

    return render_template("guests/form.html", guest=guest)


@guests_bp.route("/<int:guest_id>/delete", methods=["POST"])
@login_required
def delete_guest(guest_id):
    guest = db.get_or_404(Guest, guest_id)
    if guest.bookings:
        flash(f"Нельзя удалить гостя {guest.full_name}: у него есть брони", "danger")
        return redirect(url_for("guests.list_guests"))

    db.session.delete(guest)
    db.session.commit()
    flash(f"Гость {guest.full_name} удалён", "success")
    return redirect(url_for("guests.list_guests"))
