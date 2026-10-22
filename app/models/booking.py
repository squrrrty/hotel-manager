from ..extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey("guests.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="created")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    guest = db.relationship("Guest", back_populates="bookings")
    room = db.relationship("Room", back_populates="bookings")

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    @property
    def estimated_total(self):
        # Это оценка по текущему тарифу категории, а не сохранённый счёт.
        return self.nights * self.room.category.base_price

    __table_args__ = (
        db.CheckConstraint("check_out > check_in", name="ck_booking_dates"),
        db.CheckConstraint(
            "status IN ('created','confirmed','checked_in','checked_out','cancelled')",
            name="ck_booking_status",
        ),
    )

    def __repr__(self):
        return f"<Booking {self.id} room={self.room_id}>"
