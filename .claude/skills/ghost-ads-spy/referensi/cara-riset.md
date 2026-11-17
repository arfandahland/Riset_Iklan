# Tahap 1: mengumpulkan bukti

Tujuan tahap ini: menemukan apa yang sudah terbukti dibayar orang, bukan apa yang terdengar bagus. Bukti terkuat adalah iklan yang sudah lama tayang, karena orang jarang membayar iklan berbulan-bulan kalau tidak balik modal.

## 1. Pilih frasa pencarian

Siapkan minimal 5 frasa. Pakai bahasa pembeli, bukan nama kategori.

- Kurang bagus: "produk digital", "parenting", "bisnis online".
- Bagus: "anak susah makan", "gaji numpang lewat", "tanpa resign", "modal HP", "jualan dari rumah".

Campur tiga jenis: keluhan ("capek ngurus"), keinginan ("penghasilan tambahan"), dan bentuk produk ("template", "worksheet", "kelas online", "aplikasi").

Untuk negara lain, terjemahkan frasanya ke bahasa negara itu. Pilih minimal satu: Amerika (US), Malaysia (MY), Filipina (PH), India (IN), atau Brasil (BR). Minimal 3 frasa untuk negara lain itu.

## 2. Ambil iklan dari Facebook Ads Library

Kamu yang mengambilnya, lewat skrip. Skrip membuka Ads Library dengan browser tanpa tampilan, tanpa login, lalu membaca tiap kartu iklan. Pengguna tidak membuka apa pun.

Jalankan dari folder utama, satu perintah per negara, semua frasa sekaligus:

`python3 scripts/ambil_iklan.py --negara ID --frasa "anak susah makan" --frasa "worksheet anak" --frasa "modal HP" --frasa "tanpa resign" --frasa "template menu" --keluar papan/kerja/iklan-id.json`

`python3 scripts/ambil_iklan.py --negara US --frasa "printable worksheets" --frasa "picky eater" --frasa "side hustle template" --keluar papan/kerja/iklan-us.json`

Untuk beberapa negara dengan frasa yang sama sekaligus: `python3 scripts/ambil_iklan.py --negara US,MY,PH --frasa "printable worksheets" --keluar papan/kerja/iklan-{negara}.json` (satu file per negara). Pemilihan negara per niche ada di `negara-per-niche.md`.

Tiap frasa butuh sekitar 15 sampai 20 detik. Hasil sudah urut dari tayangan terbanyak. Untuk tiap frasa skrip mencetak:

- berapa hasil menurut Facebook dan berapa kartu yang terbaca;
- daftar pengiklan: jumlah iklan terlihat, tanggal mulai iklan tertua, umur dalam hari sampai hari ini, status, tautan iklan tertua, dan tautan tujuan tombol iklan;
- potongan teks tiap iklan. Teks lengkap ada di file JSON hasil.

Pilihan lain yang berguna:

- `--halaman <ID halaman>`: semua iklan aktif satu pengiklan. Pakai untuk pengiklan penting supaya jumlah iklan dan iklan tertuanya lebih pasti. ID halaman adalah angka di `halaman_pengiklan` pada file JSON.
- `--id <Library ID>`: satu iklan saja.
- `--bebas`: kata tidak harus berurutan persis. Pakai kalau frasa persis tidak memberi hasil.
- `--gulir 8`: menggulir lebih jauh. Bawaan 4 kali, dan biarkan 4 untuk pencarian frasa supaya jumlah kartu antar pencarian bisa dibandingkan.

Catatan membaca hasil:

- Umur satu pengiklan memakai iklan tertua yang terlihat. Tulis itu di `catatan` pembanding.
- Jumlah iklan ditulis "N iklan terlihat", bukan "N iklan aktif", karena tidak semua kartu termuat. Label "N ads use this creative and text" sudah ikut dihitung skrip.
- Tautan tujuan sudah dibersihkan dari bungkus `l.facebook.com`. Tujuan berupa Instagram, WhatsApp, atau halaman dalam Facebook tidak punya halaman jualan, catat apa adanya.
- Frasa yang terlalu umum ("ibu rumah tangga", "uang belanja") kebanyakan memunculkan barang fisik dan aplikasi besar. Tambahkan kata bentuk produk ("worksheet anak", "ebook resep", "template menu") atau ganti dengan frasa yang lebih sempit, lalu jalankan lagi.
- Satu frasa yang kosong itu wajar, ganti frasanya. Kalau SEMUA frasa tidak terbaca, ulangi sekali. Kalau tetap, ikuti bagian "Kalau browser tidak bisa jalan" di `SKILL.md`.

Kalau skrip menjawab `BELUM SIAP`, jalankan `python3 scripts/siapkan.py` lalu ulangi. Jangan mengganti langkah ini dengan pencarian web, dan jangan memberi pengguna tautan Ads Library untuk dibuka sendiri.

## 3. Beri status iklan

- **WINNING:** aktif 30 hari atau lebih.
- **POTENSIAL:** aktif 14 sampai 29 hari, atau pengiklan punya 10 iklan aktif atau lebih untuk produk itu.
- **BARU:** aktif di bawah 14 hari. Penawaran baru yang jumlah iklannya banyak justru sinyal segar, jangan dibuang.

Status hanya diberikan kalau umur iklan benar-benar terbaca. Umur menang atas jumlah: 30 hari atau lebih selalu WINNING. Di bawah 30 hari dengan 10 iklan terlihat atau lebih adalah POTENSIAL, walau umurnya di bawah 14 hari. Skrip menolak status yang tidak cocok dengan umurnya.

## 4. Buka halaman jualan penawaran terbaik

Untuk 5 sampai 8 penawaran terkuat, buka halaman tujuannya lewat skrip:

`python3 scripts/buka_lp.py --keluar papan/kerja/lp.json "https://alamat-satu" "https://alamat-dua"`

Skrip mencetak judul, alamat akhir, semua angka harga yang tertulis di halaman, dan isi teksnya. Catat harga (dan harga coret kalau ada), isi produk, dan bentuknya (ebook, template, kelas, aplikasi, langganan). Jangan menyimpulkan isi produk dari teks iklan saja, karena sering berbeda. Daftar harga dari skrip adalah semua angka di halaman: baca isinya untuk tahu mana harga jual dan mana harga coret.

Kalau skrip menjawab `BELUM TERBUKA` (beberapa situs seperti lynk.id sering menolak pembuka otomatis), tautannya tetap boleh dicantumkan dengan label "Halaman jualan (belum terbuka)", dan tulis "halaman jualan belum dibuka" di `catatan` pembanding. Harga yang hanya terbaca dari teks iklan ditulis "Rp 27.000 menurut tulisan di iklan". Harga luar negeri ditulis dalam mata uang aslinya. Jangan meminta pengguna membukanya.

Tidak semua pembanding harus dibuka halamannya. Yang wajib diusahakan: tiap produk yang punya pembanding WINNING memiliki minimal satu pembanding WINNING dengan landing page terbuka dan harga terbaca, karena produk itulah yang masuk kelompok "Paling disarankan". Kalau halaman pesaing WINNING itu menolak dibuka, cari pesaing WINNING lain yang halamannya terbuka.

## 5. Sumber di luar Meta

Cari minimal dua dari ini lewat pencarian web atau `scripts/buka_lp.py`, lalu catat sebagai sinyal:

- etalase produk digital: Gumroad, Etsy, Product Hunt, Lynk.id, Mayar. Lihat yang ulasannya banyak.
- keluhan dan pertanyaan di komunitas: grup Facebook, Reddit, Quora, kolom komentar TikTok atau YouTube. Cari kalimat keluhan asli.
- tren: kata kunci yang naik, berita, perubahan aturan atau musim (tahun ajaran baru, Ramadan, akhir tahun).

## 6. Dua cara menemukan ide yang jarang dipikirkan

- **Pindah pola:** bentuk produk yang laku di satu bidang, dipindah ke bidang lain. Contoh: pembuat worksheet anak laku, lalu dipindah jadi pembuat soal latihan untuk guru les.
- **Keunikan:** kebutuhan kecil yang spesifik pada target dan belum banyak dijual. Tandai sebagai ide baru kalau belum ada bukti langsung.

## Yang dicatat untuk papan

- `pola`: 3 sampai 5 kalimat tentang pola yang terlihat dari iklan.
- `sinyal`: temuan dari langkah 5 dan 6, satu kalimat per temuan, termasuk yang hasilnya lemah atau kosong.
- `offer_lain`: penawaran yang terlihat tapi tidak jadi ide tersendiri. Jangan disembunyikan.
- `catatan_baca`: sampai tanggal berapa umur iklan dihitung, bahwa harga dan klaim adalah tulisan di halaman pesaing dan belum diverifikasi, dan apa saja yang tidak bisa dicek.
- `sumber`: tautan sumber di luar Meta yang benar-benar kamu buka.

