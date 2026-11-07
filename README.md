# Paynora · Otto Peyzaj Ön Muhasebe Asistanı

BTK Akademi *Yapay Zekâ Çözümleri Geliştirme Kariyer Atölyesi* final projesi.

Küçük işletmeler faturalarını kâğıtta, WhatsApp'ta ve e-postada biriktirir; KDV'yi, vadesi gelen
ödemeleri ve tahsil edilmemiş alacakları ay sonunda muhasebeciden öğrenir. Paynora, bir peyzaj
firması (Otto Peyzaj) senaryosunda bu işi yerel çalışan bir yapay zekâ asistanıyla çözer:

- **Fatura/fiş okur:** metin veya fotoğraftan tutar, KDV, tedarikçi, vade bilgisini çıkarır.
- **Kontrol eder:** modelin okuduğu rakamlar matematiksel olarak doğrulanır; tutarsızsa kaydedilmez.
- **İnsana sorar:** kullanıcı onaylamadan hiçbir kayıt veritabanına yazılmaz.
- **Soruları cevaplar:** aylık KDV, ödenmemiş borçlar, tahsil edilmemiş alacaklar, vadesi yaklaşanlar.
- **Gizlidir:** model bilgisayarda (Ollama) çalışır, fatura verisi dışarı gönderilmez.

## Klasörler

| Klasör | İçerik |
|---|---|
| `muhasebe/` | Ön muhasebe asistanı (final projesi) |
| `rag/` | Atölye 5-6. gün RAG çalışmaları (kampüs asistanı) |

## Kurulum (Linux / macOS)

```bash
cd muhasebe
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen2.5:1.5b          # metinden okuma
ollama pull qwen2.5vl:3b          # fotoğraftan okuma (isteğe bağlı)

python -m unittest -v test_muhasebe.py   # model gerektirmeyen testler
python ornek_veri.py                     # kurgusal örnek faturalar
python app.py                            # asistan menüsü
python cikarim.py                        # örnek bir faturayı modele okut
```

## Mimari

```
Fatura metni / fotoğrafı
        │
        ▼
 cikarim.py ── yerel Ollama modeli ──► JSON
        │
        ▼
 dogrulama.py ── KDV oranı, matrah × oran = KDV, matrah + KDV = toplam, tarih
        │
        ▼
 app.py ── kullanıcı onayı (human-in-the-loop)
        │
        ▼
 db.py ── SQLite (veri/otto.db)
        │
        ▼
 sorgular.py ── KDV özeti, borç/alacak, vade takibi (rakamlar SQL ile, LLM ile değil)
```

## Yol haritası

| Atölye günü | Adım | Durum |
|---|---|---|
| Gün 3-4 | Yapılandırılmış çıktı, yerel LLM, doğrulama, SQLite | ✅ |
| Gün 5-6 | KDV / e-fatura mevzuatı üzerinde kaynaklı cevap veren RAG (`[K1]` atıflı) | ⬜ |
| Gün 7 | LangGraph agent: soruya göre sorgu aracı / RAG / fatura ekleme seçimi | ⬜ |
| Gün 8 | n8n: her sabah vadesi yaklaşan faturalar için e-posta/Telegram hatırlatması | ⬜ |
| Gün 9-10 | Test senaryoları, ölçümler, sunum | ⬜ |

## Gizlilik notu

Bu repo herkese açıktır. `ornek_veri.py` içindeki firma adları kurgusaldır. Gerçek faturalar ve
`veri/` klasöründeki veritabanı `.gitignore` ile GitHub'a gönderilmez.

Asistanın KDV hesapları bilgilendirme amaçlıdır; resmi beyanname için mali müşavire danışılmalıdır.
