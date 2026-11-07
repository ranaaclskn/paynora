"""RAG Adım 1-2: belgeleri (.txt ve .pdf) yükle, chunk'lara böl. Çalıştır: python rag_1_belgeler.py"""
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import BELGE_DIR
from pdf_okuyucu import pdf_sayfalari

VARSAYILAN_META = {".pdf": {"tur": "kaynak_kitap"}, ".txt": {"tur": "genel"}}


def belgeleri_yukle():
    """belgeler/ klasöründeki .txt ve .pdf dosyalarını, meta.json'daki bilgilerle yükler.
    PDF'ler sayfa sayfa yüklenir; her sayfanın numarası metadata'da tutulur (kaynak gösterirken lazım)."""
    meta_yolu = BELGE_DIR / "meta.json"
    meta = json.loads(meta_yolu.read_text(encoding="utf-8")) if meta_yolu.exists() else {}
    belgeler = []
    for yol in sorted(BELGE_DIR.iterdir()):
        uzanti = yol.suffix.lower()
        if uzanti not in VARSAYILAN_META:
            continue
        ortak = {"source": yol.name, **VARSAYILAN_META[uzanti], **meta.get(yol.name, {})}
        if uzanti == ".txt":
            metin = yol.read_text(encoding="utf-8").strip()
            if metin:
                belgeler.append(Document(page_content=metin, metadata=ortak))
        else:
            for sayfa_no, metin in pdf_sayfalari(yol):
                belgeler.append(Document(page_content=metin, metadata={**ortak, "page": sayfa_no}))
    return belgeler


def chunklara_bol(belgeler, chunk_size=500, chunk_overlap=80):
    """Önce paragraf, sonra satır, sonra cümle sınırından böler.
    overlap: bir chunk'ın sonu sonrakinin başında tekrar eder, cümle ortadan kesilse de anlam kaybolmaz."""
    bolucu = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    parcalar = bolucu.split_documents(belgeler)
    sayac = {}
    for p in parcalar:
        kaynak = p.metadata["source"]
        sayac[kaynak] = sayac.get(kaynak, -1) + 1
        sayfa = f":s{p.metadata['page']}" if "page" in p.metadata else ""
        p.metadata["chunk_id"] = f"{kaynak}{sayfa}:{sayac[kaynak]:04d}"
    return parcalar


if __name__ == "__main__":
    belgeler = belgeleri_yukle()
    ozet = {}
    for b in belgeler:
        s = ozet.setdefault(b.metadata["source"], {"tur": b.metadata.get("tur", "-"), "parca": 0, "karakter": 0})
        s["parca"] += 1
        s["karakter"] += len(b.page_content)
    print("Belge sayısı:", len(ozet))
    for ad, s in ozet.items():
        birim = "sayfa" if ad.lower().endswith(".pdf") else "dosya"
        print(f"  {ad[:45]:<45} {s['tur']:<18} {s['parca']:>4} {birim}  {s['karakter']:>8} karakter")

    parcalar = chunklara_bol(belgeler)
    print("\nChunk sayısı:", len(parcalar))
    for p in parcalar[:3] + parcalar[-2:]:
        print(f"\n[{p.metadata['chunk_id']}] ({len(p.page_content)} karakter)")
        print(p.page_content[:160].replace("\n", " "), "...")
