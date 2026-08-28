import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

# Inisialisasi penyimpanan sementara sesi
if 'data_transaksi' not in st.session_state:
    st.session_state.data_transaksi = pd.DataFrame(columns=[
        "Tanggal", "Sumber Transaksi", "Nomor Bukti", "Keterangan", "Kode Akun", "Nama Akun", "Debit", "Kredit"
    ])

st.title("📊 Sistem Akuntansi & Keuangan PT Banggai Sentral Sulawesi")
st.write("Portal manajemen data operasional dan laporan keuangan perusahaan.")

# Menu Navigasi Utama
menu = st.sidebar.selectbox("Pilih Menu Utama", [
    "Dashboard", 
    "Input Transaksi (Berdasarkan Sumber)", 
    "Jurnal Umum", 
    "Buku Besar", 
    "Laporan Laba Rugi", 
    "Neraca & Arus Kas"
])

# 1. DASHBOARD
if menu == "Dashboard":
    st.subheader("Ringkasan Keuangan Perusahaan")
    df = st.session_state.data_transaksi
    total_transaksi = len(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Baris Jurnal", f"{total_transaksi}")
    col2.metric("Status Sistem", "Online", "Aman")
    col3.metric("Cloud Storage", "Session State", "Aktif")
    
    st.info("Pilih menu **Input Transaksi (Berdasarkan Sumber)** di samping untuk mencatat transaksi dari Kas, Bank, Logistik, Gudang, atau Memorial.")

# 2. INPUT TRANSAKSI BERDASARKAN SUMBER
elif menu == "Input Transaksi (Berdasarkan Sumber)":
    st.subheader("Form Input Transaksi Sesuai Sumber Dokumen")
    
    # Pilih Sumber Transaksi
    sumber_transaksi = st.selectbox("Pilih Sumber Transaksi / Modul Input", [
        "Kas Besar / Kas Proyek",
        "Kas Kecil (Petty Cash)",
        "Bank Masuk / Keluar",
        "Logistik & Pengadaan Barang",
        "Gudang (Pemakaian/Persediaan)",
        "Memorial (Penyesuaian/Koreksi)"
    ])
    
    st.divider()
    
    # Daftar Akun Perkiraan (COA) Standar PT BSS
    coa_list = [
        "11101 - Kas Besar",
        "11102 - Kas Proyek",
        "11103 - Kas Kecil",
        "11200 - Bank Utama",
        "11300 - Piutang Usaha",
        "11500 - Persediaan Barang Gudang",
        "21100 - Hutang Usaha",
        "31100 - Modal Disetor",
        "41100 - Pendapatan Kontrak / Jasa",
        "51100 - Pembelian Material / Logistik",
        "61100 - Biaya Gaji Karyawan",
        "61200 - Biaya Operasional & Sewa Alat"
    ]

    with st.form(f"form_{sumber_transaksi}", clear_on_submit=True):
        st.markdown(f"### Form Pencatatan: **{sumber_transaksi}**")
        
        tgl = st.date_input("Tanggal Transaksi", datetime.now())
        no_bukti = st.text_input("Nomor Bukti / Ref (Contoh: BSS/KK/VIII/2026/001)")
        keterangan = st.text_area("Uraian / Keterangan Transaksi")
        
        col_a, col_b = st.columns(2)
        with col_a:
            akun_debit = st.selectbox("Akun Sisi DEBIT", coa_list)
        with col_b:
            akun_kredit = st.selectbox("Akun Sisi KREDIT", coa_list, index=3)
            
        nominal = st.number_input("Nominal Transaksi (Rp)", min_value=0.0, step=10000.0)
        
        submitted = st.form_submit_button(f"Simpan Transaksi {sumber_transaksi}")
        
        if submitted:
            if nominal > 0 and no_bukti:
                baris_debit = {
                    "Tanggal": tgl, "Sumber Transaksi": sumber_transaksi, "Nomor Bukti": no_bukti, 
                    "Keterangan": keterangan, "Kode Akun": akun_debit.split(" - ")[0], 
                    "Nama Akun": akun_debit.split(" - ")[1], "Debit": nominal, "Kredit": 0.0
                }
                baris_kredit = {
                    "Tanggal": tgl, "Sumber Transaksi": sumber_transaksi, "Nomor Bukti": no_bukti, 
                    "Keterangan": keterangan, "Kode Akun": akun_kredit.split(" - ")[0], 
                    "Nama Akun": akun_kredit.split(" - ")[1], "Debit": 0.0, "Kredit": nominal
                }
                
                st.session_state.data_transaksi = pd.concat([
                    st.session_state.data_transaksi, 
                    pd.DataFrame([baris_debit, baris_kredit])
                ], ignore_index=True)
                
                st.success(f"Transaksi dari **{sumber_transaksi}** (No Bukti: {no_bukti}) senilai Rp {nominal:,.0f} berhasil disimpan ke sistem!")
            else:
                st.error("Mohon isi nomor bukti dan pastikan nominal lebih besar dari 0.")

# 3. JURNAL UMUM
elif menu == "Jurnal Umum":
    st.subheader("Daftar Jurnal Umum Keseluruhan")
    df = st.session_state.data_transaksi
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        if st.button("Hapus Semua Data Jurnal"):
            st.session_state.data_transaksi = pd.DataFrame(columns=df.columns)
            st.rerun()
    else:
        st.warning("Belum ada data transaksi yang tercatat.")

# 4. BUKU BESAR
elif menu == "Buku Besar":
    st.subheader("Buku Besar Per Akun (General Ledger)")
    df = st.session_state.data_transaksi
    if not df.empty:
        daftar_akun = df['Kode Akun'] + " - " + df['Nama Akun']
        pilih_akun = st.selectbox("Pilih Akun Perkiraan", daftar_akun.unique())
        if pilih_akun:
            kode_pilih = pilih_akun.split(" - ")[0]
            df_filtered = df[df['Kode Akun'] == kode_pilih]
            st.write(f"Mutasi untuk Akun: {pilih_akun}")
            st.dataframe(df_filtered, use_container_width=True)
    else:
        st.info("Buku besar akan terisi otomatis setelah ada transaksi.")

# 5. LAPORAN LABA RUGI
elif menu == "Laporan Laba Rugi":
    st.subheader("Laporan Laba Rugi (Income Statement)")
    df = st.session_state.data_transaksi
    if not df.empty:
        df_pendapatan = df[df['Kode Akun'].str.startswith('4')]
        df_biaya = df[df['Kode Akun'].str.startswith('5') | df['Kode Akun'].str.startswith('6')]
        
        total_pendapatan = df_pendapatan['Kredit'].sum() - df_pendapatan['Debit'].sum()
        total_biaya = df_biaya['Debit'].sum() - df_biaya['Kredit'].sum()
        laba_bersih = total_pendapatan - total_biaya
        
        st.metric("Total Pendapatan", f"Rp {total_pendapatan:,.0f}")
        st.metric("Total Biaya & Pengadaan", f"Rp {total_biaya:,.0f}")
        st.divider()
        if laba_bersih >= 0:
            st.success(f"### Laba Bersih: Rp {laba_bersih:,.0f}")
        else:
            st.error(f"### Rugi Bersih: Rp {laba_bersih:,.0f}")
    else:
        st.info("Belum ada data laporan.")

# 6. NERACA & ARUS KAS
elif menu == "Neraca & Arus Kas":
    st.subheader("Posisi Keuangan & Neraca")
    df = st.session_state.data_transaksi
    if not df.empty:
        df_aktiva = df[df['Kode Akun'].str.startswith('1')]
        total_aktiva = df_aktiva['Debit'].sum() - df_aktiva['Kredit'].sum()
        st.metric("Total Aktiva / Harta Perusahaan", f"Rp {total_aktiva:,.0f}")
    else:
        st.info("Belum ada data neraca.")