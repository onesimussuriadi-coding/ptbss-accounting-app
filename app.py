import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

# Inisialisasi penyimpanan sementara sesi dengan kolom yang diperinci
if 'data_transaksi' not in st.session_state:
    st.session_state.data_transaksi = pd.DataFrame(columns=[
        "Tanggal", "Sumber Transaksi", "Nomor Bukti", "Business Unit", 
        "Jumlah", "Satuan", "Keterangan", "Peruntukan", 
        "Kode Akun Debit", "Nama Akun Debit", "Kode Akun Kredit", "Nama Akun Kredit", "Nilai Uang"
    ])

st.title("📊 Sistem Akuntansi & Keuangan PT Banggai Sentral Sulawesi")
st.write("Portal manajemen data operasional dan laporan keuangan perusahaan.")

# Menu Navigasi Utama
menu = st.sidebar.selectbox("Pilih Menu Utama", [
    "Dashboard", 
    "Input Transaksi (Rinci)", 
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
    col1.metric("Total Entri Data", f"{total_transaksi}")
    col2.metric("Status Sistem", "Online", "Aman")
    col3.metric("Cloud Storage", "Session State", "Aktif")
    
    st.info("Pilih menu **Input Transaksi (Rinci)** di samping untuk mulai mencatat data operasional dengan indikator lengkap (Business Unit, Jumlah, Satuan, Peruntukan, dll).")

# 2. INPUT TRANSAKSI (RINCI)
elif menu == "Input Transaksi (Rinci)":
    st.subheader("Form Input Transaksi Rinci & Operasional")
    
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
    
    # Daftar Business Unit PT BSS (Pengganti Kode Proyek)
    business_units = [
        "BU-01 - Operasional Kantor Pusat",
        "BU-02 - Proyek Senoro-Toili (JOB Pertamina-Medco)",
        "BU-03 - Sektor Logistik & Heavy Equipment",
        "BU-04 - Gudang & Pengadaan Umum"
    ]
    
    # Daftar Akun Perkiraan (COA) Standar
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

    with st.form(f"form_rinci_{sumber_transaksi}", clear_on_submit=True):
        st.markdown(f"### Form Pencatatan: **{sumber_transaksi}**")
        
        col_1, col_2 = st.columns(2)
        with col_1:
            tgl = st.date_input("Tanggal Transaksi", datetime.now())
            no_bukti = st.text_input("Nomor Bukti / Ref (Contoh: BSS/KK/VIII/2026/001)")
            bu_pilihan = st.selectbox("Business Unit", business_units)
            jumlah = st.number_input("Jumlah (Volume / Qty)", min_value=0.0, step=1.0, value=1.0)
            satuan = st.text_input("Satuan (Contoh: Unit, Liter, Pcs, Lot, Jam)")
            
        with col_2:
            peruntukan = st.text_input("Peruntukan (Contoh: Unit Vacuum Truck / Operasional Lapangan)")
            akun_debit = st.selectbox("Akun Sisi DEBIT", coa_list)
            akun_kredit = st.selectbox("Akun Sisi KREDIT", coa_list, index=3)
            nilai_uang = st.number_input("Nilai Uang (Rp)", min_value=0.0, step=10000.0)
            
        keterangan = st.text_area("Uraian / Keterangan Lengkap Transaksi")
        
        submitted = st.form_submit_button(f"Simpan Transaksi {sumber_transaksi}")
        
        if submitted:
            if nilai_uang > 0 and no_bukti:
                baris_baru = {
                    "Tanggal": tgl, 
                    "Sumber Transaksi": sumber_transaksi, 
                    "Nomor Bukti": no_bukti, 
                    "Business Unit": bu_pilihan,
                    "Jumlah": jumlah,
                    "Satuan": satuan,
                    "Keterangan": keterangan,
                    "Peruntukan": peruntukan,
                    "Kode Akun Debit": akun_debit.split(" - ")[0], 
                    "Nama Akun Debit": akun_debit.split(" - ")[1], 
                    "Kode Akun Kredit": akun_kredit.split(" - ")[0], 
                    "Nama Akun Kredit": akun_kredit.split(" - ")[1], 
                    "Nilai Uang": nilai_uang
                }
                
                st.session_state.data_transaksi = pd.concat([
                    st.session_state.data_transaksi, 
                    pd.DataFrame([baris_baru])
                ], ignore_index=True)
                
                st.success(f"Transaksi **{sumber_transaksi}** (No Bukti: {no_bukti}) senilai Rp {nilai_uang:,.0f} berhasil disimpan!")
            else:
                st.error("Mohon isi nomor bukti dan pastikan Nilai Uang lebih besar dari 0.")

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
        # Gabungkan akun debit atau kredit untuk buku besar
        st.info("Menampilkan seluruh rekapan transaksi berdasarkan akun perkiraan.")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Buku besar akan terisi otomatis setelah ada transaksi.")

# 5. LAPORAN LABA RUGI
elif menu == "Laporan Laba Rugi":
    st.subheader("Laporan Laba Rugi (Income Statement)")
    df = st.session_state.data_transaksi
    if not df.empty:
        # Hitung berdasarkan akun pendapatan (4) dan biaya (5 atau 6)
        df_pendapatan = df[df['Kode Akun Kredit'].str.startswith('4')]
        df_biaya = df[df['Kode Akun Debit'].str.startswith('5') | df['Kode Akun Debit'].str.startswith('6')]
        
        total_pendapatan = df_pendapatan['Nilai Uang'].sum()
        total_biaya = df_biaya['Nilai Uang'].sum()
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
        st.metric("Total Nilai Transaksi Tercatat", f"Rp {df['Nilai Uang'].sum():,.0f}")
        st.write("Modul neraca komprehensif siap dikembangkan lebih lanjut sesuai pergerakan aset dan kewajiban.")
    else:
        st.info("Belum ada data neraca.")