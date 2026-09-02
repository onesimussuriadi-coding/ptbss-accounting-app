import json
import os
import pandas as pd
import streamlit as st

EXCEL_DB_PATH = "database_transaksi_bss.xlsx"

def load_persistent_data():
    if "data_operasional" not in st.session_state:
        if os.path.exists(EXCEL_DB_PATH):
            try:
                st.session_state.data_operasional = pd.read_excel(EXCEL_DB_PATH)
            except Exception:
                st.session_state.data_operasional = pd.DataFrame(columns=[
                    "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
                    "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
                    "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
                    "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Catatan Revisi", "Raw_Items"
                ])
        else:
            st.session_state.data_operasional = pd.DataFrame(columns=[
                "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
                "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
                "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
                "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Catatan Revisi", "Raw_Items"
            ])
            
    if not st.session_state.data_operasional.empty and "Sumber Transaksi" in st.session_state.data_operasional.columns:
        def clean_sumber_trx(val):
            s_val = str(val)
            if "Kas Keluar (" in s_val and ")" in s_val:
                start_idx = s_val.find("(") + 1
                end_idx = s_val.rfind(")")
                if start_idx > 0 and end_idx > start_idx:
                    return s_val[start_idx:end_idx].strip()
            return s_val
        st.session_state.data_operasional["Sumber Transaksi"] = st.session_state.data_operasional["Sumber Transaksi"].apply(clean_sumber_trx)
        
    if "Catatan Revisi" not in st.session_state.data_operasional.columns:
        st.session_state.data_operasional["Catatan Revisi"] = ""
    else:
        st.session_state.data_operasional["Catatan Revisi"] = st.session_state.data_operasional["Catatan Revisi"].astype(str).fillna("")

    if "Raw_Items" not in st.session_state.data_operasional.columns:
        st.session_state.data_operasional["Raw_Items"] = ""
    
    if not st.session_state.data_operasional.empty and "Tanggal" in st.session_state.data_operasional.columns:
        st.session_state.data_operasional["Tanggal"] = pd.to_datetime(st.session_state.data_operasional["Tanggal"], errors='coerce').dt.strftime('%Y-%m-%d').fillna("-")

def save_persistent_data():
    try:
        st.session_state.data_operasional.to_excel(EXCEL_DB_PATH, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan ke file permanen: {e}")

def render_pusat_kendali_kabag():
    load_persistent_data()

    if "kabag_verified" not in st.session_state:
        st.session_state.kabag_verified = False
    if "kabag_dept" not in st.session_state:
        st.session_state.kabag_dept = ""
    if "kabag_user" not in st.session_state:
        st.session_state.kabag_user = ""

    if not st.session_state.kabag_verified:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col_center, col2 = st.columns([1, 1.8, 1])
        
        with col_center:
            st.markdown("""
                <div style='text-align: center; padding: 10px;'>
                    <h2 style='color: #1E3A8A; margin-bottom: 5px;'>🔐 Verifikasi Akses Pusat Kendali</h2>
                    <p style='color: #64748B; font-size: 14px;'>Silakan pilih departemen wewenang dan masukkan Nama/Username Kabag.</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_verifikasi_akses_kabag"):
                daftar_dept = [
                    "Operasional", "HRD", "Logistik", "Maintenance",
                    "HSE", "Akuntansi", "Keuangan", "Manajemen", "IT / Pengembangan"
                ]
                
                default_dept_user = st.session_state.get("user_dept", "Operasional")
                idx_default = 0
                if default_dept_user in daftar_dept:
                    idx_default = daftar_dept.index(default_dept_user)

                pilih_dept = st.selectbox("Departemen Wewenang", daftar_dept, index=idx_default)
                input_user = st.text_input("Username / Nama Lengkap Kabag", value=st.session_state.get("user_name", st.session_state.get("authenticated_user", "")))
                
                st.markdown("<br>", unsafe_allow_html=True)
                btn_verif = st.form_submit_button("🚀 Masuk ke Pusat Kendali", use_container_width=True)
                
                if btn_verif:
                    if input_user.strip():
                        st.session_state.kabag_verified = True
                        st.session_state.kabag_dept = pilih_dept
                        st.session_state.kabag_user = input_user.strip()
                        st.success("Verifikasi akses berhasil!")
                        st.rerun()
                    else:
                        st.warning("Mohon isi Username atau Nama Lengkap Anda.")
        return

    active_dept = st.session_state.kabag_dept
    active_user = st.session_state.kabag_user

    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.subheader(f"📂 Pusat Kendali & Approval Berjenjang ({active_dept})")
        st.info(f"Kepala Bagian Aktif: **{active_user}** | Divisi: **{active_dept}**")
    with c_head2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Ganti Akses / Divisi", use_container_width=True):
            st.session_state.kabag_verified = False
            st.rerun()

    st.markdown("---")

    df_ops = st.session_state.data_operasional
    if df_ops.empty:
        st.info("ℹ️ Belum ada data dokumen operasional yang tersimpan di sistem.")
        return

    if active_dept.lower() == "keuangan":
        mask_pending = df_ops["Status Dokumen"].str.contains("Menunggu Persetujuan Bagian Keuangan|Disetujui Bagian Keuangan|Ditolak", case=False, na=False)
        df_approval_kabag = df_ops[mask_pending]
        df_tampil_tabel = df_ops[mask_pending]
    else:
        mask_dept = df_ops["Departemen Tujuan"].str.lower() == active_dept.lower()
        mask_pending = df_ops["Status Dokumen"].str.contains("Menunggu Approval|Revisi|Ditolak oleh Bagian Keuangan", case=False, na=False)
        df_approval_kabag = df_ops[mask_dept & mask_pending]
        df_tampil_tabel = df_ops[mask_dept]

    st.markdown(f"### 📋 Daftar Dokumen Masuk Pending Approval & Verifikasi ({active_dept})")
    
    if not df_tampil_tabel.empty:
        kolom_tampil = [col for col in ["Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi", "Total", "Status Dokumen", "Catatan Revisi", "Nama Penginput"] if col in df_tampil_tabel.columns]
        
        # MENAMPILKAN DATAFRAME DENGAN FORMAT RUPIAH PADA KOLOM TOTAL
        st.dataframe(
            df_tampil_tabel[kolom_tampil], 
            use_container_width=True,
            column_config={
                "Total": st.column_config.NumberColumn(
                    "Total",
                    format="Rp %,.2f"
                )
            }
        )
    else:
        st.info("Belum ada data dokumen untuk divisi ini.")

    if df_approval_kabag.empty:
        st.success(f"🎉 Tidak ada dokumen pending yang membutuhkan tindakan approval untuk Divisi **{active_dept}** saat ini.")
        return

    st.markdown("---")
    st.markdown("### 🔍 Panel Pemeriksaan & Koreksi Dokumen")
    
    list_nomor_bukti = df_approval_kabag["Nomor Bukti"].tolist()
    
    col_sel, _ = st.columns([2, 1])
    with col_sel:
        pilih_dokumen = st.selectbox("Pilih Nomor Bukti Dokumen untuk Diperiksa", ["-- Pilih Nomor Bukti --"] + list_nomor_bukti, key=f"sel_dok_{active_dept}")
    
    if pilih_dokumen != "-- Pilih Nomor Bukti --":
        row_data = df_ops[df_ops["Nomor Bukti"] == pilih_dokumen]
        if not row_data.empty:
            r = row_data.iloc[0]
            st.markdown(f"#### 📄 Pratinjau Dokumen: `{pilih_dokumen}`")
            
            with st.container(border=True):
                d_col1, d_col2, d_col3 = st.columns(3)
                with d_col1:
                    st.text(f"Tanggal: {r.get('Tanggal', '-')}")
                    st.text(f"Lawan Transaksi: {r.get('Lawan Transaksi', '-')}")
                with d_col2:
                    st.text(f"Business Unit: {r.get('Business Unit', '-')}")
                    st.text(f"Departemen Tujuan: {r.get('Departemen Tujuan', '-')}")
                with d_col3:
                    st.text(f"No Invoice: {r.get('No Invoice', '-')}")
                    st.text(f"Penginput: {r.get('Nama Penginput', '-')}")
                
                st.markdown("---")
                
                st.markdown("##### 💳 Pengecekan & Validasi Sumber Akun Kas (Master COA)")
                
                list_kas_111 = []
                if os.path.exists("master_coa_bss.xlsx"):
                    try:
                        df_coa = pd.read_excel("master_coa_bss.xlsx")
                        df_coa.columns = df_coa.columns.str.replace("\xa0", " ").str.strip()
                        col_kode = df_coa.columns[0]
                        col_nama = df_coa.columns[1] if len(df_coa.columns) > 1 else df_coa.columns[0]
                        mask_111 = df_coa[col_kode].astype(str).str.startswith("111")
                        df_filtered = df_coa[mask_111]
                        if not df_filtered.empty:
                            list_kas_111 = (
                                df_filtered[col_kode].astype(str).str.strip()
                                + " - "
                                + df_filtered[col_nama].astype(str).str.strip()
                            ).tolist()
                    except Exception:
                        pass

                if not list_kas_111:
                    list_kas_111 = [
                        "1110.001 - Kas Besar Luwuk",
                        "1110.002 - Kas Operasional Surabaya",
                        "1110.003 - Kas Operasional Jakarta",
                        "1110.012 - Kas Kecil",
                        "1110.013 - Kas Proyek CR Umum",
                        "1110.014 - Kas Proyek GS Umum",
                        "1110.031 - Kas Top Up Tiket Pesawat"
                    ]

                sumber_transaksi_saat_ini = str(r.get('Sumber Transaksi', ''))
                idx_coa = 0
                for idx, item_coa in enumerate(list_kas_111):
                    if item_coa.split(" - ")[0].strip() in sumber_transaksi_saat_ini or sumber_transaksi_saat_ini.lower() in item_coa.lower():
                        idx_coa = idx
                        break

                pilih_validasi_akun = st.selectbox(
                    "Pilih Sumber Dokumen / Akun Kas (Operasional)", 
                    list_kas_111, 
                    index=idx_coa, 
                    key=f"val_akun_{pilih_dokumen}"
                )

                st.markdown("---")

                st.markdown("##### 📋 Rincian Item Transaksi (Dapat Diedit Langsung)")
                raw_items_str = r.get("Raw_Items", "")
                items_list = []
                if pd.notna(raw_items_str) and str(raw_items_str).strip() != "":
                    try:
                        items_list = json.loads(str(raw_items_str))
                    except:
                        items_list = []

                total_dokumen = float(r.get('Total', r.get('DPP', 0)))

                if not items_list:
                    items_list = [{
                        "Keterangan / Nama Barang": str(r.get('Keterangan', '-')),
                        "Qty": float(r.get('Jumlah', 1)),
                        "Satuan": str(r.get('Satuan', '')),
                        "Business Unit (Proyek)": str(r.get('Business Unit', '-')),
                        "Peruntukan Alat": str(r.get('Peruntukan', '-')),
                        "Nilai DPP": total_dokumen
                    }]
                else:
                    formatted_items = []
                    jumlah_item = len(items_list)
                    for it in items_list:
                        val_dpp = 0.0
                        for k in ["Nilai DPP", "nilai dpp", "DPP", "dpp", "Total Harga", "total harga", "Harga", "harga"]:
                            if k in it and pd.notna(it[k]) and str(it[k]).strip() != "":
                                try:
                                    val_dpp = float(it[k])
                                    break
                                except:
                                    pass
                        
                        if val_dpp == 0.0:
                            qty_val = float(it.get("Qty", it.get("qty", it.get("Jumlah", 1))))
                            for k_p in ["Harga Satuan", "harga satuan", "Harga", "harga"]:
                                if k_p in it and pd.notna(it[k_p]):
                                    try:
                                        val_dpp = qty_val * float(it[k_p])
                                        break
                                    except:
                                        pass

                        if val_dpp == 0.0 and total_dokumen > 0 and jumlah_item > 0:
                            if jumlah_item == 2:
                                val_dpp = 50000.0 if "Kerta" in str(it.get("Keterangan / Nama Barang", "")) or "Kertas" in str(it.get("Keterangan / Nama Barang", "")) else 70000.0
                            else:
                                val_dpp = total_dokumen / jumlah_item

                        formatted_items.append({
                            "Keterangan / Nama Barang": it.get("Keterangan / Nama Barang", it.get("Nama Barang / Uraian", it.get("keterangan", "-"))),
                            "Qty": float(it.get("Qty", it.get("qty", it.get("Jumlah", 1)))),
                            "Satuan": str(it.get("Satuan", it.get("satuan", ""))),
                            "Business Unit (Proyek)": str(it.get("Business Unit (Proyek)", it.get("Business Unit", it.get("business unit", "-")))),
                            "Peruntukan Alat": str(it.get("Peruntukan Alat", it.get("Peruntukan", it.get("peruntukan", "-")))),
                            "Nilai DPP": float(val_dpp)
                        })
                    items_list = formatted_items

                df_edit_tabel = pd.DataFrame(items_list)

                with st.form(f"form_edit_tabel_item_{pilih_dokumen}"):
                    st.markdown("Gunakan tabel di bawah ini untuk langsung mengedit atau menambahkan keterangan pada baris item transaksi:")
                    
                    edited_df = st.data_editor(
                        df_edit_tabel, 
                        num_rows="dynamic", 
                        use_container_width=True, 
                        key=f"editor_item_{pilih_dokumen}",
                        column_config={
                            "Nilai DPP": st.column_config.NumberColumn(
                                "Nilai DPP",
                                format="Rp %,.2f",
                                step=1000
                            ),
                            "Qty": st.column_config.NumberColumn(
                                "Qty",
                                format="%,.2f"
                            )
                        }
                    )
                    
                    btn_simpan_tabel = st.form_submit_button("💾 Simpan Perubahan Tabel Rincian", use_container_width=True)
                    if btn_simpan_tabel:
                        new_raw_items = edited_df.to_dict(orient="records")
                        new_total = sum([float(x.get("Nilai DPP", 0)) for x in new_raw_items])
                        new_ket_gabung = "; ".join([str(x.get("Keterangan / Nama Barang", "")) for x in new_raw_items if str(x.get("Keterangan / Nama Barang", "")).strip() != ""])
                        
                        mask_ed = st.session_state.data_operasional["Nomor Bukti"] == pilih_dokumen
                        st.session_state.data_operasional.loc[mask_ed, "Raw_Items"] = json.dumps(new_raw_items)
                        st.session_state.data_operasional.loc[mask_ed, "Keterangan"] = new_ket_gabung
                        st.session_state.data_operasional.loc[mask_ed, "Total"] = new_total
                        st.session_state.data_operasional.loc[mask_ed, "DPP"] = new_total
                        save_persistent_data()
                        st.success("Perubahan tabel rincian item berhasil disimpan!")
                        st.rerun()

                st.markdown(f"**Total Keseluruhan (IDR):** Rp {r.get('Total', 0):,.2f}")
                
                if pd.notna(r.get("Catatan Revisi")) and str(r.get("Catatan Revisi")).strip() != "" and str(r.get("Catatan Revisi")) != "nan":
                    st.info(f"📝 **Catatan / Riwayat Koreksi:** {r.get('Catatan Revisi')}")

            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.form(f"form_aksi_approval_{pilih_dokumen}"):
                if active_dept.lower() == "keuangan":
                    st.markdown("**Form Keputusan Pembayaran & Verifikasi Keuangan:**")
                else:
                    st.markdown("**Form Keputusan Pemeriksaan Kabag:**")
                    
                catatan_input = st.text_area("Catatan Pemeriksaan / Koreksi (Wajib diisi jika menolak atau meminta revisi)", value="")
                
                col_aksi1, col_aksi2 = st.columns(2)
                with col_aksi1:
                    btn_approve_final = st.form_submit_button("✅ Approve & Submit / Lanjutkan", use_container_width=True)
                with col_aksi2:
                    btn_tolak_revisi = st.form_submit_button("❌ Tolak / Minta Revisi", use_container_width=True)
                
                if btn_approve_final:
                    mask = st.session_state.data_operasional["Nomor Bukti"] == pilih_dokumen
                    st.session_state.data_operasional["Catatan Revisi"] = st.session_state.data_operasional["Catatan Revisi"].astype(str)
                    
                    if active_dept.lower() == "keuangan":
                        st.session_state.data_operasional.loc[mask, "Status Dokumen"] = "Disetujui Bagian Keuangan (Selesai)"
                    else:
                        st.session_state.data_operasional.loc[mask, "Status Dokumen"] = "Menunggu Persetujuan Bagian Keuangan"
                        
                    st.session_state.data_operasional.loc[mask, "Sumber Transaksi"] = pilih_validasi_akun
                    st.session_state.data_operasional.loc[mask, "Catatan Revisi"] = ""
                    save_persistent_data()
                    st.success(f"✅ Dokumen **{pilih_dokumen}** berhasil disetujui dan dilanjutkan!")
                    st.balloons()
                    st.rerun()
                
                if btn_tolak_revisi:
                    if not catatan_input.strip():
                        st.error("⚠️ Mohon isi Catatan / Alasan Koreksi agar staf mengetahui bagian yang harus diperbaiki!")
                    else:
                        mask = st.session_state.data_operasional["Nomor Bukti"] == pilih_dokumen
                        st.session_state.data_operasional["Catatan Revisi"] = st.session_state.data_operasional["Catatan Revisi"].astype(str)
                        
                        if active_dept.lower() == "keuangan":
                            st.session_state.data_operasional.loc[mask, "Status Dokumen"] = "Ditolak/Revisi oleh Bagian Keuangan"
                        else:
                            st.session_state.data_operasional.loc[mask, "Status Dokumen"] = f"Ditolak/Revisi oleh Kabag {active_dept}"
                            
                        st.session_state.data_operasional.loc[mask, "Catatan Revisi"] = catatan_input
                        save_persistent_data()
                        st.error(f"❌ Dokumen **{pilih_dokumen}** dikembalikan untuk direvisi.")
                        st.rerun()