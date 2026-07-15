import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.base import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    staff_profile = db.relationship('StaffProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete-orphan')
    assigned_treks = db.relationship('Trek', back_populates='assigned_staff')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_details = db.Column(db.String(150), nullable=False)
    registration_status = db.Column(db.String(20), default='Pending', nullable=False)
    bio = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship('User', back_populates='staff_profile')
