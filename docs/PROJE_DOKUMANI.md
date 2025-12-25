# Sunum Değerlendirme Sistemi (Flask) – Proje Dokümantasyonu

## 1) Projenin Amacı

Bu proje, sınıf gruplarının (ekiplerin) sunumlarını değerlendirmek ve notlandırmak için geliştirilmiş bir web uygulamasıdır.

- Öğrenciler ve öğretmenler, sunumları belirli kriterlere göre puanlar.
- Sistem, değerlendirmelerden **ağırlıklı ortalama** ve **final notu** hesaplar.
- Ağırlıklar veritabanında tutulur ve admin panelinden güncellenebilir.

## 2) Mimari Yaklaşım

Proje “tamamen nesne tabanlı” olacak şekilde katmanlara ayrılmıştır:

- **App Factory** yaklaşımı ile uygulama oluşturma: `sunum_app.create_app()`
- **Extension** nesneleri ayrı modülde: `sunum_app/extensions.py`
- **Model katmanı** (ORM): `sunum_app/models.py`
- **Service katmanı** (iş kuralları / hesaplama): `sunum_app/services/not_hesaplama.py`
- **Controller katmanı** (class-based view): `sunum_app/controllers.py`
- **Route kaydı** (endpoint haritası): `sunum_app/routes.py`

Bu yapı sayesinde:

- Kod tek dosyada şişmez.
- Her sınıfın görevi netleşir.
- Test/yeniden kullanım kolaylaşır.

## 3) Proje Yapısı

```
python_nesne/
├── app.py
├── sunum_app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── controllers.py
│   ├── routes.py
│   └── services/
│       ├── __init__.py
│       └── not_hesaplama.py
├── templates/
├── static/
└── docs/
    └── PROJE_DOKUMANI.md
```

## 4) Çalıştırma

1. Bağımlılıkları kur:

```bash
pip install -r requirements.txt
```

2. Uygulamayı başlat:

```bash
python app.py
```

3. Tarayıcı:

- Ana sayfa: `http://127.0.0.1:5000/`
- Admin panel: `http://127.0.0.1:5000/admin`

Varsayılan admin kullanıcı, uygulama ilk kez açılırken otomatik oluşturulur:

- kullanıcı adı: `admin`
- şifre: `admin123`

## 5) Uygulama Akışı (Yüksek Seviye)

### 5.1 Uygulamanın ayağa kalkması

- `app.py` dosyası `create_app()` çağırır.
- `create_app()`:
  - Flask uygulamasını üretir.
  - `db` ve `login_manager` extension’larını init eder.
  - Route’ları register eder.
  - `db.create_all()` ile tabloları oluşturur.
  - `User.ensure_default_admin()` ile varsayılan admini garanti eder.

### 5.2 Sayfa akışı

- Kullanıcı `/login` ile giriş yapar.
- Admin yetkisi olan kullanıcı `/admin` paneline erişir.
- Admin panelinden:
  - Ekip / Öğrenci / Öğretmen / Sunum CRUD işlemleri yapılır.
  - Ayarlar ekranından ağırlıklar düzenlenir.
- Ana sayfada sunumlar listelenir, final notları servis üzerinden hesaplanır.

## 6) Sınıflar ve Görevleri

### 6.1 `sunum_app/extensions.py`

#### `db: SQLAlchemy`
- Uygulamanın veritabanı bağlantı ve ORM altyapısını sağlar.
- Model sınıfları `db.Model` üzerinden tanımlanır.

#### `login_manager: LoginManager`
- Flask-Login altyapısıdır.
- Session tabanlı giriş/çıkış ve `@login_required` gibi mekanizmaları sağlar.

### 6.2 `sunum_app/models.py`

Bu dosya proje verisini temsil eden ORM sınıflarını içerir.

#### `class User(UserMixin, db.Model)`
- Amaç: Sisteme giriş yapan kullanıcı (admin/normal) modelidir.
- Alanlar:
  - `username`, `email`, `password_hash`, `is_admin`
- Metodlar:
  - `set_password(password)`: şifreyi hashleyip saklar.
  - `check_password(password)`: hash doğrulaması yapar.
  - `ensure_default_admin()`: yoksa `admin/admin123` kullanıcısını oluşturur.

#### `class Ayarlar(db.Model)`
- Amaç: Değerlendirme kriter ağırlıkları ve final not ağırlıklarını tutar.
- Alanlar:
  - Kriter ağırlıkları: `konu_hakimiyeti_agirlik`, `anlatim_agirlik`, `giyim_agirlik`, `ekip_uyumu_agirlik`, `gorsellik_agirlik`, `genel_gorus_agirlik`
  - Final ağırlıkları: `ogretmen_notu_agirlik`, `ogrenci_notu_agirlik`
  - `aktif`: aktif ayar seti
- Metodlar:
  - `get_aktif_ayarlar()`: aktif ayar yoksa oluşturur ve döndürür.

#### `class Ekip(db.Model)`
- Amaç: Sunum yapan ekip bilgisini tutar.
- İlişkiler:
  - `ogrenciler`: ekipteki öğrenciler
  - `sunumlar`: ekibin sunumları

#### `class Ogrenci(db.Model)`
- Amaç: Öğrenci bilgilerini tutar.
- Alanlar:
  - `ad`, `soyad`, `numara`, `ekip_id`
- Özellikler:
  - `tam_ad`: ad + soyad birleşimi
- İlişkiler:
  - `yaptigi_degerlendirmeler`: öğrencinin yaptığı değerlendirmeler

#### `class Ogretmen(db.Model)`
- Amaç: Öğretmen bilgilerini tutar.
- Alanlar:
  - `ad`, `soyad`, `unvan`
- Özellikler:
  - `tam_ad`: ad + soyad birleşimi
- İlişkiler:
  - `yaptigi_degerlendirmeler`: öğretmenin yaptığı değerlendirmeler

#### `class Sunum(db.Model)`
- Amaç: Ekiplerin yaptığı sunum kayıtlarını tutar.
- Alanlar:
  - `baslik`, `aciklama`, `sunum_tarihi`, `ekip_id`
- İlişkiler:
  - `degerlendirmeler`: sunuma yapılan tüm değerlendirmeler

#### `class Degerlendirme(db.Model)`
- Amaç: Bir sunum için yapılan puanlama kaydı.
- Alanlar:
  - `sunum_id`
  - `degerlendiren_tipi`: `ogrenci` / `ogretmen`
  - `degerlendiren_ogrenci_id` / `degerlendiren_ogretmen_id`
  - 6 kriter puanı + `yorum`
- Kurallar:
  - Aynı öğrenci aynı sunuma tekrar puan veremesin diye `UniqueConstraint` var.
  - Aynı öğretmen aynı sunuma tekrar puan veremesin diye `UniqueConstraint` var.
- Metod:
  - `degerlendiren_adi()`: değerlendiren kişinin okunabilir adını döndürür.

### 6.3 `sunum_app/services/not_hesaplama.py`

#### `@dataclass FinalNotBilgisi`
- Amaç: Not hesaplama sonucunu tek bir obje olarak taşımak.
- Alanlar:
  - `ogretmen_notu`, `ogrenci_ortalama`, `final_notu`, `ogrenci_notlari`, `degerlendirme_sayisi`

#### `class NotHesaplamaServisi`
- Amaç: Not hesaplama iş kurallarını merkezi bir sınıfta toplamak.
- Tasarım:
  - Servis **instance tabanlıdır**. (Statik fonksiyonlar yerine OOP yaklaşımı)
  - `ayarlar` bilgisi lazy-load edilir (ilk ihtiyaçta DB’den çekilir).
- Metodlar:
  - `hesapla_agirlikli_ortalama(degerlendirme)`: kriter ağırlıklarına göre tek değerlendirme notu hesaplar.
  - `hesapla_final_notu(sunum)`: öğretmen notu ve öğrenci ortalamasını birleştirerek final notunu üretir.

### 6.4 `sunum_app/controllers.py` (Class-Based Views)

Her endpoint bir sınıf ile temsil edilir. Bu sayede HTTP metodları (`GET`, `POST`) sınıf içinde ayrı method olarak düzenlenir.

#### `class IndexView(MethodView)`
- Amaç: Ana sayfa.
- İş:
  - Sunumları listeler.
  - Her sunumun final notunu `NotHesaplamaServisi` ile hesaplar.

#### `class LoginView(MethodView)`
- Amaç: Giriş ekranı.
- `GET`: login sayfasını gösterir.
- `POST`: kullanıcı doğrulayıp session’a login eder.

#### `class LogoutView(MethodView)`
- Amaç: Çıkış.
- `GET`: kullanıcıyı logout eder.

#### `class AdminPanelView(MethodView)`
- Amaç: Admin dashboard.
- İş:
  - Admin yetkisi kontrolü (`current_user.is_admin`).
  - Sayısal istatistikler ve listeler.

#### `class SunumDetayView(MethodView)`
- Amaç: Sunum detay sayfası.
- İş:
  - Sunuma ait değerlendirmeleri listeler.
  - Her değerlendirme için ağırlıklı ortalama hesaplar.

#### `class DegerlendirmeYapView(MethodView)`
- Amaç: Değerlendirme formu.
- `GET`: form için öğrenci/öğretmen listelerini hazırlar.
- `POST`: değerlendirme kaydeder.
- Kritik kural:
  - Öğrenci, kendi ekibinin sunumuna puan veremez (controller içinde kontrol).

#### `class AyarlarView(MethodView)`
- Amaç: Ağırlık ayarlarını düzenleme ekranı.
- Yetki: admin.
- `POST`:
  - Ağırlıkların toplamlarını kontrol eder (kriter toplamı 100 olmalı; not toplamı 100 olmalı).

#### CRUD Controller’ları
- `AdminEkipView`: ekip ekle/düzenle/sil
- `AdminOgrenciView`: öğrenci ekle/düzenle/sil
- `AdminOgretmenView`: öğretmen ekle/düzenle/sil
- `AdminSunumView`: sunum ekle/düzenle/sil

Bu CRUD controller’larda `POST` içinde hangi butona basıldığına göre (`ekle/duzenle/sil`) işlem yapılır.

### 6.5 `sunum_app/routes.py`

- Amaç: URL -> Controller eşleştirmesini tek noktada tutmak.
- Her route `app.add_url_rule(...)` ile register edilir.
- Endpoint isimleri (ör. `login`, `admin_panel`) template’lerde `url_for(...)` ile kullanılır.

## 7) Endpoint Haritası

| URL | Metod | Controller | Açıklama |
|---|---|---|---|
| `/` | GET | `IndexView` | Ana sayfa |
| `/login` | GET/POST | `LoginView` | Giriş |
| `/logout` | GET | `LogoutView` | Çıkış |
| `/admin` | GET | `AdminPanelView` | Admin panel |
| `/sunum/<sunum_id>` | GET | `SunumDetayView` | Sunum detay |
| `/sunum/<sunum_id>/degerlendirme` | GET/POST | `DegerlendirmeYapView` | Değerlendirme |
| `/ayarlar` | GET/POST | `AyarlarView` | Ağırlık ayarları |
| `/admin/ekip` | GET/POST | `AdminEkipView` | Ekip CRUD |
| `/admin/ogrenci` | GET/POST | `AdminOgrenciView` | Öğrenci CRUD |
| `/admin/ogretmen` | GET/POST | `AdminOgretmenView` | Öğretmen CRUD |
| `/admin/sunum` | GET/POST | `AdminSunumView` | Sunum CRUD |

## 8) Önemli Notlar / İyileştirme Fikirleri

- `requirements.txt` dosyası projede olmalıdır (kurulum için). Eğer silindiyse tekrar eklemek gerekir.
- Form doğrulama (örn. puan aralığı 0-100) tarafında HTML input kısıtları + server-side validation genişletilebilir.
- `Ayarlar` modelinde “aktif tek kayıt” politikası gerekiyorsa, güncelleme ekranı bunu enforce edecek şekilde genişletilebilir.
