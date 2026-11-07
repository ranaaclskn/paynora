"""Muhasebe soruları: SQL ile hesaplanır, LLM'e bırakılmaz (rakamlar kesin olmalı).

Sonraki adımda (Gün 7) bu fonksiyonlar LangGraph agent'ına araç (tool) olarak verilecek.
"""
from datetime import date, timedelta


def _donem(yil, ay):
    return f"{yil:04d}-{ay:02d}"


def aylik_kdv(con, yil, ay):
    """Hesaplanan KDV (satış) - indirilecek KDV (alış).

    Basitleştirilmiş özettir; resmi beyanname için mali müşavire danışılmalı.
    """
    satir = con.execute(
        """SELECT
             COALESCE(SUM(CASE WHEN yon='satis' THEN kdv_tutari END), 0) AS hesaplanan,
             COALESCE(SUM(CASE WHEN yon='alis'  THEN kdv_tutari END), 0) AS indirilecek
           FROM faturalar WHERE substr(tarih, 1, 7) = ?""",
        (_donem(yil, ay),),
    ).fetchone()
    hesaplanan, indirilecek = round(satir["hesaplanan"], 2), round(satir["indirilecek"], 2)
    fark = round(hesaplanan - indirilecek, 2)
    return {
        "donem": _donem(yil, ay),
        "hesaplanan_kdv": hesaplanan,
        "indirilecek_kdv": indirilecek,
        "odenecek_kdv": max(fark, 0),
        "devreden_kdv": max(-fark, 0),
    }


def odenmemis(con, yon=None):
    """Ödenmemiş faturalar. yon='alis' → bizim borçlarımız, 'satis' → alacaklarımız."""
    sql = "SELECT * FROM faturalar WHERE odendi = 0"
    params = ()
    if yon:
        sql += " AND yon = ?"
        params = (yon,)
    sql += " ORDER BY COALESCE(vade, tarih)"
    return [dict(r) for r in con.execute(sql, params)]


def vadesi_yaklasan(con, gun=7, bugun=None):
    """Vadesi geçmiş veya önümüzdeki `gun` gün içinde dolacak ödenmemiş faturalar."""
    bugun = bugun or date.today()
    sinir = (bugun + timedelta(days=gun)).isoformat()
    satirlar = con.execute(
        """SELECT * FROM faturalar
           WHERE odendi = 0 AND vade IS NOT NULL AND vade <= ?
           ORDER BY vade""",
        (sinir,),
    )
    sonuc = []
    for r in satirlar:
        d = dict(r)
        d["kalan_gun"] = (date.fromisoformat(d["vade"]) - bugun).days
        sonuc.append(d)
    return sonuc


def kategori_ozeti(con, yil, ay, yon="alis"):
    return [dict(r) for r in con.execute(
        """SELECT COALESCE(kategori, 'Kategorisiz') AS kategori,
                  COUNT(*) AS adet, ROUND(SUM(toplam), 2) AS toplam
           FROM faturalar WHERE yon = ? AND substr(tarih, 1, 7) = ?
           GROUP BY 1 ORDER BY toplam DESC""",
        (yon, _donem(yil, ay)),
    )]


def gelir_gider(con, yil, ay):
    satir = con.execute(
        """SELECT
             COALESCE(SUM(CASE WHEN yon='satis' THEN matrah END), 0) AS gelir,
             COALESCE(SUM(CASE WHEN yon='alis'  THEN matrah END), 0) AS gider
           FROM faturalar WHERE substr(tarih, 1, 7) = ?""",
        (_donem(yil, ay),),
    ).fetchone()
    gelir, gider = round(satir["gelir"], 2), round(satir["gider"], 2)
    return {"donem": _donem(yil, ay), "gelir": gelir, "gider": gider, "fark": round(gelir - gider, 2)}
