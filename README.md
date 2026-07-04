# Trekking Management System

A role-based trekking application for managing treks, bookings, trek staff, and users (trekkers). Built with Flask and styled with a premium outdoor design system.

## Technologies Used

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Templating | Jinja2 |
| Frontend | HTML, CSS, Bootstrap 5 |
| Database | SQLite |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login, Werkzeug Password Hashing |
| Forms | WTForms, Flask-WTF |

## Python Version

Python 3.8 or higher is required.

## Setup Instructions

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**Linux / macOS:**
```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000`.

On the first launch, the local database (`instance/trekking.db`) is automatically initialized and seeded with default administrator credentials (see below).

## Database Initialization & Default Admin

The application uses an SQLite database located at `instance/trekking.db` which is generated programmatically on startup by standard SQLAlchemy `db.create_all()` routines.

A default administrative user is created automatically if it's missing in the database:
- **Role:** Administrator
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@trekker.com`

## Project Status

The Trekking Management System UI modernization is complete. All core features (treks, bookings, interactive search, slots adjustments, roles authentication, and staff workflow assignment) are functional with a premium outdoor theme.

## Project Folder Structure

```text
trekking_web_app/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── instance/
│   └── trekking.db
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── booking.py
│   ├── trek.py
│   └── user.py
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── main.py
│   ├── staff.py
│   └── user.py
├── forms/
│   ├── __init__.py
│   ├── auth_forms.py
│   └── trek_forms.py
├── services/
│   └── __init__.py
├── utils/
│   ├── __init__.py
│   └── decorators.py
├── templates/
│   ├── index.html
│   ├── layouts/
│   │   └── base.html
│   ├── components/
│   │   ├── alert_banner.html
│   │   ├── form_macros.html
│   │   ├── navbar.html
│   │   └── trek_card.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── register_staff.html
│   │   └── register_trekker.html
│   ├── admin/
│   │   ├── bookings_list.html
│   │   ├── dashboard.html
│   │   ├── search.html
│   │   ├── trek_create.html
│   │   ├── trek_edit.html
│   │   ├── treks_list.html
│   │   └── users_list.html
│   ├── staff/
│   │   ├── dashboard.html
│   │   ├── edit_slots.html
│   │   └── participants.html
│   ├── user/
│   │   ├── booking_detail.html
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   └── trek_search.html
│   └── errors/
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
└── static/
    ├── css/
    │   └── style.css
    ├── icons/
    │   └── .gitkeep
    └── images/
        ├── .gitkeep
        └── trek_home.png
```

## IDE Interpreter Note

If your IDE shows errors for `flask_sqlalchemy` or `flask_login`, it is using the system Python instead of the virtual environment. Point your IDE to `venv\Scripts\python.exe` (Windows) or `venv/bin/python` (Linux/macOS).
