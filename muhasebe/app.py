"""Otto Peyzaj ön muhasebe asistanı — terminal menüsü: python app.py"""
from datetime import date

from config import FIRMA_ADI, KATEGORILER
from db import baglan, fatura_ekle, odendi_isaretle
from dogrulama import fatura_dogrula
import sorgular


def tl(x):
    """12345.6 → '12.345,60 TL'"""
    return f"{x:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def fatura_satiri(f):
    durum = "ödendi" if f["odendi"] else "AÇIK"
    yon = "Alış " if f["yon"] == "alis" else "Satış"
    vade = f" | vade {f['vade']}" if f.get("vade") else ""
    ek = f" ({f['kalan_gun']} gün)" if "kalan_gun" in f else ""
    return (f"#{f['id']:<3} {yon} | {f['tarih']} | {f['karsi_taraf'][:28]:<28} | "
            f"{tl(f['toplam']):>15} | {durum}{vade}{ek}")


def goster(fatura):
    for alan in ("yon", "fatura_no", "karsi_taraf", "tarih", "vade", "kategori",
                 "matrah", "kdv_orani", "kdv_tutari", "toplam", "aciklama"):
        print(f"  {alan:<12}: {fatura.get(alan)}")


def cok_satirli_girdi(mesaj):
    print(mesaj + " (bitirmek için boş satırda Enter)")
    satirlar = []
    while (satir := input()) != "":
        satirlar.append(satir)
    return "\n".join(satirlar)


def onayla_ve_kaydet(con, ham):
    """İnsan kontrolü (human-in-the-loop): kullanıcı onaylamadan hiçbir şey kaydedilmez."""
    fatura, hatalar = fatura_dogrula(ham)
    print("\nOkunan bilgiler:")
    goster(fatura)
    if hatalar:
        print("\n⚠ Kontrol hataları — bu haliyle kaydedilemez:")
        for h in hatalar:
            print("  -", h)
        return
    if not fatura.get("kategori"):
        print("\nKategori seç:")
        for i, k in enumerate(KATEGORILER, 1):
            print(f"  {i}. {k}")
        secim = input("Numara (boş = kategorisiz): ").strip()
        if secim.isdigit() and 1 <= int(secim) <= len(KATEGORILER):
            fatura["kategori"] = KATEGORILER[int(secim) - 1]
    if input("\nKaydedilsin mi? (e/h): ").strip().lower() == "e":
        print(f"✓ Kaydedildi (#{fatura_ekle(con, fatura)})")
    else:
        print("Kaydedilmedi.")


def metinden_ekle(con):
    from cikarim import metinden_cikar  # LangChain sadece bu adımda gerekli
    metin = cok_satirli_girdi("Fatura / fiş metnini yapıştır")
    if metin.strip():
        print("Model okuyor...")
        onayla_ve_kaydet(con, metinden_cikar(metin))


def fotograftan_ekle(con):
    from cikarim import fotograftan_cikar
    yol = input("Fotoğrafın dosya yolu: ").strip().strip("'\"")
    if yol:
        print("Model görseli okuyor...")
        onayla_ve_kaydet(con, fotograftan_cikar(yol))


def donem_sor():
    bugun = date.today()
    girdi = input(f"Dönem YYYY-AA (boş = {bugun:%Y-%m}): ").strip()
    if not girdi:
        return bugun.year, bugun.month
    yil, ay = girdi.split("-")
    return int(yil), int(ay)


def kdv_ozeti(con):
    yil, ay = donem_sor()
    k = sorgular.aylik_kdv(con, yil, ay)
    g = sorgular.gelir_gider(con, yil, ay)
    print(f"\n{k['donem']} dönemi")
    print(f"  Gelir (KDV hariç)      : {tl(g['gelir'])}")
    print(f"  Gider (KDV hariç)      : {tl(g['gider'])}")
    print(f"  Hesaplanan KDV (satış) : {tl(k['hesaplanan_kdv'])}")
    print(f"  İndirilecek KDV (alış) : {tl(k['indirilecek_kdv'])}")
    print(f"  → Ödenecek KDV         : {tl(k['odenecek_kdv'])}")
    if k["devreden_kdv"]:
        print(f"  → Sonraki aya devreden : {tl(k['devreden_kdv'])}")
    print("  (Tahmini özettir; beyanname için mali müşavirinize danışın.)")


def listele(baslik, kayitlar):
    print(f"\n{baslik}: {len(kayitlar)} fatura")
    for f in kayitlar:
        print(" ", fatura_satiri(f))
    if kayitlar:
        print(f"  Toplam: {tl(sum(f['toplam'] for f in kayitlar))}")


def kategori_raporu(con):
    yil, ay = donem_sor()
    print(f"\n{yil}-{ay:02d} giderleri:")
    for s in sorgular.kategori_ozeti(con, yil, ay):
        print(f"  {s['kategori']:<20} {s['adet']:>3} adet  {tl(s['toplam']):>15}")


MENU = f"""
===== {FIRMA_ADI} · Ön Muhasebe Asistanı =====
 1. Fatura metninden ekle (yapay zekâ)
 2. Fiş/fatura fotoğrafından ekle (yapay zekâ)
 3. Aylık KDV ve gelir-gider özeti
 4. Ödenmemiş borçlarımız (alış)
 5. Tahsil edilmemiş alacaklarımız (satış)
 6. Vadesi geçen / 7 gün içinde dolan faturalar
 7. Kategori bazında giderler
 8. Faturayı ödendi işaretle
 9. Belgelere soru sor (KDV kuralları, ödeme politikası, tedarikçi anlaşmaları)
 0. Çıkış"""


def belgelere_sor():
    from rag_3_sorgu import cevapla  # RAG paketleri sadece bu adımda gerekli
    soru = input("Soru: ").strip()
    if not soru:
        return
    print("Belgelerde aranıyor...")
    cevap, kaynaklar, _ = cevapla(soru)
    print("\n" + cevap)
    print("\nKaynaklar:", ", ".join(f"{k}={v}" for k, v in kaynaklar.items()))


def main():
    con = baglan()
    while True:
        print(MENU)
        secim = input("Seçim: ").strip()
        try:
            if secim == "1":
                metinden_ekle(con)
            elif secim == "2":
                fotograftan_ekle(con)
            elif secim == "3":
                kdv_ozeti(con)
            elif secim == "4":
                listele("Ödenmemiş alış faturaları", sorgular.odenmemis(con, "alis"))
            elif secim == "5":
                listele("Tahsil edilmemiş satış faturaları", sorgular.odenmemis(con, "satis"))
            elif secim == "6":
                listele("Vadesi geçen / yaklaşan", sorgular.vadesi_yaklasan(con, 7))
            elif secim == "7":
                kategori_raporu(con)
            elif secim == "8":
                no = input("Fatura # numarası: ").strip()
                print("✓ Güncellendi" if no.isdigit() and odendi_isaretle(con, int(no)) else "Bulunamadı")
            elif secim == "9":
                belgelere_sor()
            elif secim == "0":
                break
        except Exception as hata:  # menü çökmesin, hatayı göster
            print(f"Hata: {hata}")


if __name__ == "__main__":
    main()
