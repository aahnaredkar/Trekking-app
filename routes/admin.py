from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import or_
from models.base import db
from models.user import User, StaffProfile
from models.trek import Trek
from models.booking import Booking
from forms.trek_forms import TrekForm
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    return render_template('admin/dashboard.html',
                           total_treks=total_treks,
                           total_users=total_users,
                           total_staff=total_staff,
                           total_bookings=total_bookings)

@admin_bp.route('/admin/treks')
@login_required
@admin_required
def treks():
    trek_list = Trek.query.all()
    return render_template('admin/treks_list.html', trek_list=trek_list)

@admin_bp.route('/admin/treks/new', methods=['GET', 'POST'])
@login_required
@admin_required
def trek_create():
    form = TrekForm()
    approved_staff = User.query.join(StaffProfile).filter(
        User.role == 'staff',
        StaffProfile.registration_status == 'Approved',
        User.is_active == True
    ).all()
    form.assigned_staff_id.choices = [(0, '— Select Staff (Optional) —')] + [(s.id, f"{s.staff_profile.name} ({s.username})") for s in approved_staff]
    if form.validate_on_submit():
        assigned_id = form.assigned_staff_id.data
        trek = Trek(
            name=form.name.data,
            location=form.location.data,
            difficulty=form.difficulty.data,
            duration_days=form.duration_days.data,
            slots_total=form.slots_total.data,
            slots_available=form.slots_available.data,
            status=form.status.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            description=form.description.data,
            assigned_staff_id=assigned_id if assigned_id and assigned_id != 0 else None
        )
        db.session.add(trek)
        db.session.commit()
        flash('Trek created successfully.', 'success')
        return redirect(url_for('admin.treks'))
    return render_template('admin/trek_create.html', form=form)

@admin_bp.route('/admin/treks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def trek_edit(id):
    trek = Trek.query.get_or_404(id)
    form = TrekForm(obj=trek)
    approved_staff = User.query.join(StaffProfile).filter(
        User.role == 'staff',
        StaffProfile.registration_status == 'Approved'
    ).all()
    approved_active_staff = [s for s in approved_staff if s.is_active]
    form.assigned_staff_id.choices = [(0, '— Select Staff (Optional) —')] + [(s.id, f"{s.staff_profile.name} ({s.username})") for s in approved_active_staff]
    if form.validate_on_submit():
        trek.name = form.name.data
        trek.location = form.location.data
        trek.difficulty = form.difficulty.data
        trek.duration_days = form.duration_days.data
        trek.slots_total = form.slots_total.data
        trek.slots_available = form.slots_available.data
        trek.status = form.status.data
        trek.start_date = form.start_date.data
        trek.end_date = form.end_date.data
        trek.description = form.description.data
        db.session.commit()
        flash('Trek updated successfully.', 'success')
        return redirect(url_for('admin.treks'))
    return render_template('admin/trek_edit.html', form=form, trek=trek, approved_staff=approved_staff)

@admin_bp.route('/admin/treks/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def trek_delete(id):
    trek = Trek.query.get_or_404(id)
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted.', 'success')
    return redirect(url_for('admin.treks'))

@admin_bp.route('/admin/treks/<int:id>/assign', methods=['POST'])
@login_required
@admin_required
def assign_staff(id):
    trek = Trek.query.get_or_404(id)
    staff_id = request.form.get('staff_id', type=int)
    if staff_id:
        staff_user = User.query.get(staff_id)
        if staff_user and staff_user.staff_profile and staff_user.staff_profile.registration_status == 'Approved':
            trek.assigned_staff_id = staff_id
            db.session.commit()
            flash('Staff assigned successfully.', 'success')
        else:
            flash('Only approved staff can be assigned.', 'danger')
    else:
        trek.assigned_staff_id = None
        db.session.commit()
        flash('Staff assignment removed.', 'info')
    return redirect(url_for('admin.trek_edit', id=id))

@admin_bp.route('/admin/staff')
@login_required
@admin_required
def staff():
    q = request.args.get('q', '').strip()
    staff_query = User.query.join(StaffProfile).filter(User.role == 'staff')
    if q:
        staff_query = staff_query.filter(
            or_(User.username.ilike(f'%{q}%'), StaffProfile.name.ilike(f'%{q}%'))
        )
    users = staff_query.all()
    return render_template('admin/users_list.html', users=users, role_filter='staff', query=q)

@admin_bp.route('/admin/staff/approve/<int:id>', methods=['POST'])
@login_required
@admin_required
def staff_approve(id):
    user = User.query.get_or_404(id)
    if user.staff_profile:
        user.staff_profile.registration_status = 'Approved'
        user.is_active = True
        db.session.commit()
        flash(f'{user.username} has been approved.', 'success')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/admin/staff/reject/<int:id>', methods=['POST'])
@login_required
@admin_required
def staff_reject(id):
    user = User.query.get_or_404(id)
    if user.staff_profile:
        user.staff_profile.registration_status = 'Rejected'
        db.session.commit()
        flash(f'{user.username} has been rejected.', 'warning')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/admin/staff/blacklist/<int:id>', methods=['POST'])
@login_required
@admin_required
def staff_blacklist(id):
    user = User.query.get_or_404(id)
    if user.staff_profile:
        user.staff_profile.registration_status = 'Blacklisted'
        user.is_active = False
        db.session.commit()
        flash(f'{user.username} has been blacklisted.', 'danger')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/admin/trekkers')
@login_required
@admin_required
def trekkers():
    q = request.args.get('q', '').strip()
    trekkers_query = User.query.filter_by(role='trekker')
    if q:
        trekkers_query = trekkers_query.filter(
            or_(User.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'))
        )
    users = trekkers_query.all()
    return render_template('admin/users_list.html', users=users, role_filter='trekker', query=q)

@admin_bp.route('/admin/trekkers/blacklist/<int:id>', methods=['POST'])
@login_required
@admin_required
def trekker_blacklist(id):
    user = User.query.get_or_404(id)
    user.is_active = False
    db.session.commit()
    flash(f'{user.username} has been blacklisted.', 'danger')
    return redirect(url_for('admin.trekkers'))

@admin_bp.route('/admin/bookings')
@login_required
@admin_required
def bookings():
    booking_list = Booking.query.all()
    return render_template('admin/bookings_list.html', booking_list=booking_list)

@admin_bp.route('/admin/search')
@login_required
@admin_required
def search():
    q = request.args.get('q', '').strip()
    results = {'users': [], 'staff': [], 'treks': []}
    if q:
        results['users'] = User.query.filter(
            User.role == 'trekker',
            or_(User.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'))
        ).all()
        results['staff'] = User.query.join(StaffProfile).filter(
            User.role == 'staff',
            or_(User.username.ilike(f'%{q}%'), StaffProfile.name.ilike(f'%{q}%'))
        ).all()
        results['treks'] = Trek.query.filter(
            or_(Trek.name.ilike(f'%{q}%'), Trek.location.ilike(f'%{q}%'))
        ).all()
    return render_template('admin/search.html', results=results, query=q)
