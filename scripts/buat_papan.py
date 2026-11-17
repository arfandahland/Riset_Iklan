#!/usr/bin/env python3
"""Perakit Papan Produk Winning Ghost Ads Spy.

Produk resmi Regrow Labs.

Pemakaian (hanya butuh Python 3, tanpa internet, tanpa pustaka tambahan). Jalankan dari folder Ghost Ads Spy:

  python3 scripts/buat_papan.py mulai                      rakit papan; sebelum riset pertama papan hanya berisi petunjuk
  python3 scripts/buat_papan.py tambah hasil.json          tambah riset baru atau hasil validasi, lalu rakit ulang papan
  python3 scripts/buat_papan.py pulihkan papan-lama.html   ambil data dari file papan lama atau salinan di papan/cadangan/ (.json)
  python3 scripts/buat_papan.py lihat                      daftar riset dan ide yang sudah tersimpan
  python3 scripts/buat_papan.py contoh                     rakit halaman Contoh Riset Nyata (terpisah dari papan pengguna)

Semua perintah menerima --folder <folder kerja>. Bawaan: folder papan/ di dalam folder Ghost Ads Spy,
jadi riset lama selalu terbawa selama folder ini tidak dihapus.

Hasil di folder kerja:
  data-riset.json            gudang data, sumber kebenaran
  papan-produk-winning.html  papan pengguna, dibuka di browser mana saja
  contoh-riset.html          halaman Contoh Riset Nyata, hanya dibuat oleh perintah contoh
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
TEMPLATE = AKAR / "papan" / "bahan" / "papan.html"
CONTOH = AKAR / "papan" / "bahan" / "data-contoh.json"
STATUS = {"WINNING", "POTENSIAL", "BARU"}
VONIS = {"LANJUT TES KECIL", "PERLU BUKTI", "TAHAN"}
WAJIB_RISET = ["id", "judul", "tanggal", "input", "ringkas"]
WAJIB_IDE = ["id", "riset", "nama", "target", "formula", "malas", "instant", "applicable"]
KERANGKA = ('<!doctype html><html lang="id"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '</head><body>')


def gagal(pesan):
    sys.exit("GAGAL: " + pesan)


def baca_template():
    if not TEMPLATE.is_file():
        gagal("papan/bahan/papan.html tidak ada, jadi papan tidak bisa dirakit. Ekstrak ulang file zip produknya.")
    t = TEMPLATE.read_text(encoding="utf-8")
    if "__DATA_RISET__" not in t:
        gagal("papan/bahan/papan.html sudah berubah dan tidak bisa dirakit. Ekstrak ulang file zip produknya.")
    return t


def folder_kerja(arg):
    if arg:
        f = Path(arg).expanduser()
    else:
        f = AKAR / "papan"
    f.mkdir(parents=True, exist_ok=True)
    return f


def baca_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        gagal(f"file tidak ada: {p}")
    except json.JSONDecodeError as e:
        gagal(f"{p} bukan JSON yang sah: {e}")


def gudang_kosong():
    return {"riset": [], "ide": []}


def baca_gudang(folder):
    p = folder / "data-riset.json"
    if not p.is_file():
        return None
    d = baca_json(p)
    d.setdefault("riset", [])
    d.setdefault("ide", [])
    d.pop("_contoh", None)
    # Papan pengguna tidak pernah memuat contoh. Sisa contoh dari versi lama dibuang.
    contoh = {r["id"] for r in d["riset"] if r.get("contoh")}
    d["riset"] = [r for r in d["riset"] if r["id"] not in contoh]
    d["ide"] = [i for i in d["ide"] if i["riset"] not in contoh]
    return d


def bersih(x):
    """Buang tanda pisah panjang dari semua teks."""
    if isinstance(x, str):
        return x.replace(" " + chr(8212) + " ", ", ").replace(chr(8212), ", ").replace(chr(8211), "-")
    if isinstance(x, list):
        return [bersih(v) for v in x]
    if isinstance(x, dict):
        return {k: bersih(v) for k, v in x.items()}
    return x


def periksa_riset(r):
    for k in WAJIB_RISET:
        if not r.get(k):
            gagal(f"riset '{r.get('id', '?')}' belum punya '{k}'")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r["tanggal"])):
        gagal(f"tanggal riset '{r['id']}' harus berbentuk 2026-01-31")
    for o in r.get("offer_lain", []) or []:
        if o.get("status") and o["status"] not in STATUS:
            gagal(f"status penawaran lain '{o.get('nama')}' harus salah satu dari {sorted(STATUS)}")


def periksa_ide(i):
    for k in WAJIB_IDE:
        if i.get(k) in (None, ""):
            gagal(f"ide '{i.get('id', '?')}' belum punya '{k}'")
    for k in ("malas", "instant", "applicable"):
        if not isinstance(i[k], int) or not 0 <= i[k] <= 10:
            gagal(f"nilai '{k}' ide '{i['id']}' harus bilangan bulat 0 sampai 10")
    i["total"] = i["malas"] + i["instant"] + i["applicable"]
    for p in i.get("pembanding", []) or []:
        if not p.get("nama") or not p.get("isi"):
            gagal(f"pembanding di ide '{i['id']}' wajib punya 'nama' dan 'isi'")
        if p.get("hari") is not None and not isinstance(p["hari"], int):
            gagal(f"'hari' pembanding '{p['nama']}' harus bilangan bulat, atau null kalau umur iklan belum dicek")
        if p.get("status") and p["status"] not in STATUS:
            gagal(f"status pembanding '{p['nama']}' harus salah satu dari {sorted(STATUS)}")
        if p.get("hari") is not None and (
                (p.get("status") == "WINNING" and p["hari"] < 30) or (p.get("status") == "BARU" and p["hari"] >= 14)
                or (p.get("status") == "POTENSIAL" and p["hari"] >= 30)):
            gagal(f"status pembanding '{p['nama']}' tidak cocok dengan umur {p['hari']} hari. "
                  "WINNING 30 hari atau lebih, POTENSIAL di bawah 30 hari, BARU di bawah 14 hari.")
        if p.get("hari") is None and p.get("status"):
            gagal(f"pembanding '{p['nama']}' diberi status padahal umur iklannya belum dicek. Hapus status atau isi 'hari'.")
        for u in [x.get("url") for x in p.get("lp", []) or []] + list(p.get("iklan", []) or []):
            if not str(u).startswith("https://"):
                gagal(f"tautan di pembanding '{p['nama']}' harus diawali https://")
    if i.get("validasi"):
        periksa_validasi(i["id"], i["validasi"])


def periksa_validasi(idnya, v):
    if v.get("vonis") not in VONIS:
        gagal(f"vonis ide '{idnya}' harus salah satu dari {sorted(VONIS)}")
    if not v.get("alasan"):
        gagal(f"validasi ide '{idnya}' wajib punya 'alasan'")


def gabung(gudang, masuk, timpa=False):
    masuk = bersih(masuk)
    riset_baru = masuk.get("riset")
    if isinstance(riset_baru, dict):
        riset_baru = [riset_baru]
    riset_baru = riset_baru or []
    ide_baru = masuk.get("ide") or []
    validasi = masuk.get("validasi") or []
    if not (riset_baru or ide_baru or validasi):
        gagal("file masukan tidak berisi 'riset', 'ide', atau 'validasi'. Lihat referensi/bentuk-data.md.")

    ada_riset = {r["id"] for r in gudang["riset"]}
    ada_ide = {i["id"] for i in gudang["ide"]}
    for r in riset_baru:
        periksa_riset(r)
        if r["id"] in ada_riset and not timpa:
            gagal(f"riset '{r['id']}' sudah ada. Riset baru memakai id baru supaya riset lama tidak tertimpa. "
                  "Pakai --timpa hanya untuk memperbaiki riset yang sama.")
    id_riset = ada_riset | {r["id"] for r in riset_baru}
    for i in ide_baru:
        periksa_ide(i)
        if i["riset"] not in id_riset:
            gagal(f"ide '{i['id']}' menunjuk riset '{i['riset']}' yang tidak ada")
        if i["id"] in ada_ide and not timpa:
            gagal(f"ide '{i['id']}' sudah ada. Pakai id baru, atau --timpa untuk memperbaiki ide yang sama.")

    baru_r = {r["id"] for r in riset_baru}
    baru_i = {i["id"] for i in ide_baru}
    gudang["riset"] = [r for r in gudang["riset"] if r["id"] not in baru_r] + riset_baru
    gudang["ide"] = [i for i in gudang["ide"] if i["id"] not in baru_i] + ide_baru

    peta = {i["id"]: i for i in gudang["ide"]}
    for v in validasi:
        idnya = v.get("id")
        if idnya not in peta:
            gagal(f"validasi menunjuk ide '{idnya}' yang tidak ada. Jalankan 'lihat' untuk daftar id.")
        isi = {k: x for k, x in v.items() if k != "id"}
        periksa_validasi(idnya, isi)
        isi.setdefault("tanggal", datetime.date.today().isoformat())
        peta[idnya]["validasi"] = isi

    for r in gudang["riset"]:
        milik = [i for i in gudang["ide"] if i["riset"] == r["id"]]
        milik.sort(key=lambda i: -i["total"])
        for n, i in enumerate(milik, 1):
            i["no"] = n
        # "Paling disarankan" ditentukan skrip, bukan penulis data: hanya produk yang punya bukti iklan WINNING.
        layak = sorted((i for i in milik if kunci_saran(i)), key=kunci_saran, reverse=True)
        r["rekomendasi"] = [i["id"] for i in layak[:3]]
    return gudang


def bukti_winning(i):
    """Bukti WINNING terkuat satu produk: iklan tertua. Angka hari di papan selalu dari pesaing ini."""
    w = [p for p in i.get("pembanding") or [] if p.get("status") == "WINNING" and p.get("hari") is not None]
    return max(w, key=lambda p: p["hari"]) if w else None


def lengkap(p):
    """Bukti lengkap: ada tautan iklan, landing page yang sudah dibuka, dan harga yang terbaca."""
    belum = lambda t: "belum" in str(t or "").lower()
    return bool(p.get("iklan")) and any(not belum(l.get("label")) for l in p.get("lp") or []) \
        and bool(p.get("harga")) and not belum(p.get("harga"))


def kunci_saran(i):
    """Urutan Paling disarankan: iklan 90 hari atau lebih dulu, lalu Skor Ghost, lalu bukti lengkap, lalu umur.
    None kalau produk tidak punya bukti WINNING (BARU dan POTENSIAL tidak pernah masuk)."""
    p = bukti_winning(i)
    if not p:
        return None
    return (p["hari"] >= 90, i["total"], any(lengkap(x) for x in i.get("pembanding") or [] if x.get("status") == "WINNING"), p["hari"])


def cetak_saran(gudang):
    peta = {i["id"]: i for i in gudang["ide"]}
    for r in sorted(gudang["riset"], key=lambda r: r["tanggal"], reverse=True)[:1]:
        if not r.get("rekomendasi"):
            print("Paling disarankan: belum ada. Tidak ada produk dengan iklan pesaing WINNING (30 hari atau lebih) di riset terbaru.")
            continue
        print("Paling disarankan di riset terbaru (urutan dari skrip, pakai urutan ini di chat):")
        for n, x in enumerate(r["rekomendasi"], 1):
            i, p = peta[x], bukti_winning(peta[x])
            kurang = "" if any(lengkap(q) for q in i["pembanding"] if q.get("status") == "WINNING") else \
                " | BUKTI BELUM LENGKAP: buka landing page dan isi harga pesaing WINNING-nya, atau tambah pesaing WINNING lain yang lengkap"
            print(f"  {n}. {i['nama']} | iklan {p['hari']} hari ({p['nama']}) | Skor Ghost {i['total']}/30{kurang}")


VERSI_DATA = 2
CADANGAN_MAKS = 10


def cadangkan(folder, teks_baru):
    """Sebelum data riset ditimpa, simpan salinan data lama (maksimal 10 salinan terakhir). Riset pengguna tidak boleh hilang."""
    f = folder / "data-riset.json"
    if not f.is_file():
        return
    lama = f.read_text(encoding="utf-8")
    if lama == teks_baru or not lama.strip():
        return
    cad = folder / "cadangan"
    cad.mkdir(exist_ok=True)
    ada = sorted(cad.glob("data-riset-*.json"))
    if ada and ada[-1].read_text(encoding="utf-8") == lama:
        return
    (cad / f"data-riset-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json").write_text(lama, encoding="utf-8")
    for x in sorted(cad.glob("data-riset-*.json"))[:-CADANGAN_MAKS]:
        x.unlink()


def baca_pantauan(folder):
    """Ringkasan pantauan iklan untuk papan: hanya yang perlu ditampilkan."""
    f = folder / "pantauan.json"
    if not f.is_file():
        return None
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    iklan = []
    for i, x in d.get("iklan", {}).items():
        iklan.append({"id": i, "pengiklan": x.get("pengiklan"), "negara": x.get("negara"), "frasa": x.get("frasa"),
                      "hari_saat_rekam": x.get("hari_saat_rekam"), "hari_sekarang": x.get("hari_sekarang"),
                      "direkam": x.get("direkam"), "terakhir_terlihat": x.get("terakhir_terlihat"),
                      "masih_tayang": x.get("masih_tayang"), "tautan": x.get("tautan"), "riwayat": x.get("riwayat", [])})
    return {"cek_terakhir": d.get("cek_terakhir"), "iklan": iklan}


def baca_produk(folder):
    """Halaman jualan yang sudah dirakit buat_lp.py, supaya papan bisa menunjukkan tahap tiap produk."""
    hasil = []
    for f in sorted((folder / "produk").glob("*/spesifikasi.json")) if (folder / "produk").is_dir() else []:
        try:
            s = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        hasil.append({"id": s.get("id"), "nama": s.get("nama"), "ide": s.get("ide"), "harga": (s.get("harga") or {}).get("jual"),
                      "sudut_iklan": len(s.get("iklan") or []), "pixel": bool(s.get("pixel_id"))})
    return hasil


def rakit(folder, gudang, contoh=False):
    """Rakit papan pengguna, atau halaman Contoh Riset Nyata kalau contoh=True (tidak menyentuh data pengguna)."""
    t = baca_template()
    gudang.pop("_lisensi", None)
    if contoh:
        gudang["_contoh"] = True
    else:
        gudang["_versi"] = VERSI_DATA
        teks = json.dumps(gudang, ensure_ascii=False, indent=1)
        cadangkan(folder, teks)
        (folder / "data-riset.json").write_text(teks, encoding="utf-8")
    # Halaman hanya membawa Skor Ghost (total). Tiga nilai rinciannya tinggal di data-riset.json.
    tampil = dict(gudang, ide=[{k: v for k, v in i.items() if k not in ("malas", "instant", "applicable")}
                               for i in gudang["ide"]])
    if not contoh:
        tampil["pantau"] = baca_pantauan(folder)
        tampil["produk"] = baca_produk(folder)
    muatan = json.dumps(tampil, ensure_ascii=False).replace("</", "<\\/")
    isi = t.replace("__DATA_RISET__", muatan)
    hasil = folder / ("contoh-riset.html" if contoh else "papan-produk-winning.html")
    hasil.write_text(KERANGKA + isi + "</body></html>", encoding="utf-8")
    n_val = sum(1 for i in gudang["ide"] if i.get("validasi"))
    if contoh:
        print(f"CONTOH RISET SIAP: {hasil}")
        print("Ini halaman contoh, terpisah dari papan pengguna. Papan pengguna tidak berubah.")
    else:
        print(f"PAPAN SIAP: {hasil}")
        if gudang["riset"]:
            print(f"Isi: {len(gudang['riset'])} riset, {len(gudang['ide'])} produk, {n_val} sudah divalidasi.")
            cetak_saran(gudang)
        else:
            print("Papan masih kosong: hanya berisi petunjuk mengetik perintah riset. Belum ada produk apa pun.")


def perintah_mulai(a):
    folder = folder_kerja(a.folder)
    gudang = baca_gudang(folder)
    if gudang is None or not gudang["riset"]:
        gudang = gudang or gudang_kosong()
        print("Belum ada riset tersimpan.")
    else:
        print("Data lama ditemukan, papan dirakit ulang dari data itu.")
    rakit(folder, gudang)


def perintah_contoh(a):
    folder = folder_kerja(a.folder)
    if not CONTOH.is_file():
        gagal("papan/bahan/data-contoh.json hilang, jadi contoh riset tidak bisa ditampilkan.")
    d = baca_json(CONTOH)
    d.pop("_lisensi", None)
    rakit(folder, gabung(gudang_kosong(), d), contoh=True)


def perintah_tambah(a):
    folder = folder_kerja(a.folder)
    gudang = baca_gudang(folder) or gudang_kosong()
    rakit(folder, gabung(gudang, baca_json(a.file), a.timpa))


def perintah_pulihkan(a):
    folder = folder_kerja(a.folder)
    teks = Path(a.file).expanduser().read_text(encoding="utf-8")
    if str(a.file).lower().endswith(".json"):   # salinan dari folder cadangan
        lama = json.loads(teks)
    else:
        m = re.search(r'<script type="application/json" id="data-riset">(.*?)</script>', teks, re.S)
        if not m:
            gagal("file itu bukan papan Ghost Ads Spy, atau datanya tidak terbaca")
        lama = json.loads(m.group(1).replace("<\\/", "</"))
    lama.pop("_lisensi", None)
    if lama.pop("_contoh", None):
        gagal("file itu halaman contoh riset, bukan papan milik pengguna. Tidak ada yang diambil.")
    gudang = baca_gudang(folder) or gudang_kosong()
    ada_r = {r["id"] for r in gudang["riset"]}
    ada_i = {i["id"] for i in gudang["ide"]}
    gudang["riset"] += [r for r in lama.get("riset", []) if r["id"] not in ada_r]
    gudang["ide"] += [i for i in lama.get("ide", []) if i["id"] not in ada_i]
    print("Data dari papan lama berhasil diambil.")
    rakit(folder, gudang)


def perintah_lihat(a):
    gudang = baca_gudang(folder_kerja(a.folder))
    if not gudang or not gudang["riset"]:
        print("Belum ada riset tersimpan.")
        return
    for r in sorted(gudang["riset"], key=lambda r: r["tanggal"], reverse=True):
        print(f"\nRISET {r['id']} | {r['tanggal']} | {r['judul']}")
        for i in sorted((i for i in gudang["ide"] if i["riset"] == r["id"]), key=lambda i: i.get("no", 0)):
            v = i.get("validasi", {}).get("vonis", "belum divalidasi")
            print(f"  {i['id']} | {i['nama']} | Skor Ghost {i['total']}/30 | {v}")


def main():
    for aliran in (sys.stdout, sys.stderr):   # layar Windows sering bukan UTF-8
        try:
            aliran.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Perakit Papan Produk Winning Ghost Ads Spy (Regrow Labs)")
    sub = ap.add_subparsers(dest="perintah", required=True)
    for nama, fungsi, butuh_file in [("mulai", perintah_mulai, False), ("tambah", perintah_tambah, True),
                                      ("pulihkan", perintah_pulihkan, True), ("lihat", perintah_lihat, False),
                                      ("contoh", perintah_contoh, False)]:
        p = sub.add_parser(nama)
        if butuh_file:
            p.add_argument("file")
        if nama == "tambah":
            p.add_argument("--timpa", action="store_true", help="izinkan mengganti riset atau ide ber-id sama")
        p.add_argument("--folder", default=None)
        p.set_defaults(fungsi=fungsi)
    a = ap.parse_args()
    a.fungsi(a)


if __name__ == "__main__":
    main()
