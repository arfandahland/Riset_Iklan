#!/usr/bin/env python3
"""Pemantau iklan Ghost Ads Spy: apakah iklan pesaing MASIH tayang beberapa hari kemudian?

Produk resmi Regrow Labs.

Bukti terkuat produk winning adalah iklan yang bertahan. Skrip ini merekam iklan WINNING dan POTENSIAL dari
hasil ambil_iklan.py, lalu di hari lain mencari ulang frasa yang sama dan memeriksa apakah iklan itu masih tayang.

  python3 scripts/pantau.py rekam papan/kerja/iklan-id.json papan/kerja/iklan-us.json
  python3 scripts/pantau.py cek                  cari ulang dan laporkan (butuh internet dan browser riset)
  python3 scripts/pantau.py lihat                daftar iklan yang dipantau, tanpa internet

Data disimpan di papan/pantauan.json. Catatan membaca hasil: "MASIH TAYANG" pasti benar. "TIDAK TERLIHAT LAGI"
berarti tidak muncul di pencarian ulang, bisa karena iklannya berhenti atau tergeser dari hasil yang termuat,
jadi jangan dibaca sebagai bukti produk gagal.
Kode keluar: 0 berhasil, 2 tidak ada yang dipantau, 3 browser belum siap, 4 facebook.com tertutup.
"""
import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

AKAR = Path(__file__).resolve().parent.parent
BERKAS = AKAR / "papan" / "pantauan.json"   # bawaan; --folder mengganti untuk proyek lain
RIWAYAT_MAKS = 30
MINIMAL_HARI = 14


def pakai_folder(folder):
    global BERKAS
    if folder:
        BERKAS = Path(folder).expanduser() / "pantauan.json"


def rakit_ulang_papan():
    """Papan memuat ringkasan pantauan, jadi dirakit ulang setelah pantauan berubah."""
    folder = BERKAS.parent
    subprocess.run([sys.executable, str(AKAR / "scripts" / "buat_papan.py"), "mulai", "--folder", str(folder)],
                   capture_output=True, text=True)


def muat():
    if BERKAS.is_file():
        return json.loads(BERKAS.read_text(encoding="utf-8"))
    return {"iklan": {}}


def simpan(d):
    BERKAS.parent.mkdir(parents=True, exist_ok=True)
    BERKAS.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def perintah_rekam(a):
    pakai_folder(a.folder)
    d = muat()
    hari_ini = datetime.date.today().isoformat()
    baru = 0
    for f in a.berkas:
        h = json.loads(Path(f).read_text(encoding="utf-8"))
        negara = h.get("negara", "ID")
        for r in h["pencarian"]:
            if r["jenis"] != "frasa":
                continue
            for k in r["iklan"]:
                if k["hari"] is None or k["hari"] < MINIMAL_HARI:
                    continue
                if k["id_iklan"] in d["iklan"]:
                    continue
                d["iklan"][k["id_iklan"]] = {"pengiklan": k["pengiklan"], "negara": negara, "frasa": r["cari"],
                                             "mulai": k["mulai"], "hari_saat_rekam": k["hari"], "direkam": hari_ini,
                                             "tautan": k["tautan_iklan"], "tujuan": k["tujuan"][:2], "terakhir_terlihat": hari_ini,
                                             "masih_tayang": True}
                baru += 1
    simpan(d)
    rakit_ulang_papan()
    print(f"REKAM: {baru} iklan baru dipantau, total {len(d['iklan'])}. Disimpan di {BERKAS}")


def perintah_lihat(a):
    pakai_folder(a.folder)
    d = muat()
    if not d["iklan"]:
        print("Belum ada iklan yang dipantau. Jalankan 'rekam' setelah mengambil iklan.")
        return
    for i, x in sorted(d["iklan"].items(), key=lambda kv: -kv[1]["hari_saat_rekam"]):
        s = "masih tayang" if x["masih_tayang"] else "tidak terlihat lagi"
        print(f"{x['pengiklan']} [{x['negara']}] | direkam {x['direkam']} umur {x['hari_saat_rekam']} hari | terakhir terlihat {x['terakhir_terlihat']} | {s}")
        print(f"    {x['tautan']}")


def perintah_cek(a):
    pakai_folder(a.folder)
    d = muat()
    if not d["iklan"]:
        print("Belum ada iklan yang dipantau. Jalankan 'rekam' dulu.")
        sys.exit(2)
    import peramban
    import ambil_iklan as ai
    peramban.pakai_venv()
    from playwright.sync_api import sync_playwright

    hari_ini = datetime.date.today()
    grup = {}
    for i, x in d["iklan"].items():
        grup.setdefault((x["negara"], x["frasa"]), []).append(i)
    terlihat, gagal = set(), 0
    with sync_playwright() as p:
        browser, _ = peramban.buka_browser(p)
        ctx = peramban.konteks(browser)
        for (negara, frasa), ids in grup.items():
            try:
                # Facebook kadang sementara menjawab "tidak ada iklan". Coba sampai 3 kali dengan jeda makin panjang.
                for tunggu in (7000, 14000, 20000):
                    r = ai.ambil_satu(ctx, ai.alamat_cari(frasa, negara, False), a.gulir, hari_ini, tunggu=tunggu)
                    if r["kartu_terbaca"]:
                        break
                    time.sleep(tunggu / 1000)
            except Exception as e:
                print(f"GAGAL membuka pencarian '{frasa}' ({negara}): {str(e).splitlines()[0][:150]}")
                gagal += 1
                continue
            if not r["kartu_terbaca"]:
                gagal += 1
                print(f"Pencarian '{frasa}' ({negara}) tidak terbaca ({r['catatan']}), iklannya tidak dinilai kali ini.")
                continue
            terlihat |= {k["id_iklan"] for k in r["iklan"]}
            for k in r["iklan"]:   # catat umur terbaru iklan yang masih ada
                if k["id_iklan"] in d["iklan"]:
                    d["iklan"][k["id_iklan"]]["hari_sekarang"] = k["hari"]
        browser.close()
    if gagal == len(grup):
        print("TIDAK TERBUKA: tidak satu pun pencarian terbaca. Jangan mengarang hasil. Ulangi nanti atau ikuti SKILL.md.")
        sys.exit(4)
    dinilai = {i for (n, f), ids in grup.items() for i in ids}
    masih = hilang = 0
    print(f"PANTAU {hari_ini.isoformat()} | {len(d['iklan'])} iklan dipantau\n")
    for i, x in sorted(d["iklan"].items(), key=lambda kv: -kv[1]["hari_saat_rekam"]):
        if i in dinilai:
            x.setdefault("riwayat", []).append({"tanggal": hari_ini.isoformat(), "masih": i in terlihat, "hari": x.get("hari_sekarang") if i in terlihat else None})
            x["riwayat"] = x["riwayat"][-RIWAYAT_MAKS:]
        if i in terlihat:
            x["masih_tayang"], x["terakhir_terlihat"] = True, hari_ini.isoformat()
            masih += 1
            print(f"MASIH TAYANG | {x['pengiklan']} [{x['negara']}] | umur sekarang {x.get('hari_sekarang', '?')} hari (saat direkam {x['hari_saat_rekam']}) | {x['tautan']}")
        elif i in dinilai:
            x["masih_tayang"] = False
            hilang += 1
            print(f"TIDAK TERLIHAT LAGI | {x['pengiklan']} [{x['negara']}] | terakhir terlihat {x['terakhir_terlihat']} | {x['tautan']}")
    d["cek_terakhir"] = hari_ini.isoformat()
    simpan(d)
    rakit_ulang_papan()
    print(f"\nRingkas: {masih} masih tayang, {hilang} tidak terlihat lagi. Tidak terlihat belum tentu berhenti: bisa tergeser dari hasil yang termuat.")


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Pantau apakah iklan pesaing masih tayang.")
    sub = ap.add_subparsers(dest="perintah", required=True)
    r = sub.add_parser("rekam")
    r.add_argument("berkas", nargs="+")
    r.add_argument("--folder")
    r.set_defaults(fungsi=perintah_rekam)
    c = sub.add_parser("cek")
    c.add_argument("--gulir", type=int, default=4)
    c.add_argument("--folder")
    c.set_defaults(fungsi=perintah_cek)
    l = sub.add_parser("lihat")
    l.add_argument("--folder")
    l.set_defaults(fungsi=perintah_lihat)
    a = ap.parse_args()
    a.fungsi(a)


if __name__ == "__main__":
    main()
