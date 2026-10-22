from ..extensions import db


class RoomCategory(db.Model):
    __tablename__ = "room_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)

    rooms = db.relationship("Room", back_populates="category")

    __table_args__ = (
        db.CheckConstraint("capacity > 0", name="ck_room_category_capacity"),
        db.CheckConstraint("base_price >= 0", name="ck_room_category_price"),
    )

    def __repr__(self):
        return f"<RoomCategory {self.name}>"


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("room_categories.id"), nullable=False
    )
    floor = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False, default="free")

    category = db.relationship("RoomCategory", back_populates="rooms")
    bookings = db.relationship("Booking", back_populates="room")

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('free','occupied','cleaning','repair')",
            name="ck_room_status",
        ),
    )

    def __repr__(self):
        return f"<Room {self.number}>"
