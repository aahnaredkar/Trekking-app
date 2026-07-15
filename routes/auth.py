from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.base import db
from models.user import User, StaffProfile
from forms.auth_forms import LoginForm, TrekkerRegisterForm, StaffRegisterForm

auth_bp = Blueprint('auth', __name__)

def redirect_by_role(user):
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'staff':
        return redirect(url_for('staff.dashboard'))
    else:
        return redirect(url_for('user.dashboard'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return render_template('auth/login.html', form=form)
            if user.role == 'staff':
                profile = user.staff_profile
                if not profile:
                    flash('Staff profile not found.', 'danger')
                    return render_template('auth/login.html', form=form)
                if profile.registration_status == 'Pending':
                    flash('Your registration is awaiting admin approval.', 'warning')
                    return render_template('auth/login.html', form=form)
                if profile.registration_status == 'Blacklisted':
                    flash('Your account has been blacklisted.', 'danger')
                    return render_template('auth/login.html', form=form)
                if profile.registration_status == 'Rejected':
                    flash('Your registration request was rejected.', 'danger')
                    return render_template('auth/login.html', form=form)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect_by_role(user)
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register/trekker', methods=['GET', 'POST'])
def register_trekker():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)
    form = TrekkerRegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='trekker',
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_trekker.html', form=form)

@auth_bp.route('/register/staff', methods=['GET', 'POST'])
def register_staff():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)
    form = StaffRegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='staff',
            is_active=True
        )
        user.set_password(form.password.data)
        
        profile = StaffProfile(
            name=form.name.data,
            contact_details=form.contact_details.data,
            bio=form.bio.data,
            experience_years=form.experience_years.data or 0,
            registration_status='Pending'
        )
        user.staff_profile = profile
        
        db.session.add(user)
        db.session.commit()
        flash('Registration request submitted! Awaiting admin approval.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_staff.html', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
