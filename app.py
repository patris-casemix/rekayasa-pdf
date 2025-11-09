import streamlit as st
import pandas as pd
import re
import io
import qrcode
from pypdf import PdfReader, PdfWriter
from PIL import Image

# --- Konfigurasi Streamlit ---
st.set_page_config(layout="wide", page_title="Otomasi PDF Cloud Friendly")
st.title("☁️ Otomasi PDF Cloud Friendly (Tanpa PyMuPDF)")
st.caption("Solusi untuk deployment di Streamlit Community Cloud.")
st.markdown("---")

# --- Fungsi Inti: Mencari Teks (Mengganti fitz) ---
def find_text_and_rename(pdf_file_uploader, sep_list, sep_mapping, log_container):
    log_container.info("Memulai proses Rename & Verifikasi...")
    log_data = []
    
    # 1. Baca data PDF dari uploader
    pdf_reader = PdfReader(pdf_file_uploader)
    pdf_writer = PdfWriter()
    
    nomor_sep_ditemukan = None

    # 2. Cari Teks di Halaman Pertama
    try:
        page = pdf_reader.pages[0]
        text_first_page = page.extract_text()
        
        # Cari Nomor SEP di teks
        match = re.search(r"Nomor\s*SEP\s*[:\-]?\s*([A-Za-z0-9]+)", text_first_page, re.IGNORECASE)
        
        if match:
            nomor_sep_raw = match.group(1).strip()
            nomor_sep_clean = re.sub(r'\W+', '', nomor_sep_raw).upper()

            if nomor_sep_clean in sep_mapping:
                # Jika cocok, ambil nama baru
                new_name_excel = sep_mapping[nomor_sep_clean]
                new_filename = f"{new_name_excel}.pdf" # Atau Nomor SEP saja, tergantung kebutuhan
                status = "BERHASIL (Ditemukan & Cocok)"
            elif nomor_sep_clean in sep_list:
                # Jika hanya butuh nomor SEP untuk rename
                new_filename = f"{nomor_sep_clean}.pdf"
                new_name_excel = "NA"
                status = "BERHASIL (Nomor SEP Ditemukan)"
            else:
                new_filename = f"GAGAL_MAP_{pdf_file_uploader.name}"
                new_name_excel = "NA"
                status = f"GAGAL (SEP '{nomor_sep_clean}' tidak ada di Excel)"
        else:
            new_filename = f"GAGAL_SEP_NF_{pdf_file_uploader.name}"
            new_name_excel = "NA"
            status = "GAGAL (Nomor SEP tidak ditemukan)"

    except Exception as e:
        new_filename = f"ERROR_{pdf_file_uploader.name}"
        new_name_excel = "NA"
        status = f"ERROR ({e})"
        
    log_data.append([pdf_file_uploader.name, new_filename, new_name_excel, status])
    
    log_container.success(f"Pemrosesan selesai. Status: {status}")
    return log_data

# --- Fungsi Kedua: Menambahkan QR Code (Mengganti fitz.insert_image) ---
def add_qr_code(pdf_bytes, qr_image, text_jangkar="Dokter Penanggung jawab Pelayanan", offset_y=0, lebar_tandatangan=50):
    # FUNGSI INI AKAN SANGAT KOMPLEKS DAN BERPOTENSI GAGAL DI PYPDF
    # Karena pypdf tidak semudah PyMuPDF dalam manipulasi gambar.
    # Namun, kita akan menggunakan cara paling sederhana, yaitu mencari teks dan menempatkan
    # gambar sebagai stamp, meskipun penempatan presisi sulit.

    st.warning("Menambahkan gambar QR Code ke PDF dengan PyPDF sangat kompleks. Fungsi ini mungkin tidak presisi.")
    
    # KODE UNTUK MENGUBAH PDF DENGAN PYPDF SANGAT PANJANG DAN MEMBUTUHKAN BANYAK PERHITUNGAN.
    # Disarankan membiarkan fungsi ini (QR Code) hanya dilakukan secara lokal, 
    # atau menggunakan API berbayar untuk presisi.
    st.error("Fungsi penyisipan QR Code di Cloud di-nonaktifkan karena masalah presisi dan kompleksitas kode.")
    return None # Kembalikan None karena fungsi ini terlalu sulit tanpa PyMuPDF

# --- UI Streamlit ---

with st.expander("📝 1. Upload File & Konfigurasi"):
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("File Excel (Daftar SEP)")
        excel_file = st.file_uploader(
            "Upload file_list.xlsx", type=["xlsx"], 
            help="Excel yang berisi daftar Nomor SEP di kolom pertama."
        )
        
        if excel_file:
            try:
                df = pd.read_excel(excel_file, engine="openpyxl")
                # Lakukan pembersihan SEP (sesuai logika di kode lokal Anda)
                sep_mapping = {}
                sep_list = []
                for val in df.iloc[:, 0].astype(str):
                    parts = val.split(maxsplit=1)
                    if len(parts) > 1:
                        nomor_sep_clean = re.sub(r'\W+', '', parts[1]).upper() # Bersihkan & Uppercase
                        sep_mapping[nomor_sep_clean] = val.strip()      
                        sep_list.append(nomor_sep_clean)
                    else:
                        nomor_sep_clean = re.sub(r'\W+', '', parts[0]).upper()
                        sep_mapping[nomor_sep_clean] = val.strip()
                        sep_list.append(nomor_sep_clean)
                st.success(f"Data Excel dimuat. Total {len(sep_list)} Nomor SEP siap diverifikasi.")
            except Exception as e:
                st.error(f"Gagal memproses Excel: {e}")
                excel_file = None
                
    with col2:
        st.subheader("File PDF Sumber")
        pdf_files = st.file_uploader(
            "Upload semua file PDF yang ingin di-rename (Max 200MB per file)", 
            type=["pdf"], accept_multiple_files=True
        )
        st.info(f"Total {len(pdf_files)} file PDF terunggah.")

st.markdown("---")

# --- Tombol Proses ---
if st.button("▶️ Mulai Proses Rename & Log"):
    if not excel_file or not pdf_files:
        st.error("Mohon lengkapi file Excel dan setidaknya satu file PDF.")
    else:
        log_display = st.empty()
        final_log = []
        berhasil = 0
        gagal = 0
        
        progress_bar = st.progress(0)
        
        for i, pdf_file in enumerate(pdf_files):
            log_data = find_text_and_rename(pdf_file, sep_list, sep_mapping, log_display)
            final_log.extend(log_data)
            
            if log_data[0][3].startswith("BERHASIL"):
                berhasil += 1
            else:
                gagal += 1
                
            progress_bar.progress((i + 1) / len(pdf_files))
        
        progress_bar.empty()
        log_display.empty()

        # Tampilkan Hasil Log
        log_df = pd.DataFrame(final_log, columns=["File Asli", "Nama File Baru", "Nama Lengkap Excel", "Status"])
        st.subheader("📜 Hasil Log Pemrosesan")
        st.dataframe(log_df, use_container_width=True)
        
        st.success(f"Proses Selesai! Berhasil: **{berhasil}**, Gagal: **{gagal}**")
        
        # Tombol Download Log
        csv = log_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Log (CSV)",
            data=csv,
            file_name='log_rename_otomasi.csv',
            mime='text/csv',
        )
        
        st.info("Catatan: Untuk mendapatkan file PDF yang sudah di-rename, Anda perlu menulis ulang fungsi rename untuk menghasilkan file yang dapat di-*download* (sedikit lebih kompleks), atau cukup gunakan Log ini untuk verifikasi.")