# Bentuk data papan

Papan dirakit dari satu file JSON yang kamu tulis, lalu dimasukkan dengan `python3 scripts/buat_papan.py tambah <file>`. Skrip memeriksa isinya. Kalau ditolak, baca pesannya dan perbaiki datanya.

Semua teks bahasa Indonesia sehari-hari, tanpa tanda pisah panjang. Semua tautan diawali `https://` dan harus tautan yang benar-benar kamu temukan.

## Riset baru dengan ide

```json
{
  "riset": {
    "id": "2026-11-12-toko-online",
    "judul": "Niche pemilik toko online",
    "tanggal": "2026-11-12",
    "input": "kalimat permintaan pengguna apa adanya",
    "ringkas": "Catatan satu kalimat: berapa produk dan temuan utamanya. Judul papan disusun skrip.",
    "cara_cek": "Browser: Ads Library Indonesia 6 frasa, Amerika 3 frasa.",
    "pola": ["3 sampai 5 kalimat pola dari iklan"],
    "sinyal": ["temuan di luar Meta, satu kalimat per temuan"],
    "catatan_baca": ["Umur iklan dihitung sampai 12 November 2026.", "Harga adalah tulisan di halaman pesaing, belum diverifikasi."],
    "offer_lain": [
      { "nama": "Nama penawaran", "status": "WINNING", "isi": "Apa yang dijual, harga, umur iklan.", "iklan": "https://www.facebook.com/ads/library/?id=123" }
    ],
    "sumber": ["https://..."]
  },
  "ide": [
    {
      "id": "2026-11-12-toko-online-laporan-toko",
      "riset": "2026-11-12-toko-online",
      "nama": "Pembuat Laporan Toko",
      "target": "pemilik toko online yang mencatat penjualan sendiri",
      "formula": "Isi X, dapat Y dalam Z menit, langsung bisa W.",
      "malas": 9,
      "instant": 9,
      "applicable": 8,
      "pembanding": [
        {
          "nama": "Nama penawaran pesaing",
          "id_lokal": true,
          "isi": "Apa yang dijual dan sudut iklannya. Berapa iklan aktif.",
          "hari": 140,
          "status": "WINNING",
          "harga": "Rp 79.000 sekali bayar, harga coret Rp 299.000",
          "harga_pendek": "Rp 79.000",
          "lp": [{ "label": "Buka halaman jualannya", "url": "https://..." }],
          "iklan": ["https://www.facebook.com/ads/library/?id=123"],
          "catatan": "opsional"
        }
      ],
      "bentuk": "Bentuk produk terbaik dan alasan singkat.",
      "opsi": [
        { "nama": "Pilihan 1", "isi": "Penjelasan singkat" },
        { "nama": "Pilihan 2", "isi": "Penjelasan singkat" }
      ],
      "opsi_rekom": [0],
      "opsi_catatan": "opsional",
      "tambahan": "Produk tambahan yang bisa ditawarkan saat checkout.",
      "ragu": "Yang belum dicek atau bisa membuat ide ini gagal.",
      "saran": "Satu kalimat saran langkah."
    }
  ]
}
```

Aturan:

- `id` riset: tanggal ditambah topik, huruf kecil dan tanda hubung. `id` ide: id riset ditambah nama pendek ide. Riset baru selalu memakai id baru. Riset lama tidak ditimpa.
- `malas`, `instant`, `applicable`: bilangan bulat 0 sampai 10 (Formula Kurasi Ghost). `total` (Skor Ghost) dan `no` dihitung skrip, tidak perlu ditulis. Papan hanya menampilkan Skor Ghost, bukan tiga nilainya, jadi jangan menulis nama tiga nilai itu di teks mana pun.
- `hari`: umur iklan dalam hari, bilangan bulat. Isi `null` kalau umur iklan belum dicek, dan jangan beri `status`.
- `status`: hanya `WINNING`, `POTENSIAL`, atau `BARU`.
- `id_lokal`: `true` untuk penawaran Indonesia, `false` untuk luar negeri.
- `iklan` di pembanding berupa daftar tautan. `iklan` di `offer_lain` berupa satu tautan saja. `status` di `offer_lain` boleh dikosongkan.
- Tautan dengan spasi ditulis dengan `%20`.
- `rekomendasi` tidak perlu ditulis. Skrip yang memilih "Paling disarankan": hanya produk berbukti WINNING, iklan 90 hari atau lebih didahulukan (lihat `menyusun-ide.md`). Isi yang kamu tulis di sana diabaikan.
- Bagian yang tidak ada isinya boleh dihilangkan, kecuali yang wajib: riset (`id`, `judul`, `tanggal`, `input`, `ringkas`) dan ide (`id`, `riset`, `nama`, `target`, `formula`, tiga nilai).

## Hasil validasi

Untuk ide yang sudah ada di papan (lihat id-nya dengan `buat_papan.py lihat`):

```json
{
  "validasi": [
    {
      "id": "2026-11-12-toko-online-laporan-toko",
      "vonis": "LANJUT TES KECIL",
      "alasan": "Satu atau dua kalimat alasan untuk orang awam.",
      "iklan": ["Temuan pengecekan iklan lebih dalam, satu kalimat per butir."],
      "pesaing_app": ["Aplikasi atau AI pesaing, harga, modelnya."],
      "gratisan": ["Alternatif gratis, dan kenapa orang tetap mau bayar."],
      "harga": ["Harga saran dan dasarnya.", "Perkiraan biaya iklan per pembelian (tulis ini perkiraan).", "Sisa per penjualan.", "Jumlah penjualan untuk balik modal tes."],
      "langkah": ["Langkah berikutnya yang kecil dan konkret."],
      "tautan": [{ "label": "Pesaing A", "url": "https://..." }]
    }
  ]
}
```

`vonis` hanya `LANJUT TES KECIL`, `PERLU BUKTI`, atau `TAHAN`. `alasan` wajib. Untuk ide mentah yang belum ada di papan, satu file boleh berisi `riset`, `ide`, dan `validasi` sekaligus.

## Memperbaiki data yang sudah masuk

Tulis ulang riset atau ide itu dengan id yang sama, lalu jalankan `buat_papan.py tambah <file> --timpa`. Pakai hanya untuk memperbaiki, misalnya mengisi umur iklan yang tadinya belum dicek.

