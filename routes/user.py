from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
import datetime
from models.base import db
from models.trek import Trek
from models.booking import Booking
from forms.auth_forms import UserProfileForm
from utils.decorators import trekker_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
@trekker_required
def dashboard():
    open_treks = Trek.query.filter_by(status='Open').all()
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    upcoming_bookings = []
    completed_bookings = []
    cancelled_bookings = []
    today = datetime.date.today()
    for b in user_bookings:
        if b.status == 'Cancelled':
            cancelled_bookings.append(b)
        elif b.status == 'Completed' or b.trek.status == 'Completed' or b.trek.end_date < today:
            completed_bookings.append(b)
        else:
            upcoming_bookings.append(b)
    return render_template(
        'user/dashboard.html',
        open_treks=open_treks,
        user_bookings=user_bookings,
        upcoming_bookings=upcoming_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings
    )

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@trekker_required
def profile():
    form = UserProfileForm(original_email=current_user.email, obj=current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)

@user_bp.route('/explore')
@login_required
@trekker_required
def explore():
    query = Trek.query.filter_by(status='Open')
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter((Trek.name.like(f'%{q}%')) | (Trek.location.like(f'%{q}%')))
    difficulty = request.args.get('difficulty', '').strip()
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    location = request.args.get('location', '').strip()
    if location:
        query = query.filter(Trek.location == location)
    treks = query.all()
    loc_rows = db.session.query(Trek.location).filter_by(status='Open').distinct().all()
    locations = [r[0] for r in loc_rows]
    return render_template('user/trek_search.html', treks=treks, locations=locations, selected_location=location, selected_difficulty=difficulty)

@user_bp.route('/trek/<int:id>/book', methods=['POST'])
@login_required
@trekker_required
def book(id):
    trek = Trek.query.get_or_404(id)
    if trek.status != 'Open':
        flash('This trek is not open for booking.', 'danger')
        return redirect(url_for('user.dashboard'))
    if trek.slots_available <= 0:
        flash('No available slots for this trek.', 'danger')
        return redirect(url_for('user.dashboard'))
    existing = Booking.query.filter_by(user_id=current_user.id, trek_id=id, status='Booked').first()
    if existing:
        flash('You have already booked this trek.', 'danger')
        return redirect(url_for('user.dashboard'))
    booking = Booking(
        user_id=current_user.id,
        trek_id=id,
        status='Booked',
        booking_date=datetime.datetime.utcnow()
    )
    trek.slots_available -= 1
    db.session.add(booking)
    db.session.commit()
    flash('Trek booked successfully.', 'success')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/booking/<int:id>/cancel', methods=['POST'])
@login_required
@trekker_required
def cancel(id):
    booking = Booking.query.get_or_404(id)
    if booking.user_id != current_user.id:
        flash('Unauthorized to cancel this booking.', 'danger')
        return redirect(url_for('user.dashboard'))
    if booking.status != 'Booked':
        flash('This booking cannot be cancelled.', 'danger')
        return redirect(url_for('user.dashboard'))
    booking.status = 'Cancelled'
    booking.trek.slots_available += 1
    db.session.commit()
    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/booking/<int:id>', methods=['GET'])
@login_required
@trekker_required
def booking_detail(id):
    booking = Booking.query.get_or_404(id)
    if booking.user_id != current_user.id:
        flash('Unauthorized details request.', 'danger')
        return redirect(url_for('user.dashboard'))
    return render_template('user/booking_detail.html', booking=booking)

