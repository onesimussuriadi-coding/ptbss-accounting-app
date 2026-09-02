from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

EXCEL_DB_PATH = "database_transaksi_bss.xlsx"

def save_persistent_data():
    """Menyimpan data operasional secara permanen ke file Excel."""
    try:
        if "data_operasional" in st.session_state:
            st.session_state.data_operasional.to_excel(EXCEL_DB_PATH, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan ke file permanen: {e}")

def render_gudang_persediaan():
    st.markdown("### 📦 Modul Gudang & Persediaan (Warehouse Mutasi)")
    st.markdown("<p style='font-size:13px; color:#64748B;'>Formulir pencatatan mutasi stok gudang, penerimaan, pengeluaran, dan penyesuaian inventaris berbasis tabel rincian item.</p>", unsafe_allow_html=True)

    # --- SECURITY GATE: PILIH DEPARTEMEN TUJUAN ---
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
    current_user_dept = st.session_state.get("modul1_dept", "")
    if current_user_dept in dept_options:
        default_dept_idx = dept_options.index(current_user_dept)

    departemen_tujuan = st.selectbox(
        "Pilih Departemen Tujuan Dokumen (Wajib Sesuai Hierarki)", 
        dept_options,
        index=default_dept_idx
    )

    if departemen_tujuan == "-- Pilih Departemen Tujuan --":
        st.warning(
            "⚠️ **Akses Terbatas:** Silakan pilih **Departemen Tujuan** terlebih"
            " dahulu di atas untuk membuka formulir penginputan gudang."
        )
        return

    st.success(f"✅ Departemen Tujuan Aktif: **{departemen_tujuan}**")
    st.markdown("---")

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

    if "form_index_gudang" not in st.session_state:
        st.session_state.form_index_gudang = 0

    idx = st.session_state.form_index_gudang

    col_reset1, col_reset2 = st.columns([3, 1])
    with col_reset2:
        if st.button("🧹 Reset Form Gudang", use_container_width=True):
            st.session_state.form_index_gudang += 1
            if f"editor_gudang_items_{idx}" in st.session_state:
                del st.session_state[f"editor_gudang_items_{idx}"]
            st.success("Form gudang berhasil dibersihkan!")
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
    if not list_alat_opt:
        list_alat_opt = ["Operasional Umum", "Kendaraan Operasional", "Alat Berat"]

    list_gudang_opt = []
    if os.path.exists("master_gudang_bss.xlsx"):
        try:
            df_gudang = pd.read_excel("master_gudang_bss.xlsx")
            df_gudang.columns = df_gudang.columns.str.replace("\xa0", " ").str.strip()
            if len(df_gudang.columns) >= 2:
                list_gudang_opt = (
                    df_gudang.iloc[:, 0].astype(str).str.strip()
                    + " - "
                    + df_gudang.iloc[:, 1].astype(str).str.strip()
                ).tolist()
            elif len(df_gudang.columns) == 1:
                list_gudang_opt = df_gudang.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        except Exception:
            pass
    if not list_gudang_opt:
        list_gudang_opt = ["GD BBM - Gudang BBM dan Pelumas", "GD Part - Gudang Spare Part", "GD ATK - Gudang ATK"]

    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>📅 **Tanggal Mutasi / Transaksi Gudang**", unsafe_allow_html=True)
        with c2:
            tgl = st.date_input("Tanggal", datetime.now(), label_visibility="collapsed", key=f"tgl_gd_{idx}")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>🧾 **Nomor Bukti / Slip Gudang**", unsafe_allow_html=True)
        with c2:
            no_bukti = st.text_input("No Bukti", placeholder="Cth: BSS/GDG/VIII/2026/001", label_visibility="collapsed", key=f"nobukti_gd_{idx}")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>🔄 **Jenis Aktivitas Gudang**", unsafe_allow_html=True)
        with c2:
            jenis_aktivitas = st.selectbox(
                "Jenis Aktivitas",
                [
                    "Penerimaan Barang Masuk Gudang",
                    "Pengeluaran Barang Keluar Gudang (Pemakaian)",
                    "Transfer Antar Gudang",
                    "Penyesuaian Stok (Opname)",
                ],
                label_visibility="collapsed",
                key=f"aktivitas_gd_{idx}",
            )

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<br>🏢 **Lokasi Gudang / Sumber Barang**", unsafe_allow_html=True)
        with c2:
            lokasi_gudang_pilihan = st.selectbox(
                "Pilih Lokasi Gudang",
                ["-- Pilih Gudang Sumber / Tujuan --"] + list_gudang_opt,
                label_visibility="collapsed",
                key=f"lokasi_gudang_{idx}",
            )

    st.markdown("---")
    st.markdown("#### 📋 Rincian Item Transaksi Gudang")
    st.markdown("<p style='font-size:12px; color:#64748B;'>Gunakan tombol tambah (+) di bawah tabel untuk menambah baris barang. Nilai DPP otomatis berformat desimal rupiah (Rp %,.2f).</p>", unsafe_allow_html=True)

    # Inisialisasi DataFrame default untuk tabel item gudang
    state_key_items_gd = f"editor_gudang_items_{idx}"
    if state_key_items_gd not in st.session_state:
        st.session_state[state_key_items_gd] = pd.DataFrame([{
            "Keterangan / Nama Barang": "",
            "Qty": 0.0,
            "Satuan": "Pcs",
            "Business Unit (Proyek)": list_bu_opt[0] if list_bu_opt else "-",
            "Peruntukan Alat": "-",
            "Nilai DPP": 0.0
        }])

    bu_dropdown_options = ["-"] + list_bu_opt
    alat_dropdown_options = ["-"] + list_alat_opt

    edited_df_gudang = st.data_editor(
        st.session_state[state_key_items_gd],
        num_rows="dynamic",
        use_container_width=True,
        key=f"data_editor_gd_{idx}",
        column_config={
            "Keterangan / Nama Barang": st.column_config.TextColumn(
                "Keterangan / Nama Barang", width="medium", required=True
            ),
            "Qty": st.column_config.NumberColumn(
                "Qty", width="small", min_value=0.0, step=1.0, format="%,.2f"
            ),
            "Satuan": st.column_config.TextColumn(
                "Satuan", width="small", help="Ketik satuan manual (Pcs, Unit, Box, dll)"
            ),
            "Business Unit (Proyek)": st.column_config.SelectboxColumn(
                "Business Unit (Proyek)", width="medium", options=bu_dropdown_options, required=False
            ),
            "Peruntukan Alat": st.column_config.SelectboxColumn(
                "Peruntukan Alat", width="medium", options=alat_dropdown_options, required=False
            ),
            "Nilai DPP": st.column_config.NumberColumn(
                "Nilai DPP", width="small", min_value=0.0, step=1000.0, format="Rp %,.2f"
            )
        }
    )

    total_dpp_gudang = edited_df_gudang["Nilai DPP"].sum() if not edited_df_gudang.empty else 0.0
    total_qty_gudang = edited_df_gudang["Qty"].sum() if "Qty" in edited_df_gudang.columns else 0.0

    st.markdown(
        f"<div style='background-color: #F8FAFC; padding: 8px 12px; border-radius: 6px; border: 1px solid #E2E8F0; margin-top: 10px;'>"
        f"<span style='font-size: 13px; color: #475569;'>Total Qty Barang: <b>{total_qty_gudang:,.2f}</b></span> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<span style='font-size: 15px; color: #1E3A8A; font-weight: bold;'>Total Nilai Perolehan / DPP: Rp {total_dpp_gudang:,.2f}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("💾 Simpan Mutasi Gudang", use_container_width=True, key=f"btn_save_gd_{idx}"):
            lokasi_gudang_final = lokasi_gudang_pilihan if lokasi_gudang_pilihan != "-- Pilih Gudang Sumber / Tujuan --" else ""
            clean_items = edited_df_gudang[edited_df_gudang["Keterangan / Nama Barang"].astype(str).str.strip() != ""].to_dict(orient="records")

            if no_bukti.strip() != "" and lokasi_gudang_final != "" and total_qty_gudang > 0 and len(clean_items) > 0:
                penginput_aktif = st.session_state.get("modul1_user", "System")
                raw_items_json = json.dumps(clean_items)

                ket_gabungan = "; ".join([str(x.get("Keterangan / Nama Barang", "")) for x in clean_items])
                bu_pertama = "-"
                for val in edited_df_gudang["Business Unit (Proyek)"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        bu_pertama = str(val).strip()
                        break

                satuan_pertama = edited_df_gudang["Satuan"].dropna().iloc[0] if not edited_df_gudang["Satuan"].dropna().empty else "Pcs"
                peruntukan_pertama = "-"
                for val in edited_df_gudang["Peruntukan Alat"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        peruntukan_pertama = str(val).strip()
                        break

                data_baru = {
                    "Nomor Bukti": no_bukti.strip(),
                    "Tanggal": str(tgl),
                    "Sumber Transaksi": f"Gudang - {jenis_aktivitas}",
                    "Lawan Transaksi": lokasi_gudang_final,
                    "No Invoice": "-",
                    "Jatuh Tempo": "-",
                    "Business Unit": bu_pertama,
                    "Departemen Tujuan": departemen_tujuan,
                    "Jumlah": total_qty_gudang,
                    "Satuan": str(satuan_pertama),
                    "Peruntukan": str(peruntukan_pertama),
                    "Keterangan": f"[{lokasi_gudang_final}] {ket_gabungan}",
                    "DPP": total_dpp_gudang,
                    "PPN": 0.0,
                    "PPH": 0.0,
                    "Total": total_dpp_gudang,
                    "Status Dokumen": f"Menunggu Approval {departemen_tujuan}",
                    "Status Jurnal": "Belum Dijurnal",
                    "Nama Penginput": penginput_aktif,
                    "Raw_Items": raw_items_json
                }
                df_existing = st.session_state.data_operasional
                if not df_existing.empty and no_bukti.strip() in df_existing["Nomor Bukti"].values:
                    df_existing = df_existing[df_existing["Nomor Bukti"] != no_bukti.strip()]
                
                st.session_state.data_operasional = pd.concat([df_existing, pd.DataFrame([data_baru])], ignore_index=True)
                save_persistent_data()
                st.success(f"Slip Gudang Nomor **{no_bukti}** dengan total nilai **Rp {total_dpp_gudang:,.2f}** berhasil disimpan permanen!")
            else:
                st.error("Mohon lengkapi Nomor Bukti, Lokasi Gudang, dan pastikan tabel rincian item barang terisi dengan Qty > 0.")

    with col_b2:
        if st.button("➕ Simpan & Entri Dokumen Baru", use_container_width=True, key=f"btn_save_new_gd_{idx}"):
            lokasi_gudang_final = lokasi_gudang_pilihan if lokasi_gudang_pilihan != "-- Pilih Gudang Sumber / Tujuan --" else ""
            clean_items = edited_df_gudang[edited_df_gudang["Keterangan / Nama Barang"].astype(str).str.strip() != ""].to_dict(orient="records")

            if no_bukti.strip() != "" and lokasi_gudang_final != "" and total_qty_gudang > 0 and len(clean_items) > 0:
                penginput_aktif = st.session_state.get("modul1_user", "System")
                raw_items_json = json.dumps(clean_items)

                ket_gabungan = "; ".join([str(x.get("Keterangan / Nama Barang", "")) for x in clean_items])
                bu_pertama = "-"
                for val in edited_df_gudang["Business Unit (Proyek)"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        bu_pertama = str(val).strip()
                        break

                satuan_pertama = edited_df_gudang["Satuan"].dropna().iloc[0] if not edited_df_gudang["Satuan"].dropna().empty else "Pcs"
                peruntukan_pertama = "-"
                for val in edited_df_gudang["Peruntukan Alat"].dropna():
                    if str(val).strip() and str(val).strip() != "-":
                        peruntukan_pertama = str(val).strip()
                        break

                data_baru = {
                    "Nomor Bukti": no_bukti.strip(),
                    "Tanggal": str(tgl),
                    "Sumber Transaksi": f"Gudang - {jenis_aktivitas}",
                    "Lawan Transaksi": lokasi_gudang_final,
                    "No Invoice": "-",
                    "Jatuh Tempo": "-",
                    "Business Unit": bu_pertama,
                    "Departemen Tujuan": departemen_tujuan,
                    "Jumlah": total_qty_gudang,
                    "Satuan": str(satuan_pertama),
                    "Peruntukan": str(peruntukan_pertama),
                    "Keterangan": f"[{lokasi_gudang_final}] {ket_gabungan}",
                    "DPP": total_dpp_gudang,
                    "PPN": 0.0,
                    "PPH": 0.0,
                    "Total": total_dpp_gudang,
                    "Status Dokumen": f"Menunggu Approval {departemen_tujuan}",
                    "Status Jurnal": "Belum Dijurnal",
                    "Nama Penginput": penginput_aktif,
                    "Raw_Items": raw_items_json
                }
                df_existing = st.session_state.data_operasional
                if not df_existing.empty and no_bukti.strip() in df_existing["Nomor Bukti"].values:
                    df_existing = df_existing[df_existing["Nomor Bukti"] != no_bukti.strip()]
                
                st.session_state.data_operasional = pd.concat([df_existing, pd.DataFrame([data_baru])], ignore_index=True)
                save_persistent_data()
                st.session_state.form_index_gudang += 1
                if state_key_items_gd in st.session_state:
                    del st.session_state[state_key_items_gd]
                st.success("Tersimpan permanen! Form diset ke entri baru.")
                st.rerun()
            else:
                st.error("Mohon lengkapi Nomor Bukti, Lokasi Gudang, dan pastikan tabel rincian item barang terisi dengan Qty > 0.")