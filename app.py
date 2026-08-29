import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import pandas as pd

from modules.master import render_modul_0
from modules.input_dokumen import render_modul_1
from modules.penjurnalan import render_modul_2
from modules.laporan import render_modul_3

st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

# --- PENGAMAN UTAMA: Mencegah data Master Akun tereset saat refresh atau update kode ---
if 'master_coa' not in st.session_state or 'Sub Kategori' not in st.session_state.master_coa.columns:
    st.session_state.master_coa = pd.DataFrame([
        {"Kode Akun": "1110.001", "Nama Akun": "Kas Besar Luwuk", "Sub Account": "111 - Kas", "Sub Kategori": "11 - Aktiva Lancar", "Kategori": "1 - Aktiva"},
        {"Kode Akun": "1120.001", "Nama Akun": "BCA 0884791339 an. Vonny", "Sub Account": "112 - Bank", "Sub Kategori": "11 - Aktiva Lancar", "Kategori": "1 - Aktiva"},
        {"Kode Akun": "5133.001", "Nama Akun": "Alat Tulis Kantor", "Sub Account": "513 - Harga Pokok Proyek Jasa Umum", "Sub Kategori": "51 - Harga Pokok Proyek GS", "Kategori": "5 - Harga Pokok Penjualan"}
    ])

if 'master_bu' not in st.session_state:
    st.session_state.master_bu = pd.DataFrame([
        {"ID BU": "BU-01", "Nama Business Unit": "Operasional Kantor Pusat"},
        {"ID BU": "BU-02", "Nama Business Unit": "Proyek Drilling"},
        {"ID BU": "BU-03", "Nama Business Unit": "Proyek Well Services"},
        {"ID BU": "BU-04", "Nama Business Unit": "Proyek Slickline"}
    ])

if 'master_satuan' not in st.session_state:
    st.session_state.master_satuan = ["Unit", "Lot", "Liter", "Jam", "Pcs", "Hari", "Bulan", "Trip", "M3"]

if 'master_supplier' not in st.session_state:
    st.session_state.master_supplier = [
        "- Tidak Ada / Kas Tunai -", 
        "PT Pertamina (Persero)", 
        "PT Medco E&P Tomori Sulawesi", 
        "CV Sumber Berkat Mandiri", 
        "Toko Maju Jaya Teknik"
    ]

if 'data_operasional' not in st.session_state:
    st.session_state.data_operasional = pd.DataFrame(columns=[
        "ID", "Tanggal", "Sumber Transaksi", "Nomor Bukti", "Supplier", "Business Unit", 
        "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH", "Total", "Status Jurnal"
    ])

if 'data_jurnal' not in st.session_state:
    st.session_state.data_jurnal = pd.DataFrame(columns=[
        "ID Jurnal", "ID Dokumen", "Tanggal", "Nomor Bukti", "Kode Akun", "Nama Akun", "Debit", "Kredit"
    ])

if 'form_index' not in st.session_state:
    st.session_state.form_index = 0

st.title("📊 Sistem Akuntansi Terintegrasi PT Banggai Sentral Sulawesi")
st.write("Dashboard Pengelolaan Keuangan Berbasis Arsitektur Modular Terpisah.")

menu = st.sidebar.selectbox("Pilih Menu / Modul Utama", [
    "Dashboard Utama",
    "Modul 0: Pengaturan Master Akun & BU",
    "Modul 1: Input Dokumen Operasional",
    "Modul 2: Proses Penjurnalan Akuntansi",
    "Modul 3: Output Laporan Keuangan"
])

if menu == "Dashboard Utama":
    st.subheader("Ringkasan Sistem Keuangan")
    total_dok = len(st.session_state.data_operasional)
    total_jurnal = len(st.session_state.data_jurnal)
    total_nilai = st.session_state.data_operasional['Total'].sum() if not st.session_state.data_operasional.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Dokumen Masuk", f"{total_dok} Item")
    col2.metric("Total Jurnal Tercatat", f"{total_jurnal} Baris")
    col3.metric("Total Nilai Transaksi", f"Rp {total_nilai:,.0f}")
    col4.metric("Status Sistem", "Modular Protected Mode")
    
    st.info("Gunakan menu navigasi di sebelah kiri untuk mengakses modul terpisah.")

elif menu == "Modul 0: Pengaturan Master Akun & BU":
    render_modul_0()

elif menu == "Modul 1: Input Dokumen Operasional":
    render_modul_1()

elif menu == "Modul 2: Proses Penjurnalan Akuntansi":
    render_modul_2()

elif menu == "Modul 3: Output Laporan Keuangan":
    render_modul_3()