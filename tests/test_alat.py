"""Tes otomatis Ghost Ads Spy. Jalankan: python3 -m unittest discover -s tests -v  (tanpa internet)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AKAR / "scripts"))
import analisa  # noqa: E402
import buat_lp  # noqa: E402
import buat_papan  # noqa: E402
import hitung  # noqa: E402


def iklan(i, nama, hari, tujuan, frasa="f"):
    return {"id_iklan": i, "tautan_iklan": f"https://www.facebook.com/ads/library/?id={i}", "pengiklan": nama,
            "mulai": "2026-01-01", "hari": hari, "iklan_sama": 1, "tujuan": tujuan, "teks": "teks"}


def hasil(negara, pencarian):
    return {"negara": negara, "umur_dihitung_sampai": "2026-11-17", "pencarian": pencarian}


class TesAnalisa(unittest.TestCase):
    def test_satu_iklan_dihitung_sekali_lintas_frasa(self):
        a = iklan("1", "Toko A", 100, ["https://a.com/x"])
        d = hasil("ID", [{"jenis": "frasa", "cari": "satu", "iklan": [a], "catatan": None},
                         {"jenis": "frasa", "cari": "dua", "iklan": [a], "catatan": None}])
        ik, fr = analisa.gabung([("x", d)])
        self.assertEqual(len(ik), 1)
        rank = analisa.peringkat(ik)
        self.assertEqual(rank[0]["iklan_terlihat"], 1)
        self.assertEqual(rank[0]["ditemukan_lewat_frasa"], ["satu", "dua"])
        self.assertEqual(rank[0]["status"], "WINNING")

    def test_urut_umur_dan_domain_bersama(self):
        d = hasil("ID", [{"jenis": "frasa", "cari": "f", "catatan": None, "iklan": [
            iklan("1", "Baru", 5, ["https://sama.com/a"]), iklan("2", "Lama", 90, ["https://sama.com/b"])]}])
        rank = analisa.peringkat(analisa.gabung([("x", d)])[0])
        self.assertEqual([r["pengiklan"] for r in rank], ["Lama", "Baru"])
        dom = analisa.per_domain(rank)
        self.assertEqual(dom[0]["domain"], "sama.com")
        self.assertEqual(len(dom[0]["pengiklan"]), 2)

    def test_domain_bising_dibuang(self):
        d = hasil("ID", [{"jenis": "frasa", "cari": "f", "catatan": None, "iklan": [
            iklan("1", "A", 40, ["https://metastatus.com/ads-transparency", "https://jual.id/"])]}])
        rank = analisa.peringkat(analisa.gabung([("x", d)])[0])
        self.assertEqual(rank[0]["domain"], ["jual.id"])

    def test_lapak_dipisah_per_penjual(self):
        self.assertEqual(analisa.domain("https://lynk.id/tokoA/xyz"), "lynk.id/tokoA")
        self.assertNotEqual(analisa.domain("https://lynk.id/tokoA/x"), analisa.domain("https://lynk.id/tokoB/x"))
        self.assertEqual(analisa.domain("https://www.valeed.id/p"), "valeed.id")

    def test_batas_status(self):
        self.assertEqual(analisa.status_dari(30, 1), "WINNING")
        self.assertEqual(analisa.status_dari(29, 1), "POTENSIAL")
        self.assertEqual(analisa.status_dari(13, 10), "POTENSIAL")
        self.assertEqual(analisa.status_dari(13, 1), "BARU")
        self.assertIsNone(analisa.status_dari(None, 5))


class TesPapan(unittest.TestCase):
    def test_contoh_riset_lolos_pemeriksaan_dan_skor_dijumlah(self):
        d = json.loads((AKAR / "papan" / "bahan" / "data-contoh.json").read_text(encoding="utf-8"))
        g = buat_papan.gabung(buat_papan.gudang_kosong(), d)
        for i in g["ide"]:
            self.assertEqual(i["total"], i["malas"] + i["instant"] + i["applicable"])

    def test_status_tidak_cocok_umur_ditolak(self):
        ide = {"id": "i", "riset": "r", "nama": "n", "target": "t", "formula": "f", "malas": 1, "instant": 1, "applicable": 1,
               "pembanding": [{"nama": "p", "isi": "x", "hari": 10, "status": "WINNING"}]}
        with self.assertRaises(SystemExit):
            buat_papan.periksa_ide(ide)

    def test_halaman_tidak_memuat_tiga_nilai(self):
        with tempfile.TemporaryDirectory() as t:
            r = subprocess.run([sys.executable, "-I", str(AKAR / "scripts" / "buat_papan.py"), "contoh", "--folder", t],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            html = (Path(t) / "contoh-riset.html").read_text(encoding="utf-8")
            for kata in ('"malas"', '"instant"', '"applicable"'):
                self.assertNotIn(kata, html)


class TesHitung(unittest.TestCase):
    def test_batas_impas_dan_skenario(self):
        h = hitung.hitung(49000, biaya_alat=2000, potongan=5)
        self.assertAlmostEqual(h["sisa_sebelum_iklan"], 49000 - 2000 - 2450)
        self.assertGreater(h["skenario"]["baik"]["untung_per_penjualan"], h["skenario"]["buruk"]["untung_per_penjualan"])
        self.assertEqual(len(h["diperkirakan"]), 2)

    def test_biaya_melebihi_harga_ditolak(self):
        with self.assertRaises(ValueError):
            hitung.hitung(1000, potongan=100)

    def test_putusan_hasil_tes(self):
        self.assertEqual(hitung.baca_hasil(49000, 0, 0, 100000, 10, 0)["putusan"], "BELUM CUKUP DATA")
        self.assertEqual(hitung.baca_hasil(49000, 0, 0, 150000, 90, 4)["putusan"], "LANJUT DAN NAIKKAN PELAN")
        self.assertEqual(hitung.baca_hasil(49000, 0, 0, 200000, 120, 0)["putusan"], "BERHENTI ATAU PERBAIKI HALAMAN")


class TesHalamanJualan(unittest.TestCase):
    def spek(self):
        return json.loads(json.dumps(buat_lp.CONTOH))

    def test_contoh_lolos(self):
        buat_lp.periksa(self.spek())

    def test_aturan_ditolak(self):
        kasus = [lambda s: s.update(judul="Pasti kaya dari jualan online"),
                 lambda s: s.update(testimoni=[{"nama": "A", "isi": "bagus"}]),
                 lambda s: s.pop("dasar_harga_coret"),
                 lambda s: s["tombol"].update(tautan="http://x.com"),
                 lambda s: s.update(subjudul="Hitung mundur 10 menit lagi")]
        for ubah in kasus:
            s = self.spek()
            ubah(s)
            with self.assertRaises(SystemExit):
                buat_lp.periksa(s)

    def test_html_lolos_aman_dan_pixel(self):
        s = self.spek()
        s["judul"] = "<script>alert(1)</script>"
        s["pixel_id"] = "123456"
        h = buat_lp.rakit_html(s)
        self.assertNotIn("<script>alert(1)</script>", h)
        self.assertIn("fbq('init','123456')", h)


class TesCadangan(unittest.TestCase):
    def test_data_lama_dicadangkan_sebelum_ditimpa(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            d = json.loads((AKAR / "papan" / "bahan" / "data-contoh.json").read_text(encoding="utf-8"))
            d.pop("_lisensi", None)
            for r in d["riset"]:
                r.pop("contoh", None)
            g = buat_papan.gabung(buat_papan.gudang_kosong(), d)
            buat_papan.rakit(t, g)
            self.assertFalse((t / "cadangan").exists())
            g["riset"][0]["ringkas"] = "diubah"
            buat_papan.rakit(t, g)
            self.assertEqual(len(list((t / "cadangan").glob("data-riset-*.json"))), 1)
            self.assertEqual(json.loads((t / "data-riset.json").read_text(encoding="utf-8"))["_versi"], buat_papan.VERSI_DATA)


if __name__ == "__main__":
    unittest.main()
