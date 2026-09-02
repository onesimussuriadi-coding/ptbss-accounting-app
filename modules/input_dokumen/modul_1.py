from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

EXCEL_DB_PATH = "database_transaksi_bss.xlsx"

def load_persistent_data():
    """Memuat data transaksi secara permanen dari file Excel tanpa modifikasi otomatis."""
    if "data_operasional" not in st.session_state:
        if os.path.exists(EXCEL_DB_PATH):
            try:
                st.session_state.data_operasional = pd.read_excel(EXCEL_DB_PATH)
            except Exception:
                st.session_state.data_operasional = pd.DataFrame(columns=[
                    "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
                    "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
                    "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
                    "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Catatan Revisi", "Raw_Items"
                ])
        else:
            st.session_state.data_operasional = pd.DataFrame(columns=[
                "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
                "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
                "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
                "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Catatan Revisi", "Raw_Items"
            ])
            
    # Normalisasi format Tanggal agar aman dari error Arrow type conversion
    if not st.session_state.data_operasional.empty and "Tanggal" in st.session_state.data_operasional.columns:
        st.session_state.data_operasional["Tanggal"] = pd.to_datetime(st.session_state.data_operasional["Tanggal"], errors='coerce').dt.strftime('%Y-%m-%d').fillna("-")

    if "Catatan Revisi" not in st.session_state.data_operasional.columns:
        st.session_state.data_operasional["Catatan Revisi"] = ""
    if "Raw_Items" not in st.session_state.data_operasional.columns:
        st.session_state.data_operasional["Raw_Items"] = ""

def save_persistent_data():
    """Menyimpan data secara permanen ke file Excel."""
    try:
        st.session_state.data_operasional.to_excel(EXCEL_DB_PATH, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan ke file permanen: {e}")

def render_modul_1():
    load_persistent_data()

    if "modul1_verified" not in st.session_state:
        st.session_state.modul1_verified = False
    if "modul1_dept" not in st.session_state:
        st.session_state.modul1_dept = None
    if "modul1_user" not in st.session_state:
        st.session_state.modul1_user = None

    st.subheader("Modul 1: Penginputan Dokumen & Manajemen Persetujuan (Workflow)")
    st.markdown("---")

    if not st.session_state.modul1_verified:
        col_spacer1, col_box, col_spacer2 = st.columns([1, 2, 1])
        with col_box:
            st.markdown("<h4 style='text-align: center; color: #1E3A8A;'>🔐 Verifikasi Akses Penginputan</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748B; font-size: 13px;'>Silakan pilih departemen dan masukkan Username atau Nama Lengkap terdaftar Anda.</p>", unsafe_allow_html=True)

            with st.form("form_verifikasi_modul1_lokal"):
                dept_list = [
                    "-- Pilih Departemen Tujuan --",
                    "Operasional", "HRD", "Logistik", "Maintenance",
                    "HSE", "Akuntansi", "Keuangan",
                ]
                pilih_dept = st.selectbox("Departemen Tujuan", dept_list)
                input_username = st.text_input("Username / Nama Penginput", placeholder="Ketik username atau nama terdaftar...")

                st.markdown("<br>", unsafe_allow_html=True)
                btn_verif = st.form_submit_button("🚀 Masuk ke Form Penginputan", use_container_width=True)

                if btn_verif:
                    if pilih_dept == "-- Pilih Departemen Tujuan --":
                        st.error("Mohon pilih Departemen Tujuan terlebih dahulu!")
                    elif not input_username.strip():
                        st.error("Username atau Nama penginput tidak boleh kosong!")
                    else:
                        clean_input = input_username.strip().lower()
                        creds = st.session_state.get("credentials_dict", {})

                        ditemukan = False
                        nama_terverifikasi = ""

                        for uname, details in creds.items():
                            stored_user = str(uname).strip().lower()
                            stored_name = str(details.get("name", "")).strip().lower()
                            stored_dept = str(details.get("dept", "")).strip().lower()

                            if clean_input == stored_user or clean_input == stored_name:
                                if (
                                    stored_dept == pilih_dept.lower()
                                    or details.get("role") == "Programmer"
                                    or "admin" in clean_input
                                ):
                                    ditemukan = True
                                    nama_terverifikasi = details.get("name", input_username)
                                    break

                        if ditemukan:
                            st.session_state.modul1_verified = True
                            st.session_state.modul1_dept = pilih_dept
                            st.session_state.modul1_user = nama_terverifikasi
                            st.success(f"Verifikasi sukses! Membuka akses untuk **{nama_terverifikasi} ({pilih_dept})**...")
                            st.rerun()
                        else:
                            st.error(f"❌ Akses Ditolak: '{input_username}' tidak terdaftar atau tidak sesuai pada departemen **{pilih_dept}**.")
        return

    col_info, col_out = st.columns([4, 1])
    with col_info:
        st.info(f"👤 Penginput Aktif: **{st.session_state.modul1_user}** | 🏢 Departemen Tujuan: **{st.session_state.modul1_dept}**")
    with col_out:
        if st.button("🔄 Ganti Sesi", use_container_width=True):
            st.session_state.modul1_verified = False
            st.session_state.modul1_dept = None
            st.session_state.modul1_user = None
            st.rerun()

    st.markdown("---")

    from modules.input_dokumen.gudang_persediaan import render_gudang_persediaan
    from modules.input_dokumen.invoice_penjualan import render_invoice_penjualan
    from modules.input_dokumen.kas_bank_keluar import render_kas_bank_keluar
    from modules.input_dokumen.kas_bank_masuk import render_kas_bank_masuk
    from modules.input_dokumen.memorial_koreksi import render_memorial_koreksi
    from modules.input_dokumen.pembelian_kredit import render_pembelian_kredit

    penginput_saat_ini = st.session_state.modul1_user
    dept_saat_ini = st.session_state.modul1_dept

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📂 Menu Data Mandiri")
        st.markdown(f"<p style='font-size:12px; color:#64748B;'>Pengguna: <b>{penginput_saat_ini}</b></p>", unsafe_allow_html=True)
        menu_data_tersimpan = st.toggle("📂 Kelola / Lihat Data Tersimpan", value=False, key="toggle_kelola_data")

    # Pembacaan Master COA akun kas berawalan "111"
    list_kas_111 = []
    if os.path.exists("master_coa_bss.xlsx"):
        try:
            df_coa = pd.read_excel("master_coa_bss.xlsx")
            df_coa.columns = df_coa.columns.str.replace("\xa0", " ").str.strip()
            col_kode = df_coa.columns[0]
            col_nama = df_coa.columns[1] if len(df_coa.columns) > 1 else df_coa.columns[0]
            mask_111 = df_coa[col_kode].astype(str).str.startswith("111")
            df_filtered = df_coa[mask_111]
            if not df_filtered.empty:
                list_kas_111 = (
                    df_filtered[col_kode].astype(str).str.strip()
                    + " - "
                    + df_filtered[col_nama].astype(str).str.strip()
                ).tolist()
        except Exception:
            pass

    if not list_kas_111:
        list_kas_111 = [
            "1110.001 - Kas Besar Luwuk",
            "1110.002 - Kas Operasional Surabaya",
            "1110.003 - Kas Operasional Jakarta",
            "1110.012 - Kas Kecil",
            "1110.013 - Kas Proyek CR Umum",
            "1110.014 - Kas Proyek GS Umum",
            "1110.031 - Kas Top Up Tiket Pesawat"
        ]

    if menu_data_tersimpan:
        st.markdown("## 📋 Dashboard Manajemen & Distribusi Dokumen")
        st.markdown(f"Berikut adalah daftar dokumen yang diinput oleh **{penginput_saat_ini}**. Anda dapat melakukan **Panggil Ulang (Edit/Update)**, **Hapus**, atau **Distribusi Berjenjang** ke meja Kepala Bagian.")
        st.markdown("---")

        df_all_ops = st.session_state.data_operasional
        if not df_all_ops.empty and "Nama Penginput" in df_all_ops.columns:
            df_user_milik_sendiri = df_all_ops[
                df_all_ops["Nama Penginput"].str.lower() == penginput_saat_ini.lower()
            ].copy()
        else:
            df_user_milik_sendiri = pd.DataFrame(columns=df_all_ops.columns)

        if df_user_milik_sendiri.empty:
            st.info("ℹ️ Belum ada data dokumen yang tersimpan atas nama Anda.")
        else:
            kolom_tampil = [
                col for col in ["Nomor Bukti", "Sumber Transaksi", "Total", "Status Dokumen", "Catatan Revisi", "Tanggal"]
                if col in df_user_milik_sendiri.columns
            ]
            st.dataframe(df_user_milik_sendiri[kolom_tampil], use_container_width=True)

            df_revisi_check = df_user_milik_sendiri[
                df_user_milik_sendiri["Status Dokumen"].str.contains("Ditolak|Revisi", case=False, na=False)
            ]
            if not df_revisi_check.empty:
                st.warning("⚠️ **Perhatian:** Terdapat dokumen yang memerlukan koreksi/revisi dari Kepala Bagian. Silakan periksa kolom **Catatan Revisi** di atas atau lakukan **Panggil Ulang (Edit)** untuk memperbaikinya.")

            st.markdown("### 🚀 Distribusi Dokumen Berjenjang ke Kepala Bagian")
            st.markdown("<p style='font-size:12px; color:#64748B;'>Pilih nomor bukti dokumen yang sudah diverifikasi, lalu klik tombol submit untuk menaikkan status approval ke Kepala Bagian.</p>", unsafe_allow_html=True)
            
            list_bukti_user = df_user_milik_sendiri["Nomor Bukti"].tolist()
            
            col_dis1, col_dis2 = st.columns([2, 1])
            with col_dis1:
                pilih_bukti_distribusi = st.selectbox(
                    "Pilih No Bukti untuk Didistribusikan", 
                    ["-- Pilih Nomor Bukti --"] + list_bukti_user,
                    key="select_distribusi_kbk"
                )
            with col_dis2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📤 Submit / Distribusikan ke Kabag", use_container_width=True):
                    if pilih_bukti_distribusi != "-- Pilih Nomor Bukti --":
                        mask = st.session_state.data_operasional["Nomor Bukti"] == pilih_bukti_distribusi
                        st.session_state.data_operasional.loc[mask, "Status Dokumen"] = f"Menunggu Approval Kepala Bagian {dept_saat_ini}"
                        save_persistent_data()
                        st.success(f"Dokumen **{pilih_bukti_distribusi}** berhasil disubmit dan didistribusikan ke Kepala Bagian!")
                        st.rerun()
                    else:
                        st.warning("Pilih Nomor Bukti terlebih dahulu untuk didistribusikan.")

            st.markdown("---")
            st.markdown("### 🛠️ Aksi Panggil Ulang (Edit) atau Hapus Dokumen")
            
            col_pil, col_btn_edit, col_btn_hapus = st.columns([2, 1, 1])
            with col_pil:
                pilih_aksi_bukti = st.selectbox("Pilih Berdasarkan Nomor Bukti untuk Edit", ["-- Pilih Nomor Bukti --"] + list_bukti_user, key="select_edit_kbk")
            
            with col_btn_edit:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📥 Panggil Ulang (Edit)", use_container_width=True):
                    if pilih_aksi_bukti != "-- Pilih Nomor Bukti --":
                        row_pilih = df_user_milik_sendiri[
                            df_user_milik_sendiri["Nomor Bukti"] == pilih_aksi_bukti
                        ].iloc[0]
                        st.session_state.edit_mode_active = True
                        st.session_state.edit_data_temp = row_pilih.to_dict()
                        st.success(f"Nomor Bukti **{pilih_aksi_bukti}** berhasil dimuat!")
                        st.info("💡 Matikan toggle 'Kelola / Lihat Data Tersimpan' di sidebar untuk melihat form edit.")
                    else:
                        st.warning("Pilih Nomor Bukti terlebih dahulu.")

            with col_btn_hapus:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Hapus Dokumen", use_container_width=True):
                    if pilih_aksi_bukti != "-- Pilih Nomor Bukti --":
                        st.session_state.data_operasional = st.session_state.data_operasional[
                            st.session_state.data_operasional["Nomor Bukti"] != pilih_aksi_bukti
                        ]
                        save_persistent_data()
                        st.success(f"Nomor Bukti '{pilih_aksi_bukti}' berhasil dihapus!")
                        st.rerun()
                    else:
                        st.warning("Pilih Nomor Bukti yang ingin dihapus.")
                        
        st.markdown("---")
        if st.button("🔙 Kembali ke Form Input Utama"):
            if "toggle_kelola_data" in st.session_state:
                del st.session_state.toggle_kelola_data
            st.rerun()
        return

    role_aktif = st.session_state.get("user_role", "")
    is_edit_mode = st.session_state.get("edit_mode_active", False)
    edit_data = st.session_state.get("edit_data_temp", {})

    if role_aktif == "Programmer":
        list_sumber_opsi = list_kas_111 + [
            "Tagihan / Pembelian Kredit (Hutang Usaha)",
            "Gudang",
            "Kas Bank Masuk (Penerimaan Dana)",
            "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)",
            "Memorial / Koreksi",
        ]
    elif dept_saat_ini == "Logistik":
        list_sumber_opsi = list_kas_111 + [
            "Tagihan / Pembelian Kredit (Hutang Usaha)",
            "Gudang",
        ]
    else:
        list_sumber_opsi = list_kas_111

    if is_edit_mode:
        st.warning(f"⚠️ **MODE EDIT AKTIF (No. Bukti: {edit_data.get('Nomor Bukti')})**: Sumber akun disesuaikan otomatis mengikuti data yang dipanggil.")
        if st.button("❌ Batalkan Mode Edit"):
            st.session_state.edit_mode_active = False
            if "edit_data_temp" in st.session_state:
                del st.session_state.edit_data_temp
            st.rerun()

        sumber_tercatat = str(edit_data.get("Sumber Transaksi", ""))
        default_idx = 0
        for i, opt in enumerate(list_sumber_opsi):
            if opt.split(" - ")[0].strip() in sumber_tercatat or sumber_tercatat.lower() in opt.lower():
                default_idx = i
                break

        sumber_transaksi = st.selectbox(
            f"Pilih Sumber Dokumen / Akun Kas ({dept_saat_ini})",
            list_sumber_opsi,
            index=default_idx,
            key="selectbox_sumber_trx_edit",
        )
    else:
        sumber_transaksi = st.selectbox(
            f"Pilih Sumber Dokumen / Akun Kas ({dept_saat_ini})",
            list_sumber_opsi,
            key="selectbox_sumber_trx_normal",
        )

    st.markdown("---")

    if sumber_transaksi == "Tagihan / Pembelian Kredit (Hutang Usaha)":
        render_pembelian_kredit()
    elif sumber_transaksi == "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)":
        render_invoice_penjualan()
    elif sumber_transaksi == "Kas Bank Masuk (Penerimaan Dana)":
        render_kas_bank_masuk()
    elif sumber_transaksi in list_kas_111 or sumber_transaksi.startswith("111"):
        render_kas_bank_keluar()
    elif sumber_transaksi == "Gudang":
        render_gudang_persediaan()
    elif sumber_transaksi == "Memorial / Koreksi":
        render_memorial_koreksi()