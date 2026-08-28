import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

# 1. INISIALISASI SESSION STATE (Dinamis & Manual)
if 'master_coa' not in st.session_state or 'Sub Kategori' not in st.session_state.master_coa.columns:
    st.session_state.master_coa = pd.DataFrame([
        {"Kode Akun": "111001", "Nama Akun": "Kas Besar", "Sub Account": "Kas & Setara Kas", "Sub Kategori": "110000 - Kas Utama", "Kategori": "100000 - Aset Lancar"},
        {"Kode Akun": "410001", "Nama Akun": "Pendapatan Usaha", "Sub Account": "Pendapatan Jasa", "Sub Kategori": "410000 - Pendapatan Proyek", "Kategori": "400000 - Pendapatan"},
        {"Kode Akun": "511101", "Nama Akun": "GAJI KARYAWAN", "Sub Account": "511000 - UPAH LANGSUNG", "Sub Kategori": "510000 - PROYEK SEWA ALAT", "Kategori": "500000 BIAYA PROYEK"}
    ])

if 'master_bu' not in st.session_state:
    st.session_state.master_bu = pd.DataFrame([
        {"ID BU": "BU-01", "Nama Business Unit": "Operasional Kantor Pusat"},
        {"ID BU": "BU-02", "Nama Business Unit": "Proyek Drilling"},
        {"ID BU": "BU-03", "Nama Business Unit": "Proyek Well Services"},
        {"ID BU": "BU-04", "Nama Business Unit": "Proyek Slickline"}
    ])

if 'data_operasional' not in st.session_state:
    st.session_state.data_operasional = pd.DataFrame(columns=[
        "ID", "Tanggal", "Sumber Transaksi", "Nomor Bukti", "Business Unit", 
        "Jumlah", "Satuan", "Keterangan", "Peruntukan", "Nilai Uang", "Status Jurnal"
    ])

if 'data_jurnal' not in st.session_state:
    st.session_state.data_jurnal = pd.DataFrame(columns=[
        "ID Jurnal", "ID Dokumen", "Tanggal", "Nomor Bukti", "Kode Akun", "Nama Akun", "Debit", "Kredit"
    ])

st.title("📊 Sistem Akuntansi Terintegrasi PT Banggai Sentral Sulawesi")
st.write("Dashboard Pengelolaan Keuangan Berbasis Akun & Business Unit Dinamis.")

# Menu Navigasi Sidebar Sesuai Struktur Modul
menu = st.sidebar.selectbox("Pilih Menu / Modul Utama", [
    "Dashboard Utama",
    "Modul 0: Pengaturan Master Akun & BU",
    "Modul 1: Input Dokumen Operasional",
    "Modul 2: Proses Penjurnalan Akuntansi",
    "Modul 3: Output Laporan Keuangan"
])

# --- 1. DASHBOARD UTAMA ---
if menu == "Dashboard Utama":
    st.subheader("Ringkasan Sistem Keuangan")
    total_dok = len(st.session_state.data_operasional)
    total_jurnal = len(st.session_state.data_jurnal)
    total_nilai = st.session_state.data_operasional['Nilai Uang'].sum() if not st.session_state.data_operasional.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Dokumen Masuk", f"{total_dok} Item")
    col2.metric("Total Jurnal Tercatat", f"{total_jurnal} Baris")
    col3.metric("Total Nilai Transaksi", f"Rp {total_nilai:,.0f}")
    col4.metric("Status Sistem", "Offline Mode (Dinamis)")
    
    st.info("Gunakan Modul 0 untuk mengatur Input Account maupun Input Business Unit (Well Services, Slickline, Drilling, dll).")

# --- 2. MODUL 0: PENGATURAN MASTER (SUB MENU: INPUT ACCOUNT & INPUT BUSINESS UNIT) ---
elif menu == "Modul 0: Pengaturan Master Akun & BU":
    st.subheader("Modul 0: Pengaturan Master Data Perusahaan")
    
    # Sub menu pilihan di dalam Modul 0
    sub_modul = st.radio("Pilih Sub Menu Master:", ["Input Account / Kode Rekening", "Input Business Unit"], horizontal=True)
    st.divider()
    
    if sub_modul == "Input Account / Kode Rekening":
        st.markdown("### 📋 Daftar Kode Rekening (Dikelola Manual & Dinamis)")
        df_tampil_coa = st.session_state.master_coa[["Kategori", "Sub Kategori", "Sub Account", "Nama Akun", "Kode Akun"]]
        st.dataframe(df_tampil_coa, use_container_width=True)
        
        st.divider()
        st.markdown("### Kelola Data Akun (Save / Panggil Ulang / Update / Delete)")
        
        mode_coa = st.radio("Pilih Aksi Pengelolaan Akun", ["Tambah Akun Baru", "Koreksi / Edit / Hapus Akun yang Ada"], horizontal=True)
        
        if mode_coa == "Tambah Akun Baru":
            with st.form("form_tambah_akun"):
                col_1, col_2, col_3, col_4, col_5 = st.columns(5)
                with col_1:
                    kat_baru = st.text_input("Kategori (Cth: 500000 BIAYA PROYEK)")
                with col_2:
                    subkat_baru = st.text_input("Sub Kategori (Cth: 510000 - SEWA ALAT)")
                with col_3:
                    subacc_baru = st.text_input("Sub Account (Cth: 511000 - UPAH)")
                with col_4:
                    nama_baru = st.text_input("Nama Account (Cth: GAJI KARYAWAN)")
                with col_5:
                    kode_baru = st.text_input("Kode Akun (6 Digit)")
                
                btn_save = st.form_submit_button("💾 Save (Simpan Akun)")
                if btn_save and kode_baru and nama_baru:
                    if kode_baru in st.session_state.master_coa['Kode Akun'].values:
                        st.error(f"Kode Akun {kode_baru} sudah ada!")
                    else:
                        df_b = pd.DataFrame([{
                            "Kode Akun": kode_baru, "Nama Akun": nama_baru, 
                            "Sub Account": subacc_baru, "Sub Kategori": subkat_baru, "Kategori": kat_baru
                        }])
                        st.session_state.master_coa = pd.concat([st.session_state.master_coa, df_b], ignore_index=True)
                        st.success(f"Akun {kode_baru} berhasil disimpan!")
                        st.rerun()
        
        else: # Mode Edit / Delete Akun
            if not st.session_state.master_coa.empty:
                pilih_kode_edit = st.selectbox("Pilih Kode Akun untuk Dipanggil Ulang", st.session_state.master_coa['Kode Akun'].tolist())
                
                if pilih_kode_edit:
                    data_akun_pilih = st.session_state.master_coa[st.session_state.master_coa['Kode Akun'] == pilih_kode_edit].iloc[0]
                    
                    with st.form("form_edit_akun"):
                        ed_kat = st.text_input("Kategori", value=data_akun_pilih['Kategori'])
                        ed_subkat = st.text_input("Sub Kategori", value=data_akun_pilih['Sub Kategori'])
                        ed_subacc = st.text_input("Sub Account", value=data_akun_pilih['Sub Account'])
                        ed_nama = st.text_input("Nama Account", value=data_akun_pilih['Nama Akun'])
                        
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            btn_update = st.form_submit_button("🔄 Update (Perbarui Akun)")
                        with col_e2:
                            btn_delete = st.form_submit_button("🗑️ Delete (Hapus Akun)")
                            
                        if btn_update:
                            st.session_state.master_coa.loc[st.session_state.master_coa['Kode Akun'] == pilih_kode_edit, 'Kategori'] = ed_kat
                            st.session_state.master_coa.loc[st.session_state.master_coa['Kode Akun'] == pilih_kode_edit, 'Sub Kategori'] = ed_subkat
                            st.session_state.master_coa.loc[st.session_state.master_coa['Kode Akun'] == pilih_kode_edit, 'Sub Account'] = ed_subacc
                            st.session_state.master_coa.loc[st.session_state.master_coa['Kode Akun'] == pilih_kode_edit, 'Nama Akun'] = ed_nama
                            st.success(f"Akun {pilih_kode_edit} berhasil diperbarui!")
                            st.rerun()
                            
                        if btn_delete:
                            st.session_state.master_coa = st.session_state.master_coa[st.session_state.master_coa['Kode Akun'] != pilih_kode_edit]
                            st.success(f"Akun {pilih_kode_edit} berhasil dihapus!")
                            st.rerun()
            else:
                st.warning("Belum ada data master akun.")

    else: # Sub Menu: Input Business Unit
        st.markdown("### 🏢 Daftar Business Unit / Proyek (Well Services, Slickline, Drilling, dll)")
        st.dataframe(st.session_state.master_bu, use_container_width=True)
        
        st.divider()
        st.markdown("### Kelola Business Unit (Save / Update / Delete)")
        
        mode_bu = st.radio("Pilih Aksi Business Unit", ["Tambah BU Baru", "Koreksi / Edit / Hapus BU yang Ada"], horizontal=True)
        
        if mode_bu == "Tambah BU Baru":
            with st.form("form_tambah_bu"):
                id_bu_baru = st.text_input("ID Business Unit (Cth: BU-05)")
                nama_bu_baru = st.text_input("Nama Business Unit (Cth: Proyek Well Services)")
                
                btn_save_bu = st.form_submit_button("💾 Save (Simpan Business Unit)")
                if btn_save_bu and id_bu_baru and nama_bu_baru:
                    if id_bu_baru in st.session_state.master_bu['ID BU'].values:
                        st.error(f"ID Business Unit {id_bu_baru} sudah terdaftar!")
                    else:
                        df_bu_b = pd.DataFrame([{"ID BU": id_bu_baru, "Nama Business Unit": nama_bu_baru}])
                        st.session_state.master_bu = pd.concat([st.session_state.master_bu, df_bu_b], ignore_index=True)
                        st.success(f"Business Unit {id_bu_baru} berhasil disimpan!")
                        st.rerun()
        else:
            if not st.session_state.master_bu.empty:
                pilih_id_bu = st.selectbox("Pilih ID Business Unit untuk Dipanggil Ulang", st.session_state.master_bu['ID BU'].tolist())
                if pilih_id_bu:
                    data_bu_pilih = st.session_state.master_bu[st.session_state.master_bu['ID BU'] == pilih_id_bu].iloc[0]
                    
                    with st.form("form_edit_bu"):
                        ed_nama_bu = st.text_input("Nama Business Unit", value=data_bu_pilih['Nama Business Unit'])
                        
                        col_bu1, col_bu2 = st.columns(2)
                        with col_bu1:
                            btn_update_bu = st.form_submit_button("🔄 Update (Perbarui BU)")
                        with col_bu2:
                            btn_delete_bu = st.form_submit_button("🗑️ Delete (Hapus BU)")
                            
                        if btn_update_bu:
                            st.session_state.master_bu.loc[st.session_state.master_bu['ID BU'] == pilih_id_bu, 'Nama Business Unit'] = ed_nama_bu
                            st.success(f"Business Unit {pilih_id_bu} berhasil diperbarui!")
                            st.rerun()
                            
                        if btn_delete_bu:
                            st.session_state.master_bu = st.session_state.master_bu[st.session_state.master_bu['ID BU'] != pilih_id_bu]
                            st.success(f"Business Unit {pilih_id_bu} berhasil dihapus!")
                            st.rerun()
            else:
                st.warning("Belum ada data Business Unit.")

# --- 3. MODUL 1: INPUT DOKUMEN OPERASIONAL ---
elif menu == "Modul 1: Input Dokumen Operasional":
    st.subheader("Modul 1: Penginputan Dokumen Operasional Harian")
    
    sumber_transaksi = st.selectbox("Pilih Sumber Dokumen", [
        "Kas Besar / Kas Proyek", "Kas Kecil (Petty Cash)", "Bank Masuk / Keluar",
        "Logistik & Pengadaan Barang", "Gudang", "Memorial / Koreksi"
    ])
    
    list_bu_opt = st.session_state.master_bu['ID BU'] + " - " + st.session_state.master_bu['Nama Business Unit'] if not st.session_state.master_bu.empty else ["BU-01 - Default"]

    with st.form("form_modul1_input"):
        col_label, col_input = st.columns([1, 2])
        
        with col_label:
            st.markdown("<br>📅 **Tanggal Transaksi**", unsafe_allow_html=True)
            st.markdown("<br>🧾 **Nomor Bukti / Ref**", unsafe_allow_html=True)
            st.markdown("<br>🏢 **Business Unit / Proyek**", unsafe_allow_html=True)
            st.markdown("<br>📦 **Jumlah (Volume / Qty)**", unsafe_allow_html=True)
            st.markdown("<br>📏 **Satuan**", unsafe_allow_html=True)
            st.markdown("<br>🎯 **Peruntukan**", unsafe_allow_html=True)
            st.markdown("<br><br>📝 **Uraian / Keterangan**", unsafe_allow_html=True)
            st.markdown("<br><br>💰 **Nilai Uang (Rp)**", unsafe_allow_html=True)

        with col_input:
            tgl = st.date_input("Tanggal", datetime.now(), label_visibility="collapsed")
            no_bukti = st.text_input("No Bukti", placeholder="Nomor Bukti...", label_visibility="collapsed")
            bu_pilihan = st.selectbox("Business Unit", list_bu_opt, label_visibility="collapsed")
            jumlah = st.number_input("Jumlah", min_value=0.0, step=1.0, value=1.0, label_visibility="collapsed")
            satuan = st.text_input("Satuan", placeholder="Satuan...", label_visibility="collapsed")
            peruntukan = st.text_input("Peruntukan", placeholder="Peruntukan...", label_visibility="collapsed")
            keterangan = st.text_area("Keterangan", placeholder="Keterangan...", label_visibility="collapsed")
            nilai_uang = st.number_input("Nilai Uang", min_value=0.0, step=10000.0, label_visibility="collapsed")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            simpan_saja = st.form_submit_button("💾 Simpan Data Dokumen")
        with col_b2:
            simpan_tambah = st.form_submit_button("➕ Simpan & Tambah Baris Baru")

        if simpan_saja or simpan_tambah:
            if nilai_uang > 0 and no_bukti:
                id_baru = f"DOC-{int(datetime.now().timestamp())}"
                data_baru = {
                    "ID": id_baru, "Tanggal": tgl, "Sumber Transaksi": sumber_transaksi,
                    "Nomor Bukti": no_bukti, "Business Unit": bu_pilihan, "Jumlah": jumlah,
                    "Satuan": satuan, "Keterangan": keterangan, "Peruntukan": peruntukan,
                    "Nilai Uang": nilai_uang, "Status Jurnal": "Belum Dijurnal"
                }
                st.session_state.data_operasional = pd.concat([
                    st.session_state.data_operasional, pd.DataFrame([data_baru])
                ], ignore_index=True)
                st.success("Dokumen berhasil disimpan!")
            else:
                st.error("Mohon lengkapi Nomor Bukti dan Nilai Uang.")

    if not st.session_state.data_operasional.empty:
        st.dataframe(st.session_state.data_operasional, use_container_width=True)

# --- 4. MODUL 2: PROSES PENJURNALAN AKUNTANSI ---
elif menu == "Modul 2: Proses Penjurnalan Akuntansi":
    st.subheader("Modul 2: Proses Penjurnalan Akuntansi")
    
    df_op = st.session_state.data_operasional
    if not df_op.empty:
        st.dataframe(df_op, use_container_width=True)
        
        id_pilih = st.selectbox("Pilih ID Dokumen untuk Dijurnal", df_op['ID'].tolist())
        dok_terpilih = df_op[df_op['ID'] == id_pilih].iloc[0]
        
        list_akun_opt = st.session_state.master_coa['Kode Akun'] + " - " + st.session_state.master_coa['Nama Akun'] if not st.session_state.master_coa.empty else ["-"]
        
        with st.form("form_proses_jurnal"):
            col_j1, col_j2 = st.columns(2)
            with col_j1:
                akun_debit = st.selectbox("Pilih Akun DEBIT", list_akun_opt)
            with col_j2:
                akun_kredit = st.selectbox("Pilih Akun KREDIT", list_akun_opt)
                
            nominal_jurnal = st.number_input("Nominal Jurnal (Rp)", value=float(dok_terpilih['Nilai Uang']), step=1000.0)
            submit_jurnal = st.form_submit_button("⚖️ Posting Jurnal")
            
            if submit_jurnal:
                id_jrn = f"JRN-{int(datetime.now().timestamp())}"
                baris_d = {
                    "ID Jurnal": id_jrn, "ID Dokumen": id_pilih, "Tanggal": dok_terpilih['Tanggal'],
                    "Nomor Bukti": dok_terpilih['Nomor Bukti'], "Kode Akun": akun_debit.split(" - ")[0],
                    "Nama Akun": akun_debit.split(" - ")[1] if " - " in akun_debit else akun_debit, "Debit": nominal_jurnal, "Kredit": 0.0
                }
                baris_k = {
                    "ID Jurnal": id_jrn, "ID Dokumen": id_pilih, "Tanggal": dok_terpilih['Tanggal'],
                    "Nomor Bukti": dok_terpilih['Nomor Bukti'], "Kode Akun": akun_kredit.split(" - ")[0],
                    "Nama Akun": akun_kredit.split(" - ")[1] if " - " in akun_kredit else akun_kredit, "Debit": 0.0, "Kredit": nominal_jurnal
                }
                st.session_state.data_jurnal = pd.concat([
                    st.session_state.data_jurnal, pd.DataFrame([baris_d, baris_k])
                ], ignore_index=True)
                st.session_state.data_operasional.loc[st.session_state.data_operasional['ID'] == id_pilih, 'Status Jurnal'] = 'Sudah Dijurnal'
                st.success("Jurnal berhasil diposting!")
                st.rerun()
                
        if not st.session_state.data_jurnal.empty:
            st.dataframe(st.session_state.data_jurnal, use_container_width=True)
    else:
        st.warning("Belum ada dokumen untuk dijurnal.")

# --- 5. MODUL 3: OUTPUT LAPORAN KEUANGAN ---
elif menu == "Modul 3: Output Laporan Keuangan":
    st.subheader("Modul 3: Output Laporan Keuangan Dinamis")
    
    df_jrn = st.session_state.data_jurnal
    if not df_jrn.empty:
        tab_laba, tab_neraca, tab_buku = st.tabs(["Laporan Laba Rugi", "Posisi Neraca", "Buku Besar"])
        
        with tab_laba:
            st.markdown("### Laporan Laba Rugi")
            df_pend = df_jrn[df_jrn['Kode Akun'].astype(str).str.startswith('4')]
            df_biy = df_jrn[df_jrn['Kode Akun'].astype(str).str.startswith('5')]
            
            tot_pend = df_pend['Kredit'].sum() - df_pend['Debit'].sum()
            tot_biy = df_biy['Debit'].sum() - df_biy['Kredit'].sum()
            laba_bersih = tot_pend - tot_biy
            
            st.metric("Total Pendapatan", f"Rp {tot_pend:,.0f}")
            st.metric("Total Biaya Proyek", f"Rp {tot_biy:,.0f}")
            st.divider()
            if laba_bersih >= 0:
                st.success(f"### Laba Bersih: Rp {laba_bersih:,.0f}")
            else:
                st.error(f"### Rugi Bersih: Rp {laba_bersih:,.0f}")
                
        with tab_neraca:
            st.markdown("### Posisi Keuangan / Neraca")
            df_aktiva = df_jrn[df_jrn['Kode Akun'].astype(str).str.startswith('1')]
            tot_aktiva = df_aktiva['Debit'].sum() - df_aktiva['Kredit'].sum()
            st.metric("Total Aktiva / Aset", f"Rp {tot_aktiva:,.0f}")
            
        with tab_buku:
            st.markdown("### Buku Besar Per Akun")
            pilih_akun_gl = st.selectbox("Pilih Akun", df_jrn['Kode Akun'] + " - " + df_jrn['Nama Akun'])
            if pilih_akun_gl:
                kode_gl = pilih_akun_gl.split(" - ")[0]
                df_gl_filtered = df_jrn[df_jrn['Kode Akun'] == kode_gl]
                st.dataframe(df_gl_filtered, use_container_width=True)
    else:
        st.info("Belum ada data jurnal untuk menampilkan laporan.")