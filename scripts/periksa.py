#!/usr/bin/env python3
"""Pemeriksa kesehatan Ghost Ads Spy: satu perintah untuk tahu apa yang sudah siap dan apa yang perlu diperbaiki.

Produk resmi Regrow Labs.

  python3 scripts/periksa.py              periksa cepat, tanpa internet
  python3 scripts/periksa.py --internet   plus uji buka Ads Library (butuh internet dan browser riset)

Tiap baris diawali OK (siap), PERLU (harus diperbaiki, ada caranya), atau INFO (catatan). Kode keluar 0 kalau tidak
ada PERLU, 1 kalau ada.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import peramban  # noqa: E402

SKRIP = ["siapkan", "ambil_iklan", "buka_lp", "buat_papan", "analisa", "pantau", "simpan", "hitung", "buat_lp", "buat_laporan", "periksa"]
TANPA_ARGUMEN = ("siapkan", "simpan", "periksa", "buat_laporan", "pantau")   # skrip yang boleh dijalankan tanpa tambahan
HASIL = []


def lapor(tingkat, pesan, cara=None):
    HASIL.append(tingkat)
    print(f"{tingkat:<5} {pesan}")
    if cara:
        print(f"      Cara: {cara}")


def izin_yang_kurang():
    f = AKAR / ".claude" / "settings.json"
    try:
        ada = set(json.loads(f.read_text(encoding="utf-8"))["permissions"]["allow"])
    except Exception:
        return None, []
    butuh = []
    for sc in SKRIP:
        butuh.append(f"Bash(python3 scripts/{sc}.py *)")
        if sc in TANPA_ARGUMEN:
            butuh.append(f"Bash(python3 scripts/{sc}.py)")
    return ada, [x for x in butuh if x not in ada]


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Periksa kesehatan Ghost Ads Spy")
    ap.add_argument("--internet", action="store_true")
    a = ap.parse_args()
    print("PEMERIKSAAN GHOST ADS SPY\n")

    v = sys.version_info
    if v >= (3, 8):
        lapor("OK", f"Python {v.major}.{v.minor} siap")
    else:
        lapor("PERLU", f"Python {v.major}.{v.minor} terlalu lama", "pasang Python 3.8 atau lebih baru")

    if peramban.PY_VENV.exists():
        ok = subprocess.run([str(peramban.PY_VENV), "-c", "import playwright"], capture_output=True).returncode == 0
        if ok:
            lapor("OK", "Browser riset terpasang di lingkungan terpisah")
        else:
            lapor("PERLU", "Playwright belum terpasang", "jalankan python3 scripts/siapkan.py")
    else:
        lapor("PERLU", "Browser riset belum disiapkan di mesin ini", "jalankan python3 scripts/siapkan.py (sekali, 2 sampai 10 menit)")

    cloud = os.environ.get("CLAUDE_CODE_REMOTE", "").lower() == "true"
    lapor("INFO", "Mode: sesi cloud (dipakai lewat HP atau web). Papan dikirim ke chat, riset wajib disimpan ke GitHub." if cloud
          else "Mode: komputer sendiri. Papan dibuka di browser.")

    d = AKAR / "papan" / "data-riset.json"
    if d.is_file():
        try:
            g = json.loads(d.read_text(encoding="utf-8"))
            lapor("OK", f"Data riset sehat: {len(g.get('riset', []))} riset, {len(g.get('ide', []))} produk")
        except json.JSONDecodeError as e:
            lapor("PERLU", f"Data riset rusak ({e})", "pulihkan dari papan/cadangan/ (salin file terbaru ke papan/data-riset.json)")
    else:
        lapor("INFO", "Belum ada riset. Papan masih kosong.")
    cad = list((AKAR / "papan" / "cadangan").glob("data-riset-*.json")) if (AKAR / "papan" / "cadangan").is_dir() else []
    lapor("OK" if cad or not d.is_file() else "INFO", f"Cadangan data riset: {len(cad)} file" + ("" if cad or not d.is_file() else " (dibuat otomatis setiap papan diperbarui)"))
    p = AKAR / "papan" / "pantauan.json"
    if p.is_file():
        try:
            n = len(json.loads(p.read_text(encoding="utf-8")).get("iklan", {}))
            lapor("OK", f"Pantauan iklan: {n} iklan dipantau")
        except json.JSONDecodeError:
            lapor("PERLU", "File pantauan rusak", "hapus papan/pantauan.json lalu rekam ulang dengan pantau.py rekam")

    git = subprocess.run(["git", "-C", str(AKAR), "remote", "get-url", "origin"], capture_output=True, text=True)
    if git.returncode == 0:
        lapor("OK", "Folder terhubung ke GitHub (riset bisa disimpan dengan simpan.py)")
    else:
        lapor("INFO", "Folder belum terhubung ke GitHub", "di sesi cloud riset akan hilang saat sesi selesai kalau tidak disimpan ke GitHub")

    ada, kurang = izin_yang_kurang()
    if ada is None:
        lapor("PERLU", "File .claude/settings.json tidak terbaca")
    elif not kurang:
        lapor("OK", "Izin otomatis untuk semua skrip sudah lengkap")
    else:
        lapor("PERLU", f"{len(kurang)} izin otomatis belum ada, jadi Claude akan bertanya setiap kali menjalankan skrip itu",
              "tambahkan aturan izin berikut ke .claude/settings.json (bagian permissions.allow), atau tekan Allow saat ditanya:")
        for k in kurang[:6]:
            print(f"        {k}")
        if len(kurang) > 6:
            print(f"        ... dan {len(kurang) - 6} lainnya, polanya sama untuk setiap skrip")

    if (AKAR / "papan" / "produk").is_dir():
        n = len(list((AKAR / "papan" / "produk").glob("*/index.html")))
        lapor("OK" if n else "INFO", f"Halaman jualan yang sudah dirakit: {n}")

    if a.internet:
        print("\nUji buka Ads Library (30 sampai 60 detik)...")
        r = subprocess.run([sys.executable, str(AKAR / "scripts" / "siapkan.py"), "--cek"], capture_output=True, text=True)
        akhir = (r.stdout.strip().splitlines() or [""])[-2:]
        if r.returncode == 0:
            lapor("OK", "Ads Library terbaca: " + " ".join(akhir[:1]))
        elif r.returncode == 4:
            lapor("PERLU", "Facebook tidak bisa dihubungi dari sini",
                  "di sesi cloud, izinkan www.facebook.com, facebook.com, dan static.xx.fbcdn.net di pengaturan jaringan environment. Di komputer sendiri, pindah wifi atau pakai hotspot HP")
        else:
            lapor("PERLU", "Ads Library belum terbaca", "ulangi sekali, lalu jalankan python3 scripts/siapkan.py")
    else:
        lapor("INFO", "Uji sambungan ke Facebook dilewati. Jalankan dengan --internet untuk mengujinya.")

    n_perlu = HASIL.count("PERLU")
    print(f"\n{'SEMUA SIAP' if not n_perlu else str(n_perlu) + ' hal perlu diperbaiki'}.")
    sys.exit(1 if n_perlu else 0)


if __name__ == "__main__":
    main()
