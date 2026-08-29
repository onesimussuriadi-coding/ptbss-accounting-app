import streamlit as st
import pandas as pd

def render_modul_0():
    st.subheader("Modul 0: Pengaturan Master Akun (Chart of Accounts & Business Unit)")
    
    tab1, tab2 = st.tabs(["📁 Master Akun (COA)", "🏢 Master Business Unit (BU)"])
    
    with tab1:
        st.markdown("### Daftar Master Akun")
        st.write("Sistem otomatis mendeteksi Kategori 1, Kategori 2, Sub Kategori, dan Account berdasarkan awalan Nomor Akun yang Anda masukkan.")
        
        # Form Input Akun Baru dengan Auto-Detection
        with st.form("form_tambah_akun", clear_on_submit=True):
            st.markdown("#### Tambah / Daftarkan Akun Baru")
            c1, c2 = st.columns(2)
            with c1:
                input_no_akun = st.text_input("Nomor Akun (Cth: 1110.002 atau 5133.002)")
            with c2:
                input_nama_akun = st.text_input("Nama Account (Variabel / Bebas Diedit)")
                
            submitted = st.form_submit_button("➕ Tambahkan ke Master Akun")
            
            if submitted:
                if input_no_akun and input_nama_akun:
                    kode_bersih = input_no_akun.strip()
                    
                    # --- LOGIKA OTOMATIS PEMBACAAN HIERARKI DARI KODE AKUN ---
                    kategori_1 = ""
                    kategori_2 = ""
                    sub_kategori = ""
                    account_utama = ""
                    
                    # 1. Deteksi Kategori 1 (Digit Pertama)
                    p1 = kode_bersih[0] if len(kode_bersih) > 0 else ""
                    if p1 == '1': kategori_1 = "1 - Aktiva"[cite: 1]
                    elif p1 == '2': kategori_1 = "2 - Hutang"[cite: 1]
                    elif p1 == '3': kategori_1 = "3 - Ekuitas"[cite: 1]
                    elif p1 == '4': kategori_1 = "4 - Pendapatan"[cite: 1]
                    elif p1 == '5': kategori_1 = "5 - Harga Pokok Penjualan"[cite: 1]
                    
                    # 2. Deteksi Kategori 2 (Dua Digit Pertama)
                    p2 = kode_bersih[:2] if len(kode_bersih) >= 2 else ""
                    if p2 == '11': kategori_2 = "11 - Aktiva Lancar"[cite: 1]
                    elif p2 == '12': kategori_2 = "12 - Aktiva Tetap / Lainnya"[cite: 1]
                    elif p2 == '13': kategori_2 = "13 - Aktiva Tetap / Akumulasi"[cite: 1]
                    elif p2 == '21': kategori_2 = "21 - Hutang Lancar"[cite: 1]
                    elif p2 == '22': kategori_2 = "22 - Hutang Jangka Panjang"[cite: 1]
                    elif p2 == '31': kategori_2 = "31 - Modal"[cite: 1]
                    elif p2 == '32': kategori_2 = "32 - Laba Ditahan"[cite: 1]
                    elif p2 == '41': kategori_2 = "41 - Pendapatan Proyek GS"[cite: 1]
                    elif p2 == '42': kategori_2 = "42 - Pendapatan Proyek CR"[cite: 1]
                    elif p2 == '51': kategori_2 = "51 - Harga Pokok Proyek GS"[cite: 1]

                    # 3. Deteksi Sub Kategori (Tiga Digit Pertama)
                    p3 = kode_bersih[:3] if len(kode_bersih) >= 3 else ""
                    if p3 == '111': sub_kategori = "111 - Kas"[cite: 1]
                    elif p3 == '112': sub_kategori = "112 - Bank"[cite: 1]
                    elif p3 == '113': sub_kategori = "113 - Investasi Jk Pendek"[cite: 1]
                    elif p3 == '114': sub_kategori = "114 - Piutang Usaha"[cite: 1]
                    elif p3 == '115': sub_kategori = "115 - Uang Muka Pembelian"[cite: 1]
                    elif p3 == '116': sub_kategori = "116 - Piutang Lain"[cite: 1]
                    elif p3 == '117': sub_kategori = "117 - Persediaan Barang"[cite: 1]
                    elif p3 == '118': sub_kategori = "118 - Uang Muka Biaya / Pajak"[cite: 1]
                    elif p3 == '121': sub_kategori = "121 - Investasi Jangka Panjang"[cite: 1]
                    elif p3 == '131': sub_kategori = "131 - Harga Peroleh Aktiva Tetap"[cite: 1]
                    elif p3 == '132': sub_kategori = "132 - Akumulasi Penyusutan"[cite: 1]
                    elif p3 == '211': sub_kategori = "211 - Hutang Bank"[cite: 1]
                    elif p3 == '212': sub_kategori = "212 - Hutang Usaha"[cite: 1]
                    elif p3 == '213': sub_kategori = "213 - Pendapatan Diterima Dimuka"[cite: 1]
                    elif p3 == '214': sub_kategori = "214 - Hutang Pajak"[cite: 1]
                    elif p3 == '215': sub_kategori = "215 - Hutang Biaya"[cite: 1]
                    elif p3 == '216': sub_kategori = "216 - Hutang Lain-Lain"[cite: 1]
                    elif p3 == '221': sub_kategori = "221 - Kewajiban Jangka Panjang"[cite: 1]
                    elif p3 == '311': sub_kategori = "311 - Modal"[cite: 1]
                    elif p3 == '321': sub_kategori = "321 - Laba Ditahan"[cite: 1]
                    elif p3 == '411': sub_kategori = "411 - Penjualan Barang Dagangan"[cite: 1]
                    elif p3 == '412': sub_kategori = "412 - Pendapatan Jasa Tronton"[cite: 1]
                    elif p3 == '413': sub_kategori = "413 - Pendapatan Proyek Jasa Umum"[cite: 1]
                    elif p3 == '421': sub_kategori = "421 - Pendapatan Proyek Konstruksi"[cite: 1]
                    elif p3 == '511': sub_kategori = "511 - Harga Pokok Pengadaan Barang"[cite: 1]
                    elif p3 == '512': sub_kategori = "512 - Harga Pokok Operasional Tronton"[cite: 1]
                    elif p3 == '513': sub_kategori = "513 - Harga Pokok Proyek Jasa Umum / Supplies"[cite: 1]
                    elif p3 == '514': sub_kategori = "514 - Biaya Lain-Lain Proyek"[cite: 1]

                    # 4. Deteksi Account Utama (Empat digit sebelum titik)
                    if '.' in kode_bersih:
                        account_utama = kode_bersih.split('.')[0]
                    else:
                        account_utama = kode_bersih[:4]

                    # Simpan ke DataFrame Master COA di Session State
                    data_baru = {
                        "Kode Akun": kode_bersih,
                        "Nama Akun": input_nama_akun,
                        "Sub Account": sub_kategori,
                        "Sub Kategori": kategori_2,
                        "Kategori": kategori_1
                    }
                    
                    st.session_state.master_coa = pd.concat([
                        st.session_state.master_coa, pd.DataFrame([data_baru])
                    ], ignore_index=True)
                    
                    st.success(f"Akun **{input_no_akun} - {input_nama_akun}** berhasil ditambahkan dan dibaca otomatis oleh sistem!")
                    st.rerun()
                else:
                    st.error("Mohon lengkapi Nomor Akun dan Nama Account.")

        st.divider()
        st.markdown("#### Tabel Master Akun Aktif")
        if not st.session_state.master_coa.empty:
            st.dataframe(st.session_state.master_coa, use_container_width=True)
        else:
            st.info("Belum ada data master akun.")

    with tab2:
        st.markdown("### Daftar Business Unit (BU) / Proyek")
        if not st.session_state.master_bu.empty:
            st.dataframe(st.session_state.master_bu, use_container_width=True)
        else:
            st.info("Belum ada data Business Unit.")