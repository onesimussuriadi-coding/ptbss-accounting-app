from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Impor modul utama secara aman
from modules.master import (
    render_modul_0,
    FILE_MASTER_COA,
    simpan_excel_cantik,
)
from modules.input_dokumen.modul_1 import render_modul_1
from modules.penjurnalan import render_modul_2
from modules.laporan import render_modul_3

# Impor aman untuk pusat_kendali_kabag (mendukung root maupun folder modules)
try:
    from pusat_kendali_kabag import render_pusat_kendali_kabag
except ImportError:
    try:
        from modules.pusat_kendali_kabag import render_pusat_kendali_kabag
    except ImportError:
        def render_pusat_kendali_kabag():
            st.error("Modul pusat_kendali_kabag belum ditemukan. Pastikan file sudah tersimpan di direktori utama atau folder modules.")

st.set_page_config(
    page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide"
)

FILE_USERS_EXCEL = "master_users.xlsx"
EXCEL_DB_PATH = "database_transaksi_bss.xlsx"

current_dir = os.path.dirname(os.path.abspath(__file__))
abs_users_path = os.path.join(current_dir, "modules", FILE_USERS_EXCEL)
if not os.path.exists(abs_users_path):
    abs_users_path = os.path.join(current_dir, FILE_USERS_EXCEL)

# INISIALISASI ATAU LOAD DATABASE USERS
if "credentials_dict" not in st.session_state:
    default_users = {
        "programmer": {
            "pass": "bss2026",
            "role": "Programmer",
            "dept": "IT / Pengembangan",
            "name": "Lead System Programmer",
        }
    }

    if os.path.exists(abs_users_path):
        try:
            df_u = pd.read_excel(abs_users_path, header=0)
            loaded_creds = {}
            for _, row in df_u.iterrows():
                if pd.notna(row.iloc[0]):
                    u_name = str(row.iloc[0]).strip()
                    loaded_creds[u_name] = {
                        "pass": str(row.iloc[1]).strip(),
                        "role": str(row.iloc[2]).strip(),
                        "dept": str(row.iloc[3]).strip(),
                        "name": str(row.iloc[4]).strip(),
                    }
            st.session_state.credentials_dict = loaded_creds
        except Exception:
            st.session_state.credentials_dict = default_users
    else:
        st.session_state.credentials_dict = default_users
        initial_rows = []
        for u, d in default_users.items():
            initial_rows.append({
                "Username": u,
                "Password": d["pass"],
                "Role": d["role"],
                "Departemen": d["dept"],
                "Nama Lengkap": d["name"],
            })
        try:
            pd.DataFrame(initial_rows).to_excel(abs_users_path, index=False)
        except:
            pass

def save_users_to_excel():
    rows = []
    for u, d in st.session_state.credentials_dict.items():
        rows.append({
            "Username": u,
            "Password": d["pass"],
            "Role": d["role"],
            "Departemen": d["dept"],
            "Nama Lengkap": d["name"],
        })
    df_save = pd.DataFrame(rows)
    try:
        df_save.to_excel(abs_users_path, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan data user: {e}")

# SESSION STATE UTAMA
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_dept" not in st.session_state:
    st.session_state.user_dept = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "data_operasional" not in st.session_state:
    if os.path.exists(EXCEL_DB_PATH):
        try:
            st.session_state.data_operasional = pd.read_excel(EXCEL_DB_PATH)
        except Exception:
            st.session_state.data_operasional = pd.DataFrame(columns=[
                "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
                "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
                "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
                "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Raw_Items"
            ])
    else:
        st.session_state.data_operasional = pd.DataFrame(columns=[
            "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
            "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
            "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
            "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Raw_Items"
        ])

abs_file_path = os.path.join(current_dir, "modules", FILE_MASTER_COA)
if not os.path.exists(abs_file_path):
    abs_file_path = os.path.join(current_dir, FILE_MASTER_COA)

if "master_coa" not in st.session_state:
    if os.path.exists(abs_file_path):
        try:
            st.session_state.master_coa = pd.read_excel(abs_file_path)
        except Exception:
            st.session_state.master_coa = pd.DataFrame(
                columns=[
                    "Kode Akun",
                    "Nama Akun",
                    "Sub Account",
                    "Sub Kategori",
                    "Kategori",
                ]
            )
    else:
        st.session_state.master_coa = pd.DataFrame([
            {
                "Kode Akun": "1110.001",
                "Nama Akun": "Kas Besar Luwuk",
                "Sub Account": "111 - Kas",
                "Sub Kategori": "11 - Aktiva Lancar",
                "Kategori": "1 - Aktiva",
            },
        ])
        try:
            simpan_excel_cantik(st.session_state.master_coa, abs_file_path)
        except:
            pass

if "master_bu" not in st.session_state:
    st.session_state.master_bu = pd.DataFrame([
        {"ID BU": "BU-01", "Nama Business Unit": "Operasional Kantor Pusat"},
        {"ID BU": "BU-02", "Nama Business Unit": "Proyek Drilling"},
        {"ID BU": "BU-03", "Nama Business Unit": "Proyek Well Services"},
        {"ID BU": "BU-04", "Nama Business Unit": "Proyek Slickline"},
    ])

if "master_satuan" not in st.session_state:
    st.session_state.master_satuan = [
        "Unit", "Lot", "Liter", "Jam", "Pcs", "Hari", "Bulan", "Trip", "M3",
    ]

if "master_supplier" not in st.session_state:
    st.session_state.master_supplier = [
        "- Tidak Ada / Kas Tunai -",
        "PT Pertamina (Persero)",
        "PT Medco E&P Tomori Sulawesi",
        "CV Sumber Berkat Mandiri",
        "Toko Maju Jaya Teknik",
    ]

if "data_jurnal" not in st.session_state:
    st.session_state.data_jurnal = pd.DataFrame(
        columns=[
            "ID Jurnal", "ID Dokumen", "Tanggal", "Nomor Bukti",
            "Kode Akun", "Nama Akun", "Debit", "Kredit",
        ]
    )

# HALAMAN LOGIN
if not st.session_state.authenticated_user:
    col_spacer1, col_center, col_spacer2 = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='text-align: center; color: #1E3A8A; font-size: 28px;"
            " white-space: nowrap;'>PT Banggai Sentral Sulawesi</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h4 style='text-align: center; color: #475569; font-size: 18px;"
            " margin-top: -10px;'>Dashboard Keuangan Terintegrasi</h4>",
            unsafe_allow_html=True,
        )
        with st.form("login_center_form"):
            u_input = st.text_input("Username", value="")
            p_input = st.text_input("Password", type="password", value="")
            st.markdown("<br>", unsafe_allow_html=True)
            b_login = st.form_submit_button("🔑 Masuk Sistem", use_container_width=True)

            if b_login:
                creds = st.session_state.credentials_dict
                if u_input in creds and creds[u_input]["pass"] == p_input:
                    st.session_state.authenticated_user = u_input
                    st.session_state.user_role = creds[u_input]["role"]
                    st.session_state.user_dept = creds[u_input]["dept"]
                    st.session_state.user_name = creds[u_input]["name"]
                    st.success("Autentikasi berhasil! Memuat sistem...")
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
    st.stop()

role_kini = st.session_state.user_role
dept_kini = st.session_state.user_dept
nama_kini = st.session_state.user_name

# SIDEBAR PANEL
with st.sidebar:
    st.title("🔐 Panel Akses PT BSS")
    st.success(f"Login: **{st.session_state.authenticated_user}**")
    st.write(f"Nama: **{nama_kini}**")
    st.write(f"Peran: **{role_kini}**")
    st.write(f"Departemen: **{dept_kini}**")
    st.markdown("---")

    if role_kini == "Programmer":
        with st.expander("⚙️ Manajemen Akun & Hak Akses", expanded=True):
            with st.form("sidebar_tambah_user"):
                st.markdown("**Tambah Akun Baru:**")
                new_name = st.text_input("Nama Lengkap (Kolom E)")
                new_username = st.text_input("Username (Kolom A)")
                new_password = st.text_input("Password (Kolom B)", type="password")
                new_role = st.selectbox(
                    "Hak Akses / Role (Kolom C)",
                    [
                        "Staf", "Kabag", "Kabag Keuangan", "Kasir",
                        "Accounting", "Manajer", "Programmer",
                    ],
                )
                new_dept = st.selectbox(
                    "Departemen (Kolom D)",
                    [
                        "Operasional", "HRD", "Logistik", "Maintenance",
                        "HSE", "Akuntansi", "Keuangan", "Manajemen", "IT / Pengembangan",
                    ],
                )
                btn_daftarkan = st.form_submit_button("➕ Daftarkan Akun", use_container_width=True)

                if btn_daftarkan:
                    if new_username and new_password and new_name:
                        if new_username in st.session_state.credentials_dict:
                            st.error("Username sudah terdaftar!")
                        else:
                            st.session_state.credentials_dict[new_username] = {
                                "pass": new_password, "role": new_role,
                                "dept": new_dept, "name": new_name,
                            }
                            save_users_to_excel()
                            st.success(f"Akun **{new_username}** berhasil didaftarkan!")
                            st.rerun()
                    else:
                        st.warning("Lengkapi Nama, Username, dan Password!")

        st.markdown("---")

    if st.button("🚪 Keluar (Logout)", use_container_width=True):
        st.session_state.authenticated_user = None
        st.session_state.user_role = None
        st.session_state.user_dept = None
        st.session_state.user_name = None
        st.rerun()

st.title("📊 Sistem Akuntansi Terintegrasi PT Banggai Sentral Sulawesi")
st.write(f"Dashboard Keuangan Berbasis Wewenang Aktif: `{role_kini} - {dept_kini}`")

# PENGATURAN MENU BERDASARKAN HIERARKI
if role_kini == "Staf":
    daftar_menu = ["Dashboard Utama", "Modul 1: Input Dokumen Operasional"]
elif role_kini == "Kabag":
    daftar_menu = ["Dashboard Utama", "Pusat Kendali & Approval Bertingkat"]
elif role_kini in ["Kabag Keuangan", "Kasir"]:
    daftar_menu = ["Dashboard Utama", "Pusat Kendali & Approval Bertingkat"]
elif role_kini == "Accounting":
    daftar_menu = [
        "Dashboard Utama",
        "Pusat Kendali & Approval Bertingkat",
        "Modul 2: Proses Penjurnalan Akuntansi",
        "Modul 3: Output Laporan Keuangan",
    ]
elif role_kini == "Manajer":
    daftar_menu = [
        "Dashboard Utama",
        "Pusat Kendali & Approval Bertingkat",
        "Modul 3: Output Laporan Keuangan",
    ]
else:  # Programmer
    daftar_menu = [
        "Dashboard Utama",
        "Modul 0: Pengaturan Master Akun & BU",
        "Modul 1: Input Dokumen Operasional",
        "Pusat Kendali & Approval Bertingkat",
        "Modul 2: Proses Penjurnalan Akuntansi",
        "Modul 3: Output Laporan Keuangan",
    ]

menu = st.sidebar.selectbox("Pilih Menu / Modul Utama", daftar_menu)

# ROUTING MENU UTAMA
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
    st.info(
        f"💡 **Status Akun:** Anda masuk sebagai **{role_kini}** ({nama_kini}) pada"
        f" Departemen **{dept_kini}**."
    )
elif menu == "Modul 0: Pengaturan Master Akun & BU":
    render_modul_0()
elif menu == "Modul 1: Input Dokumen Operasional":
    render_modul_1()
elif menu == "Pusat Kendali & Approval Bertingkat":
    render_pusat_kendali_kabag()
elif menu == "Modul 2: Proses Penjurnalan Akuntansi":
    render_modul_2()
elif menu == "Modul 3: Output Laporan Keuangan":
    render_modul_3()