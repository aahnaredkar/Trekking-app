from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.base import db
from models.trek import Trek
from models.booking import Booking
from forms.trek_forms import SlotUpdateForm, StatusUpdateForm
from utils.decorators import staff_required

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff/dashboard')
@login_required
@staff_required
def dashboard():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    treks_data = []
    for trek in assigned_treks:
        booked_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        treks_data.append({
            'trek': trek,
            'booked_count': booked_count
        })
    return render_template('staff/dashboard.html', treks_data=treks_data)

@staff_bp.route('/staff/trek/<int:id>/participants')
@login_required
@staff_required
def participants(id):
    trek = Trek.query.get_or_404(id)
    if trek.assigned_staff_id != current_user.id:
        flash('Unauthorized: You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
    trek_bookings = Booking.query.filter_by(trek_id=trek.id).all()
    return render_template('staff/participants.html', trek=trek, bookings=trek_bookings)

@staff_bp.route('/staff/trek/<int:id>/slots', methods=['GET', 'POST'])
@login_required
@staff_required
def edit_slots(id):
    trek = Trek.query.get_or_404(id)
    if trek.assigned_staff_id != current_user.id:
        flash('Unauthorized: You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
    confirmed_bookings_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
    slot_form = SlotUpdateForm(
        slots_available=trek.slots_available,
        confirmed_bookings_count=confirmed_bookings_count,
        slots_total_limit=trek.slots_total
    )
    status_form = StatusUpdateForm(
        status=trek.status,
        current_status=trek.status
    )
    if request.method == 'POST':
        form_name = request.form.get('form_name')
        if form_name == 'slot_form':
            if slot_form.validate_on_submit():
                trek.slots_available = slot_form.slots_available.data
                db.session.commit()
                flash('Slots updated successfully.', 'success')
                return redirect(url_for('staff.edit_slots', id=trek.id))
        elif form_name == 'status_form':
            if status_form.validate_on_submit():
                trek.status = status_form.status.data
                db.session.commit()
                flash('Status updated successfully.', 'success')
                return redirect(url_for('staff.edit_slots', id=trek.id))
    return render_template(
        'staff/edit_slots.html',
        trek=trek,
        slot_form=slot_form,
        status_form=status_form,
        confirmed_bookings_count=confirmed_bookings_count
    )

@staff_bp.route('/staff/trek/<int:id>/status', methods=['POST'])
@login_required
@staff_required
def update_status(id):
    trek = Trek.query.get_or_404(id)
    if trek.assigned_staff_id != current_user.id:
        flash('Unauthorized: You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
    status_form = StatusUpdateForm(current_status=trek.status)
    if status_form.validate_on_submit():
        trek.status = status_form.status.data
        db.session.commit()
        flash('Status updated successfully.', 'success')
    else:
        for field, errors in status_form.errors.items():
            for error in errors:
                flash(error, 'danger')
    return redirect(url_for('staff.dashboard'))

