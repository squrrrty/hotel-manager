from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if app.config.get("PRODUCTION"):
        if len(app.config.get("SECRET_KEY", "")) < 32:
            raise RuntimeError("Для хостинга задайте SECRET_KEY длиной не менее 32 символов")
        if not app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("postgresql"):
            raise RuntimeError("Для хостинга задайте DATABASE_URL вашей PostgreSQL")

    from . import models  # noqa: F401

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .csrf import init_csrf
    init_csrf(app)

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.rooms import rooms_bp
    from .routes.guests import guests_bp
    from .routes.bookings import bookings_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(rooms_bp, url_prefix="/rooms")
    app.register_blueprint(guests_bp, url_prefix="/guests")
    app.register_blueprint(bookings_bp, url_prefix="/bookings")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    return app
