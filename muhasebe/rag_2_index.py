"""RAG Adım 3-4: chunk'ları embedding'e çevir, Chroma vektör veritabanına kaydet.
Çalıştır: python rag_2_index.py   (belgeler değişince tekrar çalıştır)
"""
import shutil
import time
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from config import CHROMA_DIR, COLLECTION, EMBED_MODEL, OLLAMA_URL, VERI_DIR
from rag_1_belgeler import belgeleri_yukle, chunklara_bol

PAKET = 64  # her seferde embedding'e gönderilen chunk sayısı


def embedding_modeli():
    return OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL)


def indeks_olustur(sifirla=True):
    if sifirla and CHROMA_DIR.exists():
        # Güvenlik: yalnızca kendi indeks klasörümüzü sil
        if CHROMA_DIR.resolve().parent != VERI_DIR.resolve():
            raise RuntimeError(f"Güvensiz silme yolu: {CHROMA_DIR}")
        shutil.rmtree(CHROMA_DIR)
    parcalar = chunklara_bol(belgeleri_yukle())
    vt = Chroma(collection_name=COLLECTION, embedding_function=embedding_modeli(),
                persist_directory=str(CHROMA_DIR))
    baslangic = time.time()
    for i in range(0, len(parcalar), PAKET):
        paket = parcalar[i:i + PAKET]
        vt.add_documents(paket, ids=[p.metadata["chunk_id"] for p in paket])
        bitti = i + len(paket)
        print(f"\r  {bitti}/{len(parcalar)} chunk  ({time.time() - baslangic:.0f} sn)", end="", flush=True)
    print()
    return vt, len(parcalar)


if __name__ == "__main__":
    print("Chunk'lar embedding'e çevriliyor (Ollama:", EMBED_MODEL, ")...")
    vt, n = indeks_olustur()
    vektor = embedding_modeli().embed_query("deneme")
    print("Kaydedilen chunk  :", n)
    print("Vektör boyutu     :", len(vektor))
    print("Koleksiyon kaydı  :", len(vt.get()["ids"]))
    print("Chroma klasörü    :", CHROMA_DIR)
