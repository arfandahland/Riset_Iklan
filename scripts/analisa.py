#!/usr/bin/env python3
"""Perangkum hasil ambil_iklan.py untuk Ghost Ads Spy: dari banyak frasa jadi satu peringkat.

Produk resmi Regrow Labs.

Menggabungkan semua file hasil ambil_iklan.py (beberapa frasa, beberapa negara) menjadi:
  1. peringkat pengiklan lintas frasa (satu pengiklan yang muncul di banyak frasa dihitung sekali),
  2. kelompok per alamat jualan (domain), karena satu produk sering dijual banyak pengiklan,
  3. frasa mana yang paling banyak menemukan iklan lama (WINNING), untuk memilih frasa berikutnya,
  4. daftar alamat jualan terbaik yang siap dibuka dengan buka_lp.py.

Tanpa internet dan tanpa pustaka tambahan. Pemakaian:

  python3 scripts/analisa.py papan/kerja/iklan-id.json papan/kerja/iklan-us.json
  python3 scripts/analisa.py papan/kerja/iklan-*.json --lp 8 --keluar papan/kerja/peringkat.json --csv papan/kerja/peringkat.csv

Pilihan: --lp 8 (berapa alamat jualan dicetak untuk dibuka), --top 15 (berapa pengiklan dicetak),
--keluar <json>, --csv <file>.
"""
import argparse
import csv
import glob
import json
import sys
import urllib.parse
from pathlib import Path


BISING = ("metastatus.com", "fbcdn.net")   # bukan tujuan jualan


# Situs lapak dan penyingkat tautan dipakai banyak penjual berbeda, jadi satu domain di sini BUKAN satu produk.
LAPAK = ("lynk.id", "mayar.id", "gumroad.com", "etsy.com", "linktr.ee", "bit.ly", "s.id", "wa.me", "shopee.co.id",
         "tokopedia.com", "payhip.com", "teachable.com", "kajabi.com", "canva.com")


def domain(u):
    """Domain, atau domain plus penjualnya (segmen pertama alamat) untuk situs lapak, supaya penjual berbeda tidak tercampur."""
    h = urllib.parse.urlparse(u)
    n = h.netloc.lower()
    n = n[4:] if n.startswith("www.") else n
    if n in LAPAK:
        seg = h.path.strip("/").split("/")[0]
        return f"{n}/{seg}" if seg else n
    return n


def status_dari(hari, jumlah):
    if hari is None:
        return None
    if hari >= 30:
        return "WINNING"
    if hari >= 14 or jumlah >= 10:
        return "POTENSIAL"
    return "BARU"


def muat(berkas):
    semua = []
    for pola in berkas:
        cocok = sorted(glob.glob(pola)) or [pola]
        for f in cocok:
            p = Path(f)
            if not p.is_file():
                sys.exit(f"GAGAL: file tidak ada: {f}")
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                sys.exit(f"GAGAL: {f} bukan JSON yang sah: {e}")
            if "pencarian" not in d:
                sys.exit(f"GAGAL: {f} bukan hasil ambil_iklan.py")
            semua.append((f, d))
    return semua


def gabung(data):
    """Satu iklan (Library ID) dihitung sekali walau muncul di banyak frasa."""
    iklan = {}
    frasa = {}
    for f, d in data:
        negara = d.get("negara", "?")
        for r in d["pencarian"]:
            kunci_frasa = (negara, r["jenis"], r["cari"])
            fr = frasa.setdefault(kunci_frasa, {"negara": negara, "jenis": r["jenis"], "cari": r["cari"],
                                                "kartu": 0, "winning": 0, "pengiklan": set(), "catatan": r.get("catatan")})
            for k in r["iklan"]:
                fr["kartu"] += 1
                fr["pengiklan"].add(k["pengiklan"])
                if (k["hari"] or 0) >= 30:
                    fr["winning"] += 1
                a = iklan.setdefault(k["id_iklan"], dict(k, negara=negara, frasa=[]))
                if r["cari"] not in a["frasa"]:
                    a["frasa"].append(r["cari"])
    return iklan, frasa


def peringkat(iklan):
    grup = {}
    for a in iklan.values():
        g = grup.setdefault((a["negara"], a["pengiklan"] or "(nama tidak terbaca)"), [])
        g.append(a)
    hasil = []
    for (negara, nama), isi in grup.items():
        jumlah = sum(a["iklan_sama"] for a in isi)
        umur = [a for a in isi if a["hari"] is not None]
        tertua = max(umur, key=lambda a: a["hari"]) if umur else None
        tujuan, frasa = [], []
        for a in isi:
            for t in a["tujuan"]:
                if t not in tujuan and not domain(t).endswith(BISING):
                    tujuan.append(t)
            for f in a["frasa"]:
                if f not in frasa:
                    frasa.append(f)
        hari = tertua["hari"] if tertua else None
        hasil.append({"negara": negara, "pengiklan": nama, "iklan_terlihat": jumlah, "hari_tertua": hari,
                      "mulai_tertua": tertua["mulai"] if tertua else None,
                      "status": status_dari(hari, jumlah),
                      "tautan_iklan_tertua": (tertua or isi[0])["tautan_iklan"],
                      "tujuan": tujuan[:5], "domain": sorted({domain(t) for t in tujuan}),
                      "ditemukan_lewat_frasa": frasa,
                      "contoh_teks": ((tertua or isi[0])["teks"] or "")[:240].replace("\n", " / ")})
    hasil.sort(key=lambda r: (-(r["hari_tertua"] if r["hari_tertua"] is not None else -1), -r["iklan_terlihat"]))
    return hasil


def per_domain(rank):
    peta = {}
    for r in rank:
        for dm in r["domain"]:
            g = peta.setdefault(dm, {"domain": dm, "pengiklan": [], "hari_tertua": None, "iklan_terlihat": 0, "tujuan": None})
            g["pengiklan"].append(r["pengiklan"])
            g["iklan_terlihat"] += r["iklan_terlihat"]
            if r["hari_tertua"] is not None and (g["hari_tertua"] is None or r["hari_tertua"] > g["hari_tertua"]):
                g["hari_tertua"] = r["hari_tertua"]
            if not g["tujuan"]:
                g["tujuan"] = next((t for t in r["tujuan"] if domain(t) == dm), None)
    for g in peta.values():
        g["status"] = status_dari(g["hari_tertua"], g["iklan_terlihat"])
    return sorted(peta.values(), key=lambda g: (-(g["hari_tertua"] if g["hari_tertua"] is not None else -1), -g["iklan_terlihat"]))


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Rangkum hasil ambil_iklan.py menjadi satu peringkat.")
    ap.add_argument("berkas", nargs="+", help="file JSON hasil ambil_iklan.py (boleh pola seperti iklan-*.json)")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--lp", type=int, default=8)
    ap.add_argument("--keluar")
    ap.add_argument("--csv")
    a = ap.parse_args()

    data = muat(a.berkas)
    iklan, frasa = gabung(data)
    if not iklan:
        print("TIDAK ADA IKLAN di file-file itu. Ganti frasa atau ulangi ambil_iklan.py. Jangan mengarang hasil.")
        sys.exit(2)
    rank = peringkat(iklan)
    dom = per_domain(rank)
    sampai = ", ".join(sorted({d.get("umur_dihitung_sampai", "?") for _, d in data}))
    n_win = sum(1 for r in rank if r["status"] == "WINNING")
    print(f"RANGKUMAN | {len(data)} file | {len(iklan)} iklan unik | {len(rank)} pengiklan | {n_win} WINNING | umur dihitung sampai {sampai}")

    print("\nPERINGKAT PENGIKLAN (iklan tertua dulu)")
    for n, r in enumerate(rank[:a.top], 1):
        umur = f"{r['hari_tertua']} hari" if r["hari_tertua"] is not None else "umur tidak terbaca"
        print(f"{n:>2}. [{r['negara']}] {r['pengiklan']} | {umur} | {r['iklan_terlihat']} iklan terlihat | {r['status'] or 'tanpa status'}")
        print(f"      frasa: {', '.join(r['ditemukan_lewat_frasa'])} | tujuan: {', '.join(r['domain']) or 'tidak ada'}")
        print(f"      iklan tertua: {r['tautan_iklan_tertua']}")

    banyak = [g for g in dom if len(g["pengiklan"]) > 1]
    if banyak:
        print("\nDIJUAL BANYAK PENGIKLAN (alamat jualan yang sama dipakai lebih dari satu pengiklan, tanda produk yang sedang ramai)")
        for g in banyak[:8]:
            print(f"  - {g['domain']} | {len(g['pengiklan'])} pengiklan: {', '.join(g['pengiklan'][:4])} | tertua {g['hari_tertua']} hari")

    print("\nFRASA PALING BERHASIL (pakai pola serupa untuk frasa berikutnya)")
    for f in sorted(frasa.values(), key=lambda f: (-f["winning"], -f["kartu"]))[:8]:
        cat = f" | {f['catatan']}" if f["catatan"] else ""
        print(f"  - [{f['negara']}] {f['cari']} | {f['kartu']} kartu | {f['winning']} iklan 30 hari atau lebih{cat}")
    kosong = [f for f in frasa.values() if f["kartu"] == 0]
    if kosong:
        print("  Frasa kosong (ganti atau persempit): " + "; ".join(f["cari"] for f in kosong))

    calon = [g for g in dom if g["tujuan"] and g["status"] in ("WINNING", "POTENSIAL")][:a.lp]
    if calon:
        print("\nALAMAT JUALAN TERBAIK, SIAP DIBUKA (satu per domain, umur tertua dulu)")
        urls = " ".join(f'"{g["tujuan"]}"' for g in calon)
        print(f"python3 scripts/buka_lp.py --keluar papan/kerja/lp.json {urls}")

    if a.keluar:
        Path(a.keluar).parent.mkdir(parents=True, exist_ok=True)
        Path(a.keluar).write_text(json.dumps({"umur_dihitung_sampai": sampai, "pengiklan": rank, "domain": dom,
                                              "frasa": [dict(f, pengiklan=len(f["pengiklan"])) for f in frasa.values()]},
                                             ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nPeringkat lengkap: {Path(a.keluar).resolve()}")
    if a.csv:
        Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
        with open(a.csv, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["negara", "pengiklan", "hari_tertua", "mulai_tertua", "status", "iklan_terlihat", "domain", "tautan_iklan_tertua", "frasa"])
            for r in rank:
                w.writerow([r["negara"], r["pengiklan"], r["hari_tertua"], r["mulai_tertua"], r["status"], r["iklan_terlihat"],
                            " ".join(r["domain"]), r["tautan_iklan_tertua"], " | ".join(r["ditemukan_lewat_frasa"])])
        print(f"CSV: {Path(a.csv).resolve()}")


if __name__ == "__main__":
    main()
