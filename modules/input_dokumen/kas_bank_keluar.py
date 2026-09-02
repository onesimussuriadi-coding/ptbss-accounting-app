from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

# File database permanen yang tersimpan di direktori lokal / sinkronisasi Google Drive
EXCEL_DB_PATH = "database_transaksi_bss.xlsx"

def load_persistent_data():
    """Memuat data transaksi secara permanen dari file Excel."""
    if "data_operasional" not in st.session_state:
        if os.path.exists(EXCEL_DB_PATH):
            try:
                st.session_state.data_operasional = pd.read_excel(EXCEL_DB_PATH)
            except Exception:
                st.session_state.data_operasional = pd.DataFrame(columns=[
                    "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
                    "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
                    "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
                    "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Raw_Items"
                ])
        else:
            st.session_state.data_operasional = pd.DataFrame(columns=[
                "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi",
                "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan",
                "Jumlah", "Satuan", "Peruntukan", "Keterangan", "DPP", "PPN", "PPH",
                "Total", "Status Dokumen", "Status Jurnal", "Nama Penginput", "Raw_Items"
            ])

def save_persistent_data():
    """Menyimpan data secara permanen ke file Excel."""
    try:
        st.session_state.data_operasional.to_excel(EXCEL_DB_PATH, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan ke file permanen: {e}")

def render_kas_bank_keluar():
    # Pastikan data permanen termuat di awal modul
    load_persistent_data()

    st.markdown(
        "### 📤 Modul Khusus: Kas & Bank Keluar / Pembayaran Tunai"
    )

    is_edit_mode = st.session_state.get("edit_mode_active", False)
    edit_data = st.session_state.get("edit_data_temp", {})

    if is_edit_mode:
        st.info(f"✏️ **Mode Update Aktif:** Memperbarui Nomor Bukti: **{edit_data.get('Nomor Bukti', '')}**")

    dept_options = [
        "-- Pilih Departemen Tujuan --",
        "Operasional",
        "HRD",
        "Logistik",
        "Maintenance",
        "HSE",
        "Akuntansi",
        "Keuangan",
    ]
    
    default_dept_idx = 0
    if is_edit_mode and edit_data.get("Departemen Tujuan") in dept_options:
        default_dept_idx = dept_options.index(edit_data.get("Departemen Tujuan"))

    departemen_tujuan = st.selectbox(
        "Pilih Departemen Tujuan Dokumen (Wajib Sesuai Hierarki)", 
        dept_options,
        index=default_dept_idx
    )

    if departemen_tujuan == "-- Pilih Departemen Tujuan --":
        st.warning("⚠️ Silakan pilih **Departemen Tujuan** terlebih dahulu di atas.")
        return

    st.success(f"✅ Departemen Tujuan Aktif: **{departemen_tujuan}**")
    st.markdown("---")

    if "form_index_kbk" not in st.session_state:
        st.session_state.form_index_kbk = 0

    idx = st.session_state.form_index_kbk

    default_tgl = datetime.now()
    if is_edit_mode and edit_data.get("Tanggal"):
        try:
            default_tgl = pd.to_datetime(edit_data.get("Tanggal"))
        except:
            pass

    default_nobukti = edit_data.get("Nomor Bukti", "") if is_edit_mode else ""
    default_penerima = edit_data.get("Lawan Transaksi", "") if is_edit_mode else ""
    default_ref = edit_data.get("No Invoice", "") if is_edit_mode else ""

    col_reset1, col_reset2 = st.columns([3, 1])
    with col_reset2:
        if st.button("🧹 Reset / Batal Edit", use_container_width=True):
            if "edit_mode_active" in st.session_state:
                st.session_state.edit_mode_active = False
            if "edit_data_temp" in st.session_state:
                del st.session_state.edit_data_temp
            if f"items_table_kbk_{idx}" in st.session_state:
                del st.session_state[f"items_table_kbk_{idx}"]
            if f"active_edit_tracker_kbk_{idx}" in st.session_state:
                del st.session_state[f"active_edit_tracker_kbk_{idx}"]
            st.session_state.form_index_kbk += 1
            st.rerun()

    # --- PEMBACAAN MASTER DATA DINAMIS ---
    list_bu_opt = []
    if os.path.exists("master_bu_bss.xlsx"):
        try:
            df_bu = pd.read_excel("master_bu_bss.xlsx")
            df_bu.columns = df_bu.columns.str.replace("\xa0", " ").str.strip()
            if len(df_bu.columns) >= 2:
                list_bu_opt = (
                    df_bu.iloc[:, 0].astype(str).str.strip()
                    + " - "
                    + df_bu.iloc[:, 1].astype(str).str.strip()
                ).tolist()
        except Exception:
            pass
    if not list_bu_opt:
        list_bu_opt = ["BU Umum - PT Banggai Sentral Sulawesi"]

    list_supplier_opt = []
    if os.path.exists("master_pemasok_bss.xlsx"):
        try:
            df_supp = pd.read_excel("master_pemasok_bss.xlsx")
            df_supp.columns = df_supp.columns.str.replace("\xa0", " ").str.strip()
            col_sup = df_supp.columns[1] if len(df_supp.columns) > 1 else df_supp.columns[0]
            list_supplier_opt = df_supp[col_sup].dropna().astype(str).str.strip().tolist()
        except Exception:
            pass
    if not list_supplier_opt:
        list_supplier_opt = ["Penerima Pembayaran Umum"]

    list_kas_bank_opt = []
    if os.path.exists("master_coa_bss.xlsx"):
        try:
            df_coa = pd.read_excel("master_coa_bss.xlsx")
            df_coa.columns = df_coa.columns.str.replace("\xa0", " ").str.strip()
            col_kode = df_coa.columns[0]
            col_nama = df_coa.columns[1] if len(df_coa.columns) > 1 else df_coa.columns[0]
            mask_kb = df_coa[col_kode].astype(str).str.startswith("1110")
            df_kb = df_coa[mask_kb]
            if not df_kb.empty:
                list_kas_bank_opt = (
                    df_kb[col_kode].astype(str).str.strip()
                    + " — "
                    + df_kb[col_nama].astype(str).str.strip()
                ).tolist()
        except Exception:
            pass

    if not list_kas_bank_opt:
        list_kas_bank_opt = ["1110.001 — Kas Besar Luwuk", "1110.002 — Kas Operasional Surabaya"]

    list_alat_opt = []
    if os.path.exists("master_alat_bss.xlsx"):
        try:
            df_alat = pd.read_excel("master_alat_bss.xlsx")
            df_alat.columns = df_alat.columns.str.replace("\xa0", " ").str.strip()
            if len(df_alat.columns) >= 2:
                col_a1 = df_alat.columns[1]
                list_alat_opt = df_alat[col_a1].dropna().astype(str).str.strip().tolist()
        except Exception:
            pass

    # --- HEADER INFORMASI UTAMA ---
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>📅 **Tanggal Pembayaran**", unsafe_allow_html=True)
        with c2:
            tgl = st.date_input("Tanggal", default_tgl, label_visibility="collapsed", key=f"tgl_kbk_{idx}")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>🧾 **Nomor Bukti / Ref Internal**", unsafe_allow_html=True)
        with c2:
            no_bukti = st.text_input("No Bukti", value=default_nobukti, placeholder="Cth: BSS/BK/VIII/2026/001", label_visibility="collapsed", key=f"nobukti_kbk_{idx}")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>🏦 **Akun Kas Sumber (1110)**", unsafe_allow_html=True)
        with c2:
            bank_sumber = st.selectbox("Pilih Akun Kas", ["-- Pilih Akun Kas 1110 --"] + list_kas_bank_opt, key=f"bank_sumber_kbk_{idx}", label_visibility="collapsed")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>🏢 **Penerima / Vendor**", unsafe_allow_html=True)
        with c2:
            sub_sup1, sub_sup2 = st.columns([3, 1])
            with sub_sup1:
                idx_p = list_supplier_opt.index(default_penerima) + 1 if default_penerima in list_supplier_opt else 0
                penerima_pilihan = st.selectbox("Pilih Penerima", ["-- Pilih Penerima --"] + list_supplier_opt, index=idx_p, label_visibility="collapsed", key=f"penerima_kbk_{idx}")
            with sub_sup2:
                tambah_penerima_baru = st.text_input("Baru", placeholder="Ketik baru...", label_visibility="collapsed", key=f"t_penerima_kbk_{idx}")
            
            lawan_transaksi_final = default_penerima if is_edit_mode else ""
            if penerima_pilihan != "-- Pilih Penerima --":
                lawan_transaksi_final = penerima_pilihan
            if tambah_penerima_baru.strip():
                lawan_transaksi_final = tambah_penerima_baru.strip()

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>🏷️ **No. Referensi / Invoice**", unsafe_allow_html=True)
        with c2:
            no_invoice_ref = st.text_input("No Ref", value=default_ref, placeholder="Cth: INV/001", label_visibility="collapsed", key=f"ref_kbk_{idx}")

    st.markdown("---")
    st.markdown("#### 📋 Rincian Item Transaksi")
    st.markdown("<p style='font-size:12px; color:#64748B;'>Gunakan tombol tambah (+) di bawah tabel untuk menambah baris. Nilai DPP otomatis berformat desimal rupiah (Rp %,.2f).</p>", unsafe_allow_html=True)

    # --- LOGIKA PEMUATAN KEMBALI MULTI-ITEM DARI RAW_ITEMS ---
    state_key_items = f"items_table_kbk_{idx}"
    active_edit_tracker_key = f"active_edit_tracker_kbk_{idx}"
    current_edit_nobukti = edit_data.get("Nomor Bukti", "") if is_edit_mode else ""

    if active_edit_tracker_key not in st.session_state:
        st.session_state[active_edit_tracker_key] = ""

    if is_edit_mode and st.session_state[active_edit_tracker_key] != current_edit_nobukti:
        loaded_df = None
        raw_json = edit_data.get("Raw_Items", "")
        if raw_json and isinstance(raw_json, str) and raw_json.strip():
            try:
                parsed_data = json.loads(raw_json)
                if parsed_data:
                    loaded_df = pd.DataFrame(parsed_data)
            except Exception:
                pass
        
        if loaded_df is not None and not loaded_df.empty:
            st.session_state[state_key_items] = loaded_df
        else:
            st.session_state[state_key_items] = pd.DataFrame([{
                "Keterangan / Nama Barang": edit_data.get("Keterangan", ""),
                "Qty": edit_data.get("Jumlah", 0.0),
                "Satuan": edit_data.get("Satuan", ""),
                "Business Unit": edit_data.get("Business Unit", "-"),
                "Peruntukan Alat": edit_data.get("Peruntukan", "-"),
                "Nilai DPP (Rp)": edit_data.get("DPP", 0.0)
            }])
        st.session_state[active_edit_tracker_key] = current_edit_nobukti

    elif not is_edit_mode and st.session_state[active_edit_tracker_key] != "":
        st.session_state[active_edit_tracker_key] = ""
        st.session_state[state_key_items] = pd.DataFrame([{
            "Keterangan / Nama Barang": "",
            "Qty": 0.0,
            "Satuan": "",
            "Business Unit": "-",
            "Peruntukan Alat": "-",
            "Nilai DPP (Rp)": 0.0
        }])

    if state_key_items not in st.session_state:
        st.session_state[state_key_items] = pd.DataFrame([{
            "Keterangan / Nama Barang": "",
            "Qty": 0.0,
            "Satuan": "",
            "Business Unit": "-",
            "Peruntukan Alat": "-",
            "Nilai DPP (Rp)": 0.0
        }])

    bu_dropdown_options = ["-"] + list_bu_opt
    alat_dropdown_options = ["-"] + list_alat_opt

    edited_df = st.data_editor(
        st.session_state[state_key_items],
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_kbk_{idx}",
        column_config={
            "Keterangan / Nama Barang": st.column_config.TextColumn(
                "Keterangan / Nama Barang", width="medium", required=True
            ),
            "Qty": st.column_config.NumberColumn(
                "Qty", width="small", min_value=0.0, step=1.0, format="%,.2f"
            ),
            "Satuan": st.column_config.TextColumn(
                "Satuan", width="small", help="Ketik satuan manual bebas"
            ),
            "Business Unit": st.column_config.SelectboxColumn(
                "Business Unit (Proyek)", width="medium", options=bu_dropdown_options, required=False
            ),
            "Peruntukan Alat": st.column_config.SelectboxColumn(
                "Peruntukan Alat", width="medium", options=alat_dropdown_options, required=False
            ),
            "Nilai DPP (Rp)": st.column_config.NumberColumn(
                "Nilai DPP (Rp)", width="small", min_value=0.0, step=1000.0, format="Rp %,.2f"
            )
        }
    )

    st.markdown("---")

    # --- PAJAK & KALKULASI TOTAL ---
    col_tax1, col_tax2 = st.columns(2)
    with col_tax1:
        pakai_ppn = st.checkbox("Gunakan PPN (11% Otomatis)", key=f"chk_ppn_kbk_{idx}")
    with col_tax2:
        col_ph1, col_ph2 = st.columns([1, 1])
        with col_ph1:
            pakai_pph = st.checkbox("Gunakan PPh", key=f"chk_pph_kbk_{idx}")
        with col_ph2:
            tarif_pilihan = st.selectbox(
                "Tarif PPh",
                [0.01, 0.015, 0.0175, 0.02, 0.03, 0.04],
                format_func=lambda x: f"{x*100}%".replace(".0", ""),
                key=f"sel_tarif_kbk_{idx}",
                label_visibility="collapsed"
            )

    total_dpp = edited_df["Nilai DPP (Rp)"].sum() if not edited_df.empty else 0.0
    total_ppn = round(total_dpp * 0.11, 2) if pakai_ppn else 0.0
    total_pph = round(total_dpp * tarif_pilihan, 2) if pakai_pph else 0.0
    total_transaksi = (total_dpp + total_ppn) - total_pph

    st.markdown(
        f"<div style='background-color: #F8FAFC; padding: 8px 12px; border-radius: 6px; border: 1px solid #E2E8F0; margin-top: 10px;'>"
        f"<span style='font-size: 13px; color: #475569;'>Total DPP: <b>Rp {total_dpp:,.2f}</b></span> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<span style='font-size: 13px; color: #475569;'>PPN: <b>Rp {total_ppn:,.2f}</b></span> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<span style='font-size: 13px; color: #475569;'>PPh: <b>Rp {total_pph:,.2f}</b></span><br>"
        f"<span style='font-size: 15px; color: #1E3A8A; font-weight: bold;'>Total Nilai Pengeluaran: Rp {total_transaksi:,.2f}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # --- TOMBOL AKSI SIMPAN / UPDATE & PENYIMPANAN PERMANEN ---
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        label_tombol_simpan = "💾 Update / Timpa Dokumen" if is_edit_mode else "💾 Simpan Data Kas Keluar"
        if st.button(label_tombol_simpan, use_container_width=True, key=f"btn_save_kbk_{idx}"):
            valid_kondisi = (no_bukti.strip() != "" and total_transaksi > 0 and not edited_df.empty and lawan_transaksi_final != "")
            
            if valid_kondisi:
                penginput_aktif = st.session_state.get("modul1_user", "System")
                
                raw_items_json = edited_df.to_json(orient="records")

                ket_gabungan = "; ".join(edited_df["Keterangan / Nama Barang"].dropna().astype(str).tolist())
                bu_pertama = "-"
                for val in edited_df["Business Unit"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        bu_pertama = str(val).strip()
                        break

                satuan_pertama = edited_df["Satuan"].dropna().iloc[0] if not edited_df["Satuan"].dropna().empty else ""
                qty_total = edited_df["Qty"].sum() if "Qty" in edited_df.columns else 0.0
                
                peruntukan_pertama = "-"
                for val in edited_df["Peruntukan Alat"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        peruntukan_pertama = str(val).strip()
                        break

                data_baru = {
                    "Nomor Bukti": no_bukti,
                    "Tanggal": tgl,
                    "Sumber Transaksi": f"Kas Keluar ({bank_sumber})",
                    "Lawan Transaksi": lawan_transaksi_final,
                    "No Invoice": no_invoice_ref,
                    "Jatuh Tempo": "-",
                    "Business Unit": str(bu_pertama),
                    "Departemen Tujuan": departemen_tujuan,
                    "Jumlah": qty_total,
                    "Satuan": str(satuan_pertama),
                    "Peruntukan": str(peruntukan_pertama),
                    "Keterangan": str(ket_gabungan),
                    "DPP": total_dpp,
                    "PPN": total_ppn,
                    "PPH": total_pph,
                    "Total": total_transaksi,
                    "Status Dokumen": f"Menunggu Approval {departemen_tujuan}",
                    "Status Jurnal": "Belum Dijurnal",
                    "Nama Penginput": penginput_aktif,
                    "Raw_Items": raw_items_json
                }
                df_existing = st.session_state.data_operasional
                if not df_existing.empty and no_bukti in df_existing["Nomor Bukti"].values:
                    df_existing = df_existing[df_existing["Nomor Bukti"] != no_bukti]
                
                st.session_state.data_operasional = pd.concat(
                    [df_existing, pd.DataFrame([data_baru])], ignore_index=True
                )
                
                save_persistent_data()
                
                if is_edit_mode:
                    st.success(f"Nomor Bukti '{no_bukti}' berhasil di-update dengan {len(edited_df)} item rincian!")
                    st.session_state.edit_mode_active = False
                    if "edit_data_temp" in st.session_state:
                        del st.session_state.edit_data_temp
                    if active_edit_tracker_key in st.session_state:
                        del st.session_state[active_edit_tracker_key]
                else:
                    st.success(f"Data kas keluar berhasil disimpan dan diamankan secara permanen!")
            else:
                st.error("Mohon lengkapi Nomor Bukti, Vendor/Penerima, pastikan tabel rincian terisi, dan total nilai > 0.")

    with col_b2:
        if st.button("➕ Simpan & Mulai Entri Baru", use_container_width=True, key=f"btn_save_new_kbk_{idx}"):
            if no_bukti.strip() != "" and total_transaksi > 0 and not edited_df.empty:
                penginput_aktif = st.session_state.get("modul1_user", "System")
                
                raw_items_json = edited_df.to_json(orient="records")
                ket_gabungan = "; ".join(edited_df["Keterangan / Nama Barang"].dropna().astype(str).tolist())
                
                bu_pertama = "-"
                for val in edited_df["Business Unit"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        bu_pertama = str(val).strip()
                        break

                satuan_pertama = edited_df["Satuan"].dropna().iloc[0] if not edited_df["Satuan"].dropna().empty else ""
                qty_total = edited_df["Qty"].sum() if "Qty" in edited_df.columns else 0.0
                
                peruntukan_pertama = "-"
                for val in edited_df["Peruntukan Alat"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        peruntukan_pertama = str(val).strip()
                        break

                data_baru = {
                    "Nomor Bukti": no_bukti,
                    "Tanggal": tgl,
                    "Sumber Transaksi": f"Kas Keluar ({bank_sumber})",
                    "Lawan Transaksi": lawan_transaksi_final,
                    "No Invoice": no_invoice_ref,
                    "Jatuh Tempo": "-",
                    "Business Unit": str(bu_pertama),
                    "Departemen Tujuan": departemen_tujuan,
                    "Jumlah": qty_total,
                    "Satuan": str(satuan_pertama),
                    "Peruntukan": str(peruntukan_pertama),
                    "Keterangan": str(ket_gabungan),
                    "DPP": total_dpp,
                    "PPN": total_ppn,
                    "PPH": total_pph,
                    "Total": total_transaksi,
                    "Status Dokumen": f"Menunggu Approval {departemen_tujuan}",
                    "Status Jurnal": "Belum Dijurnal",
                    "Nama Penginput": penginput_aktif,
                    "Raw_Items": raw_items_json
                }
                df_existing = st.session_state.data_operasional
                if not df_existing.empty and no_bukti in df_existing["Nomor Bukti"].values:
                    df_existing = df_existing[df_existing["Nomor Bukti"] != no_bukti]
                st.session_state.data_operasional = pd.concat(
                    [df_existing, pd.DataFrame([data_baru])], ignore_index=True
                )
                
                save_persistent_data()
                
                if st.session_state.get("edit_mode_active", False):
                    st.session_state.edit_mode_active = False
                    if "edit_data_temp" in st.session_state:
                        del st.session_state.edit_data_temp
                    if active_edit_tracker_key in st.session_state:
                        del st.session_state[active_edit_tracker_key]

                st.session_state.form_index_kbk += 1
                st.success("Tersimpan permanen! Form diset ke entri baru.")
                st.rerun()
            else:
                st.error("Nomor Bukti wajib diisi dan pastikan rincian item valid.")