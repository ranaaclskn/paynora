"""Deneme ve sunum için KURGUSAL örnek faturalar yükler: python ornek_veri.py

Buradaki firma ve kişi adları uydurmadır. Gerçek faturaları sadece kendi
bilgisayarında kullan; veri/ klasörü GitHub'a gönderilmez.
"""
from db import baglan, fatura_ekle
from dogrulama import fatura_dogrula

ORNEKLER = [
    # --- Ekim 2026 ---
    dict(yon="alis", fatura_no="YVF-0388", karsi_taraf="Yeşil Vadi Fidancılık", tarih="2026-10-03",
         vade="2026-11-02", kategori="Fidan ve Bitki", matrah=18500, kdv_orani=10, odendi=1,
         aciklama="Mazı ve şimşir fidanı"),
    dict(yon="alis", fatura_no="AS-7781", karsi_taraf="Anadolu Sulama Sistemleri", tarih="2026-10-08",
         vade="2026-11-07", kategori="Sulama Ekipmanı", matrah=9400, kdv_orani=20, odendi=1,
         aciklama="Damla sulama hortumu, vana"),
    dict(yon="alis", fatura_no="PO-55012", karsi_taraf="Merkez Petrol", tarih="2026-10-15",
         kategori="Akaryakıt", matrah=4200, kdv_orani=20, odendi=1),
    dict(yon="satis", fatura_no="OTP-2026-041", karsi_taraf="Bahçeli Konutları Site Yönetimi",
         tarih="2026-10-20", vade="2026-11-19", kategori="Peyzaj Hizmeti", matrah=68000,
         kdv_orani=20, odendi=1, aciklama="Ortak alan çim serimi ve ağaçlandırma"),
    dict(yon="satis", fatura_no="OTP-2026-042", karsi_taraf="Mavi Kule Plaza",
         tarih="2026-10-31", vade="2026-11-30", kategori="Bakım Sözleşmesi", matrah=15000,
         kdv_orani=20, aciklama="Ekim ayı bahçe bakımı"),
    # --- Kasım 2026 ---
    dict(yon="alis", fatura_no="YVF-0412", karsi_taraf="Yeşil Vadi Fidancılık", tarih="2026-11-04",
         vade="2026-12-04", kategori="Fidan ve Bitki", matrah=12000, kdv_orani=10,
         aciklama="40 adet mazı fidanı"),
    dict(yon="alis", fatura_no="TG-1190", karsi_taraf="Toprak Gübre Tarım Ürünleri", tarih="2026-11-05",
         vade="2026-11-12", kategori="Toprak ve Gübre", matrah=6750, kdv_orani=1,
         aciklama="Organik gübre, bitki toprağı"),
    dict(yon="alis", fatura_no="MK-3021", karsi_taraf="Usta Makine Servis", tarih="2026-11-06",
         vade="2026-11-10", kategori="Makine ve Bakım", matrah=3800, kdv_orani=20,
         aciklama="Çim biçme makinesi bakımı"),
    dict(yon="alis", fatura_no="KR-11", karsi_taraf="Demir Gayrimenkul", tarih="2026-11-01",
         vade="2026-11-05", kategori="Kira", matrah=25000, kdv_orani=20,
         aciklama="Depo kirası (vadesi geçti)"),
    dict(yon="satis", fatura_no="OTP-2026-043", karsi_taraf="Güneş Villaları",
         tarih="2026-11-06", vade="2026-11-21", kategori="Peyzaj Hizmeti", matrah=42000,
         kdv_orani=20, aciklama="Villa bahçesi düzenleme ve sulama kurulumu"),
]


def yukle(con=None):
    con = con or baglan()
    eklenen = 0
    for ornek in ORNEKLER:
        fatura, hatalar = fatura_dogrula(ornek)
        if hatalar:
            raise ValueError(f"{ornek['fatura_no']}: {hatalar}")
        fatura_ekle(con, fatura)
        eklenen += 1
    return eklenen


if __name__ == "__main__":
    con = baglan()
    if con.execute("SELECT COUNT(*) FROM faturalar").fetchone()[0]:
        print("Veritabanında zaten kayıt var; tekrar yüklenmedi.")
    else:
        print(f"{yukle(con)} örnek fatura yüklendi.")
