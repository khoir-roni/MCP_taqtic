# Sistem Manajemen Transkrip Kuliah & Bimbingan Tesis S2 (Tactiq + MCP + AI)

Repositori ini adalah ruang kerja terstruktur untuk mengelola transkrip perkuliahan S2, bimbingan tesis daring, dan sintesis catatan akademik dengan memanfaatkan integrasi **Tactiq** melalui **Model Context Protocol (MCP)** dan asisten AI (**Gemini / Antigravity CLI**).

---

## 💡 Apa Fungsi MCP di Sini?

Saat kuliah S2 atau bimbingan tesis secara daring:
1. **Perekaman Otomatis**: **Tactiq** merekam audio Google Meet / Zoom / MS Teams dan mengubahnya menjadi teks transkrip di cloud Tactiq.
2. **Jembatan Terstandar (MCP)**: **MCP Server** (`https://mcp.tactiq.io/mcp`) membuka gerbang aman agar AI Assistant dapat mengakses data perkuliahan tersebut secara langsung.
3. **Analisis Akademik Mendalam**: Anda tidak perlu menyalin ribuan kata manual. AI langsung mengambil teks dari Tactiq, menganalisis teori dan metodologi riset, menyusun rangkuman perkuliahan berstandar S2, serta memetakan daftar revisi dari dosen pembimbing.

---

## 📁 Struktur Direktori

```
transcrip_kuliah/
├── mcp_config.json                 # Konfigurasi koneksi Tactiq MCP Server
├── config/
│   └── mcp_tactiq_setup.md         # Panduan detail autentikasi & aktivasi MCP
├── templates/
│   ├── template_catatan_kuliah_s2.md # Format catatan kuliah akademik komprehensif
│   └── template_bimbingan_tesis.md   # Format log arahan revisi dosen pembimbing
├── mata_kuliah/                    # Folder catatan perkuliahan per mata kuliah
├── bimbingan_tesis/                # Log pertemuan & revisi naskah tesis
├── scripts/
│   └── process_transcript.py       # Skrip pembantu pemrosesan berkas mentah
└── README.md                       # Dokumentasi utama
```

---

## 🚀 Alur Kerja Cepat (Workflow)

### 1. Setelah Kuliah Daring Selesai
1. Pastikan Tactiq telah selesai mentranskripsi pertemuan di browser Anda.
2. Buka terminal Antigravity / Gemini CLI di folder ini:
   ```text
   AI, periksa transkrip kuliah terbaru di Tactiq untuk sesi hari ini.
   Gunakan template di templates/template_catatan_kuliah_s2.md,
   lalu simpan hasilnya ke mata_kuliah/[nama_matkul]/pertemuan_01.md.
   ```

### 2. Setelah Sesi Bimbingan Tesis Daring
1. Jalankan prompt:
   ```text
   AI, ambil sesi meeting terakhir dengan Dosen Pembimbing dari Tactiq.
   Ekstrak seluruh masukan kritis dan poin revisi naskah tesis,
   lalu buat log baru di folder bimbingan_tesis/.
   ```

### 3. Menjelang UTS / UAS / Ujian Komprehensif
1. Lakukan penelusuran lintas pertemuan:
   ```text
   AI, telusuri seluruh catatan kuliah di folder mata_kuliah/ dan Tactiq,
   rangkumkan perbedaan utama antara Paradigma Positivisme vs Konstruktivisme
   yang sempat diperdebatkan dosen pada pertemuan 2 dan 4.
   ```

---

## 🛠️ Konfigurasi Lanjutan
Untuk melihat cara menghubungkan akun Tactiq atau menyetel API token, buka [config/mcp_tactiq_setup.md](config/mcp_tactiq_setup.md).
