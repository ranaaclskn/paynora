"""LLM çıktısına körü körüne güvenmemek için kural tabanlı kontrol.

Model tutarları yanlış okuyabilir veya uydurabilir. Kayda geçmeden önce
matematik ve format kontrol edilir; tutarsız fatura kaydedilmez.
"""
from datetime import date
from config import KDV_ORANLARI, KATEGORILER

TOLERANS = 0.05  # kuruş yuvarlama farkı (TL)


def _sayi(deger):
    """'1.250,50' / '1250.50' / 1250.5 biçimlerini float'a çevirir."""
    if deger is None or deger == "":
        return None
    if isinstance(deger, (int, float)):
        return float(deger)
    metin = str(deger).replace("TL", "").replace("₺", "").strip()
    if "," in metin:  # Türkçe biçim: binlik nokta, ondalık virgül
        metin = metin.replace(".", "").replace(",", ".")
    try:
        return float(metin)
    except ValueError:
        return None


def _tarih(deger):
    if not deger:
        return None
    metin = str(deger).strip()
    for ayirici in (".", "/"):  # 05.11.2026 → 2026-11-05
        if ayirici in metin:
            parca = metin.split(ayirici)
            if len(parca) == 3 and len(parca[2]) == 4:
                metin = f"{parca[2]}-{parca[1].zfill(2)}-{parca[0].zfill(2)}"
    try:
        return date.fromisoformat(metin).isoformat()
    except ValueError:
        return None


def fatura_dogrula(ham):
    """(temiz_fatura, hatalar) döndürür. hatalar boşsa kayda hazırdır."""
    hatalar = []
    f = dict(ham)

    f["yon"] = (f.get("yon") or "alis").strip().lower()
    if f["yon"] not in ("alis", "satis"):
        hatalar.append(f"yön 'alis' veya 'satis' olmalı: {f['yon']}")

    f["karsi_taraf"] = (f.get("karsi_taraf") or "").strip()
    if not f["karsi_taraf"]:
        hatalar.append("tedarikçi / müşteri adı yok")

    f["tarih"] = _tarih(f.get("tarih"))
    if not f["tarih"]:
        hatalar.append("tarih okunamadı (YYYY-AA-GG veya GG.AA.YYYY)")
    if f.get("vade"):
        f["vade"] = _tarih(f["vade"])
        if not f["vade"]:
            hatalar.append("vade tarihi okunamadı")

    oran = _sayi(f.get("kdv_orani"))
    matrah, kdv, toplam = (_sayi(f.get(k)) for k in ("matrah", "kdv_tutari", "toplam"))

    if oran is None or int(oran) not in KDV_ORANLARI:
        hatalar.append(f"KDV oranı {KDV_ORANLARI} içinden olmalı: {f.get('kdv_orani')}")
    else:
        oran = int(oran)
        # Eksik tutarları diğerlerinden hesapla
        if matrah is None and toplam is not None:
            matrah = round(toplam / (1 + oran / 100), 2)
        if matrah is not None and kdv is None:
            kdv = round(matrah * oran / 100, 2)
        if matrah is not None and toplam is None and kdv is not None:
            toplam = round(matrah + kdv, 2)

        if None in (matrah, kdv, toplam):
            hatalar.append("tutar bilgisi yetersiz (matrah veya toplam gerekli)")
        else:
            if matrah <= 0:
                hatalar.append("matrah sıfırdan büyük olmalı")
            if abs(matrah * oran / 100 - kdv) > max(TOLERANS, matrah * 0.001):
                hatalar.append(f"KDV tutarı oranla uyuşmuyor: {matrah} × %{oran} ≠ {kdv}")
            if abs(matrah + kdv - toplam) > TOLERANS:
                hatalar.append(f"matrah + KDV ≠ toplam: {matrah} + {kdv} ≠ {toplam}")

    f.update(kdv_orani=oran, matrah=matrah, kdv_tutari=kdv, toplam=toplam)

    if f.get("kategori") and f["kategori"] not in KATEGORILER:
        hatalar.append(f"bilinmeyen kategori: {f['kategori']}")

    return f, hatalar
