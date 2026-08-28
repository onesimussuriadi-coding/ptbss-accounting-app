import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

# Inisialisasi penyimpanan sementara di memori sesi agar data tidak hilang saat pindah menu
if 'data_transaksi' not in st.session_state:
    st.session_state.data_transaksi = pd.DataFrame(columns=[
        "Tanggal", "Nomor Bukti", "Keterangan", "Kode Akun", "Nama Akun", "Debit", "Kredit"
    ])

st.title("📊 Sistem Akuntansi & Keuangan PT Banggai Sentral Sulawesi")
st.write("Portal manajemen data operasional dan laporan keuangan perusahaan.")

# Menu Navigasi Sidebar
menu = st.sidebar.selectbox("Pilih Menu Utama", [
    "Dashboard", 
    "Input Transaksi (Jurnal)", 
    "Jurnal Umum", 
    "Buku Besar", 
    "Laporan Laba Rugi", 
    "Neraca & Arus Kas"
])

# 1. DASHBOARD UTAMA
if menu == "Dashboard":
    st.subheader("Ringkasan Keuangan Perusahaan")
    
    df = st.session_state.data_transaksi
    total_transaksi = len(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Entri Jurnal", f"{total_transaksi} Baris")
    col2.metric("Status Sistem", "Online", "Aman")
    col3.metric("Database", "Session Cloud", "Aktif")
    
    st.info("Gunakan menu **Input Transaksi (Jurnal)** di samping untuk mulai mencatat transaksi keuangan masuk, keluar, atau biaya operasional.")

# 2. INPUT TRANSAKSI (JURNAL)
elif menu == "Input Transaksi (Jurnal)":
    st.subheader("Form Input Transaksi Keuangan")
    
    # Daftar Standar Akun (COA) PT BSS
    coa_dict = {
        "11100 - Kas Kecil (Petty Cash)": "Aktiva",
        "11200 - Bank Utama (Operasional)": "Aktiva",
        "11300 - Piutang Usaha": "Aktiva",
        "21100 - Hutang Usaha": "Kewajiban",
        "31100 - Modal Disetor": "Ekuitas",
        "41100 - Pendapatan Jasa / Kontrak": "Pendapatan",
        "61100 - Biaya Gaji & Karyawan": "Biaya",
        "61200 - Biaya Operasional & Sewa Alat": "Biaya"
    }

    with st.form("form_jurnal", clear_on_submit=True):
        tgl = st.date_input("Tanggal Transaksi", datetime.now())
        no_bukti = st.text_input("Nomor Bukti / Ref (Contoh: BSS/KK/VIII/2026/001)")
        keterangan = st.text_area("Uraian / Keterangan Transaksi")
        
        col_a, col_b = st.columns(2)
        with col_a:
            akun_debit = st.selectbox("Akun Sisi DEBIT", list(coa_dict.keys()))
        with col_b:
            akun_kredit = st.selectbox("Akun Sisi KREDIT", list(coa_dict.keys()))
            
        nominal = st.number_input("Nominal Transaksi (Rp)", min_value=0.0, step=10000.0)
        
        submitted = st.form_submit_button("Simpan Transaksi ke Jurnal")
        
        if submitted:
            if nominal > 0 and no_bukti:
                # Tambah Baris Debit
                baris_debit = {
                    "Tanggal": tgl, "Nomor Bukti": no_bukti, "Keterangan": keterangan,
                    "Kode Akun": akun_debit.split(" - ")[0], "Nama Akun": akun_debit.split(" - ")[1],
                    "Debit": nominal, "Kredit": 0.0
                }
                # Tambah Baris Kredit
                baris_kredit = {
                    "Tanggal": tgl, "Nomor Bukti": no_bukti, "Keterangan": keterangan,
                    "Kode Akun": akun_kredit.split(" - ")[0], "Nama Akun": akun_kredit.split(" - ")[1],
                    "Debit": 0.0, "Kredit": nominal
                }
                
                # Masukkan ke dataframe session state
                st.session_state.data_transaksi = pd.concat([
                    st.session_state.data_transaksi, 
                    pd.DataFrame([baris_debit, baris_kredit])
                ], ignore_index=True)
                
                st.success(f"Transaksi dengan nomor bukti {no_bukti} berhasil dicatat berimbang (Debit/Kredit Rp {nominal:,.0f})!")
            else:
                st.error("Mohon isi nomor bukti dan pastikan nominal lebih besar dari 0.")

# 3. JURNAL UMUM
elif menu == "Jurnal Umum":
    st.subheader("Daftar Jurnal Umum (General Journal)")
    df = st.session_state.data_transaksi
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Tombol Reset Data jika diperlukan
        if st.button("Hapus Semua Data Jurnal"):
            st.session_state.data_transaksi = pd.DataFrame(columns=df.columns)
            st.rerun()
    else:
        st.warning("Belum ada data transaksi yang dimasukkan. Silakan input melalui menu sebelah.")

# 4. BUKU BESAR
elif menu == "Buku Besar":
    st.subheader("Buku Besar Per Akun (General Ledger)")
    df = st.session_state.data_transaksi
    if not df.empty:
        daftar_akun = df['Kode Akun'] + " - " + df['Nama Akun']
        pilih_akun = st.selectbox("Pilih Akun Perkiraan", unique_akun := daftar_akun.unique())
        
        if pilih_akun:
            kode_pilih = pilih_akun.split(" - ")[0]
            df_filtered = df[df['Kode Akun'] == kode_pilih]
            st.write(ampilkan := f"Mutasi untuk Akun: {pilih_akun}")
            st.dataframe(df_filtered, use_container_width=True)
            
            total_d = df_filtered['Debit'].sum()
            total_k = df_filtered['Kredit'].sum()
            st.metric("Total Mutasi Debit", f"Rp {total_d:,.0f}")
            st.metric("Total Mutasi Kredit", f"Rp {total_k:,.0f}")
    else:
        st.info("Data buku besar akan muncul otomatis setelah transaksi diinput.")

# 5. LAPORAN LABA RUGI
elif menu == "Laporan Laba Rugi":
    st.subheader("Laporan Laba Rugi (Income Statement)")
    df = st.session_state.data_transaksi
    if not df.empty:
        # Filter akun pendapatan (kode 4) dan biaya (kode 6)
        df_pendapatan = df[df['Kode Akun'].str.startswith('4')]
        df_biaya = df[df['Kode Akun'].str.startswith('6')]
        
        total_pendapatan = df_pendapatan['Kredit'].sum() - df_pendapatan['Debit'].sum()
        total_biaya = df_biaya['Debit'].sum() - df_biaya['Kredit'].sum()
        laba_bersih = total_pendapatan - total_biaya
        
        st.markdown("### Pendapatan")
        if not df_pendapatan.empty:
            st.dataframe(df_pendapatan[['Kode Akun', 'Nama Akun', 'Kredit']], use_container_width=True)
        st.write(f"**Total Pendapatan: Rp {total_pendapatan:,.0f}**")
        
        st.markdown("### Biaya Operasional")
        if not df_biaya.empty:
            st.dataframe(df_biaya[['Kode Akun', 'Nama Akun', 'Debit']], use_container_width=True)
        st.write(f"**Total Biaya: Rp {total_biaya:,.0f}**")
        
        st.divider()
        if laba_bersih >= 0:
            st.success(f"### Laba Bersih: Rp {laba_bersih:,.0f}")
        else:
            st.error(f"### Rugi Bersih: Rp {laba_bersih:,.0f}")
    else:
        st.info("Belum ada data laporan laba rugi.")

# 6. NERACA & ARUS KAS
elif menu == "Neraca & Arus Kas":
    st.subheader("Posisi Keuangan & Neraca (Balance Sheet)")
    df = st.session_state.data_transaksi
    if not df.empty:
        df_aktiva = df[df['Kode Akun'].str.startswith('1')]
        total_aktiva = df_aktiva['Debit'].sum() - df_aktiva['Kredit'].sum()
        
        st.metric("Total Aktiva / Harta", f"Rp {total_aktiva:,.0f}")
        st.write("Modul rekapitulasi neraca dan analisis arus kas (*cash flow*) akan otomatis merangkum posisi aset perusahaan secara *real-time* berdasarkan transaksi harian.")
    else:
        st.info("Belum ada data untuk ditampilkan pada neraca.")