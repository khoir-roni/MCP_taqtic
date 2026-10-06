#!/usr/bin/env python3
"""
compile_lecture_transcript.py

Mengompilasi dan menyinkronkan transkrip kuliah real-time Tactiq.io (berisi screenshot slide)
dengan transkrip rekaman resmi Zoom (.vtt / .srt) yang akurat.

Fitur:
1. Deteksi tanggal kuliah otomatis (dari nama file atau metadata PDF).
2. Pembuatan struktur folder berbasis tanggal (misal: 02_Materi_dan_Bahan_Ajar/2026-09-29/).
3. Ekstraksi otomatis screenshot resolusi tinggi dari PDF Tactiq ke folder screenshots/ lokal per tanggal.
4. Deteksi offset waktu dan perataan urutan (monotonic dynamic alignment) antara Tactiq dan Zoom.
5. Penggabungan dialog per pembicara menjadi paragraf utuh yang rapi dan mudah dibaca.
6. Pembuatan dokumen catatan kuliah Markdown (.md) lengkap dengan metadata, daftar isi,
   gambar slide tersemat, dan transkrip akurat.
"""

import os
import sys
import re
import argparse
import fitz  # PyMuPDF


MONTH_MAP = {
    'januari': '01', 'january': '01', 'jan': '01',
    'februari': '02', 'february': '02', 'feb': '02',
    'maret': '03', 'march': '03', 'mar': '03',
    'april': '04', 'apr': '04',
    'mei': '05', 'may': '05',
    'juni': '06', 'june': '06', 'jun': '06',
    'juli': '07', 'july': '07', 'jul': '07',
    'agustus': '08', 'august': '08', 'aug': '08',
    'september': '09', 'sep': '09',
    'oktober': '10', 'october': '10', 'oct': '10',
    'november': '11', 'nov': '11',
    'desember': '12', 'december': '12', 'dec': '12'
}


def detect_lecture_date(zoom_name, tactiq_name, p1_text=""):
    """Mendeteksi tanggal kuliah dalam format YYYY-MM-DD secara otomatis."""
    # 1. Dari nama file Zoom (misal: GMT20260929-085216...)
    m = re.search(r'GMT(\d{4})(\d{2})(\d{2})', zoom_name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 2. Dari nama file Tactiq (misal: Transcript kuliah 29 September 2026...)
    m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', tactiq_name)
    if m:
        day = int(m.group(1))
        mon = MONTH_MAP.get(m.group(2).lower(), '01')
        year = m.group(3)
        return f"{year}-{mon}-{day:02d}"

    # 3. Dari teks Halaman 1 Tactiq (misal: Meeting started: Sep 29, 2026...)
    m = re.search(r'Meeting started:\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', p1_text)
    if m:
        mon = MONTH_MAP.get(m.group(1).lower(), '01')
        day = int(m.group(2))
        year = m.group(3)
        return f"{year}-{mon}-{day:02d}"

    return "unknown_date"


def parse_vtt(vtt_path):
    """Membaca file WebVTT dari Zoom dan mengekstrak cue berurutan."""
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(
        r'(\d+)\n(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\n(?:([^\n:]+): )?(.*?)(?=\n\s*\n\d+\n|\Z)',
        re.DOTALL
    )

    def to_sec(ts):
        parts = ts.split(':')
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

    cues = []
    for m in pattern.finditer(content):
        cue_id, start_str, end_str, speaker, text = m.groups()
        cues.append({
            'id': int(cue_id),
            'start_str': start_str[:8],
            'end_str': end_str[:8],
            'start_sec': to_sec(start_str),
            'end_sec': to_sec(end_str),
            'speaker': (speaker or 'Unknown').strip(),
            'text': text.strip().replace('\n', ' ')
        })

    return cues


def parse_time_str(ts_str):
    """Konversi format MM:SS atau HH:MM:SS ke total detik."""
    parts = list(map(int, ts_str.split(':')))
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0


def format_sec(sec):
    """Format total detik ke string HH:MM:SS atau MM:SS."""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def extract_tactiq_pdf(pdf_path, assets_dir):
    """
    Ekstrak screenshot dan struktur teks/waktu dari PDF Tactiq.
    Menghasilkan metadata dokumen, daftar gambar, dan alur kronologis.
    """
    os.makedirs(assets_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    # 1. Ekstrak Metadata Halaman 1
    p1_text = doc[0].get_text()
    meta = {
        'title': 'Kuliah Sains Data',
        'started': '',
        'duration': '',
        'participants': [],
        'p1_text': p1_text
    }
    for line in p1_text.split('\n'):
        line_s = line.strip()
        if 'Meeting started:' in line_s:
            meta['started'] = line_s.replace('Meeting started:', '').strip()
        elif 'Meeting duration:' in line_s:
            meta['duration'] = line_s.replace('Meeting duration:', '').strip()
        elif 'Meeting participants:' in line_s:
            meta['participants'].append(line_s.replace('Meeting participants:', '').strip())

    # 2. Rekonstruksi alur visual dan transkrip
    flow = []
    ts_regex = re.compile(r'^(\d{2}:\d{2}(?::\d{2})?)\s+([^:]+):(.*)$')
    img_counter = 0

    for p_idx, page in enumerate(doc):
        p_num = p_idx + 1
        blocks = page.get_text('blocks')
        for b in blocks:
            if b[6] == 0:  # text block
                lines = [l.strip() for l in b[4].split('\n') if l.strip()]
                for l in lines:
                    m = ts_regex.match(l)
                    if m:
                        flow.append({
                            'type': 'timestamp',
                            'page': p_num,
                            'y': b[1],
                            'time_str': m.group(1),
                            'sec': parse_time_str(m.group(1)),
                            'speaker': m.group(2).strip(),
                            'text': m.group(3).strip()
                        })
                    else:
                        flow.append({
                            'type': 'text',
                            'page': p_num,
                            'y': b[1],
                            'text': l
                        })

        imgs = page.get_images(full=True)
        for img in imgs:
            xref = img[0]
            rects = page.get_image_rects(xref)
            y0 = rects[0].y0 if rects else 0
            base_img = doc.extract_image(xref)
            img_bytes = base_img['image']
            ext = base_img['ext']

            img_counter += 1
            filename = f"slide_{img_counter:02d}_p{p_num:02d}.{ext}"
            file_path = os.path.join(assets_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(img_bytes)

            flow.append({
                'type': 'image',
                'page': p_num,
                'y': y0,
                'xref': xref,
                'img_counter': img_counter,
                'filename': filename,
                'file_path': file_path
            })

    # Urutkan berdasarkan urutan halaman lalu koordinat vertikal y
    flow.sort(key=lambda x: (x['page'], x['y']))

    # 3. Kumpulkan image anchor points
    image_points = []
    for i, item in enumerate(flow):
        if item['type'] == 'image':
            t_before = None
            for j in range(i - 1, -1, -1):
                if flow[j]['type'] == 'timestamp':
                    t_before = flow[j]
                    break

            tactiq_sec = t_before['sec'] if t_before else 0

            words = set()
            for j in range(max(0, i - 6), min(len(flow), i + 7)):
                if flow[j]['type'] in ('text', 'timestamp'):
                    t = flow[j]['text'].lower()
                    w = re.findall(r'[a-zA-Z]{4,}', t)
                    words.update(w)

            image_points.append({
                'img_id': item['img_counter'],
                'page': item['page'],
                'filename': item['filename'],
                'file_path': item['file_path'],
                'tactiq_sec': tactiq_sec,
                'context_words': words
            })

    return meta, image_points, flow


def align_images_to_zoom(image_points, flow, vtt_cues):
    """
    Sinkronisasi gambar slide Tactiq dengan cue Zoom VTT secara monoton.
    """
    best_offset = 36.5
    for item in flow:
        if item['type'] == 'timestamp' and len(item['text']) > 15:
            txt = item['text'].lower()[:30]
            for c in vtt_cues[:25]:
                if txt[:15] in c['text'].lower():
                    best_offset = c['start_sec'] - item['sec']
                    break
            if best_offset != 36.5:
                break

    last_cue_idx = 0
    aligned_slides = []

    for img in image_points:
        approx_zoom_sec = img['tactiq_sec'] + best_offset
        best_cue_idx = last_cue_idx + 1
        best_score = -float('inf')

        for c_idx in range(last_cue_idx + 1, len(vtt_cues)):
            c = vtt_cues[c_idx]
            time_diff = abs(c['start_sec'] - approx_zoom_sec)
            if c['start_sec'] > approx_zoom_sec + 150 and c_idx > last_cue_idx + 2:
                break

            c_words = set(re.findall(r'[a-zA-Z]{4,}', c['text'].lower()))
            overlap = len(img['context_words'].intersection(c_words))
            score = overlap * 2.0 - 0.05 * time_diff

            if score > best_score:
                best_score = score
                best_cue_idx = c_idx

        if best_cue_idx <= last_cue_idx:
            best_cue_idx = last_cue_idx + 1

        last_cue_idx = best_cue_idx
        aligned_slides.append({
            'img_id': img['img_id'],
            'page': img['page'],
            'filename': img['filename'],
            'cue_idx': best_cue_idx,
            'start_str': vtt_cues[best_cue_idx]['start_str'],
            'start_sec': vtt_cues[best_cue_idx]['start_sec'],
            'score': best_score
        })

    return aligned_slides


def format_speaker_dialogue(cues):
    """
    Menggabungkan cue berturutan dari pembicara yang sama menjadi paragraf dialog terstruktur.
    """
    if not cues:
        return ""

    turns = []
    current_turn = None

    for c in cues:
        spk = c['speaker']
        txt = c['text'].strip()
        if not txt:
            continue

        if current_turn and current_turn['speaker'] == spk:
            current_turn['texts'].append(txt)
            current_turn['end_str'] = c['end_str']
            current_turn['end_sec'] = c['end_sec']
        else:
            if current_turn:
                turns.append(current_turn)
            current_turn = {
                'speaker': spk,
                'start_str': c['start_str'],
                'end_str': c['end_str'],
                'start_sec': c['start_sec'],
                'end_sec': c['end_sec'],
                'texts': [txt]
            }

    if current_turn:
        turns.append(current_turn)

    lines = []
    for t in turns:
        combined_text = " ".join(t['texts'])
        combined_text = re.sub(r'\s+', ' ', combined_text).strip()
        lines.append(f"> ⏱️ **{t['start_str']} - {t['end_str']}** | **{t['speaker']}**  \n> {combined_text}\n")

    return "\n".join(lines)


SLIDE_TITLES = {
    1: "Judul Materi: Exploratory Data Analysis - Statistik Deskriptif secara Numerik",
    2: "Subtopik & Tujuan Instruksional Khusus (TIK)",
    3: "Kerangka Kerja EDA: Sari Numerik vs Visualisasi Grafik",
    4: "Perbedaan Terminologi: Statistik vs Statistika",
    5: "Penerapan Statistik dalam Sains Data & Tipe Data",
    6: "Karakteristik Data Numerik: Diskrit vs Kontinu",
    7: "Eksplorasi Data Non-Numerik: Kasus Citra & Seni Lukis",
    8: "Representasi Fitur Citra Menjadi Data Numerik (Piksel & Vektor)",
    9: "Eksplorasi Sinyal Audio dan Suara dalam Sains Data",
    10: "Konsep Distribusi Data: Bentuk Simetris vs Kemencengan",
    11: "Empat Parameter Distribusi Utama (Pemusatan, Penyebaran, Skewness, Kurtosis)",
    12: "Distribusi Menceng (Skewed) dan Keberadaan Nilai Ekstrem",
    13: "Distribusi Normal & Pengaruh Ukuran Sampel (Central Limit Theorem)",
    14: "Parameter Ukuran Pemusatan: Mean, Median, dan Modus",
    15: "Karakteristik Nilai Tengah: Ketahanan Median terhadap Nilai Ekstrem",
    16: "Pembagian Data Berdasarkan Kuartil (Q1, Q2, Q3)",
    17: "Ukuran Penyebaran Data: Rentang (Range) dan Variansi",
    18: "Jangkauan Antarkuartil (Interquartile Range / IQR)",
    19: "Analisis Kemencengan (Skewness): Hubungan Posisi Mean, Median, dan Modus",
    20: "Dampak Normalisasi & Transformasi Fitur terhadap Distribusi",
    21: "Analisis Kelancipan (Kurtosis): Leptokurtik, Mesokurtik, dan Platikurtik",
    22: "Deteksi Pencilan (Outlier): Metode Pagar Tukey (1.5 x IQR)",
    23: "Strategi Penanganan Pencilan & Evaluasi Threshold Deteksi",
    24: "Studi Kasus 1: Perhitungan Ukuran Pemusatan pada Data Sampel",
    25: "Studi Kasus 2: Perhitungan Dispersi, Variansi, dan Simpangan Baku",
    26: "Studi Kasus Nyata: Distribusi Pendapatan & Ketimpangan Ekonomi",
    27: "Urgensi Visualisasi Data dalam Analisis Eksploratif (EDA)",
    28: "Visualisasi Univariat: Diagram Batang, Diagram Lingkaran, dan Histogram",
    29: "Visualisasi Distribusi & Outlier: Box Plot (Diagram Kotak-Garis)",
    30: "Visualisasi Data Deret Waktu (Time Series) & Analisis Tren Temporal",
    31: "Visualisasi Bivariat & Analisis Korelasi: Scatter Plot",
    32: "Prinsip Desain Visualisasi Data yang Efektif & Representatif"
}


def build_markdown(meta, aligned_slides, vtt_cues, assets_rel_dir, output_path, lecture_date):
    """
    Menyusun dokumen Markdown catatan kuliah lengkap dan menyimpannya.
    """
    total_cues = len(vtt_cues)
    total_slides = len(aligned_slides)

    doc_lines = []
    doc_lines.append("# Catatan Kuliah: II5005 Sains Data")
    doc_lines.append("## W05 Exploratory Data Analysis: Statistik Deskriptif secara Numerik\n")

    doc_lines.append("### Informasi Perkuliahan")
    doc_lines.append("- **Mata Kuliah:** II5005 Sains Data (S2 Rekayasa Perangkat Lunak / Magister Terapan)")
    doc_lines.append("- **Topik:** Exploratory Data Analysis (EDA) - Statistik Deskriptif secara Numerik & Visualisasi")
    doc_lines.append("- **Dosen Pengampu:** Dr. Lenny Putri Yulianti, S.T., M.T.")
    doc_lines.append(f"- **Waktu / Tanggal:** {lecture_date}")
    doc_lines.append("- **Durasi Sesi:** 134 Menit (~02:15:16)")
    doc_lines.append("- **Platform Pertemuan:** Zoom Meeting (Sinkronisasi Tactiq.io + Official Zoom Transcript)\n")

    doc_lines.append("---\n")
    doc_lines.append("## Daftar Isi Perkuliahan\n")

    doc_lines.append(f"- [Pembukaan Kuliah & Apersepsi W04](#pembukaan-kuliah--apersepsi-w04) *(00:00:27 - {aligned_slides[0]['start_str']})*")

    for s in aligned_slides:
        sid = s['img_id']
        title = SLIDE_TITLES.get(sid, f"Slide {sid:02d}")
        slug = f"slide-{sid:02d}-{re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')}"
        doc_lines.append(f"- [Slide {sid:02d}: {title}](#{slug}) *({s['start_str']})*")

    doc_lines.append(f"- [Sesi Tanya Jawab & Penutup](#sesi-tanya-jawab--penutup) *({vtt_cues[-10]['start_str']} - {vtt_cues[-1]['end_str']})*\n")
    doc_lines.append("---\n")

    # 1. Pembukaan Kuliah
    slide1_cue_idx = aligned_slides[0]['cue_idx']
    intro_cues = vtt_cues[:slide1_cue_idx]
    if intro_cues:
        doc_lines.append("## Pembukaan Kuliah & Apersepsi W04\n")
        doc_lines.append(format_speaker_dialogue(intro_cues))
        doc_lines.append("\n---\n")

    # 2. Iterasi Setiap Slide
    for i, s in enumerate(aligned_slides):
        sid = s['img_id']
        title = SLIDE_TITLES.get(sid, f"Slide {sid:02d}")

        c_start = s['cue_idx']
        c_end = aligned_slides[i + 1]['cue_idx'] if i + 1 < total_slides else total_cues

        if sid == total_slides:
            qa_start = c_end
            for idx in range(c_start, c_end):
                if 'ada lagi bapak' in vtt_cues[idx]['text'].lower() or 'pertanyaan' in vtt_cues[idx]['text'].lower():
                    qa_start = idx
                    break
            slide_cues = vtt_cues[c_start:qa_start]
            qa_cues = vtt_cues[qa_start:c_end]
        else:
            slide_cues = vtt_cues[c_start:c_end]
            qa_cues = []

        doc_lines.append(f"## Slide {sid:02d}: {title}\n")
        doc_lines.append(f"**Waktu Tayang:** `{s['start_str']}` | **Halaman Dokumen Tactiq:** `{s['page']}`\n")

        img_rel_path = f"{assets_rel_dir}/{s['filename']}".replace('\\', '/')
        doc_lines.append(f"![Slide {sid:02d}: {title}]({img_rel_path})\n")

        doc_lines.append("### Transkrip Diskusi & Penjelasan Dosen\n")
        doc_lines.append(format_speaker_dialogue(slide_cues))
        doc_lines.append("\n---\n")

        if qa_cues:
            doc_lines.append("## Sesi Tanya Jawab & Penutup\n")
            doc_lines.append(format_speaker_dialogue(qa_cues))
            doc_lines.append("\n---\n")

    content = "\n".join(doc_lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Catatan kuliah berhasil disimpan ke: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Kompilasi transkrip Tactiq.io dan Zoom VTT menjadi catatan kuliah Markdown dalam folder tanggal."
    )
    parser.add_argument("-t", "--tactiq", required=True, help="Path ke file PDF transkrip Tactiq.io")
    parser.add_argument("-z", "--zoom", required=True, help="Path ke file transkrip resmi Zoom (.vtt)")
    parser.add_argument("-d", "--date", default=None, help="Tanggal kuliah (format YYYY-MM-DD). Jika kosong, dideteksi otomatis.")
    parser.add_argument("-o", "--output", default=None, help="Path target file Markdown output (.md)")
    parser.add_argument("--outdir", default=None, help="Direktori induk (misal: 02_Materi_dan_Bahan_Ajar). Folder tanggal akan dibuat di dalamnya.")
    parser.add_argument("-a", "--assets-dir", default=None, help="Direktori penyimpanan screenshot slide")

    args = parser.parse_args()

    pdf_path = os.path.abspath(args.tactiq)
    vtt_path = os.path.abspath(args.zoom)

    if not os.path.exists(pdf_path):
        print(f"Error: File Tactiq PDF tidak ditemukan: {pdf_path}")
        sys.exit(1)
    if not os.path.exists(vtt_path):
        print(f"Error: File Zoom VTT tidak ditemukan: {vtt_path}")
        sys.exit(1)

    # Deteksi Tanggal Kuliah
    lecture_date = args.date
    if not lecture_date:
        lecture_date = detect_lecture_date(
            os.path.basename(vtt_path),
            os.path.basename(pdf_path)
        )
    print(f"[Info] Tanggal terdeteksi: {lecture_date}")

    # Tentukan Target Folder Sesuai Tanggal
    if args.output:
        output_path = os.path.abspath(args.output)
        target_folder = os.path.dirname(output_path)
    elif args.outdir:
        base_dir = os.path.abspath(args.outdir)
        target_folder = os.path.join(base_dir, lecture_date)
        os.makedirs(target_folder, exist_ok=True)
        output_path = os.path.join(target_folder, f"Catatan_Kuliah_{lecture_date}_II5005_Sains_Data.md")
    else:
        # Default di direktori yang sama dengan PDF
        base_dir = os.path.dirname(pdf_path)
        target_folder = os.path.join(base_dir, lecture_date)
        os.makedirs(target_folder, exist_ok=True)
        output_path = os.path.join(target_folder, f"Catatan_Kuliah_{lecture_date}_II5005_Sains_Data.md")

    os.makedirs(target_folder, exist_ok=True)

    if args.assets_dir:
        assets_dir = os.path.abspath(args.assets_dir)
    else:
        assets_dir = os.path.join(target_folder, "screenshots")
    os.makedirs(assets_dir, exist_ok=True)

    assets_rel_dir = os.path.relpath(assets_dir, target_folder)

    print(f"[1/4] Parsing file Zoom VTT: {os.path.basename(vtt_path)}...")
    vtt_cues = parse_vtt(vtt_path)
    print(f"      -> Ditemukan {len(vtt_cues)} cue dialog.")

    print(f"[2/4] Mengekstrak visual & teks dari Tactiq PDF: {os.path.basename(pdf_path)}...")
    meta, image_points, flow = extract_tactiq_pdf(pdf_path, assets_dir)
    print(f"      -> Berhasil mengekstrak {len(image_points)} screenshot slide.")

    print(f"[3/4] Melakukan perataan waktu (monotonic dynamic alignment)...")
    aligned_slides = align_images_to_zoom(image_points, flow, vtt_cues)
    print(f"      -> Berhasil menyinkronkan {len(aligned_slides)} slide dengan transkrip resmi.")

    print(f"[4/4] Membangun dokumen catatan kuliah Markdown di {target_folder}...")
    build_markdown(meta, aligned_slides, vtt_cues, assets_rel_dir, output_path, lecture_date)
    print("Selesai! Seluruh file berhasil disusun rapi di folder tanggal.")


if __name__ == '__main__':
    main()
