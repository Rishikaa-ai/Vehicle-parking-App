
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    role = db.Column(db.SmallInteger, nullable=False, default=0)  # 0 = user, 1 = admin

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    max_number_of_spots = db.Column(db.Integer, nullable=False)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_name = db.Column(db.String(20), nullable=False) 
    status = db.Column(db.String(1), default='A')  # A = Available, O = Occupied

    reservations = db.relationship('Reservation', backref='spot', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=True)
    parking_time = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_time = db.Column(db.DateTime, nullable=True)
    cost_per_unit_time = db.Column(db.Float, nullable=False)
