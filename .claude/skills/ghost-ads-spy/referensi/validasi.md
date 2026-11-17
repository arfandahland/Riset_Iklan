# Tahap 3: validasi ide

Dipakai saat pengguna menulis "Validasi ide: ..." atau memberi ide mentah. Tujuannya menjawab satu pertanyaan: layakkah ide ini dicoba dengan modal kecil?

## Menemukan idenya

- Kalau nama ide cocok dengan ide di papan (jalankan `python3 scripts/buat_papan.py lihat` untuk daftar id), validasi ide itu dan tulis hasilnya ke id tersebut.
- Kalau ide mentah belum ada di papan, buat dulu satu riset kecil berisi ide itu (id riset baru, judul "Ide dari kamu: ..."), isi kalimat formula dan tiga nilainya, lalu validasi.

## Empat pengecekan

1. **Iklan pesaing, lebih dalam.** Cari di Ads Library Indonesia dan minimal satu negara lain dengan 3 sampai 5 frasa yang spesifik ke ide ini. Berapa pengiklan, berapa lama, sudut iklan apa yang dipakai. Ambil lewat `scripts/ambil_iklan.py` seperti di `cara-riset.md`, dan pakai `--halaman` untuk pesaing terpenting.
2. **Pesaing berbentuk aplikasi atau AI.** Cari aplikasi, situs, atau GPT yang menyelesaikan masalah yang sama, termasuk iklan yang mengarah ke aplikasi. Catat harganya dan modelnya (gratis, langganan, sekali bayar).
3. **Alternatif gratis.** Apa yang bisa dipakai pembeli tanpa membayar (ChatGPT, Canva gratis, template gratis, video YouTube)? Lalu jawab jujur: kenapa orang tetap mau membayar produk ini? Kalau jawabannya lemah, itu alasan untuk TAHAN atau PERLU BUKTI.
4. **Hitungan harga.** Tulis hitungan sederhana:
   - harga jual yang disarankan, dibanding harga pesaing;
   - perkiraan biaya iklan per pembelian. Kalau pengguna punya angka sendiri, pakai itu. Kalau tidak, pakai rentang perkiraan dan tulis jelas bahwa ini perkiraan, bukan data;
   - sisa per penjualan setelah biaya iklan dan biaya alat;
   - berapa penjualan untuk balik modal tes kecil.
   Jangan menjanjikan penghasilan. Tulis sebagai hitungan, bukan ramalan.

Kalau pengecekan ini menemukan bukti yang lebih baru atau lebih kuat dari yang ada di papan (iklan lebih tua, pesaing baru yang penting), perbaiki juga pembanding ide itu dan kalimat `ringkas` risetnya lewat `buat_papan.py tambah --timpa`, supaya papan tidak memuat dua angka yang berbeda. Pesaing baru yang penting masuk ke `pembanding` ide, lengkap dengan umur dan status.

Tentang hitungan harga: tanya dulu apakah pengguna punya angka biaya iklan per pembelian sendiri. Kalau tidak ada, pakai rentang perkiraan, tulis jelas bahwa itu perkiraan, dan katakan bahwa vonis bisa berubah kalau angka aslinya berbeda. "Biaya alat" adalah biaya untuk menjalankan produknya per pembeli (misalnya biaya AI atau langganan alat), isi nol kalau tidak ada.

Kalau kasusnya di tengah antara dua vonis, pilih yang lebih hati-hati dan sebutkan satu hal yang akan mengubahnya.

## Vonis

- **LANJUT TES KECIL:** ada bukti orang membayar untuk masalah ini, ada alasan kuat membayar dibanding gratisan, dan hitungan harga masih menyisakan untung.
- **PERLU BUKTI:** ada satu hal penting yang belum terjawab. Sebutkan hal itu dan cara mengeceknya.
- **TAHAN:** tidak ada bukti orang membayar, gratisannya sudah cukup, atau hitungannya rugi.

Vonis adalah saran. Tulis alasan dalam satu atau dua kalimat yang bisa dipahami orang awam.

Untuk LANJUT TES KECIL, tulis langkah tes yang kecil dan konkret, misalnya: buat halaman jualan sederhana, pasang 2 sampai 3 iklan dengan anggaran kecil selama 3 hari, lihat apakah ada yang membeli. Untuk PERLU BUKTI, tulis apa yang harus dicari. Untuk TAHAN, tulis apa yang harus berubah supaya ide ini layak dilihat lagi.

## Menulis ke papan

Bentuk data ada di `bentuk-data.md` bagian validasi. Setelah ditulis, jalankan `python3 scripts/buat_papan.py tambah <file>` lalu tampilkan papan terbaru. Di chat cukup tulis vonis, alasan satu kalimat, ajakan membuka idenya di papan, dan paling banyak 3 butir pendek tentang yang belum bisa dicek. `tautan` di validasi boleh berisi halaman pesaing dan tautan iklan, paling banyak 12.

