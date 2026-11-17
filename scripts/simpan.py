#!/usr/bin/env python3
"""Penyimpan hasil riset Ghost Ads Spy ke GitHub, untuk pengguna yang bekerja lewat Claude di HP (sesi cloud).

Produk resmi Regrow Labs.

Sesi cloud dihapus setelah selesai, jadi riset yang tidak disimpan ikut hilang. Skrip ini memasukkan folder
papan/ (data riset, papan, pantauan, hasil kerja) ke git lalu mengirimnya ke cabang yang sedang dipakai.
Tidak membuat pull request, tidak menyentuh folder scripts/ dan lainnya.

  python3 scripts/simpan.py
  python3 scripts/simpan.py --pesan "Riset niche ibu rumah tangga"

Kode keluar: 0 tersimpan atau tidak ada yang baru, 1 gagal (izin GitHub, jaringan, atau bukan folder git).
"""
import argparse
import datetime
import subprocess
import sys
import time
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent


def git(*arg, cek=False):
    return subprocess.run(["git", *arg], cwd=AKAR, capture_output=True, text=True, check=cek)


def main():
    ap = argparse.ArgumentParser(description="Simpan hasil riset ke GitHub.")
    ap.add_argument("--pesan", default=None)
    a = ap.parse_args()
    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        print("GAGAL: folder ini bukan repositori git, jadi tidak bisa disimpan ke GitHub.")
        sys.exit(1)
    cabang = git("branch", "--show-current").stdout.strip()
    if not cabang:
        print("GAGAL: tidak ada cabang aktif.")
        sys.exit(1)
    git("add", "--", "papan")
    git("reset", "-q", "--", "papan/kerja/__pycache__")
    if git("diff", "--cached", "--quiet", "--", "papan").returncode == 0:
        print("Tidak ada riset baru untuk disimpan.")
    else:
        pesan = a.pesan or f"Simpan hasil riset {datetime.date.today().isoformat()}"
        r = git("commit", "-q", "-m", pesan, "--", "papan")
        if r.returncode:
            print("GAGAL menyimpan ke git: " + (r.stderr or r.stdout).strip()[-300:])
            sys.exit(1)
        print(f"Tersimpan di git: {pesan}")
    for n in range(4):
        r = git("push", "-u", "origin", cabang)
        if r.returncode == 0:
            print(f"TERKIRIM ke GitHub, cabang {cabang}. Riset aman walau sesi ini selesai.")
            return
        err = (r.stderr or r.stdout).strip()
        if "403" in err or "denied" in err.lower():
            print("GAGAL mengirim: Claude belum punya izin menulis ke repo ini. Sambungkan GitHub di claude.ai/connect-github "
                  "dan pasang aplikasi Claude GitHub di repo ini, lalu ulangi.")
            sys.exit(1)
        time.sleep(2 * 2 ** n)
    print("GAGAL mengirim setelah 4 kali coba: " + err[-300:])
    sys.exit(1)


if __name__ == "__main__":
    main()
