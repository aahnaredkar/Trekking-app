from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional, ValidationError

class TrekForm(FlaskForm):
    name = StringField('Trek Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    difficulty = SelectField('Difficulty', choices=[
        ('Easy', 'Easy'), ('Moderate', 'Moderate'), ('Hard', 'Hard')
    ], validators=[DataRequired()])
    duration_days = IntegerField('Duration (Days)', validators=[InputRequired(), NumberRange(min=1)])
    slots_total = IntegerField('Total Slots', validators=[InputRequired(), NumberRange(min=1)])
    slots_available = IntegerField('Available Slots', validators=[InputRequired(), NumberRange(min=0)])
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'), ('Approved', 'Approved'),
        ('Open', 'Open'), ('Closed', 'Closed'), ('Completed', 'Completed')
    ])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    assigned_staff_id = SelectField('Assigned Staff', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Trek')

    def validate_start_date(self, start_date):
        import datetime
        if start_date.data and start_date.data < datetime.date.today():
            raise ValidationError("Start date cannot be earlier than today's local date.")

    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data:
            if end_date.data < self.start_date.data:
                raise ValidationError("End date cannot be earlier than start date.")

    def validate_slots_available(self, slots_available):
        if self.slots_total.data is not None and slots_available.data is not None:
            if slots_available.data > self.slots_total.data:
                raise ValidationError('Available slots cannot exceed total slots.')


class SlotUpdateForm(FlaskForm):
    slots_available = IntegerField('Available Slots', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Slots')

    def __init__(self, *args, **kwargs):
        self.confirmed_bookings_count = kwargs.pop('confirmed_bookings_count', 0)
        self.slots_total_limit = kwargs.pop('slots_total_limit', 0)
        super(SlotUpdateForm, self).__init__(*args, **kwargs)

    def validate_slots_available(self, slots_available):
        if slots_available.data is not None:
            if slots_available.data > self.slots_total_limit:
                raise ValidationError('Available slots cannot exceed total slots.')
            if slots_available.data < self.confirmed_bookings_count:
                raise ValidationError(f'Available slots cannot be less than confirmed bookings ({self.confirmed_bookings_count}).')


class StatusUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')

    def __init__(self, *args, **kwargs):
        self.current_status = kwargs.pop('current_status', 'Pending')
        super(StatusUpdateForm, self).__init__(*args, **kwargs)

    def validate_status(self, status_field):
        val = status_field.data
        allowed = {
            'Pending': ['Approved'],
            'Approved': ['Open'],
            'Open': ['Closed'],
            'Closed': ['Completed'],
            'Completed': []
        }
        if val != self.current_status:
            if val not in allowed.get(self.current_status, []):
                raise ValidationError(f'Invalid status transition from {self.current_status} to {val}.')

