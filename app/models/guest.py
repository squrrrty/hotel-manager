from ..extensions import db


class Guest(db.Model):
    __tablename__ = "guests"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    passport = db.Column(db.String(30), unique=True)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    bookings = db.relationship("Booking", back_populates="guest")

    def __repr__(self):
        return f"<Guest {self.full_name}>"