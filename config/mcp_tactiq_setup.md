# Panduan Konfigurasi & Integrasi Tactiq MCP Server untuk Studi S2

Dokumen ini menjelaskan cara menghubungkan **Tactiq** dengan **Gemini / Antigravity CLI** (dan klien MCP lainnya) menggunakan protokol **Model Context Protocol (MCP)**.

---

## 1. Apa itu Tactiq MCP?
Tactiq merekam dan mentranskripsi sesi perkuliahan daring (Google Meet, Zoom, MS Teams). Dengan mengaktifkan server MCP Tactiq:
- AI dapat langsung membaca daftar rekaman pertemuan Anda (`list_meetings`).
- AI dapat membaca transkrip penuh beserta stempel waktu dan pembicara (`get_meeting_transcript`).
- AI dapat mencari materi tertentu berdasarkan kata kunci (`search_meetings`).

---

## 2. Langkah Menghubungkan Akun Tactiq ke MCP

### Langkah A: Dapatkan Akses MCP dari Tactiq
1. Buka [app.tactiq.io/mcp](https://app.tactiq.io/mcp) di browser Anda.
2. Pastikan Anda sudah login ke akun Tactiq yang terpasang di Google Chrome / browser Anda.
3. Di halaman **MCP Integrations**, Anda akan melihat URL server MCP:
   - Endpoint resmi: `https://mcp.tactiq.io`
4. Tactiq menggunakan **Browser-based OAuth**, sehingga Anda **tidak memerlukan API Key statis**. Saat pertama kali diakses, browser akan otomatis membuka prompt persetujuan login.

### Langkah B: File Konfigurasi MCP Workspace
File [mcp_config.json](../mcp_config.json) dan [.gemini/settings.json](../.gemini/settings.json) di direktori ini sudah disetel menggunakan bridge `mcp-remote`:

```json
{
  "$schema": "https://json.schemastore.org/mcp-config.json",
  "mcpServers": {
    "tactiq": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.tactiq.io"],
      "description": "Tactiq MCP Server for fetching meeting notes and lecture transcripts"
    }
  }
}
```

---

## 3. Perintah Prompt AI yang Berguna untuk Kuliah S2

Setelah terhubung, Anda cukup memberikan prompt langsung ke AI:

### A. Merangkum Kuliah Terakhir
> *"AI, ambil transkrip kuliah terbaru dari Tactiq untuk mata kuliah Metodologi Penelitian. Buat ringkasan akademik menggunakan template S2 di `templates/template_catatan_kuliah_s2.md` dan simpan ke `mata_kuliah/metodologi_penelitian/pertemuan_01.md`."*

### B. Melacak Catatan Bimbingan Tesis
> *"AI, periksa sesi meeting Tactiq dengan Dosen Pembimbing hari ini. Ekstrak poin revisi bab 2 dan masukkan ke file `bimbingan_tesis/log_bimbingan.md`."*

### C. Mencari Konsep Lintas Kuliah
> *"AI, cari di seluruh rekaman Tactiq semester ini penjelasan dosen tentang 'Endogenitas dalam Model Ekonometrika' dan jelaskan solusi yang disarankan dosen."*
