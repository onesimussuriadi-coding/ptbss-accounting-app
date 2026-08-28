import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Akuntansi PT BSS", page_icon="📊", layout="wide")

# Inisialisasi penyimpanan sesi untuk data transaksi operasional mentah
if 'data_operasional' not in st.session_state:
    st.session_state.data_operasional = pd.DataFrame(columns=[
        "ID", "Tanggal", "Sumber Transaksi", "Nomor Bukti", "Business Unit", 
        "Jumlah", "Satuan", "Keterangan", "Peruntukan", "Nilai Uang"
    ])

st.title("📊 Sistem Pencatatan Data & Akuntansi PT Banggai Sentral Sulawesi")
st.write("Portal input dokumen operasional harian (tanpa jurnal manual, langsung direkap untuk tim akuntansi).")

# Menu Navigasi Utama
menu = st.sidebar.selectbox("Pilih Menu Utama", [
    "Dashboard", 
    "Input Transaksi Operasional", 
    "Daftar Transaksi Masuk", 
    "Modul Jurnal Akuntansi"
])

# 1. DASHBOARD
if menu == "Dashboard":
    st.subheader("Ringkasan Data Operasional")
    df = st.session_state.data_operasional
    total_data = len(df)
    total_nilai = df['Nilai Uang'].sum() if not df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Dokumen Tercatat", f"{total_data} Item")
    col2.metric("Total Nilai Transaksi", f"Rp {total_nilai:,.0f}")
    col3.metric("Status Sistem", "Online", "Aman")
    
    st.info("Gunakan menu **Input Transaksi Operasional** di samping untuk memasukkan data harian secara rapi dan terstruktur.")

# 2. INPUT TRANSAKSI OPERASIONAL (LAYOUT KIRI-KANAN & MULTI-BARIS)
elif menu == "Input Transaksi Operasional":
    st.subheader("Form Input Dokumen Operasional Harian")
    
    sumber_transaksi = st.selectbox("Pilih Sumber Dokumen / Modul", [
        "Kas Besar / Kas Proyek",
        "Kas Kecil (Petty Cash)",
        "Bank Masuk / Keluar",
        "Logistik & Pengadaan Barang",
        "Gudang (Pemakaian/Persediaan)",
        "Memorial / Koreksi"
    ])
    
    st.divider()
    
    business_units = [
        "BU-01 - Operasional Kantor Pusat",
        "BU-02 - Proyek Senoro-Toili (JOB Pertamina-Medco)",
        "BU-03 - Sektor Logistik & Heavy Equipment",
        "BU-04 - Gudang & Pengadaan Umum"
    ]

    with st.form("form_input_operasional"):
        st.markdown("### Masukkan Data Transaksi")
        
        # Layout Dua Kolom Rapi (Kiri: Template/Label, Kanan: Kolom Isian)
        col_label, col_input = st.columns([1, 2])
        
        with col_label:
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**Tanggal Transaksi**")
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**Nomor Bukti / Ref**")
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**Business Unit**")
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**Jumlah (Volume / Qty)**")
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**Satuan**")
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**Peruntukan**")
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.write("**Uraian / Keterangan**")
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.write("**Nilai Uang (Rp)**")

        with col_input:
            tgl = st.date_input("Tanggal", datetime.now(), label_visibility="collapsed")
            no_bukti = st.text_input("No Bukti", placeholder="Contoh: BSS/KK/VIII/2026/001", label_visibility="collapsed")
            bu_pilihan = st.selectbox("Business Unit", business_units, label_visibility="collapsed")
            jumlah = st.number_input("Jumlah", min_value=0.0, step=1.0, value=1.0, label_visibility="collapsed")
            satuan = st.text_input("Satuan", placeholder="Contoh: Unit, Liter, Pcs, Lot, Jam", label_visibility="collapsed")
            peruntukan = st.text_input("Peruntukan", placeholder="Contoh: Unit Vacuum Truck / Operasional Lapangan", label_visibility="collapsed")
            keterangan = st.text_area("Keterangan", placeholder="Uraian lengkap transaksi...", label_visibility="collapsed")
            nilai_uang = st.number_input("Nilai Uang", min_value=0.0, step=10000.0, label_visibility="collapsed")

        st.divider()
        
        # Tombol Aksi Simpan / Tambah Baris
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted_simpan = st.form_submit_button("💾 Simpan Transaksi Ini")
        with col_btn2:
            submitted_tambah = st.form_submit_button("➕ Simpan & Tambah Baris Baru")

        if submitted_simpan or submitted_tambah:
            if nilai_uang > 0 and no_bukti:
                id_baru = f"TRX-{int(datetime.now().timestamp())}"
                data_baru = {
                    "ID": id_baru,
                    "Tanggal": tgl,
                    "Sumber Transaksi": sumber_transaksi,
                    "Nomor Bukti": no_bukti,
                    "Business Unit": bu_pilihan,
                    "Jumlah": jumlah,
                    "Satuan": satuan,
                    "Keterangan": keterangan,
                    "Peruntukan": peruntukan,
                    "Nilai Uang": nilai_uang
                }
                
                st.session_state.data_operasional = pd.concat([
                    st.session_state.data_operasional, 
                    pd.DataFrame([data_baru])
                ], ignore_index=True)
                
                st.success(f"Data dengan No Bukti **{no_bukti}** berhasil disimpan ke sistem!")
            else:
                st.error("Mohon lengkapi Nomor Bukti dan pastikan Nilai Uang lebih besar dari 0.")

# 3. DAFTAR TRANSAKSI MASUK & FITUR UPDATE/KOREKSI
elif menu == "Daftar Transaksi Masuk":
    st.subheader("Daftar & Koreksi Data Operasional Masuk")
    df = st.session_state.data_operasional
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.markdown("### 🔄 Koreksi / Update Data")
        st.write("Jika ada kesalahan input, pilih ID transaksi di bawah ini untuk memperbarui data:")
        
        pilih_id = st.selectbox("Pilih ID Transaksi yang akan dikoreksi", df['ID'].tolist())
        if pilih_id:
            data_terpilih = df[df['ID'] == pilih_id].iloc[0]
            
            with st.form("form_update"):
                up_bukti = st.text_input("Nomor Bukti", value=data_terpilih['Nomor Bukti'])
                up_ket = st.text_area("Keterangan", value=data_terpilih['Keterangan'])
                up_nilai = st.number_input("Nilai Uang (Rp)", value=float(data_terpilih['Nilai Uang']))
                
                update_button = st.form_submit_button("🔄 Perbarui (Update) Data")
                if update_button:
                    st.session_state.data_operasional.loc[st.session_state.data_operasional['ID'] == pilih_id, 'Nomor Bukti'] = up_bukti
                    st.session_state.data_operasional.loc[st.session_state.data_operasional['ID'] == pilih_id, 'Keterangan'] = up_ket
                    st.session_state.data_operasional.loc[st.session_state.data_operasional['ID'] == pilih_id, 'Nilai Uang'] = up_nilai
                    st.success(f"Data transaksi {pilih_id} berhasil diperbarui!")
                    st.rerun()
        
        if st.button("Hapus Seluruh Data"):
            st.session_state.data_operasional = pd.DataFrame(columns=df.columns)
            st.rerun()
    else:
        st.warning("Belum ada data transaksi operasional yang dimasukkan.")

# 4. MODUL JURNAL AKUNTANSI
elif menu == "Modul Jurnal Akuntansi":
    st.subheader("Modul Khusus Tim Akuntansi (Jurnal & Posting)")
    df = st.session_state.data_operasional
    if not df.empty:
        st.write("Berikut adalah daftar dokumen operasional yang siap untuk divalidasi dan diberi akun jurnal oleh bagian akuntansi:")
        st.dataframe(df, use_container_width=True)
        st.info("Fitur penjurnalan otomatis dan buku besar lanjutan akan membaca data dari tabel di atas.")
    else:
        st.info("Belum ada data dokumen untuk dijurnal.")