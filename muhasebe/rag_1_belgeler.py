"""RAG Adım 1-2: belgeleri yükle, chunk'lara böl. Çalıştır: python rag_1_belgeler.py"""
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import BELGE_DIR


def belgeleri_yukle():
    """belgeler/ klasöründeki her .txt dosyasını, meta.json'daki bilgilerle birlikte yükler."""
    meta = json.loads((BELGE_DIR / "meta.json").read_text(encoding="utf-8"))
    belgeler = []
    for yol in sorted(BELGE_DIR.glob("*.txt")):
        metin = yol.read_text(encoding="utf-8").strip()
        if metin:
            belgeler.append(Document(page_content=metin, metadata={"source": yol.name, **meta.get(yol.name, {})}))
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
        p.metadata["chunk_id"] = f"{kaynak}:{sayac[kaynak]:03d}"
    return parcalar


if __name__ == "__main__":
    belgeler = belgeleri_yukle()
    print("Belge sayısı:", len(belgeler))
    for b in belgeler:
        print(f"  {b.metadata['source']:<30} {b.metadata.get('tur', '-'):<18} {len(b.page_content)} karakter")

    parcalar = chunklara_bol(belgeler)
    print("\nChunk sayısı:", len(parcalar))
    for p in parcalar[:4]:
        print(f"\n[{p.metadata['chunk_id']}] ({len(p.page_content)} karakter)")
        print(p.page_content[:160].replace("\n", " "), "...")
