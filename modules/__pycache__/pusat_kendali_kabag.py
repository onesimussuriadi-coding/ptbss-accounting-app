import os
import pandas as pd
import streamlit as st

EXCEL_DB_PATH = "database_transaksi_bss.xlsx"

def load_persistent_data():
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

def save_persistent_data():
    try:
        st.session_state.data_operasional.to_excel(EXCEL_DB_PATH, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan ke file permanen: {e}")

def render_pusat_kendali_kabag():
    load_persistent_data()

    # Inisialisasi state verifikasi khusus Kabag
    if "kabag_verified" not in st.session_state:
        st.session_state.kabag_verified = False
    if "kabag_dept" not in st.session_state:
        st.session_state.kabag_dept = ""
    if "kabag_user" not in st.session_state:
        st.session_state.kabag_user = ""

    # FORM VERIFIKASI AKSES (SERUPA DENGAN MODUL 1 ADMIN/STAF)
    if not st.session_state.kabag_verified:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col_center, col2 = st.columns([1, 1.8, 1])
        
        with col_center:
            st.markdown("""
                <div style='text-align: center; padding: 15px;'>
                    <h2 style='color: #1E3A8A; margin-bottom: 5px;'>🔐 Verifikasi Akses Pusat Kendali Kabag</h2>
                    <p style='color: #64748B; font-size: 14px;'>Silakan pilih departemen wewenang dan masukkan Username atau Nama Lengkap Anda.</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_verifikasi_akses_kabag"):
                daftar_dept = [
                    "Operasional",
                    "HRD",
                    "Logistik",
                    "Maintenance",
                    "HSE",
                    "Akuntansi",
                    "Keuangan",
                    "Manajemen"
                ]
                
                # Default pilihan departemen sesuai akun login aktif jika ada
                default_dept_user = st.session_state.get("user_dept", "Operasional")
                idx_default = 0
                if default_dept_user in daftar_dept:
                    idx_default = daftar_dept.index(default_dept_user)

                pilih_dept = st.selectbox("Departemen Tujuan / Wewenang", daftar_dept, index=idx_default)
                input_user = st.text_input("Username / Nama Lengkap Pengguna", value=st.session_state.get("user_name", st.session_state.get("authenticated_user", "")))
                
                st.markdown("<br>", unsafe_allow_html=True)
                btn_verif = st.form_submit_button("🚀 Masuk ke Pusat Kendali Kabag", use_container_width=True)
                
                if btn_verif:
                    if input_user.strip():
                        st.session_state.kabag_verified = True
                        st.session_state.kabag_dept = pilih_dept
                        st.session_state.kabag_user = input_user.strip()
                        st.success("Verifikasi akses berhasil! Memuat dashboard...")
                        st.rerun()
                    else:
                        st.warning("Mohon isi Username atau Nama Lengkap Anda.")
        return

    # JIKA SUDAH TERVERIFIKASI, TAMPILKAN DASHBOARD APPROVAL
    active_dept = st.session_state.kabag_dept
    active_user = st.session_state.kabag_user

    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.subheader(f"📂 Pusat Kendali Dokumen & Workflow Berjenjang ({active_dept})")
        st.info(f"Kepala Bagian Aktif: **{active_user}** | Wewenang Divisi: **{active_dept}**")
    with c_head2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset / Ganti Akses", use_container_width=True):
            st.session_state.kabag_verified = False
            st.rerun()

    st.markdown("---")

    df_ops = st.session_state.data_operasional
    if df_ops.empty:
        st.info("Belum ada dokumen operasional yang tersimpan di sistem.")
        return

    # Filter dokumen berdasarkan departemen tujuan yang dipilih pada verifikasi
    if "Status Dokumen" in df_ops.columns and "Departemen Tujuan" in df_ops.columns:
        df_pusat = df_ops[
            df_ops["Departemen Tujuan"].str.lower() == active_dept.lower()
        ]
    else:
        df_pusat = pd.DataFrame(columns=df_ops.columns)

    if not df_pusat.empty:
        st.dataframe(df_pusat, use_container_width=True)
        st.markdown("---")
        
        list_nobukti = df_pusat["Nomor Bukti"].tolist()
        pilih_bukti = st.selectbox("Pilih Nomor Bukti untuk Diproses", ["-- Pilih --"] + list_nobukti)

        if pilih_bukti != "-- Pilih --":
            row = df_pusat[df_pusat["Nomor Bukti"] == pilih_bukti].iloc[0]
            st.write(f"Status Dokumen Saat Ini: **{row.get('Status Dokumen', 'Menunggu Approval')}**")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Approve Dokumen", use_container_width=True):
                    mask = st.session_state.data_operasional["Nomor Bukti"] == pilih_bukti
                    st.session_state.data_operasional.loc[mask, "Status Dokumen"] = f"Disetujui Kabag {active_dept} ➡️ Menunggu Verifikasi Akuntansi"
                    save_persistent_data()
                    st.success(f"Dokumen **{pilih_bukti}** berhasil disetujui!")
                    st.rerun()
            with c2:
                if st.button("❌ Tolak / Revisi", use_container_width=True):
                    mask = st.session_state.data_operasional["Nomor Bukti"] == pilih_bukti
                    st.session_state.data_operasional.loc[mask, "Status Dokumen"] = f"Ditolak Kabag {active_dept} (Perlu Revisi)"
                    save_persistent_data()
                    st.error(f"Dokumen **{pilih_bukti}** ditolak dan dikembalikan.")
                    st.rerun()
    else:
        st.warning(f"Tidak ada dokumen yang masuk untuk departemen **{active_dept}**.")