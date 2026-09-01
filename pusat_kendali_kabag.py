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

    # Inisialisasi session state verifikasi khusus Kabag
    if "kabag_verified" not in st.session_state:
        st.session_state.kabag_verified = False
    if "kabag_dept" not in st.session_state:
        st.session_state.kabag_dept = ""
    if "kabag_user" not in st.session_state:
        st.session_state.kabag_user = ""

    # =========================================================================
    # FORM VERIFIKASI AKSES PENGINPUTAN (SEPERTI DI MODUL 1)
    # =========================================================================
    if not st.session_state.kabag_verified:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col_center, col2 = st.columns([1, 1.8, 1])
        
        with col_center:
            st.markdown("""
                <div style='text-align: center; padding: 10px;'>
                    <h2 style='color: #1E3A8A; margin-bottom: 5px;'>🔐 Verifikasi Akses Pusat Kendali</h2>
                    <p style='color: #64748B; font-size: 14px;'>Silakan pilih departemen tujuan dan masukkan Username atau Nama Lengkap Kabag.</p>
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
                    "Manajemen",
                    "IT / Pengembangan"
                ]
                
                default_dept_user = st.session_state.get("user_dept", "Operasional")
                idx_default = 0
                if default_dept_user in daftar_dept:
                    idx_default = daftar_dept.index(default_dept_user)

                pilih_dept = st.selectbox("Departemen Tujuan / Wewenang", daftar_dept, index=idx_default)
                input_user = st.text_input("Username / Nama Penginput", value=st.session_state.get("user_name", st.session_state.get("authenticated_user", "")))
                
                st.markdown("<br>", unsafe_allow_html=True)
                btn_verif = st.form_submit_button("🚀 Masuk ke Pusat Kendali", use_container_width=True)
                
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

    # =========================================================================
    # DASHBOARD UTAMA PUSAT KENDALI KABAG SETELAH TERVERIFIKASI
    # =========================================================================
    active_dept = st.session_state.kabag_dept
    active_user = st.session_state.kabag_user

    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.subheader(f"📂 Pusat Kendali & Approval Berjenjang ({active_dept})")
        st.info(f"Kepala Bagian Aktif: **{active_user}** | Wewenang Divisi: **{active_dept}**")
    with c_head2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Ganti Akses / Departemen", use_container_width=True):
            st.session_state.kabag_verified = False
            st.rerun()

    st.markdown("---")

    df_ops = st.session_state.data_operasional
    if df_ops.empty:
        st.info("ℹ️ Belum ada data dokumen operasional yang tersimpan di sistem.")
        return

    # Filter dokumen berdasarkan Departemen Tujuan yang dipilih
    if "Status Dokumen" in df_ops.columns and "Departemen Tujuan" in df_ops.columns:
        df_approval_kabag = df_ops[
            (
                df_ops["Status Dokumen"].str.contains(f"Kepala Bagian {active_dept}", case=False, na=False) |
                df_ops["Status Dokumen"].str.contains(f"Menunggu Approval.*{active_dept}", case=False, na=False)
            ) & 
            (
                df_ops["Departemen Tujuan"].str.lower() == active_dept.lower()
            )
        ]
    else:
        df_approval_kabag = pd.DataFrame(columns=df_ops.columns)

    if df_approval_kabag.empty:
        st.success(f"🎉 Tidak ada dokumen pending yang menunggu approval untuk Divisi **{active_dept}** saat ini.")
        
        st.markdown("---")
        st.markdown(f"### 📚 Riwayat Dokumen Masuk Divisi {active_dept}")
        if "Departemen Tujuan" in df_ops.columns:
            df_riwayat = df_ops[df_ops["Departemen Tujuan"].str.lower() == active_dept.lower()]
            if not df_riwayat.empty:
                kolom_riwayat = [c for c in ["Nomor Bukti", "Sumber Transaksi", "Total", "Status Dokumen", "Tanggal", "Nama Penginput"] if c in df_riwayat.columns]
                st.dataframe(df_riwayat[kolom_riwayat], use_container_width=True)
        return

    st.markdown(f"### 📋 Daftar Dokumen Masuk Pending Approval ({active_dept})")
    
    kolom_tampil = [
        col for col in ["Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi", "Total", "Status Dokumen", "Nama Penginput"]
        if col in df_approval_kabag.columns
    ]
    st.dataframe(df_approval_kabag[kolom_tampil], use_container_width=True)

    st.markdown("---")
    st.markdown("### ✍️ Panel Aksi Verifikasi & Approval Kabag")
    
    list_nomor_bukti = df_approval_kabag["Nomor Bukti"].tolist()
    
    col_pilih, col_app, col_tolak = st.columns([2, 1, 1])
    with col_pilih:
        pilih_dokumen = st.selectbox("Pilih Nomor Bukti Dokumen", ["-- Pilih Nomor Bukti --"] + list_nomor_bukti, key=f"sel_approval_kabag_{active_dept}")
    
    with col_app:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Approve Dokumen", use_container_width=True, key=f"btn_app_{active_dept}"):
            if pilih_dokumen != "-- Pilih Nomor Bukti --":
                mask = st.session_state.data_operasional["Nomor Bukti"] == pilih_dokumen
                st.session_state.data_operasional.loc[mask, "Status Dokumen"] = f"Disetujui Kabag {active_dept} - Menunggu Verifikasi Akuntansi"
                save_persistent_data()
                st.success(f"Dokumen **{pilih_dokumen}** berhasil di-Approve dan diteruskan ke bagian Akuntansi!")
                st.rerun()
            else:
                st.warning("Pilih Nomor Bukti dokumen.")

    with col_tolak:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("❌ Tolak / Revisi", use_container_width=True, key=f"btn_tolak_{active_dept}"):
            if pilih_dokumen != "-- Pilih Nomor Bukti --":
                mask = st.session_state.data_operasional["Nomor Bukti"] == pilih_dokumen
                st.session_state.data_operasional.loc[mask, "Status Dokumen"] = f"Ditolak Kabag {active_dept} (Perlu Revisi)"
                save_persistent_data()
                st.error(f"Dokumen **{pilih_dokumen}** ditolak dan dikembalikan.")
                st.rerun()
            else:
                st.warning("Pilih Nomor Bukti dokumen.")