from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from ..models import Ayarlar, Degerlendirme, Sunum


@dataclass
class FinalNotBilgisi:
    ogretmen_notu: Optional[float]
    ogrenci_ortalama: Optional[float]
    final_notu: Optional[float]
    ogrenci_notlari: list[float]
    degerlendirme_sayisi: int


class NotHesaplamaServisi:
    def __init__(self, ayarlar: Optional[Ayarlar] = None):
        self._ayarlar = ayarlar

    @property
    def ayarlar(self) -> Ayarlar:
        if self._ayarlar is None:
            self._ayarlar = Ayarlar.get_aktif_ayarlar()
        return self._ayarlar

    def hesapla_agirlikli_ortalama(self, degerlendirme: Degerlendirme) -> float:
        a = self.ayarlar

        toplam = (
            (degerlendirme.konu_hakimiyeti * a.konu_hakimiyeti_agirlik / 100)
            + (degerlendirme.anlatim * a.anlatim_agirlik / 100)
            + (degerlendirme.giyim * a.giyim_agirlik / 100)
            + (degerlendirme.ekip_uyumu * a.ekip_uyumu_agirlik / 100)
            + (degerlendirme.gorsellik * a.gorsellik_agirlik / 100)
            + (degerlendirme.genel_gorus * a.genel_gorus_agirlik / 100)
        )

        return round(toplam, 2)

    def hesapla_final_notu(self, sunum: Sunum) -> Dict:
        a = self.ayarlar

        ogretmen_degerlendirme = Degerlendirme.query.filter_by(
            sunum_id=sunum.id, degerlendiren_tipi="ogretmen"
        ).first()

        ogrenci_degerlendirmeleri = Degerlendirme.query.filter_by(
            sunum_id=sunum.id, degerlendiren_tipi="ogrenci"
        ).all()

        ogretmen_notu = (
            self.hesapla_agirlikli_ortalama(ogretmen_degerlendirme)
            if ogretmen_degerlendirme
            else None
        )

        ogrenci_notlari: list[float] = [
            self.hesapla_agirlikli_ortalama(d) for d in ogrenci_degerlendirmeleri
        ]

        ogrenci_ortalama: Optional[float]
        if ogrenci_notlari:
            ogrenci_ortalama = round(sum(ogrenci_notlari) / len(ogrenci_notlari), 2)
        else:
            ogrenci_ortalama = None

        final_notu: Optional[float]
        if ogretmen_notu is not None and ogrenci_ortalama is not None:
            final_notu = round(
                (ogretmen_notu * a.ogretmen_notu_agirlik / 100)
                + (ogrenci_ortalama * a.ogrenci_notu_agirlik / 100),
                2,
            )
        elif ogretmen_notu is not None:
            final_notu = ogretmen_notu
        elif ogrenci_ortalama is not None:
            final_notu = ogrenci_ortalama
        else:
            final_notu = None

        result = FinalNotBilgisi(
            ogretmen_notu=ogretmen_notu,
            ogrenci_ortalama=ogrenci_ortalama,
            final_notu=final_notu,
            ogrenci_notlari=ogrenci_notlari,
            degerlendirme_sayisi=len(ogrenci_degerlendirmeleri),
        )

        return {
            "ogretmen_notu": result.ogretmen_notu,
            "ogrenci_ortalama": result.ogrenci_ortalama,
            "final_notu": result.final_notu,
            "ogrenci_notlari": result.ogrenci_notlari,
            "degerlendirme_sayisi": result.degerlendirme_sayisi,
        }
