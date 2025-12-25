from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def ensure_default_admin(cls) -> None:
        if not cls.query.filter_by(username="admin").first():
            admin = cls(username="admin", email="admin@example.com", is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()


class Ayarlar(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    konu_hakimiyeti_agirlik = db.Column(db.Float, default=15.0)
    anlatim_agirlik = db.Column(db.Float, default=15.0)
    giyim_agirlik = db.Column(db.Float, default=5.0)
    ekip_uyumu_agirlik = db.Column(db.Float, default=10.0)
    gorsellik_agirlik = db.Column(db.Float, default=35.0)
    genel_gorus_agirlik = db.Column(db.Float, default=20.0)

    ogretmen_notu_agirlik = db.Column(db.Float, default=60.0)
    ogrenci_notu_agirlik = db.Column(db.Float, default=40.0)

    aktif = db.Column(db.Boolean, default=True)

    @classmethod
    def get_aktif_ayarlar(cls) -> "Ayarlar":
        ayarlar = cls.query.filter_by(aktif=True).first()
        if not ayarlar:
            ayarlar = cls()
            db.session.add(ayarlar)
            db.session.commit()
        return ayarlar


class Ekip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)

    ogrenciler = db.relationship("Ogrenci", backref="ekip", lazy=True)
    sunumlar = db.relationship("Sunum", backref="ekip", lazy=True)

    def __repr__(self) -> str:
        return f"<Ekip {self.isim}>"


class Ogrenci(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    numara = db.Column(db.String(20), unique=True, nullable=False)
    ekip_id = db.Column(db.Integer, db.ForeignKey("ekip.id"), nullable=True)

    yaptigi_degerlendirmeler = db.relationship(
        "Degerlendirme", backref="degerlendiren_ogrenci", lazy=True
    )

    @property
    def tam_ad(self) -> str:
        return f"{self.ad} {self.soyad}"

    def __repr__(self) -> str:
        return f"<Ogrenci {self.tam_ad}>"


class Ogretmen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    unvan = db.Column(db.String(50))

    yaptigi_degerlendirmeler = db.relationship(
        "Degerlendirme", backref="degerlendiren_ogretmen", lazy=True
    )

    @property
    def tam_ad(self) -> str:
        return f"{self.ad} {self.soyad}"

    def __repr__(self) -> str:
        return f"<Ogretmen {self.tam_ad}>"


class Sunum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    sunum_tarihi = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ekip_id = db.Column(db.Integer, db.ForeignKey("ekip.id"), nullable=False)

    degerlendirmeler = db.relationship(
        "Degerlendirme", backref="sunum", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sunum {self.baslik}>"


class Degerlendirme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sunum_id = db.Column(db.Integer, db.ForeignKey("sunum.id"), nullable=False)
    degerlendiren_tipi = db.Column(db.String(10), nullable=False)
    degerlendiren_ogrenci_id = db.Column(db.Integer, db.ForeignKey("ogrenci.id"), nullable=True)
    degerlendiren_ogretmen_id = db.Column(db.Integer, db.ForeignKey("ogretmen.id"), nullable=True)

    konu_hakimiyeti = db.Column(db.Float, nullable=False)
    anlatim = db.Column(db.Float, nullable=False)
    giyim = db.Column(db.Float, nullable=False)
    ekip_uyumu = db.Column(db.Float, nullable=False)
    gorsellik = db.Column(db.Float, nullable=False)
    genel_gorus = db.Column(db.Float, nullable=False)

    yorum = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("sunum_id", "degerlendiren_ogrenci_id", name="unique_ogrenci_degerlendirme"),
        db.UniqueConstraint("sunum_id", "degerlendiren_ogretmen_id", name="unique_ogretmen_degerlendirme"),
    )

    def degerlendiren_adi(self) -> str:
        if self.degerlendiren_tipi == "ogrenci" and self.degerlendiren_ogrenci:
            return str(self.degerlendiren_ogrenci)
        if self.degerlendiren_tipi == "ogretmen" and self.degerlendiren_ogretmen:
            return str(self.degerlendiren_ogretmen)
        return "Bilinmeyen"

    def __repr__(self) -> str:
        return f"<Degerlendirme {self.id}>"
