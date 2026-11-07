"""PDF'ten sayfa sayfa metin çıkarma (pypdf). LangChain gerektirmez."""
from pypdf import PdfReader

# Bazı PDF'lerde yazı tipi kodlaması yüzünden Türkçe harfler bozuk çıkar (ı → Õ, ş → ú ...).
BOZUK_HARFLER = str.maketrans({"Õ": "ı", "ú": "ş", "÷": "ğ", "ù": "Ş"})

EN_AZ_KARAKTER = 80  # boş veya sadece sayfa numarası olan sayfaları atla


def temizle(metin):
    if any(h in metin for h in "Õú÷ù"):
        metin = metin.translate(BOZUK_HARFLER)
    satirlar = [s.rstrip() for s in metin.splitlines()]
    return "\n".join(satirlar).strip()


def pdf_sayfalari(yol):
    """(sayfa_no, metin) listesi döndürür. Sayfa numarası 1'den başlar.
    Taranmış (resim) sayfalardan metin çıkmaz; onlar için OCR gerekir."""
    okuyucu = PdfReader(str(yol))
    sonuc = []
    for i, sayfa in enumerate(okuyucu.pages, 1):
        metin = temizle(sayfa.extract_text() or "")
        if len(metin) >= EN_AZ_KARAKTER:
            sonuc.append((i, metin))
    return sonuc


if __name__ == "__main__":
    import sys
    sayfalar = pdf_sayfalari(sys.argv[1])
    print(len(sayfalar), "sayfada metin bulundu")
    print(sayfalar[0][1][:500] if sayfalar else "Metin yok (taranmış PDF olabilir)")
