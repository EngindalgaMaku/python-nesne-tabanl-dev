from __future__ import annotations

from pathlib import Path

from flask import Flask

from .extensions import db, login_manager
from .models import User
from .routes import register_routes


def create_app() -> Flask:
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )

    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///sunum_degerlendirme.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Lütfen giriş yapın."

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    register_routes(app)

    with app.app_context():
        db.create_all()
        User.ensure_default_admin()

    return app
