#!/usr/bin/env python3
"""Pengambil iklan Facebook Ads Library untuk Ghost Ads Spy.

Produk resmi Regrow Labs.

Membuka Ads Library lewat browser tanpa tampilan, tanpa login, lalu membaca tiap kartu iklan:
pengiklan, tanggal mulai tayang, umur dalam hari, status, teks iklan, tautan iklan, dan tautan
tujuan dari tombol iklan. Asisten AI yang menjalankannya. Pengguna tidak perlu membuka apa pun.

Pemakaian:

  python3 ambil_iklan.py --negara ID --frasa "anak susah makan" --frasa "worksheet anak"
  python3 ambil_iklan.py --negara US --frasa "printable worksheets" --keluar iklan-us.json
  python3 ambil_iklan.py --halaman 1109965875532383 --negara ID      semua iklan satu pengiklan (ID halaman)
  python3 ambil_iklan.py --id 1747758156509492                       satu iklan (Library ID)

Pilihan: --gulir 4 (berapa kali menggulir, bawaan 4, supaya jumlah kartu antar pencarian bisa
dibandingkan), --bebas (kata tidak harus berurutan persis), --keluar <file json>, --teks 400 (panjang
teks iklan yang dicetak).

Hasil lengkap ditulis ke file JSON (bawaan: iklan-<negara>.json di folder saat ini) dan ringkasannya
dicetak. Kode keluar: 0 berhasil, 2 halaman terbuka tapi kartu iklan tidak terbaca, 3 browser belum siap,
4 internet ke facebook.com tertutup.
"""
import argparse
import datetime
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import peramban  # noqa: E402

DASAR = "https://www.facebook.com/ads/library/"
BULAN = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "mei": 5, "jun": 6, "jul": 7, "aug": 8, "agu": 8,
         "ags": 8, "sep": 9, "oct": 10, "okt": 10, "nov": 11, "dec": 12, "des": 12}
POLA_MULAI = re.compile(r"(?:Started running on|Mulai ditayangkan pada)\s+([^\n]+)")
POLA_ID = re.compile(r"(?:Library ID|ID Galeri):\s*(\d+)")
POLA_SAMA = re.compile(r"(\d+)\s+(?:ads use this creative and text|iklan menggunakan materi iklan dan teks ini)")
JS_KARTU = r"""() => {
  const pola = /^(Library ID|ID Galeri):\s*\d+/;
  const daun = [...document.querySelectorAll('span,div')].filter(e => e.childElementCount === 0 && pola.test((e.textContent || '').trim()));
  const hasil = [];
  for (const d of daun) {
    let n = d, kartu = d;
    while (n.parentElement) {
      const t = n.parentElement.innerText || '';
      if ((t.match(/(Library ID|ID Galeri):/g) || []).length > 1) break;
      kartu = n.parentElement; n = n.parentElement;
      if (kartu === document.body) break;
    }
    hasil.push({teks: kartu.innerText || '', link: [...kartu.querySelectorAll('a[href]')].map(a => a.href)});
  }
  return hasil;
}"""


def alamat_cari(frasa, negara, bebas):
    q = urllib.parse.quote(frasa if bebas else f'"{frasa}"')
    jenis = "keyword_unordered" if bebas else "keyword_exact_phrase"
    return (f"{DASAR}?active_status=active&ad_type=all&country={negara}&media_type=all&q={q}"
            f"&search_type={jenis}&sort_data[mode]=total_impressions&sort_data[direction]=desc")


def alamat_halaman(id_halaman, negara):
    return (f"{DASAR}?active_status=active&ad_type=all&country={negara}&media_type=all"
            f"&search_type=page&view_all_page_id={id_halaman}")


def baca_tanggal(s):
    s = s.strip().replace(",", " ")
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})[A-Za-z]*\s+(\d{4})", s) or None
    if m:
        h, b, t = m.group(1), m.group(2), m.group(3)
    else:
        m = re.search(r"([A-Za-z]{3})[A-Za-z]*\s+(\d{1,2})\s+(\d{4})", s)
        if not m:
            return None
        b, h, t = m.group(1), m.group(2), m.group(3)
    bulan = BULAN.get(b.lower())
    if not bulan:
        return None
    try:
        return datetime.date(int(t), bulan, int(h))
    except ValueError:
        return None


def tujuan_asli(link):
    """Tautan tombol iklan sering terbungkus l.facebook.com/l.php?u=... Ambil alamat aslinya."""
    u = urllib.parse.urlparse(link)
    if u.netloc.startswith("l.facebook.com") or u.netloc.startswith("l.instagram.com"):
        asli = urllib.parse.parse_qs(u.query).get("u", [""])[0]
        return asli or None
    if u.netloc.endswith("facebook.com") or u.netloc.endswith("fb.com") or not u.netloc:
        return None
    return link


def urai_kartu(k, hari_ini):
    teks = k["teks"].replace("​", "")
    baris = [b.strip() for b in teks.split("\n") if b.strip()]
    m_id = POLA_ID.search(teks)
    if not m_id:
        return None
    mulai = None
    m = POLA_MULAI.search(teks)
    if m:
        mulai = baca_tanggal(m.group(1))
    pengiklan, isi = "", ""
    for tanda in ("Sponsored", "Bersponsor"):
        if tanda in baris:
            i = baris.index(tanda)
            pengiklan = baris[i - 1] if i > 0 else ""
            isi = "\n".join(baris[i + 1:])
            break
    halaman = next((l for l in k["link"] if re.match(r"https://www\.facebook\.com/[^/?]+/?$", l)), None)
    tujuan = []
    for l in k["link"]:
        t = tujuan_asli(l)
        if t and t not in tujuan:
            tujuan.append(t)
    sama = POLA_SAMA.search(teks)
    umur = (hari_ini - mulai).days if mulai else None
    return {
        "id_iklan": m_id.group(1),
        "tautan_iklan": f"{DASAR}?id={m_id.group(1)}",
        "pengiklan": pengiklan,
        "halaman_pengiklan": halaman,
        "mulai": mulai.isoformat() if mulai else None,
        "hari": umur,
        "iklan_sama": int(sama.group(1)) if sama else 1,
        "tujuan": tujuan,
        "tombol": baris[-1] if baris else "",
        "teks": isi,
    }


def status_dari(hari, jumlah):
    if hari is None:
        return None
    if hari >= 30:
        return "WINNING"
    if hari >= 14 or jumlah >= 10:
        return "POTENSIAL"
    return "BARU"


def ringkas_pengiklan(kartu):
    grup = {}
    for k in kartu:
        g = grup.setdefault(k["pengiklan"] or "(nama tidak terbaca)", [])
        g.append(k)
    hasil = []
    for nama, isi in grup.items():
        jumlah = sum(k["iklan_sama"] for k in isi)
        berumur = [k for k in isi if k["hari"] is not None]
        tertua = max(berumur, key=lambda k: k["hari"]) if berumur else None
        tujuan = []
        for k in isi:
            for t in k["tujuan"]:
                if t not in tujuan:
                    tujuan.append(t)
        hasil.append({
            "pengiklan": nama,
            "iklan_terlihat": jumlah,
            "hari_tertua": tertua["hari"] if tertua else None,
            "mulai_tertua": tertua["mulai"] if tertua else None,
            "tautan_iklan_tertua": tertua["tautan_iklan"] if tertua else isi[0]["tautan_iklan"],
            "status": status_dari(tertua["hari"] if tertua else None, jumlah),
            "tujuan": tujuan[:5],
        })
    hasil.sort(key=lambda r: (-(r["hari_tertua"] or -1), -r["iklan_terlihat"]))
    return hasil


def ambil_satu(ctx, alamat, gulir, hari_ini):
    hal = ctx.new_page()
    try:
        hal.goto(alamat, wait_until="domcontentloaded", timeout=60000)
        hal.wait_for_timeout(7000)
        for _ in range(gulir):
            hal.mouse.wheel(0, 3500)
            hal.wait_for_timeout(1800)
        badan = hal.inner_text("body")
        mentah = hal.evaluate(JS_KARTU)
    finally:
        hal.close()
    kartu, lihat = [], set()
    for k in mentah:
        u = urai_kartu(k, hari_ini)
        if u and u["id_iklan"] not in lihat:
            lihat.add(u["id_iklan"])
            kartu.append(u)
    m = re.search(r"(~?[\d.,]+\+?)\s+(?:results?|hasil)", badan)
    catatan = None
    if not kartu:
        if re.search(r"log in to continue|masuk untuk melanjutkan|You must log in", badan, re.I):
            catatan = "Facebook meminta login, halaman tidak terbaca"
        elif re.search(r"No ads match|Tidak ada iklan yang cocok|0 results", badan, re.I):
            catatan = "tidak ada iklan untuk pencarian ini"
        else:
            catatan = "kartu iklan tidak terbaca (halaman kosong atau diblokir)"
    return {"alamat": alamat, "jumlah_hasil": m.group(1) if m else None, "kartu_terbaca": len(kartu),
            "catatan": catatan, "pengiklan": ringkas_pengiklan(kartu), "iklan": kartu}


def main():
    ap = argparse.ArgumentParser(description="Ambil iklan dari Facebook Ads Library tanpa login.")
    ap.add_argument("--negara", default="ID", help="kode negara 2 huruf: ID, US, MY, PH, IN, BR, atau ALL")
    ap.add_argument("--frasa", action="append", default=[], help="frasa pencarian, ulangi untuk beberapa frasa")
    ap.add_argument("--halaman", action="append", default=[], help="ID halaman pengiklan, untuk melihat semua iklannya")
    ap.add_argument("--id", action="append", default=[], help="Library ID satu iklan")
    ap.add_argument("--gulir", type=int, default=4)
    ap.add_argument("--bebas", action="store_true", help="kata tidak harus berurutan persis")
    ap.add_argument("--keluar", help="file JSON hasil")
    ap.add_argument("--teks", type=int, default=400)
    a = ap.parse_args()
    if not (a.frasa or a.halaman or a.id):
        ap.error("isi minimal satu --frasa, --halaman, atau --id")
    peramban.pakai_venv()
    from playwright.sync_api import sync_playwright

    negara = a.negara.upper()
    hari_ini = datetime.date.today()
    tugas = [("frasa", f, alamat_cari(f, negara, a.bebas)) for f in a.frasa]
    tugas += [("halaman", h, alamat_halaman(h, negara)) for h in a.halaman]
    tugas += [("id", i, f"{DASAR}?id={i}") for i in a.id]
    hasil = {"diambil": datetime.datetime.now().isoformat(timespec="minutes"), "umur_dihitung_sampai": hari_ini.isoformat(),
             "negara": negara, "gulir": a.gulir, "pencarian": []}
    with sync_playwright() as p:
        browser, nama = peramban.buka_browser(p)
        hasil["browser"] = nama
        ctx = peramban.konteks(browser)
        for jenis, isi, alamat in tugas:
            try:
                r = ambil_satu(ctx, alamat, a.gulir if jenis != "id" else 0, hari_ini)
            except Exception as e:
                pesan = str(e).splitlines()[0][:200]
                r = {"alamat": alamat, "jumlah_hasil": None, "kartu_terbaca": 0, "catatan": "gagal dibuka: " + pesan,
                     "pengiklan": [], "iklan": []}
            r = {"jenis": jenis, "cari": isi, **r}
            hasil["pencarian"].append(r)
        browser.close()

    keluar = Path(a.keluar or f"iklan-{negara.lower()}.json")
    keluar.parent.mkdir(parents=True, exist_ok=True)
    keluar.write_text(json.dumps(hasil, ensure_ascii=False, indent=1), encoding="utf-8")

    terbaca = sum(r["kartu_terbaca"] for r in hasil["pencarian"])
    print(f"ADS LIBRARY {negara} | browser {hasil['browser']} | umur dihitung sampai {hari_ini.isoformat()} | gulir {a.gulir}x")
    for r in hasil["pencarian"]:
        print(f"\n=== {r['jenis']}: {r['cari']} | hasil menurut Facebook: {r['jumlah_hasil'] or 'tidak tertulis'} | kartu terbaca: {r['kartu_terbaca']}")
        print(f"    {r['alamat']}")
        if r["catatan"]:
            print(f"    CATATAN: {r['catatan']}")
        for g in r["pengiklan"]:
            umur = f"{g['hari_tertua']} hari (mulai {g['mulai_tertua']})" if g["hari_tertua"] is not None else "umur tidak terbaca"
            print(f"  - {g['pengiklan']} | {g['iklan_terlihat']} iklan terlihat | tertua {umur} | {g['status'] or 'tanpa status'}")
            print(f"      iklan tertua: {g['tautan_iklan_tertua']}")
            for t in g["tujuan"][:2]:
                print(f"      tujuan tombol: {t}")
        if a.teks:
            for k in r["iklan"]:
                print(f"  > [{k['id_iklan']}] {k['pengiklan']} | {k['hari']} hari | {k['teks'][:a.teks].replace(chr(10), ' / ')}")
    print(f"\nHasil lengkap: {keluar.resolve()}")
    if terbaca == 0:
        gagal_buka = [r for r in hasil["pencarian"] if (r["catatan"] or "").startswith("gagal dibuka")]
        if gagal_buka and len(gagal_buka) == len(hasil["pencarian"]):
            print("TIDAK TERBUKA: komputer atau lingkungan ini tidak bisa menghubungi facebook.com.")
            print("Untuk asisten AI: jangan mengarang hasil dan jangan menyuruh pengguna membuka Ads Library sendiri. "
                  "Ikuti bagian 'Kalau browser tidak bisa jalan' di SKILL.md.")
            sys.exit(4)
        print("TIDAK ADA KARTU TERBACA. Untuk asisten AI: coba frasa lain atau ulangi sekali. Jangan mengarang hasil.")
        sys.exit(2)


if __name__ == "__main__":
    main()
