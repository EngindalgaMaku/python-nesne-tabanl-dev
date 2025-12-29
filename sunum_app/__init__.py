from __future__ import annotations

from pathlib import Path

import click
from sqlalchemy.exc import IntegrityError
from flask import Flask

from .extensions import db, login_manager
from .models import Ekip, Ogrenci, User
from .routes import register_routes


def _ensure_sqlite_columns(app: Flask) -> None:
    uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not uri or not str(uri).startswith("sqlite"):
        return

    engine = db.engine
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

    @app.cli.command("seed-sample-data")
    def seed_sample_data() -> None:
        ekip_isimleri = [
            "Kutup Yıldızları",
            "Anadolu Kartalları",
            "Gökyüzü Mühendisleri",
            "Mavi Ufuklar",
            "Bilim Yolcuları",
        ]

        ogrenciler_by_ekip = {
            "Kutup Yıldızları": [
                ("Ahmet", "Yılmaz"),
                ("Elif", "Kaya"),
                ("Mehmet", "Demir"),
                ("Zeynep", "Çelik"),
                ("Mert", "Aydın"),
            ],
            "Anadolu Kartalları": [
                ("Ayşe", "Şahin"),
                ("Mustafa", "Koç"),
                ("Fatma", "Öztürk"),
                ("Emre", "Arslan"),
                ("Sude", "Yıldırım"),
            ],
            "Gökyüzü Mühendisleri": [
                ("Can", "Kurt"),
                ("Ceren", "Aslan"),
                ("Oğuz", "Yalçın"),
                ("Buse", "Polat"),
                ("Kerem", "Güneş"),
            ],
            "Mavi Ufuklar": [
                ("Ece", "Taş"),
                ("Yusuf", "Korkmaz"),
                ("İrem", "Doğan"),
                ("Berk", "Aksoy"),
                ("Deniz", "Kaplan"),
            ],
            "Bilim Yolcuları": [
                ("Hakan", "Erdoğan"),
                ("Gizem", "Sezer"),
                ("Ömer", "Kılıç"),
                ("Duygu", "Çetin"),
                ("Kaan", "Bulut"),
            ],
        }

        existing_ekipler = {e.isim: e for e in Ekip.query.all()}
        created_teams = 0
        for ekip_adi in ekip_isimleri:
            if ekip_adi not in existing_ekipler:
                ekip = Ekip(isim=ekip_adi, aciklama="")
                db.session.add(ekip)
                existing_ekipler[ekip_adi] = ekip
                created_teams += 1

        if created_teams:
            db.session.commit()
            existing_ekipler = {e.isim: e for e in Ekip.query.all()}

        base_numara = 1001
        created_students = 0
        i = 0
        for ekip_adi in ekip_isimleri:
            ekip = existing_ekipler[ekip_adi]
            for ad, soyad in ogrenciler_by_ekip.get(ekip_adi, []):
                numara = str(base_numara + i)
                i += 1
                if Ogrenci.query.filter_by(numara=numara).first():
                    continue
                ogrenci = Ogrenci(ad=ad, soyad=soyad, numara=numara, ekip_id=ekip.id)
                db.session.add(ogrenci)
                try:
                    db.session.flush()
                except IntegrityError:
                    db.session.rollback()
                    continue
                created_students += 1

        db.session.commit()
        click.echo(
            f"Örnek veri tamamlandı. Eklenen ekip: {created_teams}, eklenen öğrenci: {created_students}."
        )

    with app.app_context():
        db.create_all()
        _ensure_sqlite_columns(app)
        User.ensure_default_admin()

    return app
