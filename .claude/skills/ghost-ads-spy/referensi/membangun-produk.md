# Tahap 5: bangun produk, halaman jualan, dan iklan

Dipakai saat pengguna menulis "Bangun produk: ..." atau memilih produk yang vonisnya LANJUT TES KECIL. Tujuannya satu paket siap pasang: halaman jualan, tiga teks iklan, rencana tes, dan hitungan modal. Semua isi berasal dari bukti di papan, bukan karangan.

## Urutan kerja

1. **Cari ide-nya di papan** (`python3 scripts/buat_papan.py lihat`). Kalau produk belum divalidasi, tawarkan validasi dulu (Tahap 3). Kalau pengguna tetap ingin lanjut, boleh, tetapi katakan satu kalimat bahwa belum divalidasi.
2. **Tanyakan hanya yang tidak boleh ditebak**, dalam satu pesan pendek:
   - tautan pembayaran atau lapak produknya (wajib, harus https). Kalau belum punya, arahkan ke PANDUAN-NGIKLAN.html langkah 2 dan tunggu. Jangan mengisi tautan palsu.
   - harga final, nama penjual atau toko, nomor WhatsApp bantuan (boleh kosong),
   - apakah ada testimoni asli dan garansi yang benar mau diberikan (boleh tidak ada),
   - ID Pixel Meta (boleh menyusul).
3. **Tulis spesifikasi** ke `papan/kerja/spek-<id>.json`. Mulai dari `python3 scripts/buat_lp.py contoh` kalau perlu bentuknya. Aturan isi:
   - `id` huruf kecil dan tanda hubung. Isi `ide` dengan id ide di papan supaya papan bisa menandai tahap "Halaman jualan".
   - `judul`, `subjudul`, `masalah`, `manfaat`, `isi_paket`, `cara_kerja` ditulis dari `formula`, `bentuk`, dan isi halaman pesaing yang sudah dibaca. Pakai kalimat pembeli dari iklan pesaing (kata yang benar-benar dipakai), bukan istilah teknis.
   - Janji waktu atau hasil harus benar-benar bisa dipenuhi produknya. Kalau tidak yakin, tulis lebih kecil.
   - Harga coret hanya kalau harga itu benar akan berlaku, dan isi `dasar_harga_coret`.
   - `iklan`: tiga sudut berbeda, dari pola di riset (hemat waktu, masalah yang tercecer, hasil yang dicari, dan sebagainya). Teks utama paling banyak 125 karakter di baris pertama, judul paling banyak 40, deskripsi paling banyak 30. Tiap iklan harus bisa dibuktikan oleh halaman jualan.
   - `target_iklan`: negara, umur, minat, anggaran harian, lama tes. Titik awal saja, katakan itu perkiraan.
   - Dilarang (skrip menolak): janji hasil atau penghasilan pasti, hitung mundur atau sisa kuota palsu, sebelum dan sesudah, menyebut kondisi pribadi pembaca, klaim penyembuhan, testimoni tanpa `"asli": true`.
4. **Rakit**: `python3 scripts/buat_lp.py rakit papan/kerja/spek-<id>.json`. Kalau ditolak, perbaiki isinya, jangan akali aturannya. Baca baris PERHATIAN dan sampaikan yang penting.
5. **Hitung modal tes**: `python3 scripts/hitung.py --harga <angka> --potongan <persen lapak> --anggaran-tes <angka>`. Tanyakan potongan lapak dan biaya alat. Kalau pengguna belum punya angka biaya per klik dan persen pembeli, pakai rentang perkiraan dan katakan itu perkiraan. Sampaikan terus terang kalau skenario tengah rugi.
6. **Kirim hasilnya** (sesi cloud): `SendUserFile` untuk `papan/produk/<id>/index.html` (display render) dan `papan/produk/<id>/iklan.md` (attach). Di komputer sendiri cukup sebut lokasinya.
7. **Simpan**: `python3 scripts/buat_papan.py mulai` (supaya papan menandai tahap), lalu `python3 scripts/simpan.py` di sesi cloud.
8. **Pandu langkah berikutnya**: arahkan ke `PANDUAN-NGIKLAN.html` mulai langkah 4 (pasang halaman). Tawarkan menemani langkah demi langkah, satu langkah per pesan, kalau pengguna baru.

## Setelah itu

- **"Pasang Pixel <angka>"**: ubah `pixel_id` di spesifikasi, rakit ulang, kirim ulang, simpan.
- **"Baca hasil tes iklan: ..."**: jalankan `python3 scripts/hitung.py --harga ... --biaya-tes ... --klik ... --pembelian ...` dan jelaskan sarannya dengan bahasa biasa. Satu perubahan saja per tes berikutnya.
- **Testimoni baru dari pembeli sungguhan**: tambahkan dengan `"asli": true`, rakit ulang.

## Yang tidak dilakukan

- Tidak mengarang testimoni, jumlah pembeli, ulasan, atau angka hasil.
- Tidak menjanjikan penghasilan, di halaman, iklan, maupun chat.
- Tidak membuat akun, memasang iklan, atau menarik pembayaran atas nama pengguna. Pengguna yang menekan Publikasikan dan menanggung biayanya.
- Tidak menyuruh membuat banyak akun untuk menghindari penolakan iklan.
