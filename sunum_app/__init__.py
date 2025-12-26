from __future__ import annotations

from pathlib import Path

from flask import Flask

from .extensions import db, login_manager
from .models import User
from .routes import register_routes


def _ensure_sqlite_columns(app: Flask) -> None:
    uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not uri or not str(uri).startswith("sqlite"):
        return

    engine = db.get_engine(app)
    with engine.connect() as conn:
        table_rows = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ayarlar'"
        ).fetchall()
        if not table_rows:
            return

        columns = conn.exec_driver_sql("PRAGMA table_info(ayarlar)").fetchall()
        existing = {row[1] for row in columns}

        to_add = {
            "konu_hakimiyeti_etiket": "TEXT",
            "anlatim_etiket": "TEXT",
            "giyim_etiket": "TEXT",
            "ekip_uyumu_etiket": "TEXT",
            "gorsellik_etiket": "TEXT",
            "genel_gorus_etiket": "TEXT",
        }

        for col, col_type in to_add.items():
            if col not in existing:
                conn.exec_driver_sql(f"ALTER TABLE ayarlar ADD COLUMN {col} {col_type}")


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
        _ensure_sqlite_columns(app)
        User.ensure_default_admin()

    return app
