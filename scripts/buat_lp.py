#!/usr/bin/env python3
"""Pembuat halaman jualan (landing page) dan lembar teks iklan Ghost Ads Spy.

Produk resmi Regrow Labs.

Claude menulis isi produk ke satu file spesifikasi JSON, skrip ini memeriksanya lalu merakit:
  papan/produk/<id>/index.html       halaman jualan satu file, siap HP, tanpa pustaka luar
  papan/produk/<id>/iklan.md         lembar teks iklan, pengaturan target, dan rencana tes
  papan/produk/<id>/spesifikasi.json salinan spesifikasi (sumber kebenaran)

Tanpa internet dan tanpa pustaka tambahan.

  python3 scripts/buat_lp.py contoh                          tulis contoh spesifikasi ke papan/kerja/spesifikasi-contoh.json
  python3 scripts/buat_lp.py rakit papan/kerja/spek.json     periksa dan rakit
  python3 scripts/buat_lp.py lihat                           daftar produk yang sudah dirakit

Skrip menolak isi yang melanggar aturan dasar iklan Meta dan kejujuran: janji penghasilan pasti, testimoni yang
tidak ditandai asli, hitung mundur palsu, dan klaim sebelum-sesudah. Peringatan (bukan penolakan) untuk teks iklan
yang melebihi batas yang disarankan.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
FOLDER = AKAR / "papan" / "produk"

DILARANG = [
    (r"\bpasti\s+(?:kaya|untung|laku|cuan|sukses|berhasil)", "janji hasil pasti"),
    (r"\bdijamin\s+(?:kaya|untung|laku|cuan|sukses|berhasil|penghasilan)", "janji hasil dijamin"),
    (r"\b(?:jutaan|puluhan juta|ratusan juta)\s+(?:rupiah\s+)?(?:per|tiap|setiap)\s+(?:hari|minggu|bulan)", "janji penghasilan berupa angka"),
    (r"\bpenghasilan\s+(?:pasti|tetap|dijamin)", "janji penghasilan"),
    (r"\b(?:sebelum|before)\s*(?:dan|&|/|-)\s*(?:sesudah|after)", "klaim sebelum dan sesudah"),
    (r"\bhitung\s*mundur\b|\bcountdown\b|\bsisa\s+\d+\s+(?:slot|kursi|stok)", "urgensi palsu (hitung mundur atau sisa kuota yang tidak nyata)"),
    (r"\b(?:anda|kamu)\s+(?:gemuk|obesitas|miskin|bangkrut|depresi|botak|jerawatan|sakit)\b", "menyebut kondisi pribadi pembaca"),
    (r"\b(?:obat|sembuh(?:kan)?|menyembuhkan)\b", "klaim kesehatan"),
]
WAJIB = ["id", "nama", "judul", "subjudul", "untuk", "manfaat", "isi_paket", "harga", "tombol"]
BATAS_IKLAN = {"teks_utama": 125, "judul": 40, "deskripsi": 30}   # batas yang disarankan Meta agar tidak terpotong


def gagal(pesan):
    sys.exit("GAGAL: " + pesan)


def e(x):
    return html.escape(str(x), quote=True)


def semua_teks(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, list):
        for v in x:
            yield from semua_teks(v)
    elif isinstance(x, dict):
        for k, v in x.items():
            if k not in ("tautan", "pixel_id", "wa", "url"):
                yield from semua_teks(v)


def bersih(x):
    if isinstance(x, str):
        return x.replace(" " + chr(8212) + " ", ", ").replace(chr(8212), ", ").replace(chr(8211), "-")
    if isinstance(x, list):
        return [bersih(v) for v in x]
    if isinstance(x, dict):
        return {k: bersih(v) for k, v in x.items()}
    return x


def periksa(s):
    for k in WAJIB:
        if s.get(k) in (None, "", [], {}):
            gagal(f"spesifikasi belum punya '{k}'")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}", s["id"]):
        gagal("'id' harus huruf kecil, angka, dan tanda hubung, 3 sampai 60 karakter")
    h = s["harga"]
    if not isinstance(h, dict) or not h.get("jual"):
        gagal("'harga' harus berisi 'jual', misalnya {\"jual\": \"Rp 49.000\", \"coret\": \"Rp 99.000\"}")
    t = s["tombol"]
    if not isinstance(t, dict) or not str(t.get("tautan", "")).startswith("https://"):
        gagal("'tombol.tautan' wajib diawali https:// (tautan pembayaran, lapak, atau WhatsApp). Isi dengan tautan nyata milik pengguna.")
    if h.get("coret") and not s.get("dasar_harga_coret"):
        gagal("ada harga coret tetapi 'dasar_harga_coret' kosong. Harga coret hanya boleh kalau harga itu benar pernah atau akan berlaku. "
              "Tulis dasarnya, atau hapus 'coret'.")
    for tm in s.get("testimoni") or []:
        if tm.get("asli") is not True:
            gagal("testimoni hanya boleh dari pembeli sungguhan. Tandai \"asli\": true setelah pengguna punya buktinya, atau hapus testimoni itu. "
                  "Jangan mengarang testimoni.")
    for t in semua_teks({k: v for k, v in s.items() if k != "dasar_harga_coret"}):
        for pola, nama in DILARANG:
            if re.search(pola, t, re.I):
                gagal(f"teks '{t[:80]}' melanggar aturan: {nama}. Tulis ulang tanpa klaim itu.")
    for i in s.get("iklan") or []:
        for k in ("nama", "teks_utama", "judul"):
            if not i.get(k):
                gagal(f"setiap iklan wajib punya '{k}'")


def peringatan(s):
    w = []
    for i in s.get("iklan") or []:
        for k, b in BATAS_IKLAN.items():
            if i.get(k) and len(i[k]) > b:
                w.append(f"iklan '{i['nama']}': '{k}' {len(i[k])} karakter, disarankan paling banyak {b} supaya tidak terpotong")
    if len(s.get("iklan") or []) < 3:
        w.append("disarankan 3 sudut iklan berbeda untuk tes")
    if not s.get("testimoni"):
        w.append("belum ada testimoni asli. Itu boleh, tapi halaman tanpa bukti sosial biasanya lebih lemah. Kumpulkan dari pembeli pertama.")
    if not s.get("garansi"):
        w.append("belum ada garansi. Isi hanya kalau pengguna benar mau memberikannya.")
    if not s.get("pixel_id"):
        w.append("Pixel Meta belum diisi. Tanpa Pixel, Meta tidak bisa mengukur pembelian. Lihat PANDUAN-NGIKLAN.html bagian Pixel.")
    return w


CSS = """
:root{color-scheme:light;--w:%(warna)s;--t:#1a1a1a;--m:#5b5b5b;--g:#f6f6f3}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%%}
body{margin:0;font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--t);background:#fff}
main{max-width:640px;margin:0 auto;padding:0 18px 96px}
section{padding:28px 0;border-top:1px solid #eee}section:first-child{border:0}
h1{font-size:clamp(28px,7vw,40px);line-height:1.12;margin:28px 0 10px;letter-spacing:-.02em}
h2{font-size:22px;margin:0 0 12px;letter-spacing:-.01em}
.sub{color:var(--m);font-size:19px;margin:0 0 18px}
.untuk{display:inline-block;background:var(--g);border-radius:999px;padding:6px 14px;font-size:14px;color:var(--m)}
ul{padding-left:0;list-style:none;margin:0;display:grid;gap:10px}
li{padding-left:30px;position:relative}li::before{content:"\\2713";position:absolute;left:0;color:var(--w);font-weight:800}
ol{padding-left:22px;display:grid;gap:10px}ol li{padding-left:6px}ol li::before{content:none}
.kartu{background:var(--g);border-radius:16px;padding:20px}
.harga{text-align:center}.coret{text-decoration:line-through;color:var(--m);font-size:18px}
.jual{font-size:44px;font-weight:900;letter-spacing:-.02em;line-height:1.1}.cat{color:var(--m);font-size:14px}
.btn{display:block;text-align:center;background:var(--w);color:#fff;text-decoration:none;font-weight:800;font-size:19px;padding:16px 20px;border-radius:14px;margin-top:14px;min-height:52px}
.btn:focus-visible{outline:3px solid #000;outline-offset:3px}
details{border:1px solid #e5e5e5;border-radius:12px;padding:12px 16px;margin-bottom:10px}summary{font-weight:700;cursor:pointer}
details p{margin:8px 0 0;color:var(--m)}
.tm{border-left:4px solid var(--w);padding:4px 14px;margin:0 0 12px}.tm b{display:block}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid #e5e5e5;padding:10px 16px;z-index:5}
.bar .btn{margin:0;max-width:640px;margin-inline:auto}
footer{font-size:12.5px;color:var(--m);padding:20px 0}
"""

PIXEL = """<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','%(pixel)s');fbq('track','PageView');
document.addEventListener('click',function(ev){var a=ev.target.closest('[data-beli]');if(a){fbq('track','InitiateCheckout');}});
</script>
"""


def rakit_html(s):
    h = s["harga"]
    t = s["tombol"]
    warna = s.get("warna") if re.fullmatch(r"#[0-9a-fA-F]{6}", str(s.get("warna", ""))) else "#DC2626"
    p = []
    p.append(f'<section><span class="untuk">Untuk {e(s["untuk"])}</span><h1>{e(s["judul"])}</h1><p class="sub">{e(s["subjudul"])}</p>'
             f'<a class="btn" data-beli href="{e(t["tautan"])}" rel="noopener">{e(t.get("teks", "Pesan Sekarang"))}</a></section>')
    if s.get("masalah"):
        p.append("<section><h2>Kamu mungkin merasakan ini</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in s["masalah"]) + "</ul></section>")
    p.append("<section><h2>Yang kamu dapat</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in s["manfaat"]) + "</ul></section>")
    if s.get("cara_kerja"):
        p.append("<section><h2>Cara pakainya</h2><ol>" + "".join(f"<li>{e(x)}</li>" for x in s["cara_kerja"]) + "</ol></section>")
    p.append("<section><h2>Isi paket</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in s["isi_paket"]) + "</ul></section>")
    if s.get("bonus"):
        p.append('<section><h2>Bonus</h2><div class="kartu"><ul>' + "".join(f"<li>{e(x)}</li>" for x in s["bonus"]) + "</ul></div></section>")
    if s.get("testimoni"):
        p.append("<section><h2>Kata pembeli</h2>" + "".join(f'<blockquote class="tm"><b>{e(x.get("nama", "Pembeli"))}</b>{e(x["isi"])}</blockquote>' for x in s["testimoni"]) + "</section>")
    coret = f'<div class="coret">{e(h["coret"])}</div>' if h.get("coret") else ""
    cat = f'<div class="cat">{e(h["catatan"])}</div>' if h.get("catatan") else ""
    gar = f'<p class="cat" style="margin-top:12px">{e(s["garansi"])}</p>' if s.get("garansi") else ""
    p.append(f'<section><div class="kartu harga">{coret}<div class="jual">{e(h["jual"])}</div>{cat}'
             f'<a class="btn" data-beli href="{e(t["tautan"])}" rel="noopener">{e(t.get("teks", "Pesan Sekarang"))}</a>{gar}</div></section>')
    if s.get("faq"):
        p.append("<section><h2>Pertanyaan yang sering muncul</h2>" + "".join(f'<details><summary>{e(x["t"])}</summary><p>{e(x["j"])}</p></details>' for x in s["faq"]) + "</section>")
    kontak = f' Pertanyaan: <a href="https://wa.me/{e(s["wa"])}" rel="noopener">WhatsApp</a>.' if re.fullmatch(r"\d{8,15}", str(s.get("wa", ""))) else ""
    p.append(f'<footer>{e(s.get("penjual", ""))} Hasil penggunaan berbeda pada tiap orang dan tidak dijamin.{kontak}</footer>')
    pixel = PIXEL % {"pixel": re.sub(r"\D", "", str(s["pixel_id"]))} if s.get("pixel_id") and re.sub(r"\D", "", str(s["pixel_id"])) else ""
    return ('<!doctype html><html lang="id"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(s["nama"])}</title><meta name="description" content="{e(s["subjudul"])}">'
            f'<style>{CSS % {"warna": warna}}</style>{pixel}</head><body><main>' + "".join(p) +
            f'</main><div class="bar"><a class="btn" data-beli href="{e(t["tautan"])}" rel="noopener">{e(t.get("teks", "Pesan Sekarang"))} · {e(h["jual"])}</a></div>'
            "</body></html>")


def rakit_iklan(s, w):
    g = s.get("target_iklan") or {}
    L = [f"# Lembar iklan: {s['nama']}", "",
         "Dibuat oleh Ghost Ads Spy (Regrow Labs). Isi tiap iklan ditulis dari halaman jualan, bukan dari janji hasil.", "",
         "## Sebelum memasang", "- Halaman jualan sudah online dan tombol beli sudah dicoba sendiri dari HP.",
         "- Pixel Meta terpasang dan terbaca di Events Manager (lihat PANDUAN-NGIKLAN.html).",
         "- Kamu sudah mencoba membeli sendiri sekali untuk memastikan pembayaran dan pengiriman produk jalan.", ""]
    for n, i in enumerate(s.get("iklan") or [], 1):
        L += [f"## Iklan {n}: {i['nama']}"]
        if i.get("sudut"):
            L += [f"Sudut: {i['sudut']}"]
        L += ["", "Teks utama:", "", i["teks_utama"], "", f"Judul: {i['judul']}"]
        if i.get("deskripsi"):
            L += [f"Deskripsi: {i['deskripsi']}"]
        L += [f"Tombol: {i.get('cta', 'Pelajari Selengkapnya')}", ""]
    L += ["## Pengaturan target (titik awal, sesuaikan dengan niche)",
          f"- Negara: {g.get('negara', 'ID')}", f"- Umur: {g.get('umur', '25-45')}"]
    if g.get("minat"):
        L += ["- Minat yang dicoba: " + ", ".join(g["minat"])]
    L += ["- Penempatan: otomatis (Advantage+ placements) untuk tes pertama.",
          "- Tujuan kampanye: Penjualan (Sales) kalau Pixel sudah terbaca. Kalau belum, Traffic dulu sambil memasang Pixel.", "",
          "## Rencana tes",
          f"- Anggaran harian: {g.get('anggaran_harian', 'Rp 50.000')}",
          f"- Lama tes: {g.get('durasi_hari', 3)} hari tanpa mengubah apa pun, supaya data cukup.",
          "- Pasang tiap sudut iklan sebagai iklan terpisah dalam satu set iklan, atau satu set iklan per sudut kalau anggaran cukup.",
          "- Jangan matikan iklan sebelum ada sekitar 1000 tayangan, kecuali ada penolakan dari Meta.", "",
          "## Cara membaca hasil tes",
          "- Biaya per klik tinggi dan sedikit yang klik: teks utama atau gambar kurang menarik. Ganti sudut.",
          "- Banyak yang klik tetapi tidak ada yang beli: masalah di halaman jualan, harga, atau kepercayaan. Perbaiki halaman, bukan iklan.",
          "- Ada pembelian: hitung biaya iklan per pembelian dan bandingkan dengan batas impas dari `python3 scripts/hitung.py`.",
          "- Iklan yang untung tiga hari berturut-turut baru dinaikkan anggarannya, pelan-pelan (naik sekitar 20 persen per hari).", "",
          "## Aturan iklan yang sering membuat iklan ditolak",
          "- Jangan menjanjikan penghasilan atau hasil tertentu.", "- Jangan menyebut kondisi pribadi pembaca (berat badan, utang, kesehatan).",
          "- Jangan memakai gambar sebelum dan sesudah.", "- Isi iklan harus sama dengan isi halaman jualan.", ""]
    if w:
        L += ["## Catatan dari pemeriksa"] + [f"- {x}" for x in w] + [""]
    return "\n".join(L)


def perintah_rakit(a):
    try:
        s = bersih(json.loads(Path(a.spek).read_text(encoding="utf-8")))
    except FileNotFoundError:
        gagal(f"file tidak ada: {a.spek}")
    except json.JSONDecodeError as ex:
        gagal(f"{a.spek} bukan JSON yang sah: {ex}")
    periksa(s)
    w = peringatan(s)
    d = FOLDER / s["id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(rakit_html(s), encoding="utf-8")
    (d / "iklan.md").write_text(rakit_iklan(s, w), encoding="utf-8")
    (d / "spesifikasi.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"HALAMAN JUALAN SIAP: {d / 'index.html'}")
    print(f"LEMBAR IKLAN SIAP: {d / 'iklan.md'}")
    for x in w:
        print("  PERHATIAN: " + x)
    print("Langkah berikutnya: pasang halaman di hosting, pasang Pixel, lalu tes iklan. Langkahnya ada di PANDUAN-NGIKLAN.html.")


CONTOH = {
    "id": "contoh-pembuat-laporan",
    "nama": "Pembuat Laporan Toko",
    "penjual": "Toko Contoh.",
    "judul": "Laporan penjualan tokomu selesai dalam 2 menit",
    "subjudul": "Isi omzet dan biaya, laporan rapi langsung jadi. Tanpa rumus, tanpa pusing.",
    "untuk": "pemilik toko online yang mencatat sendiri",
    "masalah": ["Catatan penjualan tercecer di banyak tempat", "Akhir bulan bingung untung atau rugi"],
    "manfaat": ["Laporan bulanan rapi tanpa menulis rumus", "Tahu produk mana yang paling menyisakan untung", "Siap dikirim ke partner atau diprint"],
    "cara_kerja": ["Salin template ke akunmu", "Isi omzet dan biaya", "Laporan langsung terhitung"],
    "isi_paket": ["Template laporan bulanan", "Panduan pemakaian 1 halaman"],
    "bonus": ["Template catatan stok"],
    "harga": {"coret": "Rp 99.000", "jual": "Rp 49.000", "catatan": "Sekali bayar, akses selamanya"},
    "dasar_harga_coret": "Rp 99.000 adalah harga normal setelah masa perkenalan berakhir.",
    "garansi": "Kalau template tidak bisa dibuka, kami bantu sampai bisa.",
    "testimoni": [],
    "faq": [{"t": "Perlu aplikasi khusus?", "j": "Cukup Google Sheets, bisa dibuka dari HP."}, {"t": "Bagaimana saya menerimanya?", "j": "Tautan template dikirim otomatis setelah pembayaran."}],
    "tombol": {"teks": "Pesan Sekarang", "tautan": "https://contoh.com/bayar"},
    "wa": "",
    "pixel_id": "",
    "iklan": [
        {"nama": "Sudut waktu", "sudut": "hemat waktu", "teks_utama": "Akhir bulan masih menghitung laporan satu per satu? Coba template yang menghitungnya untukmu.", "judul": "Laporan toko 2 menit", "deskripsi": "Template siap pakai", "cta": "Pelajari Selengkapnya"},
        {"nama": "Sudut rapi", "sudut": "catatan tercecer", "teks_utama": "Catatan penjualan tercecer di chat dan buku? Kumpulkan jadi satu laporan rapi.", "judul": "Satu laporan, semua tertata", "deskripsi": "Template Google Sheets"},
        {"nama": "Sudut untung", "sudut": "tahu produk terbaik", "teks_utama": "Tahu produk mana yang benar-benar menyisakan untung, bukan cuma ramai terjual.", "judul": "Cek produk paling untung", "deskripsi": "Template laporan toko"},
    ],
    "target_iklan": {"negara": "ID", "umur": "25-45", "minat": ["Toko online", "Shopee", "Usaha kecil"], "anggaran_harian": "Rp 50.000", "durasi_hari": 3},
}


def perintah_contoh(a):
    f = AKAR / "papan" / "kerja" / "spesifikasi-contoh.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(CONTOH, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Contoh spesifikasi ditulis ke {f}. Ubah isinya, lalu jalankan: python3 scripts/buat_lp.py rakit {f}")


def perintah_lihat(a):
    ada = sorted(FOLDER.glob("*/spesifikasi.json")) if FOLDER.is_dir() else []
    if not ada:
        print("Belum ada halaman jualan yang dirakit.")
        return
    for f in ada:
        s = json.loads(f.read_text(encoding="utf-8"))
        print(f"{s['id']} | {s['nama']} | {s['harga']['jual']} | {len(s.get('iklan') or [])} sudut iklan | {f.parent / 'index.html'}")


def main():
    for x in (sys.stdout, sys.stderr):
        try:
            x.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Pembuat halaman jualan dan lembar iklan")
    sub = ap.add_subparsers(dest="perintah", required=True)
    r = sub.add_parser("rakit")
    r.add_argument("spek")
    r.set_defaults(fungsi=perintah_rakit)
    sub.add_parser("contoh").set_defaults(fungsi=perintah_contoh)
    sub.add_parser("lihat").set_defaults(fungsi=perintah_lihat)
    a = ap.parse_args()
    a.fungsi(a)


if __name__ == "__main__":
    main()
