#!/usr/bin/env python3
"""Bagian bersama untuk skrip browser Ghost Ads Spy (dipakai ambil_iklan.py, buka_lp.py, siapkan.py).

Produk resmi Regrow Labs.

Skrip browser berjalan di komputer pengguna, memakai browser tanpa tampilan (tidak ada jendela yang
muncul), tanpa login ke Facebook, dan tanpa mengirim data ke server mana pun selain halaman yang dibuka.

Pustaka Playwright dipasang siapkan.py ke lingkungan Python terpisah di ~/.ghost-ads-spy/venv supaya
tidak mengubah Python milik pengguna. Skrip lain otomatis pindah ke Python itu.
"""
import os
import subprocess
import sys
from pathlib import Path

RUMAH = Path(os.environ.get("GAS_RUMAH") or (Path.home() / ".ghost-ads-spy"))
VENV = RUMAH / "venv"
PY_VENV = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
SIAPKAN = Path(__file__).resolve().parent / "siapkan.py"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")


def layar_utf8():
    """Windows sering memakai layar non-UTF-8, sehingga emoji di teks iklan membuat skrip berhenti. Paksa UTF-8."""
    for aliran in (sys.stdout, sys.stderr):
        try:
            aliran.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


layar_utf8()


def ada_playwright():
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def pakai_venv():
    """Kalau Playwright belum ada di Python ini, pindah ke Python penyiap. Kalau belum disiapkan, beri tahu."""
    if ada_playwright():
        return
    if PY_VENV.exists() and Path(sys.prefix).resolve() != VENV.resolve():
        r = subprocess.run([str(PY_VENV), *sys.argv])
        sys.exit(r.returncode)
    print("BELUM SIAP: browser riset belum dipasang di komputer ini.")
    print(f"Untuk asisten AI: jalankan dulu  python3 \"{SIAPKAN}\"  (sekali saja, 2 sampai 10 menit), lalu ulangi perintah ini.")
    print("Jangan menyuruh pengguna membuka Ads Library sendiri.")
    sys.exit(3)


def buka_browser(p):
    """Buka browser tanpa tampilan. Urutan: Chrome terpasang, Edge terpasang, lalu Chromium unduhan Playwright."""
    paksa = os.environ.get("GAS_BROWSER", "").strip().lower()
    urutan = [paksa] if paksa else ["chrome", "msedge", "chromium"]
    tambahan = []
    if os.environ.get("GAS_UJI_TUTUP_FB"):   # hanya untuk pengujian penjual: meniru jaringan yang menutup Facebook
        tambahan = ["--host-resolver-rules=MAP *.facebook.com 0.0.0.0, MAP facebook.com 0.0.0.0"]
    salah = []
    for nama in urutan:
        try:
            if nama == "chromium":
                return p.chromium.launch(headless=True, args=tambahan), "chromium"
            return p.chromium.launch(headless=True, channel=nama, args=["--headless=new", *tambahan]), nama
        except Exception as e:  # browser itu tidak ada di komputer ini, coba berikutnya
            salah.append(f"{nama}: {str(e).splitlines()[0][:160]}")
    print("BELUM SIAP: tidak ada browser yang bisa dijalankan.")
    for s in salah:
        print("  - " + s)
    print(f"Untuk asisten AI: jalankan  python3 \"{SIAPKAN}\"  lalu ulangi. Jangan menyuruh pengguna membuka Ads Library sendiri.")
    sys.exit(3)


def konteks(browser):
    return browser.new_context(locale="en-US", user_agent=UA, viewport={"width": 1280, "height": 1600})
