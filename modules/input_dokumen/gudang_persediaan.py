import streamlit as st
import pandas as pd
import os
from datetime import datetime

def render_gudang_persediaan():
    st.markdown("### 📦 Modul Khusus: Persediaan & Gudang (Logistik Internal)")

    if 'data_operasional' not in st.session_state:
        st.session_state.data_operasional = pd.DataFrame(columns=[
            "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi", 
            "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan", "Jumlah", "Satuan", "Peruntukan", "Keterangan", 
            "DPP", "PPN", "PPH", "Total", "Status Dokumen", "Status Jurnal"
        ])

    if 'master_satuan' not in st.session_state:
        st.session_state.master_satuan = ["Pcs", "EA", "Ls", "Kg", "Liter", "Trip", "Jam", "Hari", "Lot", "Bulan", "Unit", "Box", "Set", "Drum"]

    if 'form_index_gdg' not in st.session_state:
        st.session_state.form_index_gdg = 0

    idx = st.session_state.form_index_gdg

    col_reset1, col_reset2 = st.columns([3, 1])
    with col_reset2:
        if st.button("🧹 Reset Form Gudang", use_container_width=True):
            st.session_state.form_index_gdg += 1
            st.success("Form gudang berhasil dibersihkan!")
            st.rerun()

    # --- PEMBACAAN MASTER DATA DINAMIS ---
    list_bu_opt = []
    if os.path.exists("master_bu_bss.xlsx"):
        try:
            df_bu = pd.read_excel("master_bu_bss.xlsx")
            df_bu.columns = df_bu.columns.str.replace('\xa0', ' ').str.strip()
            if len(df_bu.columns) >= 2:
                list_bu_opt = (df_bu.iloc[:, 0].astype(str).str.strip() + " - " + df_bu.iloc[:, 1].astype(str).str.strip()).tolist()
        except Exception:
            pass

    list_alat_opt = []
    if os.path.exists("master_alat_bss.xlsx"):
        try:
            df_alat = pd.read_excel("master_alat_bss.xlsx")
            df_alat.columns = df_alat.columns.str.replace('\xa0', ' ').str.strip()
            if len(df_alat.columns) >= 2:
                col_a1 = df_alat.columns[1]
                list_alat_opt = df_alat[col_a1].dropna().astype(str).str.strip().tolist()
        except Exception:
            pass

    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📅 **Tanggal Mutasi / Transaksi Gudang**", unsafe_allow_html=True)
        with c2: tgl = st.date_input("Tanggal", datetime.now(), label_visibility="collapsed", key=f"tgl_gdg_{idx}")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🧾 **Nomor Bukti / Slip Gudang**", unsafe_allow_html=True)
        with c2: no_bukti = st.text_input("No Bukti", placeholder="Cth: BSS/GDG/VIII/2026/001", label_visibility="collapsed", key=f"nobukti_gdg_{idx}")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🔄 **Jenis Aktivitas Gudang**", unsafe_allow_html=True)
        with c2: jenis_aktivitas = st.selectbox("Aktivitas Gudang", ["Penerimaan Barang Masuk Gudang", "Pengeluaran / Pemakaian Material Gudang", "Opname / Penyesuaian Stok"], key=f"akt_gdg_{idx}", label_visibility="collapsed")

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🏢 **Business Unit / Proyek Terkait**", unsafe_allow_html=True)
        with c2:
            sub_bu1, sub_bu2 = st.columns([3, 1])
            with sub_bu1:
                bu_pilihan = st.selectbox("Business Unit", ["-- Pilih Business Unit --"] + list_bu_opt, label_visibility="collapsed", key=f"bu_gdg_{idx}")
            with sub_bu2:
                tambah_bu_baru = st.text_input("BU Baru", placeholder="Ketik baru...", key=f"tambah_bu_gdg_{idx}", label_visibility="collapsed")
            bu_final = bu_pilihan if bu_pilihan != "-- Pilih Business Unit --" else ""
            if tambah_bu_baru.strip(): bu_final = tambah_bu_baru.strip()

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📦 **Jumlah (Volume / Qty)**", unsafe_allow_html=True)
        with c2: jumlah = st.number_input("Jumlah", min_value=0.0, step=1.0, value=0.0, label_visibility="collapsed", key=f"jml_gdg_{idx}")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📏 **Satuan Barang**", unsafe_allow_html=True)
        with c2:
            sub_sat1, sub_sat2 = st.columns([3, 1])
            with sub_sat1:
                satuan_pilihan = st.selectbox("Pilih Satuan", ["-- Pilih Satuan --"] + st.session_state.master_satuan, label_visibility="collapsed", key=f"satuan_gdg_{idx}")
            with sub_sat2:
                tambah_satuan_baru = st.text_input("Tambah Satuan", placeholder="Baru...", label_visibility="collapsed", key=f"tambah_satuan_gdg_{idx}")
            satuan_final = satuan_pilihan if satuan_pilihan != "-- Pilih Satuan --" else ""
            if tambah_satuan_baru.strip():
                satuan_clean = tambah_satuan_baru.strip().upper()
                satuan_final = satuan_clean
                if satuan_clean not in st.session_state.master_satuan:
                    st.session_state.master_satuan.append(satuan_clean)

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🎯 **Peruntukan (Alokasi Alat / Unit)**", unsafe_allow_html=True)
        with c2:
            peruntukan_pilihan = st.selectbox("Pilih Alat / Unit", ["-- Pilih Alokasi Alat / Unit --"] + list_alat_opt, label_visibility="collapsed", key=f"peruntukan_gdg_{idx}")
            peruntukan_final = peruntukan_pilihan if peruntukan_pilihan != "-- Pilih Alokasi Alat / Unit --" else "-"

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br><br>📝 **Uraian / Keterangan Material**", unsafe_allow_html=True)
        with c2: keterangan = st.text_area("Keterangan", placeholder="Nama barang, spesifikasi, atau catatan gudang...", label_visibility="collapsed", key=f"ket_gdg_{idx}")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>💰 **Estimasi Nilai / Harga (Opsional)**", unsafe_allow_html=True)
        with c2: nilai_barang = st.number_input("Nilai", min_value=0.0, step=10000.0, format="%.2f", value=0.0, label_visibility="collapsed", key=f"val_gdg_{idx}")

        st.divider()
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Simpan Data Gudang", use_container_width=True, key=f"btn_save_gdg_{idx}"):
                if no_bukti and bu_final:
                    data_baru = {
                        "Nomor Bukti": no_bukti, "Tanggal": tgl, "Sumber Transaksi": f"Gudang - {jenis_aktivitas}",
                        "Lawan Transaksi": "Internal Gudang", "No Invoice": "-",
                        "Jatuh Tempo": "-", "Business Unit": bu_final, "Departemen Tujuan": "Logistik",
                        "Jumlah": jumlah, "Satuan": satuan_final, "Peruntukan": peruntukan_final, "Keterangan": keterangan, 
                        "DPP": nilai_barang, "PPN": 0.0, "PPH": 0.0, "Total": nilai_barang, 
                        "Status Dokumen": "Menunggu Approval Kabag Logistik", "Status Jurnal": "Belum Dijurnal"
                    }
                    df_existing = st.session_state.data_operasional
                    if not df_existing.empty and no_bukti in df_existing['Nomor Bukti'].values:
                        df_existing.loc[df_existing['Nomor Bukti'] == no_bukti] = pd.DataFrame([data_baru]).values[0]
                        st.success(f"Nomor Bukti '{no_bukti}' berhasil diperbarui!")
                    else:
                        st.session_state.data_operasional = pd.concat([df_existing, pd.DataFrame([data_baru])], ignore_index=True)
                        st.success("Data gudang berhasil disimpan!")
                else:
                    st.error("Mohon lengkapi Nomor Bukti dan Business Unit.")
                    
        with col_b2:
            if st.button("➕ Simpan & Mulai Entri Baru", use_container_width=True, key=f"btn_save_new_gdg_{idx}"):
                if no_bukti and bu_final:
                    data_baru = {
                        "Nomor Bukti": no_bukti, "Tanggal": tgl, "Sumber Transaksi": f"Gudang - {jenis_aktivitas}",
                        "Lawan Transaksi": "Internal Gudang", "No Invoice": "-",
                        "Jatuh Tempo": "-", "Business Unit": bu_final, "Departemen Tujuan": "Logistik",
                        "Jumlah": jumlah, "Satuan": satuan_final, "Peruntukan": peruntukan_final, "Keterangan": keterangan, 
                        "DPP": nilai_barang, "PPN": 0.0, "PPH": 0.0, "Total": nilai_barang, 
                        "Status Dokumen": "Menunggu Approval Kabag Logistik", "Status Jurnal": "Belum Dijurnal"
                    }
                    df_existing = st.session_state.data_operasional
                    if not df_existing.empty and no_bukti in df_existing['Nomor Bukti'].values:
                        df_existing.loc[df_existing['Nomor Bukti'] == no_bukti] = pd.DataFrame([data_baru]).values[0]
                    else:
                        st.session_state.data_operasional = pd.concat([df_existing, pd.DataFrame([data_baru])], ignore_index=True)
                    st.session_state.form_index_gdg += 1
                    st.success("Tersimpan! Form diset ke entri baru.")
                    st.rerun()
                else:
                    st.error("Mohon lengkapi Nomor Bukti dan Business Unit.")