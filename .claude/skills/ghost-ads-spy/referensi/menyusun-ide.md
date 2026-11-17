# Tahap 2: menyusun ide

Susun 8 sampai 12 ide dari bukti Tahap 1. Kalau buktinya tipis, lebih baik 6 ide yang jujur daripada 12 yang dipaksakan, dan katakan itu ke pengguna.

## Dari bukti ke ide

Ide yang baik bukan salinan produk pesaing. Ambil yang terbukti (masalahnya, pembelinya, sudut iklannya), lalu buat lebih malas, lebih cepat, atau lebih langsung terpakai.

- Pesaing menjual ebook panduan 80 halaman. Idemu: alat yang langsung menghasilkan barang jadinya.
- Pesaing menjual 500 template. Idemu: pembuat yang cukup diisi nama dan keluar satu hasil yang pas.
- Pesaing di luar negeri laku, di Indonesia belum ada. Idemu: versi Indonesia dengan harga dan contoh lokal.

Bentuk produk yang dipertimbangkan: aplikasi web sederhana, alat atau generator, template, kit, ebook, kelas singkat, layanan langganan, produk personal (hasil dibuat atas nama pembeli), jasa dengan bantuan AI, atau gabungan. Gabungan diutamakan kalau lebih kuat, misalnya alat ditambah template.

Setiap ide harus menghasilkan barang jadi di tangan pembeli. Kuis yang berujung nasihat bukan produk.

Untuk ide yang membantu pembeli berjualan, tulis apa yang didapat ("langsung bisa dipasang di status WhatsApp"), bukan janji uang ("langsung dapat pembeli"). Jangan menulis angka penghasilan.

## Kalimat formula

Tulis tiap ide sebagai: "Isi X, dapat Y dalam Z menit, langsung bisa W."

- X: yang dimasukkan pembeli, sesedikit mungkin.
- Y: barang jadinya.
- Z: perkiraan waktu sampai hasil pertama. Ini target rancangan, tulis begitu di `catatan_baca`. Kalau hasilnya memang butuh hari atau minggu, tulis jujur ("dalam 7 hari") dan beri nilai `instant` yang rendah. Jangan memaksa semua ide jadi "3 menit".
- W: yang langsung bisa dilakukan dengan hasilnya (dicetak, dikirim, diposting, dijual).

## Memberi nilai (Formula Kurasi Ghost)

Bilangan bulat 0 sampai 10. Nilai dari bukti dan dari bentuk produknya, bukan dari rasa suka. Tiga nilai ini hanya ditulis di file data. Pengguna hanya melihat jumlahnya sebagai Skor Ghost, jadi jangan menyebut nama atau rincian tiga nilai ini di chat atau di teks ide (`bentuk`, `ragu`, `saran`, `ringkas`).

**`malas`: seberapa sedikit pembeli harus berpikir dan bekerja**
- 9 sampai 10: isi satu kolom atau unggah satu foto, selesai.
- 7 sampai 8: isi beberapa kolom, pilih beberapa pilihan.
- 4 sampai 6: pembeli masih harus menyusun, mengedit, atau belajar dulu.
- 0 sampai 3: pembeli mengerjakan hampir semuanya sendiri (kursus panjang, panduan tebal).

**`instant`: seberapa cepat hasil pertama muncul**
- 9 sampai 10: hasil pertama di bawah 5 menit.
- 7 sampai 8: di hari yang sama.
- 4 sampai 6: beberapa hari.
- 0 sampai 3: berminggu-minggu atau tidak jelas kapan.

**`applicable`: seberapa langsung hasilnya terpakai**
- 9 sampai 10: hasilnya langsung dipakai atau dijual hari itu tanpa diolah lagi.
- 7 sampai 8: perlu sedikit penyesuaian.
- 4 sampai 6: berguna tapi masih harus diolah atau digabung dengan hal lain.
- 0 sampai 3: baru berupa pengetahuan.

Jangan memberi semua ide nilai tinggi. Kalau semua 27 ke atas, penilaianmu terlalu longgar.

## Isi tiap ide

- Nama ide (2 sampai 4 kata, menggambarkan hasil) dan target pembeli yang spesifik.
- Kalimat formula.
- Tiga nilai. Jumlahnya (Skor Ghost) dihitung skrip.
- Pembanding: penawaran nyata yang menjadi dasar ide, dengan umur iklan, status, harga, tautan halaman jualan, dan tautan iklan. Kalau tidak ada, kosongkan dan jelaskan di `ragu` bahwa ini ide baru tanpa bukti langsung.
- Bentuk produk terbaik dan alasan singkat.
- Pilihan bentuk: 2 sampai 4 pilihan wujud produk, dan tandai yang paling disarankan. Kalau pilihan yang masuk akal hanya satu, tulis satu.
- Produk tambahan yang bisa ditawarkan saat checkout (satu kalimat).
- Yang masih ragu: hal yang belum dicek, risiko, atau alasan ide ini bisa gagal. Wajib diisi dengan jujur.
- Saran langkah: satu kalimat, misalnya "Validasi dulu, pesaingnya banyak" atau "Layak dicoba kecil, bukti iklannya kuat".

## Paling disarankan: ditentukan skrip, hanya untuk iklan yang terbukti lama

Kelompok "Paling disarankan" di papan tidak kamu pilih sendiri. Skrip yang memilih, paling banyak 3 produk, dengan aturan tetap:

- Hanya produk yang punya pembanding berstatus WINNING (iklan 30 hari atau lebih). Produk yang buktinya masih BARU atau POTENSIAL tidak pernah masuk, setinggi apa pun Skor Ghost-nya.
- Produk yang iklan pesaingnya sudah tayang 90 hari atau lebih didahulukan. Sesudah itu Skor Ghost tertinggi, lalu bukti yang lengkap, lalu umur iklan.
- Kalau tidak ada satu pun produk berbukti WINNING, kelompok ini kosong dan papan menulisnya terus terang. Jangan dipaksakan.

Judul besar papan juga disusun skrip dari produk nomor 1 kelompok ini, jadi judul dan daftar selalu menyebut produk yang sama. Sesudah `buat_papan.py tambah`, skrip mencetak urutan "Paling disarankan". Pakai urutan dan nama itu di chat. Jangan menyebut produk lain sebagai yang terkuat.

**Bukti produk yang disarankan harus lengkap.** Untuk tiap produk yang punya pembanding WINNING, usahakan minimal satu pembanding WINNING punya tiga hal: tautan iklan, landing page yang benar-benar terbuka lewat `buka_lp.py`, dan harga yang terbaca dari halaman itu. Kalau halaman satu pesaing menolak dibuka, cari pesaing WINNING lain untuk masalah yang sama (pakai `--halaman` atau frasa lain) dan masukkan yang lengkap sebagai pembanding. Pembanding yang tidak lengkap tetap boleh dicantumkan sesudahnya. Kalau skrip mencetak "BUKTI BELUM LENGKAP" untuk sebuah produk, lengkapi dulu lalu jalankan `tambah --timpa`, baru buka papan. Kalau sesudah dicoba tetap tidak ada yang lengkap, biarkan apa adanya dan sebutkan di chat. Jangan mengarang harga atau tautan.

`ringkas` riset tetap wajib diisi sebagai catatan satu kalimat (berapa produk dan temuan utamanya), tetapi tidak dipakai sebagai judul papan. `rekomendasi` tidak perlu ditulis, skrip yang mengisinya.

