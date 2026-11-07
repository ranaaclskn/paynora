"""Model ve internet olmadan çalışan testler: python -m unittest -v test_muhasebe.py"""
import unittest
from datetime import date

from db import baglan, fatura_ekle, odendi_isaretle
from dogrulama import fatura_dogrula
import ornek_veri
import sorgular


class Dogrulama(unittest.TestCase):
    def test_turkce_tutar_ve_tarih(self):
        f, h = fatura_dogrula({"karsi_taraf": "X", "tarih": "04.11.2026",
                               "matrah": "12.000,00", "kdv_orani": 10, "toplam": "13.200,00"})
        self.assertEqual(h, [])
        self.assertEqual(f["tarih"], "2026-11-04")
        self.assertEqual(f["kdv_tutari"], 1200.0)

    def test_sadece_toplamdan_hesap(self):
        f, h = fatura_dogrula({"karsi_taraf": "X", "tarih": "2026-11-01", "toplam": 1200, "kdv_orani": 20})
        self.assertEqual(h, [])
        self.assertEqual((f["matrah"], f["kdv_tutari"]), (1000.0, 200.0))

    def test_uydurma_kdv_yakalanir(self):
        _, h = fatura_dogrula({"karsi_taraf": "X", "tarih": "2026-11-01",
                               "matrah": 1000, "kdv_orani": 20, "kdv_tutari": 150, "toplam": 1150})
        self.assertTrue(any("KDV tutarı" in x for x in h))

    def test_gecersiz_oran(self):
        _, h = fatura_dogrula({"karsi_taraf": "X", "tarih": "2026-11-01", "matrah": 100, "kdv_orani": 18})
        self.assertTrue(any("KDV oranı" in x for x in h))

    def test_eksik_alanlar(self):
        _, h = fatura_dogrula({"matrah": 100, "kdv_orani": 20})
        self.assertTrue(any("tarih" in x for x in h))
        self.assertTrue(any("tedarikçi" in x for x in h))


class Sorgular(unittest.TestCase):
    def setUp(self):
        self.con = baglan(":memory:")
        ornek_veri.yukle(self.con)

    def test_kasim_kdv(self):
        k = sorgular.aylik_kdv(self.con, 2026, 11)
        # satış: 42000×%20=8400 | alış: 1200 + 67.5 + 760 + 5000 = 7027.5
        self.assertEqual(k["hesaplanan_kdv"], 8400.0)
        self.assertEqual(k["indirilecek_kdv"], 7027.5)
        self.assertEqual(k["odenecek_kdv"], 1372.5)

    def test_odenmemis_borclar(self):
        self.assertEqual(len(sorgular.odenmemis(self.con, "alis")), 4)

    def test_vadesi_yaklasan(self):
        liste = sorgular.vadesi_yaklasan(self.con, 7, bugun=date(2026, 11, 7))
        self.assertEqual([f["fatura_no"] for f in liste], ["KR-11", "MK-3021", "TG-1190"])
        self.assertEqual(liste[0]["kalan_gun"], -2)  # vadesi geçmiş

    def test_odendi_isaretle(self):
        kira = next(f for f in sorgular.odenmemis(self.con) if f["fatura_no"] == "KR-11")
        self.assertTrue(odendi_isaretle(self.con, kira["id"]))
        self.assertEqual(len(sorgular.odenmemis(self.con, "alis")), 3)

    def test_kategori_ozeti(self):
        ozet = sorgular.kategori_ozeti(self.con, 2026, 11)
        self.assertEqual(ozet[0]["kategori"], "Kira")


if __name__ == "__main__":
    unittest.main()
