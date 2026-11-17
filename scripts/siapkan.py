#!/usr/bin/env python3
"""Penyiap browser riset Ghost Ads Spy. Dijalankan sekali per komputer oleh asisten AI.

Produk resmi Regrow Labs.

Yang dikerjakan:
  1. Membuat lingkungan Python terpisah di ~/.ghost-ads-spy/venv (Python milik pengguna tidak diubah).
  2. Memasang pustaka Playwright di sana.
  3. Mencari browser: Google Chrome atau Microsoft Edge yang sudah terpasang dipakai langsung.
     Kalau tidak ada, mengunduh Chromium khusus (sekali saja).
  4. Uji buka Ads Library tanpa login dan melaporkan hasilnya.

Pemakaian:

  python3 siapkan.py            siapkan lalu uji
  python3 siapkan.py --cek      hanya periksa, tidak memasang apa pun

Kode keluar: 0 siap, 3 belum siap (pemasangan gagal), 4 browser jalan tetapi facebook.com tidak bisa
dihubungi dari lingkungan ini.
"""
import os
import subprocess
import sys
import venv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import peramban  # noqa: E402

UJI = ("https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=ID&media_type=all"
       "&q=%22ebook%22&search_type=keyword_exact_phrase")


def jalankan(perintah, **kw):
    print("  $ " + " ".join(str(x) for x in perintah))
    return subprocess.run(perintah, **kw)


def pasang():
    if sys.version_info < (3, 8):
        print(f"BELUM SIAP: Python {sys.version.split()[0]} terlalu lama, butuh 3.8 atau lebih baru.")
        sys.exit(3)
    if not peramban.PY_VENV.exists():
        print(f"1. Membuat lingkungan Python terpisah di {peramban.VENV}")
        peramban.RUMAH.mkdir(parents=True, exist_ok=True)
        try:
            venv.EnvBuilder(with_pip=True, clear=True).create(str(peramban.VENV))
        except Exception as e:
            print(f"BELUM SIAP: lingkungan Python gagal dibuat ({str(e)[:200]}).")
            print("Untuk asisten AI: di Ubuntu atau Debian pasang dulu paket python3-venv, lalu ulangi. "
                  "Minta izin pengguna sebelum memasang.")
            sys.exit(3)
    else:
        print(f"1. Lingkungan Python sudah ada di {peramban.VENV}")
    py = str(peramban.PY_VENV)
    ada = subprocess.run([py, "-c", "import playwright"], capture_output=True).returncode == 0
    if ada:
        print("2. Playwright sudah terpasang")
    else:
        print("2. Memasang Playwright (butuh internet, 1 sampai 3 menit)")
        r = jalankan([py, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "playwright"])
        if r.returncode:
            print("BELUM SIAP: Playwright gagal dipasang. Periksa sambungan internet lalu ulangi.")
            sys.exit(3)
    return py


KODE_UJI = r'''
import sys
sys.path.insert(0, sys.argv[1])
import peramban
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b, nama = peramban.buka_browser(p)
    ctx = peramban.konteks(b)
    hal = ctx.new_page()
    try:
        hal.goto(sys.argv[2], wait_until="domcontentloaded", timeout=60000)
        hal.wait_for_timeout(7000)
        t = hal.inner_text("body")
    except Exception as e:
        print("BROWSER=" + nama); print("GAGAL=" + str(e).splitlines()[0][:200]); b.close(); sys.exit(4)
    b.close()
    n = t.count("Library ID:") + t.count("ID Galeri:")
    print("BROWSER=" + nama); print("KARTU=" + str(n))
    sys.exit(0 if n else 2)
'''


def uji(py, boleh_unduh):
    print("3. Mencari browser dan uji buka Ads Library (tanpa login, tanpa jendela)")
    sini = str(Path(__file__).resolve().parent)
    r = subprocess.run([py, "-c", KODE_UJI, sini, UJI], capture_output=True, text=True)
    keluar = r.stdout + r.stderr
    if r.returncode == 3 and boleh_unduh:
        print("   Chrome dan Edge tidak ditemukan. Mengunduh Chromium khusus (sekali saja, beberapa menit).")
        u = jalankan([py, "-m", "playwright", "install", "--only-shell", "chromium"])
        if u.returncode:   # Playwright lama belum kenal --only-shell
            u = jalankan([py, "-m", "playwright", "install", "chromium"])
        if u.returncode:
            print("BELUM SIAP: Chromium gagal diunduh. Periksa sambungan internet lalu ulangi.")
            sys.exit(3)
        r = subprocess.run([py, "-c", KODE_UJI, sini, UJI], capture_output=True, text=True)
        keluar = r.stdout + r.stderr
        if r.returncode == 3 and sys.platform.startswith("linux"):
            print("   Chromium butuh pustaka sistem tambahan di Linux.")
            print("   Untuk asisten AI: dengan izin pengguna jalankan  "
                  f"sudo {py} -m playwright install-deps chromium  lalu ulangi siapkan.py.")
    baris = dict(b.split("=", 1) for b in keluar.splitlines() if "=" in b and b.split("=", 1)[0].isupper())
    if r.returncode == 0:
        print(f"SIAP: browser {baris.get('BROWSER')} membuka Ads Library dan membaca {baris.get('KARTU')} kartu iklan.")
        print("Untuk asisten AI: lanjutkan riset dengan ambil_iklan.py dan buka_lp.py. Pengguna tidak perlu membuka apa pun.")
        return 0
    if r.returncode == 4:
        print(f"TIDAK TERBUKA: browser {baris.get('BROWSER')} jalan, tetapi facebook.com tidak bisa dihubungi dari sini.")
        print(f"   Rincian: {baris.get('GAGAL')}")
        print("Untuk asisten AI: jaringan atau lingkungan ini menutup facebook.com (wifi kantor, kampus, atau umum, atau bukan Claude Code di komputer pengguna). "
              "Ikuti bagian 'Kalau browser tidak bisa jalan' di SKILL.md. Jangan menyuruh pengguna membuka Ads Library sendiri.")
        return 4
    if r.returncode == 2:
        print(f"PERLU DIULANG: browser {baris.get('BROWSER')} membuka facebook.com, tetapi kartu iklan belum terbaca.")
        print("Untuk asisten AI: ulangi siapkan.py sekali. Kalau tetap begini, coba langsung ambil_iklan.py dengan frasa lain.")
        return 2
    print("BELUM SIAP: browser belum bisa dijalankan.")
    print(keluar.strip()[-1200:])
    return 3


def main():
    cek = "--cek" in sys.argv
    print(f"Penyiap browser riset. Folder: {peramban.RUMAH}")
    if cek:
        if not peramban.PY_VENV.exists():
            print("BELUM SIAP: belum pernah disiapkan di komputer ini. Jalankan siapkan.py tanpa --cek.")
            sys.exit(3)
        sys.exit(uji(str(peramban.PY_VENV), False))
    py = pasang()
    sys.exit(uji(py, True))


if __name__ == "__main__":
    main()
