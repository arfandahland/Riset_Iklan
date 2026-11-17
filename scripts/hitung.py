#!/usr/bin/env python3
"""Kalkulator tes iklan Ghost Ads Spy: berapa harga, biaya per pembelian, dan modal tes yang masih masuk akal.

Produk resmi Regrow Labs.

Tanpa internet dan tanpa pustaka tambahan. Semua angka hasil adalah HITUNGAN dari angka yang kamu masukkan,
bukan ramalan penghasilan. Angka biaya iklan yang tidak kamu isi memakai rentang perkiraan dan ditandai jelas.

  python3 scripts/hitung.py --harga 49000
  python3 scripts/hitung.py --harga 49000 --biaya-alat 2000 --potongan 5 --cpc 1500 --konversi 2 --anggaran-tes 150000

Pilihan:
  --harga          harga jual (Rp), wajib
  --biaya-alat     biaya menjalankan produk per pembeli, misalnya biaya AI (Rp), bawaan 0
  --potongan       potongan platform pembayaran dalam persen, bawaan 0 (isi 3 sampai 7 kalau pakai lapak seperti Lynk.id atau Mayar)
  --cpc            biaya per klik iklan (Rp). Kalau kosong, dipakai rentang perkiraan 800 sampai 3000
  --konversi       persen pengunjung halaman yang membeli. Kalau kosong, dipakai rentang perkiraan 0,8 sampai 3
  --anggaran-tes   modal tes iklan (Rp), bawaan 150000
  --json           cetak hasil sebagai JSON

Membaca hasil tes iklan yang sudah berjalan (pakai angka nyata dari Ads Manager dan lapak):

  python3 scripts/hitung.py --harga 49000 --potongan 5 --biaya-tes 150000 --klik 90 --pembelian 2

  --biaya-tes      total biaya iklan yang sudah keluar (Rp)
  --klik           jumlah klik ke halaman jualan
  --pembelian      jumlah pembelian (dari dashboard lapak)
"""
import argparse
import json
import sys

PERKIRAAN_CPC = (800, 3000)
PERKIRAAN_KONVERSI = (0.8, 3.0)


def rp(n):
    return "Rp " + f"{round(n):,}".replace(",", ".")


def hitung(harga, biaya_alat=0.0, potongan=0.0, cpc=None, konversi=None, anggaran=150000.0):
    if harga <= 0:
        raise ValueError("harga harus lebih dari 0")
    sisa = harga - biaya_alat - harga * potongan / 100.0   # untung kotor per penjualan sebelum iklan
    if sisa <= 0:
        raise ValueError("biaya alat dan potongan platform sudah menghabiskan harga jual, naikkan harga atau turunkan biaya")
    perkiraan = []
    if cpc is None:
        perkiraan.append("biaya per klik")
    if konversi is None:
        perkiraan.append("persen pembeli")
    skenario = {}
    c_lo, c_hi = (cpc, cpc) if cpc is not None else PERKIRAAN_CPC
    k_lo, k_hi = (konversi, konversi) if konversi is not None else PERKIRAAN_KONVERSI
    # baik = klik murah dan konversi tinggi, buruk = kebalikannya
    for nama, c, k in (("baik", c_lo, k_hi), ("tengah", (c_lo + c_hi) / 2, (k_lo + k_hi) / 2), ("buruk", c_hi, k_lo)):
        cpa = c / (k / 100.0)   # biaya iklan per pembelian
        skenario[nama] = {"cpc": c, "konversi_persen": k, "biaya_per_pembelian": cpa, "untung_per_penjualan": sisa - cpa,
                          "roas": harga / cpa}
    hasil = {
        "harga": harga, "sisa_sebelum_iklan": sisa,
        "batas_biaya_per_pembelian": sisa,          # di atas ini rugi
        "roas_impas": harga / sisa,
        "anggaran_tes": anggaran, "skenario": skenario, "diperkirakan": perkiraan,
    }
    tengah = skenario["tengah"]
    hasil["klik_dari_anggaran"] = anggaran / tengah["cpc"]
    hasil["penjualan_diharapkan_tengah"] = anggaran / tengah["biaya_per_pembelian"]
    # konversi minimal supaya impas pada biaya per klik tengah
    hasil["konversi_impas_persen"] = tengah["cpc"] / sisa * 100.0
    hasil["penjualan_balik_modal_tes"] = anggaran / sisa
    return hasil


def cetak(h):
    print(f"HITUNGAN TES IKLAN | harga {rp(h['harga'])}")
    print(f"- Sisa per penjualan sebelum biaya iklan: {rp(h['sisa_sebelum_iklan'])} (sudah dipotong biaya alat dan potongan platform)")
    print(f"- Batas biaya iklan per pembelian: {rp(h['batas_biaya_per_pembelian'])}. Di atas angka ini setiap penjualan rugi.")
    print(f"- ROAS impas: {h['roas_impas']:.2f}. Iklan harus menghasilkan lebih dari {h['roas_impas']:.2f} kali biaya iklannya supaya tidak rugi.")
    print(f"- Dengan biaya per klik tengah, halaman jualan harus membuat minimal {h['konversi_impas_persen']:.1f} persen pengunjung membeli untuk impas.")
    print(f"- Untuk balik modal tes {rp(h['anggaran_tes'])}, kamu butuh sekitar {h['penjualan_balik_modal_tes']:.1f} penjualan (dihitung dari sisa per penjualan).")
    print("\nTiga kemungkinan hasil tes:")
    nama = {"baik": "Kalau iklannya bagus", "tengah": "Kalau iklannya biasa saja", "buruk": "Kalau iklannya kurang bagus"}
    for k in ("baik", "tengah", "buruk"):
        s = h["skenario"][k]
        status = "UNTUNG" if s["untung_per_penjualan"] > 0 else "RUGI"
        print(f"- {nama[k]}: klik {rp(s['cpc'])}, {s['konversi_persen']:.1f} persen membeli, biaya iklan per pembelian {rp(s['biaya_per_pembelian'])}, "
              f"hasil per penjualan {rp(s['untung_per_penjualan'])} ({status}), ROAS {s['roas']:.2f}")
    t = h["skenario"]["tengah"]
    print(f"\nDengan modal tes {rp(h['anggaran_tes'])}: sekitar {h['klik_dari_anggaran']:.0f} klik dan {h['penjualan_diharapkan_tengah']:.1f} penjualan pada kemungkinan tengah.")
    if h["diperkirakan"]:
        print(f"\nCATATAN: {' dan '.join(h['diperkirakan'])} memakai rentang PERKIRAAN umum, bukan data akunmu. Ganti dengan angka nyata dari iklanmu "
              "(--cpc dan --konversi) begitu ada, dan hitung ulang. Ini hitungan, bukan janji penghasilan.")


def baca_hasil(harga, biaya_alat, potongan, biaya, klik, beli):
    """Keputusan dari angka tes nyata. Aturan sama dengan PANDUAN-NGIKLAN.html."""
    h = hitung(harga, biaya_alat, potongan, cpc=1000, konversi=1, anggaran=biaya)   # hanya untuk sisa per penjualan
    sisa = h["sisa_sebelum_iklan"]
    r = {"biaya": biaya, "klik": klik, "pembelian": beli, "sisa_per_penjualan": sisa,
         "cpc": biaya / klik if klik else None, "konversi_persen": beli / klik * 100 if klik else None,
         "cpa": biaya / beli if beli else None, "uang_masuk": beli * harga, "hasil_bersih": beli * sisa - biaya,
         "roas": beli * harga / biaya if biaya else None}
    if klik < 30:
        r["putusan"], r["alasan"] = "BELUM CUKUP DATA", "klik masih terlalu sedikit untuk disimpulkan. Biarkan iklan jalan sampai sekitar 100 klik atau 3 hari penuh."
    elif beli == 0 and biaya >= sisa * 3:
        r["putusan"], r["alasan"] = "BERHENTI ATAU PERBAIKI HALAMAN", "banyak klik tanpa pembelian setelah modal tes terpakai. Cek halaman, harga, dan kepercayaan. Kalau sudah rapi dan tetap nol, berhenti."
    elif beli == 0:
        r["putusan"], r["alasan"] = "LANJUTKAN TES", "belum ada pembelian tetapi modal tes belum sampai tiga kali sisa per penjualan. Tunggu sampai modal tes habis."
    elif r["cpa"] <= sisa:
        r["putusan"], r["alasan"] = "LANJUT DAN NAIKKAN PELAN", f"biaya iklan per pembelian {rp(r['cpa'])} masih di bawah batas impas {rp(sisa)}. Naikkan anggaran sekitar 20 persen per hari, jangan melompat."
    elif r["cpa"] <= sisa * 1.5:
        r["putusan"], r["alasan"] = "UBAH SATU HAL LALU TES LAGI", f"biaya per pembelian {rp(r['cpa'])} sedikit di atas batas impas {rp(sisa)}. Ubah satu hal saja (sudut iklan, gambar, atau harga), tes ulang dengan modal sama."
    else:
        r["putusan"], r["alasan"] = "HENTIKAN ATAU RUBAH BESAR", f"biaya per pembelian {rp(r['cpa'])} jauh di atas batas impas {rp(sisa)}. Ganti produk, harga, atau penawaran, bukan hanya iklan."
    return r


def cetak_hasil(r):
    print("HASIL TES IKLAN")
    print(f"- Biaya iklan: {rp(r['biaya'])} | klik: {r['klik']} | pembelian: {r['pembelian']}")
    if r["cpc"] is not None:
        print(f"- Biaya per klik: {rp(r['cpc'])} | pembeli dari pengunjung: {r['konversi_persen']:.1f} persen")
    print(f"- Biaya iklan per pembelian: {rp(r['cpa']) if r['cpa'] is not None else 'belum ada pembelian'} (batas impas {rp(r['sisa_per_penjualan'])})")
    print(f"- Uang masuk: {rp(r['uang_masuk'])} | hasil bersih setelah biaya iklan: {rp(r['hasil_bersih'])}")
    if r["roas"] is not None:
        print(f"- ROAS: {r['roas']:.2f}")
    print(f"\nSARAN: {r['putusan']}. {r['alasan']}")
    if 0 < r["pembelian"] < 5:
        print(f"Catatan: baru {r['pembelian']} pembelian, contohnya masih kecil. Satu pembelian lebih atau kurang bisa mengubah saran.")
    print("Ini hitungan dari angka tes yang kamu berikan, bukan ramalan. Tes tiga hari bisa menyimpang, jadi ulangi sebelum memutuskan besar.")


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Kalkulator tes iklan")
    ap.add_argument("--harga", type=float, required=True)
    ap.add_argument("--biaya-alat", type=float, default=0.0)
    ap.add_argument("--potongan", type=float, default=0.0)
    ap.add_argument("--cpc", type=float)
    ap.add_argument("--konversi", type=float)
    ap.add_argument("--anggaran-tes", type=float, default=150000.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--biaya-tes", type=float)
    ap.add_argument("--klik", type=int)
    ap.add_argument("--pembelian", type=int)
    a = ap.parse_args()
    if a.biaya_tes is not None:
        if a.klik is None or a.pembelian is None:
            sys.exit("GAGAL: untuk membaca hasil tes isi --biaya-tes, --klik, dan --pembelian")
        try:
            r = baca_hasil(a.harga, a.biaya_alat, a.potongan, a.biaya_tes, a.klik, a.pembelian)
        except ValueError as e:
            sys.exit("GAGAL: " + str(e))
        print(json.dumps(r, ensure_ascii=False, indent=1)) if a.json else cetak_hasil(r)
        return
    try:
        h = hitung(a.harga, a.biaya_alat, a.potongan, a.cpc, a.konversi, a.anggaran_tes)
    except ValueError as e:
        sys.exit("GAGAL: " + str(e))
    if a.json:
        print(json.dumps(h, ensure_ascii=False, indent=1))
    else:
        cetak(h)


if __name__ == "__main__":
    main()
