"""SQLite veritabanı: tablo oluşturma ve kayıt işlemleri."""
import sqlite3
from pathlib import Path
from config import DB_PATH

SEMA = """
CREATE TABLE IF NOT EXISTS faturalar (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    yon         TEXT NOT NULL CHECK (yon IN ('alis', 'satis')),  -- alış: gider, satış: gelir
    fatura_no   TEXT,
    karsi_taraf TEXT NOT NULL,          -- tedarikçi (alış) veya müşteri (satış)
    tarih       TEXT NOT NULL,          -- YYYY-AA-GG
    vade        TEXT,                   -- YYYY-AA-GG, yoksa NULL
    kategori    TEXT,
    matrah      REAL NOT NULL,          -- KDV hariç tutar
    kdv_orani   INTEGER NOT NULL,
    kdv_tutari  REAL NOT NULL,
    toplam      REAL NOT NULL,          -- KDV dahil tutar
    odendi      INTEGER NOT NULL DEFAULT 0,
    aciklama    TEXT,
    kaynak      TEXT DEFAULT 'manuel',  -- manuel / metin / foto
    olusturma   TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_fatura_tarih ON faturalar (tarih);
"""

ALANLAR = ("yon", "fatura_no", "karsi_taraf", "tarih", "vade", "kategori",
           "matrah", "kdv_orani", "kdv_tutari", "toplam", "odendi", "aciklama", "kaynak")


def baglan(yol=None):
    yol = Path(yol or DB_PATH)
    yol.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(yol)
    con.row_factory = sqlite3.Row
    con.executescript(SEMA)
    return con


def fatura_ekle(con, fatura):
    """Doğrulanmış bir fatura sözlüğünü kaydeder, yeni kaydın id'sini döndürür."""
    degerler = {a: fatura.get(a) for a in ALANLAR}
    degerler["odendi"] = int(bool(degerler["odendi"]))
    degerler["kaynak"] = degerler["kaynak"] or "manuel"
    sutunlar = ", ".join(degerler)
    yer = ", ".join(f":{a}" for a in degerler)
    cur = con.execute(f"INSERT INTO faturalar ({sutunlar}) VALUES ({yer})", degerler)
    con.commit()
    return cur.lastrowid


def odendi_isaretle(con, fatura_id):
    cur = con.execute("UPDATE faturalar SET odendi = 1 WHERE id = ?", (fatura_id,))
    con.commit()
    return cur.rowcount == 1
