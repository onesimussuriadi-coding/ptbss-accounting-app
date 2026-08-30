import streamlit as st
import pandas as pd
import os

def render_pembelian_kredit():
    st.markdown("### 📝 Form Entri: Tagihan / Pembelian Kredit (Hutang Usaha)")
    st.markdown("Gunakan form ini untuk mencatat transaksi pembelian atau penerimaan tagihan kredit dari pemasok/vendor.")

    # --- 1. MEMBACA MASTER PEMASOK / VENDOR (NAMA BUKAN KODE) ---
    list_supplier_opsi = ["- Tidak Ada / Kas Tunai -"]
    file_pemasok = "master_pemasok_bss.xlsx"
    
    if os.path.exists(file_pemasok):
        try:
            df_sup_file = pd.read_excel(file_pemasok)
            # Cari kolom yang berisi Nama Pemasok, hindari kolom kode/ID
            kolom_nama = None
            for col in df_sup_file.columns:
                col_lower = col.lower()
                if "nama" in col_lower or "pemasok" in col_lower or "vendor" in col_lower or "supplier" in col_lower:
                    kolom_nama = col
                    break
            
            # Jika tidak ketemu spesifik, ambil kolom teks selain kolom pertama (biasanya kode)
            if not kolom_nama and len(df_sup_file.columns) > 1:
                kolom_nama = df_sup_file.columns[1] 
            elif not kolom_nama and len(df_sup_file.columns) == 1:
                kolom_nama = df_sup_file.columns[0]

            if kolom_nama:
                list_sup_excel = df_sup_file[kolom_nama].dropna().astype(str).tolist()
                for sup in list_sup_excel:
                    if sup not in list_supplier_opsi:
                        list_supplier_opsi.append(sup)
        except Exception:
            pass

    if 'master_supplier' in st.session_state and isinstance(st.session_state.master_supplier, list):
        for sup in st.session_state.master_supplier:
            if sup not in list_supplier_opsi:
                list_supplier_opsi.append(sup)

    # Tambahkan opsi manual pihak ketiga
    list_supplier_opsi.append("-- Ketik Nama Pemasok Lain / Pihak Ketiga --")

    # --- 2. MASTER BUSINESS UNIT ---
    list_bu_opsi = ["Operasional Kantor Pusat", "CR JOB Jalan Masing", "Proyek Drilling", "Proyek Slickline"]
    if 'master_bu' in st.session_state:
        df_bu_check = st.session_state.master_bu
        if not df_bu_check.empty and 'Nama Business Unit' in df_bu_check.columns:
            list_bu_opsi = df_bu_check['Nama Business Unit'].tolist()

    # --- 3. MASTER ALAT / PERUNTUKAN DARI EXCEL MODUL 0 ---
    list_peruntukan_opsi = ["Operasional Umum", "Kendaraan Operasional", "Alat Berat / Rig", "Generator Set"]
    file_alat = "master_alat_bss.xlsx"
    if os.path.exists(file_alat):
        try:
            df_alat_file = pd.read_excel(file_alat)
            kolom_alat = None
            for col in df_alat_file.columns:
                if any(k in col.lower() for k in ["nama", "alat", "unit", "deskripsi", "peruntukan"]):
                    kolom_alat = col
                    break
            if not kolom_alat and len(df_alat_file.columns) > 0:
                kolom_alat = df_alat_file.columns[0]
            if kolom_alat:
                list_alat_excel = df_alat_file[kolom_alat].dropna().astype(str).tolist()
                for alt in list_alat_excel:
                    if alt not in list_peruntukan_opsi:
                        list_peruntukan_opsi.append(alt)
        except Exception:
            pass

    list_satuan_opsi = st.session_state.get('master_satuan', ["Unit", "Lot", "Liter", "Jam", "Pcs", "Hari", "Bulan", "Trip", "M3"])

    if 'pembelian_items' not in st.session_state:
        st.session_state.pembelian_items = [{"jumlah": 1.0, "satuan": "Unit", "peruntukan": list_peruntukan_opsi[0]}]

    with st.form("form_pembelian_kredit_v2", clear_on_submit=False):
        
        # Baris 1: Nomor Bukti & Business Unit
        c1, c2 = st.columns(2)
        with c1:
            lbl1, inp1 = st.columns([1.2, 1.8])
            with lbl1: st.markdown("📌 **Nomor Bukti / Transaksi**")
            with inp1: no_bukti = st.text_input("No Bukti", value="BKK-CR-2026-001", label_visibility="collapsed")
        with c2:
            lbl2, inp2 = st.columns([1.2, 1.8])
            with lbl2: st.markdown("🏗️ **Business Unit / Proyek**")
            with inp2: business_unit = st.selectbox("BU", list_bu_opsi, label_visibility="collapsed")

        # Baris 2: Tanggal Transaksi & Departemen Tujuan
        c3, c4 = st.columns(2)
        with c3:
            lbl3, inp3 = st.columns([1.2, 1.8])
            with lbl3: st.markdown("📅 **Tanggal Transaksi**")
            with inp3: tanggal_trx = st.date_input("Tgl Trx", label_visibility="collapsed")
        with c4:
            lbl4, inp4 = st.columns([1.2, 1.8])
            with lbl4: st.markdown("🎯 **Departemen Tujuan**")
            with inp4: dept_tujuan = st.selectbox("Dept", ["Operasional", "HRD", "Logistik", "Maintenance", "HSE", "Akuntansi", "Keuangan"], label_visibility="collapsed")

        # Baris 3: Pemasok / Vendor (Dengan Opsi Pihak Ketiga) & No Invoice
        c5, c6 = st.columns(2)
        with c5:
            lbl5, inp5 = st.columns([1.2, 1.8])
            with lbl5: st.markdown("🏢 **Pemasok / Vendor**")
            with inp5: 
                pemasok_pilihan = st.selectbox("Pemasok", list_supplier_opsi, label_visibility="collapsed")
        with c6:
            lbl6, inp6 = st.columns([1.2, 1.8])
            with lbl6: st.markdown("📄 **No Invoice Supplier**")
            with inp6: no_invoice = st.text_input("Invoice", value="-", label_visibility="collapsed")

        # Input opsional jika memilih Pihak Ketiga / Lainnya
        pemasok = pemasok_pilihan
        if pemasok_pilihan == "-- Ketik Nama Pemasok Lain / Pihak Ketiga --":
            st.markdown("<br>", unsafe_allow_html=True)
            pemasok = st.text_input("✍️ Masukkan Nama Pemasok / Pihak Ketiga Lainnya:", placeholder="Ketik nama vendor/pihak ketiga di sini...")

        # Baris 4: Jatuh Tempo Hutang
        c7, c8 = st.columns(2)
        with c7:
            lbl7, inp7 = st.columns([1.2, 1.8])
            with lbl7: st.markdown("⏳ **Jatuh Tempo Hutang**")
            with inp7: jatuh_tempo = st.date_input("Jatuh Tempo", label_visibility="collapsed")

        st.markdown("---")
        st.markdown("#### 📦 Rincian Item / Volume Pembelian")
        
        for idx, item in enumerate(st.session_state.pembelian_items):
            ic1, ic2, ic3 = st.columns([1, 1, 2])
            with ic1:
                st.session_state.pembelian_items[idx]['jumlah'] = st.number_input(f"Jumlah {idx}", min_value=0.0, value=item['jumlah'], step=1.0, key=f"qty_{idx}")
            with ic2:
                st.session_state.pembelian_items[idx]['satuan'] = st.selectbox(f"Satuan {idx}", list_satuan_opsi, index=0, key=f"sat_{idx}")
            with ic3:
                # Peruntukan ditarik dari data master alat/unit Excel
                st.session_state.pembelian_items[idx]['peruntukan'] = st.selectbox(f"Peruntukan {idx}", list_peruntukan_opsi, key=f"per_{idx}")

        st.markdown("---")

        # Uraian / Keterangan Transaksi di atas rincian keuangan
        st.markdown("##### 📝 Uraian / Keterangan Transaksi")
        keterangan = st.text_area("Keterangan", placeholder="Tuliskan keterangan detail pembelian kredit di sini...", label_visibility="collapsed")
        st.markdown("---")

        # Rincian Nilai Keuangan
        st.markdown("#### 💰 Rincian Nilai Keuangan (DPP, PPN, PPh)")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.markdown("**DPP / Nilai Pokok (Rp)**")
            dpp_val = st.number_input("DPP", min_value=0.0, value=0.0, step=10000.0, format="%.2f", label_visibility="collapsed")
        with col_f2:
            st.markdown("**PPN (Rp)**")
            ppn_val = st.number_input("PPN", min_value=0.0, value=0.0, step=1000.0, format="%.2f", label_visibility="collapsed")
        with col_f3:
            st.markdown("**PPh (Rp)**")
            pph_val = st.number_input("PPh", min_value=0.0, value=0.0, step=1000.0, format="%.2f", label_visibility="collapsed")

        total_val = (dpp_val + ppn_val) - pph_val
        st.markdown(f"### **Total Tagihan Bersih: Rp {total_val:,.2f}**")
        st.markdown("<br>", unsafe_allow_html=True)

        # Tombol Aksi
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
            submitted = st.form_submit_button("💾 Simpan / Update", use_container_width=True)
        with b_col2:
            btn_edit = st.form_submit_button("✏️ Edit Dokumen", use_container_width=True)
        with b_col3:
            btn_tambah_baris = st.form_submit_button("➕ Tambah Baris", use_container_width=True)
        with b_col4:
            btn_refresh = st.form_submit_button("🔄 Refresh Baru", use_container_width=True)

        if btn_tambah_baris:
            st.session_state.pembelian_items.append({"jumlah": 1.0, "satuan": "Unit", "peruntukan": list_peruntukan_opsi[0]})
            st.rerun()

        if btn_refresh:
            st.session_state.pembelian_items = [{"jumlah": 1.0, "satuan": "Unit", "peruntukan": list_peruntukan_opsi[0]}]
            st.success("Form berhasil di-refresh untuk input baru!")
            st.rerun()

        if submitted:
            if not no_bukti or not pemasok:
                st.error("Nomor Bukti dan Pemasok wajib diisi!")
            else:
                data_baru = {
                    "Nomor Bukti": no_bukti,
                    "Tanggal": str(tanggal_trx),
                    "Sumber Transaksi": "Tagihan / Pembelian Kredit (Hutang Usaha)",
                    "Lawan Transaksi": pemasok,
                    "No Invoice": no_invoice,
                    "Jatuh Tempo": str(jatuh_tempo),
                    "Business Unit": business_unit,
                    "Departemen Tujuan": dept_tujuan,
                    "Jumlah": st.session_state.pembelian_items[0]['jumlah'],
                    "Satuan": st.session_state.pembelian_items[0]['satuan'],
                    "Peruntukan": st.session_state.pembelian_items[0]['peruntukan'],
                    "Keterangan": keterangan,
                    "DPP": dpp_val,
                    "PPN": ppn_val,
                    "PPH": pph_val,
                    "Total": total_val,
                    "Status Dokumen": "Menunggu Approval Kabag",
                    "Status Jurnal": "Belum Dijurnal"
                }

                if 'data_operasional' in st.session_state:
                    df_existing = st.session_state.data_operasional
                    if not df_existing.empty and no_bukti in df_existing['Nomor Bukti'].values:
                        st.warning(f"Nomor Bukti {no_bukti} sudah ada di dalam sistem. Mohon gunakan nomor lain.")
                    else:
                        new_row_df = pd.DataFrame([data_baru])
                        st.session_state.data_operasional = pd.concat([df_existing, new_row_df], ignore_index=True)
                        st.success(f"Dokumen Pembelian Kredit dengan No. Bukti **{no_bukti}** berhasil disimpan!")
                else:
                    st.session_state.data_operasional = pd.DataFrame([data_baru])
                    st.success(f"Dokumen Pembelian Kredit dengan No. Bukti **{no_bukti}** berhasil disimpan!")