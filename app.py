import streamlit as st

# Konfigurasi halaman web
st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

st.title("📊 Sistem Akuntansi & Keuangan PT Banggai Sentral Sulawesi")
st.write("Selamat datang di portal keuangan online perusahaan. Silakan pilih menu di bawah ini.")

# Menu navigasi sederhana menggunakan Sidebar
menu = st.sidebar.selectbox("Pilih Menu Utama", ["Dashboard", "Input Transaksi", "Jurnal Umum", "Laporan Keuangan"])

if menu == "Dashboard":
    st.subheader("Ringkasan Keuangan Perusahaan")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pendapatan", "Rp 0", "0%")
    col2.metric("Total Biaya", "Rp 0", "0%")
    col3.metric("Saldo Kas", "Rp 0", "0%")
    st.info("Pilih menu 'Input Transaksi' di samping untuk mulai memasukkan data keuangan.")

elif menu == "Input Transaksi":
    st.subheader("Form Input Transaksi Harian")
    with st.form("form_transaksi"):
        tgl = st.date_input("Tanggal Transaksi")
        jenis = st.selectbox("Jenis Transaksi", ["Kas Masuk", "Kas Keluar", "Pembelian", "Biaya Operasional"])
        akun = st.selectbox("Pilih Akun (COA)", ["11100 - Kas Kecil", "11300 - Bank Utama", "11400 - Piutang Usaha", "61100 - Biaya Gaji"])
        jumlah = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        keterangan = st.text_area("Keterangan / Uraian Transaksi")
        
        submitted = st.form_submit_button("Simpan Transaksi")
        if submitted:
            st.success(f"Transaksi sebesar Rp {jumlah:,} berhasil dicatat!")

elif menu == "Jurnal Umum":
    st.subheader("Daftar Jurnal Umum")
    st.write("Belum ada data transaksi yang tersimpan.")

elif menu == "Laporan Keuangan":
    st.subheader("Laporan Keuangan (Laba Rugi & Neraca)")
    st.write("Laporan akan otomatis tersusun setelah ada data transaksi.")