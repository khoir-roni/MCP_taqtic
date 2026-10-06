"""
Skrip Pembantu Pengolahan Transkrip Tactiq untuk Mahasiswa S2
Fungsi:
- Membersihkan dan menstandarisasi transkrip mentah dari Tactiq (.txt, .json, .vtt)
- Menghasilkan ringkasan dan struktur markdown siap olah.
"""

import sys
import os
import re
import argparse
from datetime import datetime

def parse_txt_transcript(file_path):
    """Membaca file transkrip teks mentah dari Tactiq."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} tidak ditemukan.")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def create_summary_skeleton(transcript_text, matkul_name, pertemuan_no, dosen_name):
    """Menghasilkan draf dokumen berbasis template S2."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    template = f"""# {matkul_name.upper()}
## Pertemuan {pertemuan_no}: Pembahasan Materi Perkuliahan

- **Hari/Tanggal**: {date_str}
- **Dosen Pengampu**: {dosen_name}
- **Status Transkrip**: Diproses dari berkas lokal Tactiq

---

## 1. Executive Summary (Gagasan Utama Sesi)
> *[Gunakan AI untuk merangkum 2-3 paragraf materi utama dari transkrip di bawah]*

---

## 2. Landasan Teori & Konsep Kunci
- **Konsep Utama**: ...
- **Definisi & Penjelasan**: ...

---

## 3. Aspek Metodologis & Diskusi Empiris
- **Metode Pembahasan**: ...
- **Contoh / Studi Kasus**: ...

---

## 4. Q&A dan Diskusi Dosen-Mahasiswa
- ...

---

## 5. Rujukan Literatur & Jurnal
- ...

---

## 6. Research Gaps & Ide Tesis
- [ ] ...

---

## Transkrip Mentah Ringkas (Kutipan Penting)
```text
{transcript_text[:1500]}
... [Transkrip dipotong untuk keterbacaan, total karakter: {len(transcript_text)}]
```
"""
    return template

def main():
    parser = argparse.ArgumentParser(description="Proses transkrip Tactiq ke Markdown S2")
    parser.add_argument("--file", help="Path file transkrip mentah", default=None)
    parser.add_argument("--matkul", help="Nama Mata Kuliah", default="MATA_KULIAH")
    parser.add_argument("--pertemuan", help="Nomor Pertemuan (misal: 1)", default="1")
    parser.add_argument("--dosen", help="Nama Dosen Pengampu", default="Dosen Pengampu")
    parser.add_argument("--out", help="Path file output markdown", default=None)

    args = parser.parse_args()

    if not args.file:
        print("Penggunaan: python process_transcript.py --file raw_transcript.txt --matkul 'Metodologi Penelitian' --pertemuan 1 --dosen 'Prof. Dr. X'")
        return

    text = parse_txt_transcript(args.file)
    if text is None:
        return

    output_content = create_summary_skeleton(text, args.matkul, args.pertemuan, args.dosen)

    out_path = args.out or f"output_pertemuan_{args.pertemuan}.md"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"Berhasil mengolah transkrip menjadi: {out_path}")

if __name__ == "__main__":
    main()
