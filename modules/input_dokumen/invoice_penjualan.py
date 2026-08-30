import streamlit as st
import pandas as pd
import os
from datetime import datetime

def render_invoice_penjualan():
    st.markdown("### 🏷️ Modul Khusus: Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)")

    # Inisialisasi State Data Operasional Khusus Invoice Penjualan jika belum ada
    if 'data_operasional' not in st.session_state:
        st.session_state.data_operasional = pd.DataFrame(columns=[
            "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi", 
            "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan", "Jumlah", "Satuan", "Peruntukan", "Keterangan", 
            "DPP", "PPN", "PPH", "Total", "Status Dokumen", "Status Jurnal"
        ])

    # Inisialisasi Master Satuan Dinamis
    if 'master_satuan' not in st.session_state:
        st.session_state.master_satuan = ["Pcs", "EA", "Ls", "Kg", "Liter", "Trip", "Jam", "Hari", "Lot", "Bulan", "Unit", "Box", "Set", "Drum"]

    if 'form_index_inv' not in st.session_state:
        st.session_state.form_index_inv = 0

    idx = st.session_state.form_index_inv

    col_reset1, col_reset2 = st.columns([3, 1])
    with col_reset2:
        if st.button("🧹 Reset Form Invoice", use_container_width=True):
            st.session_state.form_index_inv += 1
            st.success("Form invoice berhasil dibersihkan!")
            st.rerun()

    # =========================================================================
    # PEMBACAAN DINAMIS MURNI DARI FILE FISIK EXCEL MASTER
    # =========================================================================

    # 1. Business Unit
    list_bu_opt = []
    if os.path.exists("master_bu_bss.xlsx"):
        try:
            df_bu = pd.read_excel("master_bu_bss.xlsx")
            df_bu.columns = df_bu.columns.str.replace('\xa0', ' ').str.strip()
            if len(df_bu.columns) >= 2:
                list_bu_opt = (df_bu.iloc[:, 0].astype(str).str.strip() + " - " + df_bu.iloc[:, 1].astype(str).str.strip()).tolist()
        except Exception:
            pass

    # 2. Pelanggan / Customer (Membaca kolom Nama Pelanggan / Index 1)
    list_pelanggan_opt = []
    if os.path.exists("master_pelanggan_bss.xlsx"):
        try:
            df_pel = pd.read_excel("master_pelanggan_bss.xlsx")
            df_pel.columns = df_pel.columns.str.replace('\xa0', ' ').str.strip()
            col_target = df_pel.columns[1] if len(df_pel.columns) > 1 else df_pel.columns[0]
            list_pelanggan_opt = df_pel[col_target].dropna().astype(str).str.strip().tolist()
        except Exception:
            pass
    if not list_pelanggan_opt:
        list_pelanggan_opt = ["Pelanggan Umum / Pihak Ketiga"]

    # 3. Alokasi Alat / Unit
    list_alat_opt = []
    if os.path.exists("master_alat_bss.xlsx"):
        try:
            df_alat = pd.read_excel("master_alat_bss.xlsx")
            df_alat.columns = df_alat.columns.str.replace('\xa0', ' ').str.strip()
            if len(df_alat.columns) >= 2:
                col_a1 = df_alat.columns[1]
                col_a2 = df_alat.columns[3] if len(df_alat.columns) > 3 else None
                if col_a2 and col_a2 in df_alat.columns:
                    list_alat_opt = (df_alat[col_a1].astype(str).str.strip() + " (" + df_alat[col_a2].astype(str).str.strip() + ")").tolist()
                else:
                    list_alat_opt = df_alat[col_a1].dropna().astype(str).str.strip().tolist()
        except Exception:
            pass

    if f'val_ppn_inv_{idx}' not in st.session_state: st.session_state[f'val_ppn_inv_{idx}'] = 0.0
    if f'val_pph_inv_{idx}' not in st.session_state: st.session_state[f'val_pph_inv_{idx}'] = 0.0

    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📅 **Tanggal Invoice**", unsafe_allow_html=True)
        with c2: tgl = st.date_input("Tanggal", datetime.now(), label_visibility="collapsed", key=f"tgl_inv_{idx}")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🧾 **Nomor Bukti / Ref Internal**", unsafe_allow_html=True)
        with c2: no_bukti = st.text_input("No Bukti", placeholder="Cth: BSS/AR/VIII/2026/001", label_visibility="collapsed", key=f"nobukti_inv_{idx}")
        
        # Pelanggan / Customer (Debitur)
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>👥 **Pelanggan / Customer (Debitur)**", unsafe_allow_html=True)
        with c2:
            sub_cust1, sub_cust2 = st.columns([3, 1])
            with sub_cust1:
                pelanggan_pilihan = st.selectbox("Pilih Pelanggan", ["-- Pilih Pelanggan --"] + list_pelanggan_opt, key=f"pelanggan_sel_inv_{idx}", label_visibility="collapsed")
            with sub_cust2:
                tambah_pelanggan_baru = st.text_input("Pelanggan Baru", placeholder="Ketik baru...", key=f"tambah_pelanggan_inv_{idx}", label_visibility="collapsed")
            
            lawan_transaksi_final = pelanggan_pilihan if pelanggan_pilihan != "-- Pilih Pelanggan --" else ""
            if tambah_pelanggan_baru.strip():
                lawan_transaksi_final = tambah_pelanggan_baru.strip()

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🏷️ **Nomor Invoice Perusahaan**", unsafe_allow_html=True)
        with c2: no_invoice_perusahaan = st.text_input("No Invoice Tagihan", placeholder="Cth: INV/BSS/2026/001", key=f"inv_perusahaan_inv_{idx}", label_visibility="collapsed")

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>⏳ **Jatuh Tempo Piutang**", unsafe_allow_html=True)
        with c2: tgl_jatuh_tempo = st.date_input("Jatuh Tempo Piutang", datetime.now(), key=f"duedate_ar_inv_{idx}", label_visibility="collapsed")

        # Business Unit / Proyek
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🏢 **Business Unit / Proyek**", unsafe_allow_html=True)
        with c2:
            sub_bu1, sub_bu2 = st.columns([3, 1])
            with sub_bu1:
                bu_pilihan = st.selectbox("Business Unit", ["-- Pilih Business Unit --"] + list_bu_opt, label_visibility="collapsed", key=f"bu_inv_{idx}")
            with sub_bu2:
                tambah_bu_baru = st.text_input("BU Baru", placeholder="Ketik baru...", key=f"tambah_bu_inv_{idx}", label_visibility="collapsed")
            bu_final = bu_pilihan if bu_pilihan != "-- Pilih Business Unit --" else ""
            if tambah_bu_baru.strip(): bu_final = tambah_bu_baru.strip()
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📦 **Jumlah (Volume / Qty)**", unsafe_allow_html=True)
        with c2: jumlah = st.number_input("Jumlah", min_value=0.0, step=1.0, value=0.0, label_visibility="collapsed", key=f"jml_inv_{idx}")
        
        # Satuan Dinamis
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📏 **Satuan**", unsafe_allow_html=True)
        with c2:
            sub_sat1, sub_sat2 = st.columns([3, 1])
            with sub_sat1:
                satuan_pilihan = st.selectbox("Pilih Satuan", ["-- Pilih Satuan --"] + st.session_state.master_satuan, label_visibility="collapsed", key=f"satuan_inv_{idx}")
            with sub_sat2:
                tambah_satuan_baru = st.text_input("Tambah Satuan", placeholder="Cth: EA...", label_visibility="collapsed", key=f"tambah_satuan_inv_{idx}")
            
            satuan_final = satuan_pilihan if satuan_pilihan != "-- Pilih Satuan --" else ""
            if tambah_satuan_baru.strip():
                satuan_baru_clean = tambah_satuan_baru.strip().upper()
                satuan_final = satuan_baru_clean
                if satuan_baru_clean not in st.session_state.master_satuan:
                    st.session_state.master_satuan.append(satuan_baru_clean)

        # Peruntukan (Alokasi Alat / Unit)
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🎯 **Peruntukan (Alokasi Alat / Unit)**", unsafe_allow_html=True)
        with c2:
            sub_p1, sub_p2 = st.columns([3, 1])
            with sub_p1:
                peruntukan_pilihan = st.selectbox("Pilih Alat / Unit", ["-- Pilih Alokasi Alat / Unit --"] + list_alat_opt, label_visibility="collapsed", key=f"peruntukan_sel_inv_{idx}")
            with sub_p2:
                peruntukan_manual = st.text_input("Atau Ketik Bebas", placeholder="Ketik manual...", label_visibility="collapsed", key=f"peruntukan_man_inv_{idx}")
            peruntukan_final = peruntukan_pilihan if peruntukan_pilihan != "-- Pilih Alokasi Alat / Unit --" else ""
            if peruntukan_manual.strip(): peruntukan_final = peruntukan_manual.strip()

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br><br>📝 **Uraian / Keterangan Tagihan**", unsafe_allow_html=True)
        with c2: keterangan = st.text_area("Keterangan", placeholder="Uraian pekerjaan atau layanan jasa penagihan...", label_visibility="collapsed", key=f"ket_inv_{idx}")
        
        # Nilai Transaksi (DPP)
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>💰 **Nilai Transaksi (DPP / Dasar)**", unsafe_allow_html=True)
        with c2:
            dpp = st.number_input("DPP", min_value=0.0, step=10000.0, format="%.2f", value=0.0, label_visibility="collapsed", key=f"val_dpp_inv_{idx}")
        
        c1, c2 = st.columns([1, 2])
        with c1: 
            st.markdown("<br>🏷️ **PPN (Pajak Pertambahan Nilai)**", unsafe_allow_html=True)
            pakai_ppn = st.checkbox("Gunakan PPN (11% Otomatis)", key=f"chk_ppn_inv_{idx}")
        with c2:
            st.info("💡 Centang PPN, pilih tarif PPh, lalu klik tombol hitung di bawah.")
        
        c1, c2 = st.columns([1, 2])
        with c1: 
            st.markdown("<br>📉 **PPH (Pajak Penghasilan)**", unsafe_allow_html=True)
            pakai_pph = st.checkbox("Gunakan PPh", key=f"chk_pph_inv_{idx}")
            tarif_pilihan = st.selectbox("Tarif PPh", [0.01, 0.015, 0.0175, 0.02, 0.03, 0.04], format_func=lambda x: f"{x*100}%".replace(".0", ""), key=f"sel_tarif_inv_{idx}", label_visibility="collapsed")
        with c2:
            if st.button("⚡ KLIK HITUNG PAJAK OTOMATIS", use_container_width=True, key=f"btn_hitung_inv_{idx}"):
                st.session_state[f'val_ppn_inv_{idx}'] = round(dpp * 0.11, 2) if pakai_ppn else 0.0
                st.session_state[f'val_pph_inv_{idx}'] = round(dpp * tarif_pilihan, 2) if pakai_pph else 0.0
                st.success("Kalkulasi PPN & PPh berhasil diterapkan!")
                st.rerun()

        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🔹 **Nominal PPN**", unsafe_allow_html=True)
        with c2: ppn = st.number_input("PPN", min_value=0.0, step=1000.0, format="%.2f", label_visibility="collapsed", key=f"val_ppn_inv_{idx}")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🔹 **Nominal PPh**", unsafe_allow_html=True)
        with c2: pph = st.number_input("PPh", min_value=0.0, step=1000.0, format="%.2f", label_visibility="collapsed", key=f"val_pph_inv_{idx}")
        
        total_transaksi = (dpp + ppn) - pph
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>💵 **Total Nilai Piutang / Invoice**", unsafe_allow_html=True)
        with c2: st.markdown(f"### **Rp {total_transaksi:,.2f}**")

        st.divider()
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Simpan Data Invoice Penjualan", use_container_width=True, key=f"btn_save_inv_{idx}"):
                if dpp > 0 and no_bukti and no_invoice_perusahaan and bu_final and lawan_transaksi_final:
                    data_baru = {
                        "Nomor Bukti": no_bukti, "Tanggal": tgl, "Sumber Transaksi": "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)",
                        "Lawan Transaksi": lawan_transaksi_final, "No Invoice": no_invoice_perusahaan,
                        "Jatuh Tempo": str(tgl_jatuh_tempo), "Business Unit": bu_final, "Departemen Tujuan": "Operasional",
                        "Jumlah": jumlah, "Satuan": satuan_final, "Peruntukan": peruntukan_final, "Keterangan": keterangan, 
                        "DPP": dpp, "PPN": ppn, "PPH": pph, "Total": total_transaksi, 
                        "Status Dokumen": "Menunggu Approval Kabag Operasional", "Status Jurnal": "Belum Dijurnal"
                    }
                    df_existing = st.session_state.data_operasional
                    if not df_existing.empty and no_bukti in df_existing['Nomor Bukti'].values:
                        df_existing.loc[df_existing['Nomor Bukti'] == no_bukti] = pd.DataFrame([data_baru]).values[0]
                        st.success(f"Nomor Bukti '{no_bukti}' berhasil diperbarui!")
                    else:
                        st.session_state.data_operasional = pd.concat([
                            df_existing, pd.DataFrame([data_baru])
                        ], ignore_index=True)
                        st.success("Data invoice penjualan berhasil disimpan!")
                else:
                    st.error("Mohon lengkapi Nomor Bukti, Pelanggan, No Invoice, Business Unit, dan nilai DPP > 0.")
                    
        with col_b2:
            if st.button("➕ Simpan & Mulai Entri Baru", use_container_width=True, key=f"btn_save_new_inv_{idx}"):
                if dpp > 0 and no_bukti and no_invoice_perusahaan and bu_final and lawan_transaksi_final:
                    data_baru = {
                        "Nomor Bukti": no_bukti, "Tanggal": tgl, "Sumber Transaksi": "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)",
                        "Lawan Transaksi": lawan_transaksi_final, "No Invoice": no_invoice_perusahaan,
                        "Jatuh Tempo": str(tgl_jatuh_tempo), "Business Unit": bu_final, "Departemen Tujuan": "Operasional",
                        "Jumlah": jumlah, "Satuan": satuan_final, "Peruntukan": peruntukan_final, "Keterangan": keterangan, 
                        "DPP": dpp, "PPN": ppn, "PPH": pph, "Total": total_transaksi, 
                        "Status Dokumen": "Menunggu Approval Kabag Operasional", "Status Jurnal": "Belum Dijurnal"
                    }
                    df_existing = st.session_state.data_operasional
                    if not df_existing.empty and no_bukti in df_existing['Nomor Bukti'].values:
                        df_existing.loc[df_existing['Nomor Bukti'] == no_bukti] = pd.DataFrame([data_baru]).values[0]
                    else:
                        st.session_state.data_operasional = pd.concat([
                            df_existing, pd.DataFrame([data_baru])
                        ], ignore_index=True)
                    st.session_state.form_index_inv += 1
                    st.success("Tersimpan! Form diset ke entri baru.")
                    st.rerun()
                else:
                    st.error("Mohon lengkapi Nomor Bukti, Pelanggan, No Invoice, Business Unit, dan nilai DPP > 0.")