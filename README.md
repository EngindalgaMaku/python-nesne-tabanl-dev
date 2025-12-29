# Sunum Değerlendirme Sistemi

Bu proje, öğrencilerin ve öğretmenlerin, yapılan sunumları belirli kriterlere göre değerlendirmesini sağlayan ve bu değerlendirmelerden otomatik olarak final notları hesaplayan bir Flask web uygulamasıdır. Sistem, özellikle Nesne Yönelimli Programlama (OOP) prensipleri kullanılarak modüler ve yönetilebilir bir yapıda geliştirilmiştir.

## Proje Akışı ve Sayfalar

### 1. Ana Sayfa (`/`)
Kullanıcıların karşılandığı ana ekrandır. Bu sayfada:
- Mevcut tüm sunumlar kartlar halinde listelenir.
- Her sunumun final notu, değerlendirme sayısı ve temel bilgileri (ekip, tarih) görüntülenir.
- Değerlendirmesi yapılmamış sunumlar için bir uyarı gösterilir.
- Kullanıcılar, sunum detaylarını görmek veya yeni bir değerlendirme yapmak için ilgili butonları kullanabilir.
- Admin kullanıcılar için "Yeni Sunum Ekle" butonu bulunur.

### 2. Sunum Detay Sayfası (`/sunum/<id>`)
Bir sunuma ait tüm detayların ve istatistiklerin bulunduğu sayfadır.
- Sunumun final notu, öğretmen ve öğrenci not ortalamaları gibi genel istatistikler gösterilir.
- Bu sunuma yapılmış tüm değerlendirmeler (hem öğretmen hem de öğrenci) listelenir.
- Her değerlendirmenin kriter bazında puanları ve ağırlıklı ortalaması görüntülenir.

### 3. Değerlendirme Yapma Sayfası (`/sunum/<id>/degerlendirme`)
Yeni bir değerlendirme eklemek için kullanılan form sayfasıdır.
- Değerlendirmeyi yapan kişinin tipi (Öğrenci/Öğretmen) seçilir.
- Seçilen tipe göre ilgili öğrenciler veya öğretmenler listelenir.
- Admin panelinden tanımlanmış 6 ana kriter için 0-100 arasında puanlama yapılır.
- **Önemli Kural:** Bir ekibe üye olan öğrenciler, kendi ekiplerinin sunumunu değerlendiremez. Sistem bunu otomatik olarak engeller.

### 4. Admin Paneli (`/admin`)
Uygulamanın yönetim merkezidir. Sadece admin yetkisine sahip kullanıcılar erişebilir. Panel sekmelere ayrılmıştır:
- **Ekipler:** Yeni ekipler oluşturulur, mevcut ekipler düzenlenir veya silinir.
- **Öğrenciler:** Öğrenciler yönetilir ve ekiplere atanır. Arama ve filtreleme özellikleri mevcuttur.
- **Öğretmenler:** Öğretmen kayıtları yönetilir.
- **Sunumlar:** Yeni sunumlar oluşturulur ve yönetilir.
- **Değerlendirmeler:** Yapılan tüm değerlendirmeler listelenir ve admin tarafından silinebilir.

### 5. Ayarlar Sayfası (`/ayarlar`)
Sistemin hesaplama mantığını yöneten kritik sayfadır. Yalnızca admin erişimine açıktır.
- **Kriter Ağırlıkları:** 6 ana değerlendirme kriterinin (Konu Hakimiyeti, Görsellik vb.) final notuna etkisini belirleyen yüzdelik ağırlıklar ayarlanır.
- **Kriter Başlıkları:** Değerlendirme formunda görünen kriter etiketleri (örn: "Görsellik" yerine "Sunum Tasarımı") değiştirilebilir.
- **Final Not Hesaplama Ağırlıkları:** Öğretmen ve öğrenci değerlendirmelerinin final notuna ne kadar etki edeceği buradan ayarlanır (örn: %60 Öğretmen, %40 Öğrenci).

---

## Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Projeyi Klonlama
```bash
git clone https://github.com/EngindalgaMaku/python-nesne-tabanl-dev.git
cd python-nesne-tabanl-dev
```

### 2. Sanal Ortam (Virtual Environment) Oluşturma
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Gerekli Paketleri Yükleme
```bash
pip install -r requirements.txt
```

### 4. Veritabanını Oluşturma
Uygulama ilk kez çalıştırıldığında `sunum_degerlendirme.db` adında bir SQLite veritabanı dosyası otomatik olarak oluşturulur ve gerekli tablolar kurulur. Ayrıca, varsayılan bir admin kullanıcısı da yaratılır.

### 5. Örnek Veri Ekleme (İsteğe Bağlı)
Uygulamayı test etmek için örnek ekipler ve öğrenciler ekleyebilirsiniz:
```bash
flask seed-sample-data
```

### 6. Uygulamayı Başlatma
```bash
flask run
# veya
python app.py
```
Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır.

### Varsayılan Admin Bilgileri
- **Kullanıcı Adı:** `admin`
- **Şifre:** `admin123`

---

## Kod Mimarisi ve Sınıf Yapıları

Proje, `sunum_app` adında bir paket içerisinde modüler bir yapıda organize edilmiştir. Bu yapı, kodun okunabilirliğini ve bakımını kolaylaştırır.

### Proje Dosya Yapısı
```
python_nesne/
├── sunum_app/
│   ├── static/              # CSS, JS, resimler ve favicon gibi statik dosyalar
│   ├── templates/           # HTML şablonları
│   ├── __init__.py          # Flask uygulama fabrikası (create_app)
│   ├── controllers.py       # Rota mantığını içeren Class-Based View'lar
│   ├── models.py            # SQLAlchemy veritabanı modelleri (sınıflar)
│   ├── routes.py            # URL rotalarını controllera bağlayan dosya
│   └── services/
│       └── not_hesaplama.py # Not hesaplama mantığını içeren servis sınıfı
├── app.py                   # Uygulama giriş noktası
├── requirements.txt         # Proje bağımlılıkları
└── README.md                # Bu dosya
```

### Ana Sınıflar ve Görevleri

#### `sunum_app/models.py`
Bu dosya, veritabanı tablolarını temsil eden tüm SQLAlchemy sınıflarını içerir. Her sınıf, bir tabloya karşılık gelir ve Nesne Yönelimli Programlama'nın temelini oluşturur.

- **`User(db.Model, UserMixin)`**: Kullanıcıları (admin) temsil eder. Giriş işlemleri için `Flask-Login` ile entegredir.
- **`Ekip(db.Model)`**: Sunum yapan öğrenci ekiplerini temsil eder. Her ekibin bir ismi, açıklaması ve birden çok öğrencisi olabilir.
- **`Ogrenci(db.Model)`**: Öğrencileri temsil eder. Her öğrencinin adı, soyadı, numarası ve bağlı olduğu bir ekibi vardır.
- **`Ogretmen(db.Model)`**: Değerlendirme yapabilen öğretmenleri temsil eder.
- **`Sunum(db.Model)`**: Ekipler tarafından yapılan sunumları temsil eder. Bir sunumun başlığı, tarihi ve hangi ekibe ait olduğu bilgisi tutulur.
- **`Degerlendirme(db.Model)`**: Bir sunuma yapılmış tek bir değerlendirmeyi temsil eder. Kimin yaptığı (öğrenci/öğretmen), hangi sunuma yapıldığı ve 6 kriter için verilen puanları içerir.
- **`Ayarlar(db.Model)`**: Sistem genelindeki tüm dinamik ayarları (kriter ve not ağırlıkları, etiketler) tutan sınıftır. Bu tablo genellikle tek bir satır içerir.

#### `sunum_app/services/not_hesaplama.py`
Bu dosya, not hesaplamayla ilgili karmaşık iş mantığını modellerden ayırarak ayrı bir servis katmanında toplar. Bu, "Separation of Concerns" (Sorumlulukların Ayrılması) ilkesine güzel bir örnektir.

- **`NotHesaplamaServisi`**:
  - **`__init__(self, sunum_id)`**: Servis, belirli bir `sunum_id`'si ile başlatılır.
  - **`hesapla_agirlikli_ortalama(self, degerlendirme)`**: Tek bir değerlendirmenin, `Ayarlar` tablosundaki ağırlıklara göre not ortalamasını hesaplar.
  - **`hesapla_final_notu(self)`**: Bir sunum için yapılmış tüm değerlendirmeleri alır, öğretmen ve öğrenci notlarını ayırır, ortalamalarını alır ve `Ayarlar` tablosundaki final notu ağırlıklarına göre nihai notu hesaplar.
  - **`sunum_istatistikleri(self)`**: Sunum detay sayfasında gösterilen tüm zengin veriyi (final notu, ortalamalar, değerlendirme listesi vb.) üreten ana metottur.

#### `sunum_app/controllers.py`
Bu dosya, Flask'in Class-Based View'larını kullanarak her bir rota için iş mantığını içerir. Her view sınıfı, belirli bir URL'ye gelen `GET`, `POST` gibi HTTP isteklerini yönetir.

- **`IndexView`**: Ana sayfayı (`/`) render eder. Tüm sunumları ve istatistiklerini `NotHesaplamaServisi`'ni kullanarak hazırlar.
- **`AdminPanelView`**: Admin panelinin (`/admin`) ana görünümüdür. Tüm sekmeler için gerekli verileri (ekip listesi, öğrenci listesi vb.) toplar ve şablona gönderir.
- **`DegerlendirmeYapView`**: Değerlendirme formunu (`/sunum/<id>/degerlendirme`) gösterir ve `POST` isteği ile gelen yeni değerlendirmeleri veritabanına kaydeder.
- **`AyarlarView`**: Ayarlar sayfasını yönetir. Mevcut ayarları gösterir ve `POST` isteği ile gelen güncellemeleri veritabanına kaydeder.
