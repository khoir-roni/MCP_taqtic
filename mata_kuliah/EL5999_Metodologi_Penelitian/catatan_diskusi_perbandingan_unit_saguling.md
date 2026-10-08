# Catatan Diskusi Metodologi Penelitian (EL5999)
## Topik: Metodologi Perbandingan Unit (*Unit Comparison*) Pasca-Retrofit PLC & Fiber Optik PLTA Saguling

- **Mata Kuliah**: EL5999 Metodologi Penelitian dan Literasi Digital (STEI ITB)
- **Hari/Tanggal**: Kamis, 08 Oktober 2026
- **Dosen Pengampu / Narasumber**: Dr. Fathin Saifur Rahman, S.T., M.T. (STEI ITB)
- **Mahasiswa Penanya**: Muhammad Ali Khoironi (Praktisi PLTA Saguling / Mahasiswa S2 Teknik Elektro ITB)

---

## 1. Resume Masalah & Dilema Teknis (Ali Khoironi)
- **Studi Kasus**: PLTA Saguling memiliki 4 unit pembangkit. **Unit 2 telah diretrofit** dengan sistem komunikasi **fiber optik** dan sistem kontrol **PLC tersendiri** untuk mengoptimalkan respons *Automatic Generation Control* (AGC).
- **Keterbatasan Data (*Data Gap*)**: Data historis Unit 2 sebelum retrofit (terutama telemetri resolusi tinggi 100 point sinyal AGC) tidak sempat terekam komprehensif di database lama (*data sudah lewat*).
- **Dilema**: 
  - Jika Unit 2 dibandingkan dengan unit lain (Unit 1, 3, atau 4), kondisi fisik operasional tidak 100% identik (misal: friksi mekanik governor, riwayat keausan turbin).
  - Ali menanyakan: *"Apakah cukup membandingkan prosesnya saja, atau boleh membandingkan dengan unit lain, dan bagaimana metodologi yang tepat?"*

---

## 2. Kesampaian & Arahan Metodologis dari Dosen

Dosen menegaskan bahwa **ketiadaan data historis empiris Unit 2 bukan hambatan penelitian**, asalkan peneliti membangun strategi komparasi ilmiah yang defensif:

### A. Alternatif 1: Pendekatan Pemodelan & Simulasi Sistem (*Simulation-Based Counterfactual*)
> *"Kita coba modelkan apa di simulasi gitu ya? Nah, kemudian kita bisa bandingkan peningkatan performa sistemnya seperti apa. Tujuan akhirnya bisa saja: kalau dengan fiber optik jadinya seperti ini, dengan yang lama seperti ini..."*

* **Aplikasi**: Bangun model dinamik governor-turbin dan jaringan komunikasi di MATLAB/Simulink.
* **Isolasi Variabel**: 
  - Skenario 1 (Lama): Parameter delay transmisi kabel tembaga/serial konvensional ($T_d = 100-300\text{ ms}$).
  - Skenario 2 (Baru): Parameter propagasi fiber optik & scan rate PLC modern ($T_d < 5\text{ ms}$).
* Efek peningkatan performa murni akibat retrofit dapat dievaluasi secara objektif tanpa terdistorsi variasi mekanik unit lain.

### B. Alternatif 2: Uji Ekuivalensi Karakteristik Antar-Unit (*Equivalent Baseline Pairing*)
> *"Kalau unitnya sama mereknya, kapasitasnya sama... misalkan ada suatu gangguan apa gitu ya, di-setting-nya sama, kemudian responnya sama. Berarti kalau seperti itu, bisa kita asumsikan kedua unit ini hampir identik, jadi bisa dibandingkan..."*

* Peneliti **boleh menggunakan unit lain sebagai unit pembanding (kontrol)** dengan syarat membuktikan ekuivalensi dasar:
  1. Ambil rekaman operasional saat kedua unit mengalami gangguan/event deviasi frekuensi yang sama.
  2. Tunjukkan secara statistik/grafis bahwa respons dasar kedua unit sebelum intervensi kontrol berada dalam toleransi ekuivalen.
  3. Setelah terbukti, unit lain sah dijadikan proksi pembanding.

### C. Alternatif 3: Kaidah Asumsi yang Dapat Dipertanggungjawabkan
> *"Penelitian bisa banyak asumsi, tapi asumsinya itu harus bisa dipertanggungjawabkan dengan data pendukung."*

* Nyatakan secara eksplisit seluruh batasan asumsi di Bab Metodologi. Sertakan data pendukung (misal: lembar *commissioning test*, kurva *droop*, atau riwayat *preventive maintenance* yang membuktikan kemiripan spesifikasi dasar).

### D. Alternatif 4: Batasan Merek, Unit, dan Kerahasiaan Industri
> *"Merek atau nama unit... terserah Bapak/Ibu saja, itu dibebaskan. Kalau memang ada data konfidensial, bisa disamarkan... Kita lebih fokus ke format penulisan yang tepat dan cara presentasinya."*

* **Anonimisasi**: Aman menyamarkan identitas PLTA Saguling atau vendor PLC jika terikat aturan konfidensial PLN/PLN Indonesia Power. Cukup sebut: *"a 700 MW (4 x 175 MW) Hydroelectric Power Plant"* atau *"Unit A & Unit B"*.

---

## 3. Matriks Tindak Lanjut untuk Tesis & Paper Ali Khoironi

| Masalah | Solusi Dosen | Rekomendasi Tindakan |
| :--- | :--- | :--- |
| Data masa lalu Unit 2 tidak lengkap | Simulasi Sistem / Model Counterfactual | Buat blok model transfer function komunikasi lama vs fiber optik di Simulink. |
| Variasi fisik antar-unit | Uji Baseline Transien | Bandingkan grafik respon kedua unit saat kondisi beban seimbang untuk membuktikan asumsi identik. |
| Penggunaan data 100 poin AGC | Kalibrasi Model dengan Data Real | Gunakan data real-time Unit 2 pasca-retrofit untuk memvalidasi model simulasi. |
| Rahasia perusahaan / PLN | Anonimisasi Merek & Lokasi | Gunakan kode generik (*Unit Under Study* vs *Baseline Unit*). |
