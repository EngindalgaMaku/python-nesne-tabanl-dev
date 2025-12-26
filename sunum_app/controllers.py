from __future__ import annotations

from datetime import datetime

from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, render_template, request, url_for
from flask.views import MethodView
from flask_login import login_required, login_user, logout_user, current_user

from .extensions import db
from .models import Ayarlar, Degerlendirme, Ekip, Ogrenci, Ogretmen, Sunum, User
from .services.not_hesaplama import NotHesaplamaServisi


class IndexView(MethodView):
    def get(self):
        sunumlar = Sunum.query.order_by(Sunum.sunum_tarihi.desc()).all()

        servis = NotHesaplamaServisi()
        sunum_listesi = []
        for sunum in sunumlar:
            final_not_bilgisi = servis.hesapla_final_notu(sunum)
            sunum_listesi.append(
                {
                    "sunum": sunum,
                    "final_notu": final_not_bilgisi["final_notu"],
                    "ogretmen_notu": final_not_bilgisi["ogretmen_notu"],
                    "ogrenci_ortalama": final_not_bilgisi["ogrenci_ortalama"],
                    "degerlendirme_sayisi": final_not_bilgisi["degerlendirme_sayisi"],
                }
            )

        return render_template("index.html", sunum_listesi=sunum_listesi)


class LoginView(MethodView):
    def get(self):
        return render_template("login.html")

    def post(self):
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Başarıyla giriş yaptınız!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("admin_panel"))

        flash("Kullanıcı adı veya şifre yanlış!", "error")
        return render_template("login.html")


class LogoutView(MethodView):
    decorators = [login_required]

    def get(self):
        logout_user()
        flash("Başarıyla çıkış yaptınız!", "success")
        return redirect(url_for("index"))


class AdminPanelView(MethodView):
    decorators = [login_required]

    def get(self):
        if not current_user.is_admin:
            flash("Bu sayfaya erişim yetkiniz yok!", "error")
            return redirect(url_for("index"))

        ekip_sayisi = Ekip.query.count()
        ogrenci_sayisi = Ogrenci.query.count()
        ogretmen_sayisi = Ogretmen.query.count()
        sunum_sayisi = Sunum.query.count()

        ekipler = Ekip.query.all()
        ogrenciler = Ogrenci.query.all()
        ogretmenler = Ogretmen.query.all()
        sunumlar = Sunum.query.all()

        return render_template(
            "admin.html",
            ekip_sayisi=ekip_sayisi,
            ogrenci_sayisi=ogrenci_sayisi,
            ogretmen_sayisi=ogretmen_sayisi,
            sunum_sayisi=sunum_sayisi,
            ekipler=ekipler,
            ogrenciler=ogrenciler,
            ogretmenler=ogretmenler,
            sunumlar=sunumlar,
        )


class SunumDetayView(MethodView):
    def get(self, sunum_id: int):
        sunum = Sunum.query.get_or_404(sunum_id)
        servis = NotHesaplamaServisi()

        final_not_bilgisi = servis.hesapla_final_notu(sunum)
        degerlendirmeler = (
            Degerlendirme.query.filter_by(sunum_id=sunum_id)
            .order_by(Degerlendirme.id.desc())
            .all()
        )

        degerlendirmeler_with_avg = [
            {"degerlendirme": d, "ortalama": servis.hesapla_agirlikli_ortalama(d)}
            for d in degerlendirmeler
        ]

        return render_template(
            "sunum_detay.html",
            sunum=sunum,
            final_not_bilgisi=final_not_bilgisi,
            degerlendirmeler_with_avg=degerlendirmeler_with_avg,
        )


class DegerlendirmeYapView(MethodView):
    def get(self, sunum_id: int):
        sunum = Sunum.query.get_or_404(sunum_id)

        # Öğrenci aynı sunuma birden fazla değerlendirme yapamasın:
        # formdaki listeden daha önce değerlendirme yapan öğrencileri çıkar.
        existing_student_rows = (
            db.session.query(Degerlendirme.degerlendiren_ogrenci_id)
            .filter(
                Degerlendirme.sunum_id == sunum_id,
                Degerlendirme.degerlendiren_tipi == "ogrenci",
                Degerlendirme.degerlendiren_ogrenci_id.isnot(None),
            )
            .all()
        )
        existing_student_ids = [row[0] for row in existing_student_rows if row[0] is not None]

        query = Ogrenci.query.filter(Ogrenci.ekip_id != sunum.ekip_id)
        if existing_student_ids:
            query = query.filter(~Ogrenci.id.in_(existing_student_ids))

        ogrenciler = query.all()
        ogretmenler = Ogretmen.query.all()

        ayarlar_obj = Ayarlar.get_aktif_ayarlar()
        kriterler = [
            {
                "key": "konu_hakimiyeti",
                "label": ayarlar_obj.konu_hakimiyeti_etiket or "Konu Hakimiyeti",
                "weight": ayarlar_obj.konu_hakimiyeti_agirlik,
            },
            {
                "key": "anlatim",
                "label": ayarlar_obj.anlatim_etiket or "Anlatım",
                "weight": ayarlar_obj.anlatim_agirlik,
            },
            {
                "key": "giyim",
                "label": ayarlar_obj.giyim_etiket or "Giyim",
                "weight": ayarlar_obj.giyim_agirlik,
            },
            {
                "key": "ekip_uyumu",
                "label": ayarlar_obj.ekip_uyumu_etiket or "Ekip Uyumu ve Görev Paylaşımı",
                "weight": ayarlar_obj.ekip_uyumu_agirlik,
            },
            {
                "key": "gorsellik",
                "label": ayarlar_obj.gorsellik_etiket or "Görsellik",
                "weight": ayarlar_obj.gorsellik_agirlik,
            },
            {
                "key": "genel_gorus",
                "label": ayarlar_obj.genel_gorus_etiket or "Genel Görüş",
                "weight": ayarlar_obj.genel_gorus_agirlik,
            },
        ]

        return render_template(
            "degerlendirme_yap.html",
            sunum=sunum,
            ogrenciler=ogrenciler,
            ogretmenler=ogretmenler,
            kriterler=kriterler,
        )

    def post(self, sunum_id: int):
        sunum = Sunum.query.get_or_404(sunum_id)

        degerlendiren_tipi = request.form.get("degerlendiren_tipi")
        degerlendiren_ogrenci_id = request.form.get("degerlendiren_ogrenci_id")
        degerlendiren_ogretmen_id = request.form.get("degerlendiren_ogretmen_id")

        if degerlendiren_tipi == "ogrenci" and degerlendiren_ogrenci_id:
            ogrenci = Ogrenci.query.get(degerlendiren_ogrenci_id)
            if ogrenci and ogrenci.ekip_id == sunum.ekip_id:
                flash("Ekipler kendi sunumlarına puan veremez!", "error")
                return redirect(url_for("degerlendirme_yap", sunum_id=sunum_id))

            # Aynı öğrenci aynı sunuma tekrar puan veremesin
            existing = Degerlendirme.query.filter_by(
                sunum_id=sunum_id,
                degerlendiren_tipi="ogrenci",
                degerlendiren_ogrenci_id=int(degerlendiren_ogrenci_id),
            ).first()
            if existing:
                flash("Bu öğrenci bu sunumu zaten değerlendirdi!", "error")
                return redirect(url_for("sunum_detay", sunum_id=sunum_id))

        degerlendirme = Degerlendirme(
            sunum_id=sunum_id,
            degerlendiren_tipi=degerlendiren_tipi,
            degerlendiren_ogrenci_id=int(degerlendiren_ogrenci_id)
            if degerlendiren_ogrenci_id
            else None,
            degerlendiren_ogretmen_id=int(degerlendiren_ogretmen_id)
            if degerlendiren_ogretmen_id
            else None,
            konu_hakimiyeti=float(request.form.get("konu_hakimiyeti")),
            anlatim=float(request.form.get("anlatim")),
            giyim=float(request.form.get("giyim")),
            ekip_uyumu=float(request.form.get("ekip_uyumu")),
            gorsellik=float(request.form.get("gorsellik")),
            genel_gorus=float(request.form.get("genel_gorus")),
            yorum=request.form.get("yorum", ""),
        )

        try:
            db.session.add(degerlendirme)
            db.session.commit()
            flash("Değerlendirme başarıyla kaydedildi!", "success")
            return redirect(url_for("sunum_detay", sunum_id=sunum_id))
        except IntegrityError:
            db.session.rollback()
            if degerlendiren_tipi == "ogrenci":
                flash("Bu öğrenci bu sunumu zaten değerlendirdi!", "error")
            else:
                flash("Bu değerlendirme daha önce kaydedilmiş olabilir.", "error")
            return redirect(url_for("sunum_detay", sunum_id=sunum_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Hata: {str(e)}", "error")
            return redirect(url_for("degerlendirme_yap", sunum_id=sunum_id))


class AyarlarView(MethodView):
    decorators = [login_required]

    def get(self):
        if not current_user.is_admin:
            flash("Bu sayfaya erişim yetkiniz yok!", "error")
            return redirect(url_for("index"))

        ayarlar_obj = Ayarlar.get_aktif_ayarlar()
        return render_template("ayarlar.html", ayarlar=ayarlar_obj)

    def post(self):
        if not current_user.is_admin:
            flash("Bu sayfaya erişim yetkiniz yok!", "error")
            return redirect(url_for("index"))

        ayarlar_obj = Ayarlar.get_aktif_ayarlar()

        ayarlar_obj.konu_hakimiyeti_agirlik = float(request.form.get("konu_hakimiyeti_agirlik"))
        ayarlar_obj.anlatim_agirlik = float(request.form.get("anlatim_agirlik"))
        ayarlar_obj.giyim_agirlik = float(request.form.get("giyim_agirlik"))
        ayarlar_obj.ekip_uyumu_agirlik = float(request.form.get("ekip_uyumu_agirlik"))
        ayarlar_obj.gorsellik_agirlik = float(request.form.get("gorsellik_agirlik"))
        ayarlar_obj.genel_gorus_agirlik = float(request.form.get("genel_gorus_agirlik"))

        ayarlar_obj.konu_hakimiyeti_etiket = request.form.get("konu_hakimiyeti_etiket", "Konu Hakimiyeti")
        ayarlar_obj.anlatim_etiket = request.form.get("anlatim_etiket", "Anlatım")
        ayarlar_obj.giyim_etiket = request.form.get("giyim_etiket", "Giyim")
        ayarlar_obj.ekip_uyumu_etiket = request.form.get("ekip_uyumu_etiket", "Ekip Uyumu ve Görev Paylaşımı")
        ayarlar_obj.gorsellik_etiket = request.form.get("gorsellik_etiket", "Görsellik")
        ayarlar_obj.genel_gorus_etiket = request.form.get("genel_gorus_etiket", "Genel Görüş")
        ayarlar_obj.ogretmen_notu_agirlik = float(request.form.get("ogretmen_notu_agirlik"))
        ayarlar_obj.ogrenci_notu_agirlik = float(request.form.get("ogrenci_notu_agirlik"))

        kriter_toplam = (
            ayarlar_obj.konu_hakimiyeti_agirlik
            + ayarlar_obj.anlatim_agirlik
            + ayarlar_obj.giyim_agirlik
            + ayarlar_obj.ekip_uyumu_agirlik
            + ayarlar_obj.gorsellik_agirlik
            + ayarlar_obj.genel_gorus_agirlik
        )

        not_toplam = ayarlar_obj.ogretmen_notu_agirlik + ayarlar_obj.ogrenci_notu_agirlik

        if abs(kriter_toplam - 100.0) > 0.01:
            flash(
                f"Değerlendirme kriterleri ağırlıklarının toplamı 100 olmalıdır. Mevcut toplam: {kriter_toplam}",
                "error",
            )
            return redirect(url_for("ayarlar"))

        if abs(not_toplam - 100.0) > 0.01:
            flash(
                f"Not hesaplama ağırlıklarının toplamı 100 olmalıdır. Mevcut toplam: {not_toplam}",
                "error",
            )
            return redirect(url_for("ayarlar"))

        db.session.commit()
        flash("Ayarlar başarıyla güncellendi!", "success")
        return redirect(url_for("ayarlar"))


class AdminEkipView(MethodView):
    decorators = [login_required]

    def get(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))
        ekipler = Ekip.query.all()
        return render_template("admin_ekip.html", ekipler=ekipler)

    def post(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))

        if "ekle" in request.form:
            ekip = Ekip(isim=request.form.get("isim"), aciklama=request.form.get("aciklama", ""))
            db.session.add(ekip)
            db.session.commit()
            flash("Ekip başarıyla eklendi!", "success")
        elif "duzenle" in request.form:
            ekip = Ekip.query.get(int(request.form.get("ekip_id")))
            if ekip:
                ekip.isim = request.form.get("isim")
                ekip.aciklama = request.form.get("aciklama", "")
                db.session.commit()
                flash("Ekip başarıyla güncellendi!", "success")
        elif "sil" in request.form:
            ekip = Ekip.query.get(int(request.form.get("ekip_id")))
            if ekip:
                db.session.delete(ekip)
                db.session.commit()
                flash("Ekip başarıyla silindi!", "success")

        return redirect(url_for("admin_panel") + "#ekip")


class AdminOgrenciView(MethodView):
    decorators = [login_required]

    def get(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))
        ogrenciler = Ogrenci.query.all()
        ekipler = Ekip.query.all()
        return render_template("admin_ogrenci.html", ogrenciler=ogrenciler, ekipler=ekipler)

    def post(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))

        if "ekle" in request.form:
            numara = request.form.get("numara")
            existing = Ogrenci.query.filter_by(numara=numara).first()
            if existing:
                flash("Bu öğrenci numarası zaten kayıtlı!", "error")
                return redirect(url_for("admin_panel") + "#ogrenci")

            ogrenci = Ogrenci(
                ad=request.form.get("ad"),
                soyad=request.form.get("soyad"),
                numara=numara,
                ekip_id=int(request.form.get("ekip_id")) if request.form.get("ekip_id") else None,
            )
            db.session.add(ogrenci)
            try:
                db.session.commit()
                flash("Öğrenci başarıyla eklendi!", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Bu öğrenci numarası zaten kayıtlı!", "error")
        elif "duzenle" in request.form:
            ogrenci = Ogrenci.query.get(int(request.form.get("ogrenci_id")))
            if ogrenci:
                numara = request.form.get("numara")
                existing = Ogrenci.query.filter_by(numara=numara).first()
                if existing and existing.id != ogrenci.id:
                    flash("Bu öğrenci numarası zaten kayıtlı!", "error")
                    return redirect(url_for("admin_panel") + "#ogrenci")

                ogrenci.ad = request.form.get("ad")
                ogrenci.soyad = request.form.get("soyad")
                ogrenci.numara = numara
                ogrenci.ekip_id = int(request.form.get("ekip_id")) if request.form.get("ekip_id") else None
                try:
                    db.session.commit()
                    flash("Öğrenci başarıyla güncellendi!", "success")
                except IntegrityError:
                    db.session.rollback()
                    flash("Bu öğrenci numarası zaten kayıtlı!", "error")
        elif "sil" in request.form:
            ogrenci = Ogrenci.query.get(int(request.form.get("ogrenci_id")))
            if ogrenci:
                db.session.delete(ogrenci)
                db.session.commit()
                flash("Öğrenci başarıyla silindi!", "success")

        return redirect(url_for("admin_panel") + "#ogrenci")


class AdminOgretmenView(MethodView):
    decorators = [login_required]

    def get(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))
        ogretmenler = Ogretmen.query.all()
        return render_template("admin_ogretmen.html", ogretmenler=ogretmenler)

    def post(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))

        if "ekle" in request.form:
            ogretmen = Ogretmen(
                ad=request.form.get("ad"),
                soyad=request.form.get("soyad"),
                unvan=request.form.get("unvan", ""),
            )
            db.session.add(ogretmen)
            db.session.commit()
            flash("Öğretmen başarıyla eklendi!", "success")
        elif "duzenle" in request.form:
            ogretmen = Ogretmen.query.get(int(request.form.get("ogretmen_id")))
            if ogretmen:
                ogretmen.ad = request.form.get("ad")
                ogretmen.soyad = request.form.get("soyad")
                ogretmen.unvan = request.form.get("unvan", "")
                db.session.commit()
                flash("Öğretmen başarıyla güncellendi!", "success")
        elif "sil" in request.form:
            ogretmen = Ogretmen.query.get(int(request.form.get("ogretmen_id")))
            if ogretmen:
                db.session.delete(ogretmen)
                db.session.commit()
                flash("Öğretmen başarıyla silindi!", "success")

        return redirect(url_for("admin_panel") + "#ogretmen")


class AdminSunumView(MethodView):
    decorators = [login_required]

    def get(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))
        sunumlar = Sunum.query.all()
        ekipler = Ekip.query.all()
        return render_template("admin_sunum.html", sunumlar=sunumlar, ekipler=ekipler)

    def post(self):
        if not current_user.is_admin:
            return redirect(url_for("index"))

        if "ekle" in request.form:
            sunum = Sunum(
                baslik=request.form.get("baslik"),
                aciklama=request.form.get("aciklama", ""),
                sunum_tarihi=datetime.strptime(request.form.get("sunum_tarihi"), "%Y-%m-%dT%H:%M"),
                ekip_id=int(request.form.get("ekip_id")),
            )
            db.session.add(sunum)
            db.session.commit()
            flash("Sunum başarıyla eklendi!", "success")
        elif "duzenle" in request.form:
            sunum = Sunum.query.get(int(request.form.get("sunum_id")))
            if sunum:
                sunum.baslik = request.form.get("baslik")
                sunum.aciklama = request.form.get("aciklama", "")
                sunum.sunum_tarihi = datetime.strptime(request.form.get("sunum_tarihi"), "%Y-%m-%dT%H:%M")
                sunum.ekip_id = int(request.form.get("ekip_id"))
                db.session.commit()
                flash("Sunum başarıyla güncellendi!", "success")
        elif "sil" in request.form:
            sunum = Sunum.query.get(int(request.form.get("sunum_id")))
            if sunum:
                db.session.delete(sunum)
                db.session.commit()
                flash("Sunum başarıyla silindi!", "success")

        return redirect(url_for("admin_panel") + "#sunum")
