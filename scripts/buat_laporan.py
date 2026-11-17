#!/usr/bin/env python3
"""Pembuat Laporan Riset Ghost Ads Spy: satu halaman rapi yang bisa dikirim atau dicetak jadi PDF.

Produk resmi Regrow Labs.

Mengubah satu riset di papan menjadi laporan satu file HTML (siap cetak, nyaman dibaca di HP), dan kalau diminta
juga PDF. Cocok untuk dikirim ke klien, tim, atau disimpan sendiri. Laporan hanya memuat Skor Ghost, tidak memuat
rincian nilainya. Tanpa internet. PDF memakai browser riset yang sama dengan skrip lain.

  python3 scripts/buat_laporan.py                       laporan riset terbaru (HTML)
  python3 scripts/buat_laporan.py --riset <id> --pdf    riset tertentu, plus PDF
  python3 scripts/buat_laporan.py --untuk "Nama Klien" --oleh "Nama Kamu" --pdf

Hasil di papan/laporan/. Kode keluar: 0 berhasil, 1 gagal.
"""
import argparse
import datetime
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import buat_papan as bp  # noqa: E402

AKAR = Path(__file__).resolve().parent.parent


def e(x):
    return html.escape(str(x if x is not None else ""), quote=True)


def aman(u):
    return e(u) if str(u).startswith("https://") else "#"


def tgl(iso):
    try:
        y, m, d = (int(x) for x in str(iso).split("-"))
        bulan = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        return f"{d} {bulan[m]} {y}"
    except Exception:
        return str(iso)


CSS = """
:root{color-scheme:light;--r:#DC2626;--t:#1a1a1a;--m:#5b5b5b;--g:#f6f6f3;--l:#e6e6e0}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--t);background:#fff}
main{max-width:780px;margin:0 auto;padding:24px 18px 60px}
.cover{border-bottom:3px solid var(--r);padding-bottom:18px;margin-bottom:24px}
.cap{font:700 12px/1.4 ui-monospace,Menlo,Consolas,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--r)}
h1{font-size:clamp(26px,6vw,38px);line-height:1.1;margin:8px 0;letter-spacing:-.02em}h2{font-size:21px;margin:30px 0 10px}h3{font-size:18px;margin:0}
.meta{color:var(--m);font-size:14px}.ringkas{background:var(--g);border-radius:14px;padding:16px 18px;margin:16px 0}
.kartu{border:1px solid var(--l);border-radius:14px;padding:16px 18px;margin:14px 0;break-inside:avoid}
.baris{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;margin:6px 0}
.skor{font-weight:900;font-size:22px}.lencana{display:inline-block;font:700 11px/1 ui-monospace,Menlo,monospace;letter-spacing:.06em;padding:5px 8px;border-radius:6px;background:#eee}
.WINNING{background:#dcfce7;color:#14532d}.POTENSIAL{background:#fef3c7;color:#78350f}.BARU{background:#e0f2fe;color:#0c4a6e}
.LANJUT{background:#dcfce7;color:#14532d}.PERLU{background:#fef3c7;color:#78350f}.TAHAN{background:#fee2e2;color:#7f1d1d}
ul{padding-left:20px;margin:6px 0}li{margin:3px 0}a{color:#b91c1c;overflow-wrap:anywhere}.kecil{font-size:13.5px;color:var(--m)}
.pembanding{border-top:1px dashed var(--l);padding-top:8px;margin-top:8px}.disc{border:1px solid var(--l);border-radius:12px;padding:12px 16px;margin-top:28px;font-size:13.5px;color:var(--m)}
.tombol{display:inline-block;margin:0 0 14px;padding:10px 16px;background:var(--r);color:#fff;border-radius:10px;border:0;font:700 15px system-ui;cursor:pointer}
@media print{.tombol{display:none}main{padding:0}a{color:inherit;text-decoration:none}.kartu{border-color:#bbb}@page{size:A4;margin:16mm}}
"""


def daftar(x):
    return "<ul>" + "".join(f"<li>{e(v)}</li>" for v in x) + "</ul>" if x else ""


def kartu_ide(i, n, rekom):
    p = bp.bukti_winning(i)
    umur = ""
    if p:
        umur = f'<span class="lencana WINNING">WINNING</span> <span class="kecil">iklan pesaing tayang {p["hari"]} hari ({e(p["nama"])})</span>'
    else:
        t = [x for x in i.get("pembanding") or [] if x.get("hari") is not None]
        if t:
            b = max(t, key=lambda x: x["hari"])
            umur = f'<span class="lencana {e(b.get("status", ""))}">{e(b.get("status", ""))}</span> <span class="kecil">iklan terlama {b["hari"]} hari</span>'
        else:
            umur = '<span class="kecil">ide baru, belum ada pesaing langsung</span>'
    v = (i.get("validasi") or {}).get("vonis")
    kv = {"LANJUT TES KECIL": "LANJUT", "PERLU BUKTI": "PERLU", "TAHAN": "TAHAN"}.get(v, "")
    vonis = f'<span class="lencana {kv}">{e(v)}</span>' if v else ""
    awal = '<span class="lencana LANJUT">PALING DISARANKAN</span> ' if rekom else ""
    bukti = ""
    for x in sorted(i.get("pembanding") or [], key=lambda x: -(x["hari"] if x.get("hari") is not None else -1))[:4]:
        tautan = "".join(f' <a href="{aman(u)}">iklan</a>' for u in (x.get("iklan") or [])[:1])
        tautan += "".join(f' <a href="{aman(l.get("url"))}">{e(l.get("label", "halaman jualan"))}</a>' for l in (x.get("lp") or [])[:1])
        bukti += (f'<div class="pembanding"><b>{e(x["nama"])}</b> '
                  f'{(str(x["hari"]) + " hari") if x.get("hari") is not None else "umur belum dicek"}'
                  f'{" · " + e(x["harga_pendek"]) if x.get("harga_pendek") else (" · " + e(x["harga"]) if x.get("harga") else "")}'
                  f'<br><span class="kecil">{e(x["isi"])}</span>{tautan}</div>')
    val = ""
    if i.get("validasi"):
        vv = i["validasi"]
        val = f'<p><b>Alasan vonis:</b> {e(vv.get("alasan"))}</p>'
        if vv.get("langkah"):
            val += "<p><b>Langkah berikutnya:</b></p>" + daftar(vv["langkah"])
    return (f'<div class="kartu"><div class="baris">{awal}<h3>{n}. {e(i["nama"])}</h3><span class="skor">{e(i["total"])}/30</span><span class="kecil">Skor Ghost</span></div>'
            f'<div class="baris">{umur} {vonis}</div><p class="kecil">Untuk {e(i["target"])}</p><p>{e(i["formula"])}</p>'
            f'{("<p><b>Bentuk produk:</b> " + e(i["bentuk"]) + "</p>") if i.get("bentuk") else ""}{val}{bukti}'
            f'{("<p class=kecil><b>Yang belum dicek:</b> " + e(i["ragu"]) + "</p>") if i.get("ragu") else ""}</div>')


def rakit(g, r, untuk, oleh):
    ide = sorted([i for i in g["ide"] if i["riset"] == r["id"]], key=lambda i: i.get("no", 0))
    rek = set(r.get("rekomendasi") or [])
    # urutan sama dengan papan: Paling disarankan memakai kunci_saran, sisanya urut Skor Ghost
    atas = sorted((i for i in ide if i["id"] in rek and bp.kunci_saran(i)), key=bp.kunci_saran, reverse=True)
    urut = atas + [i for i in ide if i not in atas]
    n_win = sum(1 for i in ide if bp.bukti_winning(i))
    n_val = sum(1 for i in ide if i.get("validasi"))
    for_ = f"Disiapkan untuk {e(untuk)}. " if untuk else ""
    oleh_ = f"Oleh {e(oleh)}. " if oleh else ""
    top = atas[0] if atas else None
    sar = (f'<p><b>Produk nomor 1:</b> {e(top["nama"])}, Skor Ghost {e(top["total"])}/30, iklan pesaing tayang {bp.bukti_winning(top)["hari"]} hari.</p>'
           if top else "<p>Belum ada produk dengan iklan pesaing berumur 30 hari atau lebih, jadi belum ada yang disarankan.</p>")
    return ('<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Laporan Riset: {e(r["judul"])}</title><style>{CSS}</style></head><body><main>'
            '<button class="tombol" onclick="window.print()">Cetak atau simpan PDF</button>'
            f'<div class="cover"><div class="cap">Laporan Riset Produk Winning</div><h1>{e(r["judul"])}</h1>'
            f'<div class="meta">{for_}{oleh_}Riset tanggal {e(tgl(r["tanggal"]))}. Dibuat {e(tgl(datetime.date.today().isoformat()))} dengan Ghost Ads Spy (Regrow Labs).</div></div>'
            f'<div class="ringkas"><p><b>Ringkasan:</b> {e(r["ringkas"])}</p><p>{len(ide)} produk dinilai, {n_win} dengan bukti iklan pesaing WINNING, {n_val} sudah divalidasi.</p>{sar}</div>'
            + (f'<h2>Pola dari iklan</h2>{daftar(r.get("pola"))}' if r.get("pola") else "")
            + (f'<h2>Sinyal lain</h2>{daftar(r.get("sinyal"))}' if r.get("sinyal") else "")
            + "<h2>Produk</h2>" + "".join(kartu_ide(i, n, i["id"] in rek) for n, i in enumerate(urut, 1))
            + (f'<h2>Cara baca angka</h2>{daftar(r.get("catatan_baca"))}' if r.get("catatan_baca") else "")
            + '<div class="disc"><b>Penting.</b> Skor Ghost (0 sampai 30) dan vonis adalah penilaian dari bukti iklan yang ditemukan, bukan jaminan produk laku '
              'atau jaminan penghasilan. Harga dan klaim adalah tulisan di halaman pesaing dan belum diverifikasi. Umur iklan dihitung sampai tanggal riset. '
              'Keputusan akhir ada pada pembaca.</div></main></body></html>')


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Buat laporan riset yang bisa dibagikan")
    ap.add_argument("--riset")
    ap.add_argument("--untuk", default="")
    ap.add_argument("--oleh", default="")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--folder")
    a = ap.parse_args()
    if a.pdf:   # pindah ke Python penyiap lebih awal supaya skrip tidak berjalan dua kali
        import peramban
        peramban.pakai_venv()
    folder = bp.folder_kerja(a.folder)
    g = bp.baca_gudang(folder)
    if not g or not g["riset"]:
        bp.gagal("belum ada riset di papan, jadi belum ada yang bisa dilaporkan")
    if a.riset:
        r = next((x for x in g["riset"] if x["id"] == a.riset), None)
        if not r:
            bp.gagal(f"riset '{a.riset}' tidak ada. Jalankan buat_papan.py lihat untuk daftar id.")
    else:
        r = sorted(g["riset"], key=lambda x: x["tanggal"], reverse=True)[0]
    # hanya Skor Ghost yang dibawa ke laporan
    g = dict(g, ide=[{k: v for k, v in i.items() if k not in ("malas", "instant", "applicable")} for i in g["ide"]])
    out = folder / "laporan"
    out.mkdir(parents=True, exist_ok=True)
    nama = re.sub(r"[^a-z0-9-]+", "-", r["id"].lower()).strip("-")
    h = out / f"laporan-{nama}.html"
    h.write_text(rakit(g, r, a.untuk, a.oleh), encoding="utf-8")
    print(f"LAPORAN SIAP: {h}")
    if a.pdf:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b, _ = peramban.buka_browser(p)
            pg = b.new_page()
            pg.goto(h.resolve().as_uri(), wait_until="load")
            pdf = h.with_suffix(".pdf")
            pg.pdf(path=str(pdf), format="A4", print_background=True, margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"})
            b.close()
        print(f"PDF SIAP: {pdf}")


if __name__ == "__main__":
    main()
