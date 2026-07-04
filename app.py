import os
from flask import Flask, render_template
from config import Config
from models import db
from routes import login_manager
from routes.main import main_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

# pyrefly: ignore [missing-import]
from flask_wtf.csrf import CSRFProtect

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()
        from models.user import User
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@trekker.com',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
