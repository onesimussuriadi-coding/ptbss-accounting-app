import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

# 1. INISIALISASI SESSION STATE (Master Akun, Business Unit, dan Data Transaksi)
if 'master_coa' not in st.session_state:
    st.session_state.master_coa = pd.DataFrame([
        {"Kode Akun": "11101", "Nama Akun": "Kas Besar", "Kategori": "Aktiva Lancar"},
        {"Kode Akun": "11102", "Nama Akun": "Kas Proyek", "Kategori": "Aktiva Lancar"},
        {"Kode Akun": "11103", "Nama Akun": "Kas Kecil (Petty Cash)", "Kategori": "Aktiva Lancar"},
        {"Kode Akun": "11200", "Nama Akun": "Bank Utama (Operasional)", "Kategori": "Aktiva Lancar"},
        {"Kode Akun": "11300", "Nama Akun": "Piutang Usaha", "Kategori": "Aktiva Lancar"},
        {"Kode Akun": "21100", "Nama Akun": "Hutang Usaha", "Kategori": "Kewajiban Lancar"},
        {"Kode Akun": "31100", "Nama Akun": "Modal Disetor", "Kategori": "Ekuitas"},
        {"Kode Akun": "41100", "Nama Akun": "Pendapatan Kontrak / Jasa", "Kategori": "Pendapatan"},
        {"Kode Akun": "51100", "Nama Akun": "Pembelian Material / Logistik", "Kategori": "Biaya / HPP"},
        {"Kode Akun": "61100", "Nama Akun": "Biaya Gaji Karyawan", "Kategori": "Biaya Operasional"},
        {"Kode Akun": "61200", "Nama Akun": "Biaya Sewa Alat & Operasional", "Kategori": "Biaya Operasional"}
    ])

if 'master_bu' not in st.session_state:
    st.session_state.master_bu = [
        "BU-01 - Operasional Kantor Pusat",
        "BU-02 - Proyek Senoro-Toili (JOB Pertamina-Medco)",
        "BU-03 - Sektor Logistik & Heavy Equipment",
        "BU-04 - Gudang & Pengadaan Umum"
    ]

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
st.write("Dashboard Pengelolaan Keuangan Berbasis Modul Terstruktur.")

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
    col4.metric("Status Sistem", "Online & Aman")
    
    st.info("Gunakan menu navigasi di sebelah kiri untuk mengakses Modul 0 (Pengaturan), Modul 1 (Input), Modul 2 (Jurnal), hingga Modul 3 (Laporan).")

# --- 2. MODUL 0: PENGATURAN MASTER AKUN & BUSINESS UNIT ---
elif menu == "Modul 0: Pengaturan Master Akun & BU":
    st.subheader("Modul 0: Pengaturan Chart of Accounts (COA) & Business Unit")
    
    tab1, tab2 = st.tabs(["Master Kode Rekening (COA)", "Master Business Unit"])
    
    with tab1:
        st.write("Daftar akun rekening yang digunakan sebagai dasar penjurnalan dan alokasi:")
        st.dataframe(st.session_state.master_coa, use_container_width=True)
        
        with st.form("tambah_akun_form"):
            st.markdown("### Tambah Akun Baru")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                kode_baru = st.text_input("Kode Akun (Contoh: 61300)")
            with col_b:
                nama_baru = st.text_input("Nama Akun (Contoh: Biaya Listrik & Air)")
            with col_c:
                kat_baru = st.selectbox("Kategori", ["Aktiva Lancar", "Aktiva Tetap", "Kewajiban Lancar", "Ekuitas", "Pendapatan", "Biaya / HPP", "Biaya Operasional"])
            
            submit_akun = st.form_submit_button("💾 Simpan Akun Baru")
            if submit_akun and kode_baru and nama_baru:
                df_baru = pd.DataFrame([{"Kode Akun": kode_baru, "Nama Akun": nama_baru, "Kategori": kat_baru}])
                st.session_state.master_coa = pd.concat([st.session_state.master_coa, df_baru], ignore_index=True)
                st.success(f"Akun {kode_baru} - {nama_baru} berhasil ditambahkan!")
                st.rerun()

    with tab2:
        st.write("Daftar Business Unit perusahaan:")
        for bu in st.session_state.master_bu:
            st.text(f"• {bu}")
            
        with st.form("tambah_bu_form"):
            st.markdown("### Tambah Business Unit Baru")
            bu_baru = st.text_input("Nama Business Unit (Contoh: BU-05 - Proyek Baru)")
            submit_bu = st.form_submit_button("💾 Simpan Business Unit")
            if submit_bu and bu_baru:
                st.session_state.master_bu.append(bu_baru)
                st.success(f"Business unit '{bu_baru}' berhasil ditambahkan!")
                st.rerun()

# --- 3. MODUL 1: INPUT DOKUMEN OPERASIONAL ---
elif menu == "Modul 1: Input Dokumen Operasional":
    st.subheader("Modul 1: Khusus Penginputan Dokumen Operasional Harian")
    st.write("Staf lapangan/operasional menginput data transaksi mentah di sini tanpa memilih akun jurnal.")
    
    sumber_transaksi = st.selectbox("Pilih Sumber Dokumen / Modul", [
        "Kas Besar / Kas Proyek",
        "Kas Kecil (Petty Cash)",
        "Bank Masuk / Keluar",
        "Logistik & Pengadaan Barang",
        "Gudang (Pemakaian/Persediaan)",
        "Memorial / Koreksi"
    ])
    
    st.divider()

    with st.form("form_modul1_input"):
        col_label, col_input = st.columns([1, 2])
        
        with col_label:
            st.markdown("<br>📅 **Tanggal Transaksi**", unsafe_allow_html=True)
            st.markdown("<br>🧾 **Nomor Bukti / Ref**", unsafe_allow_html=True)
            st.markdown("<br>🏢 **Business Unit**", unsafe_allow_html=True)
            st.markdown("<br>📦 **Jumlah (Volume / Qty)**", unsafe_allow_html=True)
            st.markdown("<br>📏 **Satuan**", unsafe_allow_html=True)
            st.markdown("<br>🎯 **Peruntukan**", unsafe_allow_html=True)
            st.markdown("<br><br>📝 **Uraian / Keterangan**", unsafe_allow_html=True)
            st.markdown("<br><br>💰 **Nilai Uang (Rp)**", unsafe_allow_html=True)

        with col_input:
            tgl = st.date_input("Tanggal", datetime.now(), label_visibility="collapsed")
            no_bukti = st.text_input("No Bukti", placeholder="Contoh: BSS/KK/VIII/2026/001", label_visibility="collapsed")
            bu_pilihan = st.selectbox("Business Unit", st.session_state.master_bu, label_visibility="collapsed")
            jumlah = st.number_input("Jumlah", min_value=0.0, step=1.0, value=1.0, label_visibility="collapsed")
            satuan = st.text_input("Satuan", placeholder="Contoh: Unit, Liter, Pcs, Lot, Jam", label_visibility="collapsed")
            peruntukan = st.text_input("Peruntukan", placeholder="Contoh: Unit Vacuum Truck", label_visibility="collapsed")
            keterangan = st.text_area("Keterangan", placeholder="Uraian lengkap dokumen...", label_visibility="collapsed")
            nilai_uang = st.number_input("Nilai Uang", min_value=0.0, step=10000.0, label_visibility="collapsed")

        st.divider()
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
                st.success(f"Dokumen dengan No Bukti **{no_bukti}** berhasil disimpan!")
            else:
                st.error("Mohon lengkapi Nomor Bukti dan pastikan Nilai Uang lebih besar dari 0.")

    st.divider()
    st.markdown("### Daftar Dokumen Masuk (Modul 1)")
    if not st.session_state.data_operasional.empty:
        st.dataframe(st.session_state.data_operasional, use_container_width=True)
    else:
        st.info("Belum ada dokumen operasional yang diinput.")

# --- 4. MODUL 2: PROSES PENJURNALAN AKUNTANSI ---
elif menu == "Modul 2: Proses Penjurnalan Akuntansi":
    st.subheader("Modul 2: Proses Penjurnalan oleh Bagian Akuntansi")
    st.write("Pilih dokumen dari Modul 1 yang masuk, lalu tentukan akun Debit dan Kreditnya.")
    
    df_op = st.session_state.data_operasional
    if not df_op.empty:
        st.markdown("### Daftar Dokumen yang Menunggu Dijurnal")
        st.dataframe(df_op, use_container_width=True)
        
        st.divider()
        st.markdown("### Form Input Jurnal Berpasangan")
        
        id_pilih = st.selectbox("Pilih ID Dokumen yang akan Dijurnal", df_op['ID'].tolist())
        dok_terpilih = df_op[df_op['ID'] == id_pilih].iloc[0]
        
        st.info(f"Memproses Dokumen: **{dok_terpilih['Nomor Bukti']}** | Keterangan: *{dok_terpilih['Keterangan']}* | Nilai: **Rp {dok_terpilih['Nilai Uang']:,.0f}**")
        
        list_akun_opt = st.session_state.master_coa['Kode Akun'] + " - " + st.session_state.master_coa['Nama Akun']
        
        with st.form("form_proses_jurnal"):
            col_j1, col_j2 = st.columns(2)
            with col_j1:
                akun_debit = st.selectbox("Pilih Akun DEBIT", list_akun_opt)
            with col_j2:
                akun_kredit = st.selectbox("Pilih Akun KREDIT", list_akun_opt, index=1)
                
            nominal_jurnal = st.number_input("Nominal Jurnal (Rp)", value=float(dok_terpilih['Nilai Uang']), step=1000.0)
            
            submit_jurnal = st.form_submit_button("⚖️ Posting Jurnal Akuntansi")
            
            if submit_jurnal:
                id_jrn = f"JRN-{int(datetime.now().timestamp())}"
                baris_d = {
                    "ID Jurnal": id_jrn, "ID Dokumen": id_pilih, "Tanggal": dok_terpilih['Tanggal'],
                    "Nomor Bukti": dok_terpilih['Nomor Bukti'], "Kode Akun": akun_debit.split(" - ")[0],
                    "Nama Akun": akun_debit.split(" - ")[1], "Debit": nominal_jurnal, "Kredit": 0.0
                }
                baris_k = {
                    "ID Jurnal": id_jrn, "ID Dokumen": id_pilih, "Tanggal": dok_terpilih['Tanggal'],
                    "Nomor Bukti": dok_terpilih['Nomor Bukti'], "Kode Akun": akun_kredit.split(" - ")[0],
                    "Nama Akun": akun_kredit.split(" - ")[1], "Debit": 0.0, "Kredit": nominal_jurnal
                }
                
                st.session_state.data_jurnal = pd.concat([
                    st.session_state.data_jurnal, pd.DataFrame([baris_d, baris_k])
                ], ignore_index=True)
                
                # Ubah status dokumen
                st.session_state.data_operasional.loc[st.session_state.data_operasional['ID'] == id_pilih, 'Status Jurnal'] = 'Sudah Dijurnal'
                st.success(f"Jurnal untuk dokumen {dok_terpilih['Nomor Bukti']} berhasil diposting!")
                st.rerun()
                
        st.divider()
        st.markdown("### Buku Jurnal Umum (General Journal Result)")
        if not st.session_state.data_jurnal.empty:
            st.dataframe(st.session_state.data_jurnal, use_container_width=True)
            if st.button("Hapus Semua Jurnal"):
                st.session_state.data_jurnal = pd.DataFrame(columns=st.session_state.data_jurnal.columns)
                st.rerun()
        else:
            st.warning("Belum ada jurnal yang diposting.")
    else:
        st.warning("Belum ada data dokumen di Modul 1 untuk dijurnal.")

# --- 5. MODUL 3: OUTPUT LAPORAN KEUANGAN ---
elif menu == "Modul 3: Output Laporan Keuangan":
    st.subheader("Modul 3: Output Laporan Keuangan Otomatis")
    
    df_jrn = st.session_state.data_jurnal
    if not df_jrn.empty:
        tab_laba, tab_neraca, tab_buku = st.tabs(["Laporan Laba Rugi", "Posisi Neraca", "Buku Besar"])
        
        with tab_laba:
            st.markdown("### Laporan Laba Rugi (Income Statement)")
            df_pend = df_jrn[df_jrn['Kode Akun'].str.startswith('4')]
            df_biy = df_jrn[df_jrn['Kode Akun'].str.startswith('5') | df_jrn['Kode Akun'].str.startswith('6')]
            
            tot_pend = df_pend['Kredit'].sum() - df_pend['Debit'].sum()
            tot_biy = df_biy['Debit'].sum() - df_biy['Kredit'].sum()
            laba_bersih = tot_pend - tot_biy
            
            st.metric("Total Pendapatan", f"Rp {tot_pend:,.0f}")
            st.metric("Total Biaya / Beban", f"Rp {tot_biy:,.0f}")
            st.divider()
            if laba_bersih >= 0:
                st.success(f"### Laba Bersih: Rp {laba_bersih:,.0f}")
            else:
                st.error(f"### Rugi Bersih: Rp {laba_bersih:,.0f}")
                
        with tab_neraca:
            st.markdown("### Posisi Keuangan / Neraca (Balance Sheet)")
            df_aktiva = df_jrn[df_jrn['Kode Akun'].str.startswith('1')]
            tot_aktiva = df_aktiva['Debit'].sum() - df_aktiva['Kredit'].sum()
            st.metric("Total Aktiva / Aset Perusahaan", f"Rp {tot_aktiva:,.0f}")
            
        with tab_buku:
            st.markdown("### Buku Besar Per Akun (General Ledger)")
            pilih_akun_gl = st.selectbox("Pilih Akun", df_jrn['Kode Akun'] + " - " + df_jrn['Nama Akun'])
            if pilih_akun_gl:
                kode_gl = pilih_akun_gl.split(" - ")[0]
                df_gl_filtered = df_jrn[df_jrn['Kode Akun'] == kode_gl]
                st.dataframe(df_gl_filtered, use_container_width=True)
    else:
        st.info("Belum ada data jurnal di Modul 2 untuk memproses output laporan keuangan.")