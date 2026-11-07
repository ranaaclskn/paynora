"""RAG Adım 3-4: chunk'ları embedding'e çevir, Chroma vektör veritabanına kaydet.
Çalıştır: python rag_2_index.py   (belgeler değişince tekrar çalıştır)
"""
import shutil
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from config import CHROMA_DIR, COLLECTION, EMBED_MODEL, OLLAMA_URL, VERI_DIR
from rag_1_belgeler import belgeleri_yukle, chunklara_bol


def embedding_modeli():
    return OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL)


def indeks_olustur(sifirla=True):
    if sifirla and CHROMA_DIR.exists():
        # Güvenlik: yalnızca kendi indeks klasörümüzü sil
        if CHROMA_DIR.resolve().parent != VERI_DIR.resolve():
            raise RuntimeError(f"Güvensiz silme yolu: {CHROMA_DIR}")
        shutil.rmtree(CHROMA_DIR)
    parcalar = chunklara_bol(belgeleri_yukle())
    vt = Chroma.from_documents(
        documents=parcalar,
        ids=[p.metadata["chunk_id"] for p in parcalar],
        embedding=embedding_modeli(),
        collection_name=COLLECTION,
        persist_directory=str(CHROMA_DIR),
    )
    return vt, len(parcalar)


if __name__ == "__main__":
    print("Chunk'lar embedding'e çevriliyor (Ollama:", EMBED_MODEL, ")...")
    vt, n = indeks_olustur()
    vektor = embedding_modeli().embed_query("deneme")
    print("Kaydedilen chunk  :", n)
    print("Vektör boyutu     :", len(vektor))
    print("Koleksiyon kaydı  :", len(vt.get()["ids"]))
    print("Chroma klasörü    :", CHROMA_DIR)
