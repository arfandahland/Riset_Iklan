#!/usr/bin/env python3
"""Pembuka halaman jualan (LP) pesaing untuk Ghost Ads Spy.

Produk resmi Regrow Labs.

Membuka halaman tujuan tombol iklan lewat browser tanpa tampilan, lalu mengambil judul, alamat akhir,
harga yang tertulis, dan isi teksnya. Asisten AI yang menjalankannya. Pengguna tidak perlu membuka apa pun.

Pemakaian:

  python3 buka_lp.py https://contoh.com/halaman https://lain.com/produk
  python3 buka_lp.py --keluar lp.json --teks 3000 --potret https://contoh.com/halaman

Pilihan: --teks 2500 (panjang isi yang dicetak per halaman), --keluar <file json> (bawaan lp.json),
--potret (simpan juga gambar halaman ke folder potret-lp/).

Kode keluar: 0 minimal satu halaman terbuka, 2 tidak ada yang terbuka, 3 browser belum siap.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import peramban  # noqa: E402

POLA_HARGA = re.compile(
    r"(?:Rp\.?\s?\d[\d.,]*(?:\s?(?:rb|ribu|k|jt|juta))?|IDR\s?\d[\d.,]*|\d{2,3}\s?(?:rb|ribu)\b|"
    r"(?:US)?\$\s?\d[\d.,]*|RM\s?\d[\d.,]*|₱\s?\d[\d.,]*|₹\s?\d[\d.,]*|R\$\s?\d[\d.,]*|€\s?\d[\d.,]*)", re.I)
POLA_TAHAN = re.compile(r"just a moment|verify you are human|checking your browser|attention required|access denied|captcha", re.I)


def nama_file(alamat):
    return re.sub(r"[^A-Za-z0-9]+", "-", alamat.split("//", 1)[-1])[:70].strip("-") or "halaman"


def baca_semua(hal):
    """Teks halaman berikut semua bingkai di dalamnya (banyak halaman jualan menaruh isinya di dalam bingkai)."""
    bagian = []
    for bingkai in hal.frames:
        try:
            t = bingkai.inner_text("body", timeout=5000)
        except Exception:
            continue
        t = re.sub(r"\n\s*\n+", "\n", t).strip()
        if t and t not in bagian:
            bagian.append(t)
    bagian.sort(key=len, reverse=True)
    return "\n".join(bagian)


def buka(ctx, alamat, potret):
    hal = ctx.new_page()
    hasil = {"alamat": alamat}
    try:
        jawab = hal.goto(alamat, wait_until="domcontentloaded", timeout=45000)
        try:
            hal.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        hal.wait_for_timeout(2500)
        for _ in range(3):
            hal.mouse.wheel(0, 4000)
            hal.wait_for_timeout(700)
        teks = baca_semua(hal)
        if len(teks) < 400:          # halaman yang dirakit lambat: tunggu sekali lagi
            hal.wait_for_timeout(6000)
            teks = baca_semua(hal)
        judul = hal.title()
        harga = []
        for h in POLA_HARGA.findall(teks):
            h = re.sub(r"\s+", " ", h).strip()
            if h not in harga:
                harga.append(h)
        tertahan = len(teks) < 600 and bool(POLA_TAHAN.search(judul + " " + teks))
        kode = jawab.status if jawab else None
        if tertahan:
            catatan = "tertahan pemeriksaan anti-robot situs itu, isi tidak terbaca"
        elif kode in (404, 410) and len(teks) < 600:
            catatan = f"halaman memberi kode {kode} (tidak ditemukan), kemungkinan sudah dihapus pemiliknya"
        elif kode and kode >= 400 and len(teks) < 600:
            catatan = f"situs itu menolak pembuka otomatis (kode {kode}), isi tidak terbaca"
        elif len(teks) <= 80:
            catatan = "isi halaman hampir kosong"
        else:
            catatan = None
        hasil.update({"alamat_akhir": hal.url, "kode": kode, "judul": judul,
                      "harga_tertulis": harga[:25], "panjang_teks": len(teks), "teks": teks[:20000],
                      "terbuka": catatan is None, "catatan": catatan})
        if potret:
            Path("potret-lp").mkdir(exist_ok=True)
            f = Path("potret-lp") / (nama_file(alamat) + ".png")
            hal.screenshot(path=str(f), full_page=False)
            hasil["potret"] = str(f.resolve())
    except Exception as e:
        hasil.update({"terbuka": False, "catatan": "gagal dibuka: " + str(e).splitlines()[0][:200]})
    finally:
        hal.close()
    return hasil


def main():
    ap = argparse.ArgumentParser(description="Buka halaman jualan pesaing dan baca isinya.")
    ap.add_argument("alamat", nargs="+")
    ap.add_argument("--teks", type=int, default=2500)
    ap.add_argument("--keluar", default="lp.json")
    ap.add_argument("--potret", action="store_true")
    a = ap.parse_args()
    peramban.pakai_venv()
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, _ = peramban.buka_browser(p)
        ctx = peramban.konteks(browser)
        semua = [buka(ctx, u, a.potret) for u in a.alamat]
        browser.close()
    Path(a.keluar).parent.mkdir(parents=True, exist_ok=True)
    Path(a.keluar).write_text(json.dumps(semua, ensure_ascii=False, indent=1), encoding="utf-8")
    for h in semua:
        print(f"\n=== {h['alamat']}")
        if not h.get("terbuka"):
            print(f"    BELUM TERBUKA: {h.get('catatan')}")
            print("    Untuk asisten AI: tulis 'halaman jualan belum dibuka' di catatan pembanding. Jangan menebak harga atau isinya.")
            continue
        print(f"    alamat akhir: {h['alamat_akhir']} | kode {h['kode']} | judul: {h['judul']}")
        print(f"    harga yang tertulis di halaman: {', '.join(h['harga_tertulis']) or 'tidak ada angka harga terbaca'}")
        if h.get("potret"):
            print(f"    potret: {h['potret']}")
        print("    --- isi ---")
        print(h["teks"][:a.teks])
    print(f"\nHasil lengkap: {Path(a.keluar).resolve()}")
    if not any(h.get("terbuka") for h in semua):
        sys.exit(2)


if __name__ == "__main__":
    main()
