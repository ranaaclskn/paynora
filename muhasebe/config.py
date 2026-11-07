"""Otto Peyzaj ön muhasebe asistanı: tüm ayarlar tek yerde."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
VERI_DIR = ROOT / "veri"            # .gitignore'da: gerçek veriler GitHub'a gitmez
DB_PATH = Path(os.getenv("MUHASEBE_DB", VERI_DIR / "otto.db"))

FIRMA_ADI = "Otto Peyzaj"

# Ollama (yerel model: fatura verisi bilgisayardan dışarı çıkmaz)
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:1.5b")      # daha isabetli: qwen3:4b
VISION_MODEL = os.getenv("VISION_MODEL", "qwen2.5vl:3b")   # fiş/fatura fotoğrafı için

# Türkiye'de geçerli KDV oranları (%)
KDV_ORANLARI = (0, 1, 10, 20)

# Bir peyzaj firmasına özgü gider/gelir kategorileri
KATEGORILER = (
    "Fidan ve Bitki",
    "Toprak ve Gübre",
    "Sulama Ekipmanı",
    "Makine ve Bakım",
    "Akaryakıt",
    "İşçilik",
    "Kira",
    "Ofis ve Diğer",
    "Peyzaj Hizmeti",      # satış faturaları
    "Bakım Sözleşmesi",    # satış faturaları
)
