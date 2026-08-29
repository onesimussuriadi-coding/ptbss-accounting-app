import streamlit as st
import pandas as pd
from datetime import datetime

def render_modul_1():
    st.subheader("Modul 1: Penginputan Dokumen Operasional Harian")
    
    sumber_transaksi = st.selectbox("Pilih Sumber Dokumen", [
        "Kas Besar / Kas Proyek", "Kas Kecil (Petty Cash)", "Bank Masuk / Keluar",
        "Logistik & Pengadaan Barang", "Gudang", "Memorial / Koreksi"
    ])
    
    list_bu_opt = st.session_state.master_bu['ID BU'] + " - " + st.session_state.master_bu['Nama Business Unit'] if not st.session_state.master_bu.empty else ["BU-01 - Default"]

    idx = st.session_state.form_index
    
    if f'val_ppn_{idx}' not in st.session_state: st.session_state[f'val_ppn_{idx}'] = 0.0
    if f'val_pph_{idx}' not in st.session_state: st.session_state[f'val_pph_{idx}'] = 0.0

    if 'Supplier' not in st.session_state.data_operasional.columns:
        if not st.session_state.data_operasional.empty:
            st.session_state.data_operasional['Supplier'] = ""

    with st.container():
        # Tanggal
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📅 **Tanggal Transaksi**", unsafe_allow_html=True)
        with c2: tgl = st.date_input("Tanggal", datetime.now(), label_visibility="collapsed", key=f"tgl_{idx}")
        
        # Nomor Bukti
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🧾 **Nomor Bukti / Ref**", unsafe_allow_html=True)
        with c2: no_bukti = st.text_input("No Bukti", placeholder="Cth: BSS/KK/VIII/2026/001", label_visibility="collapsed", key=f"nobukti_{idx}")
        
        # --- DROPDOWN SUPPLIER & INPUT SUPPLIER BARU ---
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🏢 **Supplier / Vendor**", unsafe_allow_html=True)
        with c2:
            sub_sup1, sub_sup2 = st.columns([3, 1])
            with sub_sup1:
                supplier_pilihan = st.selectbox("Pilih Supplier", st.session_state.master_supplier, label_visibility="collapsed", key=f"supplier_sel_{idx}")
            with sub_sup2:
                tambah_supplier_baru = st.text_input("Supplier Baru", placeholder="Tambah baru...", label_visibility="collapsed", key=f"tambah_supplier_{idx}")
            
            # Logika Supplier Final: Jika kotak teks diisi, masukkan ke master supplier secara otomatis
            supplier_final = supplier_pilihan
            if tambah_supplier_baru.strip():
                supplier_baru_clean = tambah_supplier_baru.strip()
                supplier_final = supplier_baru_clean
                if supplier_baru_clean not in st.session_state.master_supplier:
                    st.session_state.master_supplier.append(supplier_baru_clean)

        # Business Unit
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🏢 **Business Unit / Proyek**", unsafe_allow_html=True)
        with c2: bu_pilihan = st.selectbox("Business Unit", list_bu_opt, label_visibility="collapsed", key=f"bu_{idx}")
        
        # Jumlah
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📦 **Jumlah (Volume / Qty)**", unsafe_allow_html=True)
        with c2: jumlah = st.number_input("Jumlah", min_value=0.0, step=1.0, value=1.0, label_visibility="collapsed", key=f"jml_{idx}")
        
        # Satuan
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>📏 **Satuan**", unsafe_allow_html=True)
        with c2:
            sub_sat1, sub_sat2 = st.columns([3, 1])
            with sub_sat1:
                satuan_pilihan = st.selectbox("Pilih Satuan", st.session_state.master_satuan, label_visibility="collapsed", key=f"satuan_{idx}")
            with sub_sat2:
                tambah_satuan_baru = st.text_input("Tambah Satuan", placeholder="Baru...", label_visibility="collapsed", key=f"tambah_satuan_{idx}")
            
            satuan_final = tambah_satuan_baru.strip() if tambah_satuan_baru.strip() else satuan_pilihan
            if tambah_satuan_baru.strip() and tambah_satuan_baru.strip() not in st.session_state.master_satuan:
                st.session_state.master_satuan.append(tambah_satuan_baru.strip())

        # Peruntukan
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🎯 **Peruntukan**", unsafe_allow_html=True)
        with c2: peruntukan = st.text_input("Peruntukan", placeholder="Cth: Unit Vacuum Truck...", label_visibility="collapsed", key=f"peruntukan_{idx}")
        
        # Uraian / Keterangan
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br><br>📝 **Uraian / Keterangan**", unsafe_allow_html=True)
        with c2: keterangan = st.text_area("Keterangan", placeholder="Uraian atau keterangan lengkap...", label_visibility="collapsed", key=f"ket_{idx}")
        
        # DPP
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>💰 **DPP (Nilai Dasar)**", unsafe_allow_html=True)
        with c2: dpp = st.number_input("DPP", min_value=0.0, step=10000.0, format="%.2f", label_visibility="collapsed", key=f"val_dpp_{idx}")
        
        # PPN Checkbox
        c1, c2 = st.columns([1, 2])
        with c1: 
            st.markdown("<br>🏷️ **PPN (Pajak Pertambahan Nilai)**", unsafe_allow_html=True)
            pakai_ppn = st.checkbox("Gunakan PPN (11% Otomatis)", key=f"chk_ppn_{idx}")
        with c2:
            st.info("💡 Centang opsi pajak di sebelah kiri, pilih tarif PPh, lalu klik tombol hitung di bawah.")
        
        # PPh Checkbox & Tarif
        c1, c2 = st.columns([1, 2])
        with c1: 
            st.markdown("<br>📉 **PPH (Pajak Penghasilan)**", unsafe_allow_html=True)
            pakai_pph = st.checkbox("Gunakan PPh", key=f"chk_pph_{idx}")
            tarif_pilihan = st.selectbox("Tarif PPh", [0.01, 0.015, 0.0175, 0.02, 0.03, 0.04], format_func=lambda x: f"{x*100}%".replace(".0", ""), key=f"sel_tarif_{idx}", label_visibility="collapsed")
        with c2:
            if st.button("⚡ KLIK DISINI UNTUK HITUNG PAJAK OTOMATIS", use_container_width=True):
                if pakai_ppn:
                    st.session_state[f'val_ppn_{idx}'] = round(dpp * 0.11, 2)
                else:
                    st.session_state[f'val_ppn_{idx}'] = 0.0
                    
                if pakai_pph:
                    st.session_state[f'val_pph_{idx}'] = round(dpp * tarif_pilihan, 2)
                else:
                    st.session_state[f'val_pph_{idx}'] = 0.0
                st.success("Kalkulasi PPN & PPh berhasil diterapkan!")
                st.rerun()

        # Input Nominal PPN
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🔹 **Nominal PPN**", unsafe_allow_html=True)
        with c2: ppn = st.number_input("PPN", min_value=0.0, step=1000.0, format="%.2f", label_visibility="collapsed", key=f"val_ppn_{idx}")
        
        # Input Nominal PPh
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>🔹 **Nominal PPh**", unsafe_allow_html=True)
        with c2: pph = st.number_input("PPh", min_value=0.0, step=1000.0, format="%.2f", label_visibility="collapsed", key=f"val_pph_{idx}")
        
        total_transaksi = (dpp + ppn) - pph
        
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown("<br>💵 **Total (DPP + PPN - PPh)**", unsafe_allow_html=True)
        with c2: st.markdown(f"### **Rp {total_transaksi:,.2f}**")

        st.divider()
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Simpan Data Dokumen", use_container_width=True):
                if dpp > 0 and no_bukti:
                    id_baru = f"DOC-{int(datetime.now().timestamp())}"
                    data_baru = {
                        "ID": id_baru, "Tanggal": tgl, "Sumber Transaksi": sumber_transaksi,
                        "Nomor Bukti": no_bukti, "Supplier": supplier_final, "Business Unit": bu_pilihan, 
                        "Jumlah": jumlah, "Satuan": satuan_final, "Peruntukan": peruntukan, 
                        "Keterangan": keterangan, "DPP": dpp, "PPN": ppn, "PPH": pph, 
                        "Total": total_transaksi, "Status Jurnal": "Belum Dijurnal"
                    }
                    st.session_state.data_operasional = pd.concat([
                        st.session_state.data_operasional, pd.DataFrame([data_baru])
                    ], ignore_index=True)
                    st.success("Dokumen berhasil disimpan!")
                else:
                    st.error("Mohon lengkapi Nomor Bukti dan pastikan nilai DPP lebih besar dari 0.")
                    
        with col_b2:
            if st.button("➕ Simpan & Tambah Baris Baru", use_container_width=True):
                if dpp > 0 and no_bukti:
                    id_baru = f"DOC-{int(datetime.now().timestamp())}"
                    data_baru = {
                        "ID": id_baru, "Tanggal": tgl, "Sumber Transaksi": sumber_transaksi,
                        "Nomor Bukti": no_bukti, "Supplier": supplier_final, "Business Unit": bu_pilihan, 
                        "Jumlah": jumlah, "Satuan": satuan_final, "Peruntukan": peruntukan, 
                        "Keterangan": keterangan, "DPP": dpp, "PPN": ppn, "PPH": pph, 
                        "Total": total_transaksi, "Status Jurnal": "Belum Dijurnal"
                    }
                    st.session_state.data_operasional = pd.concat([
                        st.session_state.data_operasional, pd.DataFrame([data_baru])
                    ], ignore_index=True)
                    
                    current_tgl = tgl
                    current_nobukti = no_bukti
                    st.session_state.form_index += 1
                    new_idx = st.session_state.form_index
                    st.session_state[f"tgl_{new_idx}"] = current_tgl
                    st.session_state[f"nobukti_{new_idx}"] = current_nobukti
                    
                    st.success("Dokumen tersimpan! Tanggal & Nomor Bukti dipertahankan untuk baris baru.")
                    st.rerun()
                else:
                    st.error("Mohon lengkapi Nomor Bukti dan pastikan nilai DPP lebih besar dari 0.")

    st.divider()
    st.markdown("### 📋 Daftar Dokumen Masuk & Menu Koreksi (Edit / Update / Hapus)")
    
    if not st.session_state.data_operasional.empty:
        st.dataframe(st.session_state.data_operasional, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 🔄 Panggil Ulang Dokumen untuk Diedit atau Dihapus")
        
        list_id_doc = st.session_state.data_operasional['ID'].tolist()
        pilih_id_edit = st.selectbox("Pilih ID Dokumen yang Ingin Dikoreksi", list_id_doc)
        
        if pilih_id_edit:
            row_data = st.session_state.data_operasional[st.session_state.data_operasional['ID'] == pilih_id_edit].iloc[0]
            
            with st.form("form_koreksi_dokumen"):
                st.info(f"Sedang mengedit Dokumen ID: **{pilih_id_edit}** (No Bukti: {row_data['Nomor Bukti']})")
                
                ed_nobukti = st.text_input("Nomor Bukti", value=row_data['Nomor Bukti'])
                ed_supplier = st.text_input("Supplier / Vendor", value=row_data.get('Supplier', ''))
                ed_dpp = st.number_input("DPP (Nilai Dasar)", value=float(row_data['DPP']), step=10000.0, format="%.2f")
                ed_ppn = st.number_input("PPN", value=float(row_data['PPN']), step=1000.0, format="%.2f")
                ed_pph = st.number_input("PPh", value=float(row_data['PPH']), step=1000.0, format="%.2f")
                ed_ket = st.text_area("Uraian / Keterangan", value=row_data['Keterangan'])
                
                ed_total = (ed_dpp + ed_ppn) - ed_pph
                st.markdown(f"**Total Baru (DPP + PPN - Ph): Rp {ed_total:,.2f}**")
                
                col_e1, col_e2 = st.columns(2)
                with col_e1: btn_update = st.form_submit_button("🔄 Update / Simpan Perubahan")
                with col_e2: btn_hapus = st.form_submit_button("🗑️ Hapus Dokumen Ini")
                
                if btn_update:
                    st.session_state.data_operasional.loc[st.session_state.data_operasional['ID'] == pilih_id_edit, ['Nomor Bukti', 'Supplier', 'DPP', 'PPN', 'PPH', 'Total', 'Keterangan']] = [ed_nobukti, ed_supplier, ed_dpp, ed_ppn, ed_pph, ed_total, ed_ket]
                    st.success(f"Dokumen {pilih_id_edit} berhasil diperbarui!")
                    st.rerun()
                    
                if btn_hapus:
                    st.session_state.data_operasional = st.session_state.data_operasional[st.session_state.data_operasional['ID'] != pilih_id_edit]
                    st.success(f"Dokumen {pilih_id_edit} berhasil dihapus dari daftar!")
                    st.rerun()
    else:
        st.info("Belum ada dokumen operasional yang tersimpan.")