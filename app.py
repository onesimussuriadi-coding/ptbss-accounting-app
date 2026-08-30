import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import pandas as pd
import openpyxl
import io

from modules.master import render_modul_0, FILE_MASTER_COA, simpan_excel_cantik
from modules.input_dokumen import render_modul_1
from modules.penjurnalan import render_modul_2
from modules.laporan import render_modul_3

st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

CREDENTIALS = {
    "staf_ops": {"pass": "pass123", "role": "Staf", "dept": "Operasional", "name": "Staf Admin Operasional"},
    "kabag_ops": {"pass": "pass123", "role": "Kabag", "dept": "Operasional", "name": "Kepala Bagian Operasional"},
    "staf_hrd": {"pass": "pass123", "role": "Staf", "dept": "HRD", "name": "Staf Admin HRD"},
    "kabag_hrd": {"pass": "pass123", "role": "Kabag", "dept": "HRD", "name": "Kepala Bagian HRD"},
    "staf_log": {"pass": "pass123", "role": "Staf", "dept": "Logistik", "name": "Staf Admin Logistik"},
    "kabag_log": {"pass": "pass123", "role": "Kabag", "dept": "Logistik", "name": "Kepala Bagian Logistik"},
    "staf_maint": {"pass": "pass123", "role": "Staf", "dept": "Maintenance", "name": "Staf Admin Maintenance"},
    "kabag_maint": {"pass": "pass123", "role": "Kabag", "dept": "Maintenance", "name": "Kepala Bagian Maintenance"},
    "staf_hse": {"pass": "pass123", "role": "Staf", "dept": "HSE", "name": "Staf Admin HSE"},
    "kabag_hse": {"pass": "pass123", "role": "Kabag", "dept": "HSE", "name": "Kepala Bagian HSE"},
    "staf_akt": {"pass": "pass123", "role": "Staf", "dept": "Akuntansi", "name": "Staf Admin Akuntansi"},
    "kabag_akt": {"pass": "pass123", "role": "Kabag", "dept": "Akuntansi", "name": "Kepala Bagian Akuntansi"},
    "staff_fin": {"pass": "pass123", "role": "Keuangan", "dept": "Keuangan", "name": "Staf Akuntansi & Jurnal"},
    "manager": {"pass": "pass123", "role": "Manajer", "dept": "Manajemen", "name": "Manajer Keuangan (Administrator)"}
}

if 'authenticated_user' not in st.session_state:
    st.session_state.authenticated_user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_dept' not in st.session_state:
    st.session_state.user_dept = None

abs_file_path = os.path.join(current_dir, FILE_MASTER_COA)

if 'master_coa' not in st.session_state:
    if os.path.exists(abs_file_path):
        try:
            st.session_state.master_coa = pd.read_excel(abs_file_path)
        except Exception:
            st.session_state.master_coa = pd.DataFrame(columns=["Kode Akun", "Nama Akun", "Sub Account", "Sub Kategori", "Kategori"])
    else:
        st.session_state.master_coa = pd.DataFrame([
            {"Kode Akun": "1110.001", "Nama Akun": "Kas Besar Luwuk", "Sub Account": "111 - Kas", "Sub Kategori": "11 - Aktiva Lancar", "Kategori": "1 - Aktiva"},
            {"Kode Akun": "1120.001", "Nama Akun": "BCA 0884791339 an. Vonny", "Sub Account": "112 - Bank", "Sub Kategori": "11 - Aktiva Lancar", "Kategori": "1 - Aktiva"},
            {"Kode Akun": "5133.001", "Nama Akun": "Alat Tulis Kantor", "Sub Account": "513 - Harga Pokok Proyek Jasa Umum", "Sub Kategori": "51 - Harga Pokok Proyek GS", "Kategori": "5 - Harga Pokok Penjualan"}
        ])
        simpan_excel_cantik(st.session_state.master_coa, abs_file_path)

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
        "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Supplier", "Business Unit", 
        "Departemen Tujuan", "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH", "Total", "Status Dokumen", "Status Jurnal"
    ])

if 'data_jurnal' not in st.session_state:
    st.session_state.data_jurnal = pd.DataFrame(columns=[
        "ID Jurnal", "ID Dokumen", "Tanggal", "Nomor Bukti", "Kode Akun", "Nama Akun", "Debit", "Kredit"
    ])

if 'form_index' not in st.session_state:
    st.session_state.form_index = 0

if not st.session_state.authenticated_user:
    col_spacer1, col_center, col_spacer2 = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1E3A8A; font-size: 28px; white-space: nowrap;'>PT Banggai Sentral Sulawesi</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #475569; font-size: 18px; margin-top: -10px;'>Dashboard Keuangan Terintegrasi</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 14px;'>Silakan masukkan Username dan Password sesuai wewenang hierarki divisi Anda.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_center_form"):
            u_input = st.text_input("Username")
            p_input = st.text_input("Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            b_login = st.form_submit_button("🔑 Masuk Sistem", use_container_width=True)
            
            if b_login:
                if u_input in CREDENTIALS and CREDENTIALS[u_input]["pass"] == p_input:
                    st.session_state.authenticated_user = u_input
                    st.session_state.user_role = CREDENTIALS[u_input]["role"]
                    st.session_state.user_dept = CREDENTIALS[u_input]["dept"]
                    st.success("Autentikasi berhasil! Memuat sistem...")
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
        
        st.markdown("<p style='text-align: center; font-size: 12px; color: #CBD5E1; margin-top: 30px;'>Internal Corporate Accounting System © 2026 PT BSS</p>", unsafe_allow_html=True)
    st.stop()

role_kini = st.session_state.user_role
dept_kini = st.session_state.user_dept

with st.sidebar:
    st.title("🔐 Panel Akses PT BSS")
    st.success(f"Login: **{st.session_state.authenticated_user}**")
    st.write(f"Peran: **{role_kini}**")
    st.write(f"Departemen: **{dept_kini}**")
    st.markdown("---")
    if st.button("🚪 Keluar (Logout)", use_container_width=True):
        st.session_state.authenticated_user = None
        st.session_state.user_role = None
        st.session_state.user_dept = None
        st.rerun()

st.title("📊 Sistem Akuntansi Terintegrasi PT Banggai Sentral Sulawesi")
st.write(f"Dashboard Keuangan Berbasis Wewenang Aktif: `{role_kini} - {dept_kini}`")

if role_kini == "Staf":
    daftar_menu = ["Dashboard Utama", "Modul 1: Input Dokumen Operasional"]
elif role_kini == "Kabag":
    daftar_menu = ["Dashboard Utama", "Pusat Kendali & Approval Bertingkat"]
else:
    daftar_menu = [
        "Dashboard Utama",
        "Modul 0: Pengaturan Master Akun & BU",
        "Modul 1: Input Dokumen Operasional",
        "Pusat Kendali & Approval Bertingkat",
        "Modul 2: Proses Penjurnalan Akuntansi",
        "Modul 3: Output Laporan Keuangan"
    ]

menu = st.sidebar.selectbox("Pilih Menu / Modul Utama", daftar_menu)

if menu == "Dashboard Utama":
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 35px; border-radius: 14px; color: white; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
            <h2 style='margin: 0; color: white; font-size: 28px;'>Selamat Datang di Sistem Akuntansi PT BSS</h2>
            <p style='margin-top: 10px; font-size: 16px; color: #E2E8F0;'>Pusat Pengelolaan Dokumen, Operasional, dan Tata Kelola Keuangan Perusahaan</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("### ✨ Nilai Utama & Komitmen Kerja Profesional")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown("""
            <div style='background-color: #F8FAFC; border-left: 5px solid #2563EB; padding: 20px; border-radius: 8px; height: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                <h4 style='color: #1E3A8A; margin-top: 0;'>💎 Integritas & Kejujuran</h4>
                <p style='color: #475569; font-size: 14px; margin-bottom: 0;'>Setiap angka, nomor bukti, dan transaksi yang diinput adalah cerminan kebenaran laporan perusahaan.</p>
            </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown("""
            <div style='background-color: #F8FAFC; border-left: 5px solid #10B981; padding: 20px; border-radius: 8px; height: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                <h4 style='color: #065F46; margin-top: 0;'>⚙️ Kerja Keras & Ketelitian</h4>
                <p style='color: #475569; font-size: 14px; margin-bottom: 0;'>Ketelitian dalam memasukkan volume, satuan, dan nilai DPP mencegah kesalahan berjenjang.</p>
            </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown("""
            <div style='background-color: #F8FAFC; border-left: 5px solid #F59E0B; padding: 20px; border-radius: 8px; height: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                <h4 style='color: #92400E; margin-top: 0;'>🛡️ Tanggung Jawab Wewenang</h4>
                <p style='color: #475569; font-size: 14px; margin-bottom: 0;'>Patuhi alur hierarki approval yang berlaku dan jaga kerahasiaan data.</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(f"💡 **Status Akun:** Anda masuk sebagai **{role_kini}** pada Departemen **{dept_kini}**.")

elif menu == "Modul 0: Pengaturan Master Akun & BU":
    render_modul_0()

elif menu == "Modul 1: Input Dokumen Operasional":
    render_modul_1()

elif menu == "Pusat Kendali & Approval Bertingkat":
    st.subheader(f"📂 Pusat Kendali Dokumen & Workflow Departemen: {dept_kini}")
    st.info(f"Hak Akses Anda: **{role_kini} {dept_kini}**")
    if not st.session_state.data_operasional.empty:
        df_all = st.session_state.data_operasional.copy()
        df_pusat = df_all[df_all['Departemen Tujuan'] == dept_kini] if role_kini == "Kabag" else df_all
        if not df_pusat.empty:
            st.dataframe(df_pusat, use_container_width=True)
            st.markdown("---")
            list_nobukti = df_pusat['Nomor Bukti'].tolist()
            pilih_bukti = st.selectbox("Pilih Nomor Bukti untuk Diproses", ["-- Pilih --"] + list_nobukti)
            if pilih_bukti != "-- Pilih --":
                row = df_pusat[df_pusat['Nomor Bukti'] == pilih_bukti].iloc[0]
                st.write(f"Status Dokumen Saat Ini: **{row.get('Status Dokumen', 'Menunggu Approval Kabag')}**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if role_kini in ["Kabag", "Manajer"] and st.button(f"✅ Approve Kabag"):
                        st.session_state.data_operasional.loc[st.session_state.data_operasional['Nomor Bukti'] == pilih_bukti, 'Status Dokumen'] = f"Disetujui Kabag ➡️ Menunggu Jurnal"
                        st.success("Dokumen disetujui!")
                        st.rerun()
                with c2:
                    if role_kini in ["Keuangan", "Manajer"] and st.button("📝 Verifikasi & Jurnal"):
                        st.session_state.data_operasional.loc[st.session_state.data_operasional['Nomor Bukti'] == pilih_bukti, ['Status Jurnal', 'Status Dokumen']] = ["Sudah Dijurnal", "Menunggu Approval Manajer"]
                        st.success("Tercatat & diteruskan ke Manajer!")
                        st.rerun()
                with c3:
                    if role_kini == "Manajer" and st.button("⭐ Approval Final"):
                        st.session_state.data_operasional.loc[st.session_state.data_operasional['Nomor Bukti'] == pilih_bukti, 'Status Dokumen'] = "Approved Final (Sah)"
                        st.success("Disetujui Final!")
                        st.rerun()
        else:
            st.warning(f"Belum ada dokumen untuk Departemen **{dept_kini}**.")
    else:
        st.info("Belum ada dokumen tersimpan.")

elif menu == "Modul 2: Proses Penjurnalan Akuntansi":
    render_modul_2()

elif menu == "Modul 3: Output Laporan Keuangan":
    render_modul_3()