# Sunum Değerlendirme ve Notlandırma Sistemi

Python Nesne Yönelimli Programlama Final Projesi

## Proje Özeti

Bu proje, sınıf gruplarının sunumlarını değerlendirmek ve notlandırmak için geliştirilmiş bir web uygulamasıdır. Sistem, öğrencilerin ve öğretmenlerin sunumları belirli kriterlere göre puanlamasını ve final notlarının otomatik hesaplanmasını sağlar.

## Özellikler

- **Ekip Yönetimi**: 5-6 kişilik ekipler oluşturma ve yönetme
- **Sunum Yönetimi**: Her ekip için sunum kayıtları
- **Değerlendirme Sistemi**: 6 farklı kriterde puanlama
  - Konu Hakimiyeti (%15)
  - Anlatım (%15)
  - Giyim (%5)
  - Ekip Uyumu ve Görev Paylaşımı (%10)
  - Görsellik (%35)
  - Genel Görüş (%20)
- **Not Hesaplama**: 
  - Öğretmen notu: %60
  - Öğrenci notlarının ortalaması: %40
- **Dinamik Ayarlar**: Tüm ağırlıklar veritabanından dinamik olarak güncellenebilir
- **Güvenlik Kuralı**: Ekipler kendi sunumlarına puan veremez

## Teknolojiler

- **Dil**: Python 3.x
- **Framework**: Flask 3.x
- **Veritabanı**: SQLite (geliştirme için)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Mimari**: Nesne Yönelimli Programlama (OOP)

## Kurulum

1. Projeyi klonlayın veya indirin:
```bash
cd python_nesne
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Sunucuyu başlatın:
```bash
python app.py
```

Alternatif (Windows):
```bash
run_flask.bat
```

4. Tarayıcınızda açın:
```
http://127.0.0.1:5000
```

Varsayılan admin kullanıcı otomatik oluşturulur:
- kullanıcı adı: `admin`
- şifre: `admin123`

## Kullanım

### Admin Paneli

Admin paneline erişmek için:
```
http://127.0.0.1:5000/admin
```

Admin panelinden:
- Ekipler oluşturabilir ve düzenleyebilirsiniz
- Öğrenciler ekleyebilir ve ekiplere atayabilirsiniz
- Öğretmenler ekleyebilirsiniz
- Sunumlar oluşturabilirsiniz

### Web Arayüzü

Ana sayfadan:
- Tüm sunumları görüntüleyebilirsiniz
- Sunum detaylarını inceleyebilirsiniz
- Değerlendirme yapabilirsiniz
- Ayarları düzenleyebilirsiniz

### Değerlendirme Yapma

1. Ana sayfadan bir sunum seçin
2. "Değerlendir" butonuna tıklayın
3. Değerlendiren tipini seçin (Öğrenci veya Öğretmen)
4. İlgili kişiyi seçin
5. Her kriter için 0-100 arası puan verin
6. İsteğe bağlı yorum ekleyin
7. Kaydedin

**Önemli**: Ekipler kendi sunumlarına puan veremez. Sistem bunu otomatik olarak kontrol eder.

### Ayarları Düzenleme

Ayarlar sayfasından:
- Değerlendirme kriterleri ağırlıklarını değiştirebilirsiniz
- Final not hesaplama ağırlıklarını güncelleyebilirsiniz
- Tüm ağırlıkların toplamı 100 olmalıdır

## Veritabanı Tasarımı

### Modeller (OOP Sınıfları)

1. **Ayarlar**: Sistem ayarları ve ağırlıklar
2. **Ekip**: Sunum yapan ekipler
3. **Ogrenci**: Öğrenci bilgileri
4. **Ogretmen**: Öğretmen bilgileri
5. **Sunum**: Sunum kayıtları
6. **Degerlendirme**: Yapılan değerlendirmeler

### İlişkiler

- Bir Ekip birden fazla Ogrenci içerebilir
- Bir Ekip birden fazla Sunum yapabilir
- Bir Sunum birden fazla Degerlendirme alabilir
- Bir Degerlendirme bir Ogrenci veya Ogretmen tarafından yapılabilir

## Fonksiyonel Programlama Kullanımı

Bu proje ağırlıklı olarak **OOP mimari** ile düzenlenmiştir:

- Modeller: `sunum_app/models.py`
- Servis katmanı: `sunum_app/services/not_hesaplama.py`
- Controller (class-based views): `sunum_app/controllers.py`
- Route kaydı: `sunum_app/routes.py`

## Sınıf Yapıları

### NotHesaplamaServisi

Not hesaplama işlemlerini yöneten servis sınıfı.

**Metodlar:**
- `hesapla_agirlikli_ortalama()`: Bir değerlendirmenin ağırlıklı ortalamasını hesaplar
- `hesapla_final_notu()`: Final notunu hesaplar
- `sunum_istatistikleri()`: Sunum için detaylı istatistikler döndürür

## Proje Yapısı

```
python_nesne/
├── requirements.txt
├── README.md
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
└── static/
```

## Rapor İçeriği

Bu proje için hazırlanan rapor şunları içermelidir:

1. **Kullanılan Teknolojiler**: Flask, Python, Bootstrap
2. **Veritabanı Tasarımı**: Modeller ve ilişkiler
3. **Sınıf Yapıları**: OOP prensipleri ve UML diyagramı (opsiyonel)
4. **Sistem Özellikleri**: Değerlendirme kriterleri, not hesaplama

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## İletişim

Sorularınız için proje sahibi ile iletişime geçebilirsiniz.



