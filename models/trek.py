from models.base import db

class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    slots_total = db.Column(db.Integer, nullable=False)
    slots_available = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    assigned_staff = db.relationship('User', back_populates='assigned_treks')
    bookings = db.relationship('Booking', back_populates='trek', cascade='all, delete-orphan')
