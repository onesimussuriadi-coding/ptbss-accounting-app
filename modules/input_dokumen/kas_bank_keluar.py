from datetime import datetime
import os
import pandas as pd
import streamlit as st


def render_kas_bank_keluar():
  st.markdown(
      "### 📤 Modul Khusus: Kas & Bank Keluar / Pembayaran Tunai"
  )

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
  departemen_tujuan = st.selectbox(
      "Pilih Departemen Tujuan Dokumen (Wajib Sesuai Hierarki)", dept_options
  )

  if departemen_tujuan == "-- Pilih Departemen Tujuan --":
    st.warning(
        "⚠️ **Akses Terbatas:** Silakan pilih **Departemen Tujuan** terlebih"
        " dahulu di atas untuk membuka formulir kas/bank keluar."
    )
    return  # Menghentikan eksekusi sehingga seluruh form di bawah terkunci

  st.success(f"✅ Departemen Tujuan Aktif: **{departemen_tujuan}**")
  st.markdown("---")
  # ----------------------------------------------

  if "data_operasional" not in st.session_state:
    st.session_state.data_operasional = pd.DataFrame(
        columns=[
            "Nomor Bukti",
            "Tanggal",
            "Sumber Transaksi",
            "Lawan Transaksi",
            "No Invoice",
            "Jatuh Tempo",
            "Business Unit",
            "Departemen Tujuan",
            "Jumlah",
            "Satuan",
            "Peruntukan",
            "Keterangan",
            "DPP",
            "PPN",
            "PPH",
            "Total",
            "Status Dokumen",
            "Status Jurnal",
        ]
    )

  if "master_satuan" not in st.session_state:
    st.session_state.master_satuan = [
        "Pcs",
        "EA",
        "Ls",
        "Kg",
        "Liter",
        "Trip",
        "Jam",
        "Hari",
        "Lot",
        "Bulan",
        "Unit",
        "Box",
        "Set",
        "Drum",
    ]

  if "form_index_kbk" not in st.session_state:
    st.session_state.form_index_kbk = 0

  idx = st.session_state.form_index_kbk

  col_reset1, col_reset2 = st.columns([3, 1])
  with col_reset2:
    if st.button("🧹 Reset Form Kas Keluar", use_container_width=True):
      st.session_state.form_index_kbk += 1
      st.success("Form kas keluar berhasil dibersihkan!")
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

  list_supplier_opt = []
  if os.path.exists("master_pemasok_bss.xlsx"):
    try:
      df_supp = pd.read_excel("master_pemasok_bss.xlsx")
      df_supp.columns = df_supp.columns.str.replace("\xa0", " ").str.strip()
      col_sup = (
          df_supp.columns[1] if len(df_supp.columns) > 1 else df_supp.columns[0]
      )
      list_supplier_opt = (
          df_supp[col_sup].dropna().astype(str).str.strip().tolist()
      )
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
      col_nama = (
          df_coa.columns[1] if len(df_coa.columns) > 1 else df_coa.columns[0]
      )
      mask_kb = df_coa[col_kode].astype(str).str.startswith(("111", "112"))
      df_kb = df_coa[mask_kb]
      if not df_kb.empty:
        list_kas_bank_opt = (
            df_kb[col_kode].astype(str).str.strip()
            + " - "
            + df_kb[col_nama].astype(str).str.strip()
        ).tolist()
    except Exception:
      pass
  if not list_kas_bank_opt:
    list_kas_bank_opt = [
        "111.01 - Kas Besar",
        "111.02 - Kas Kecil",
        "112.01 - Bank Mandiri",
    ]

  list_alat_opt = []
  if os.path.exists("master_alat_bss.xlsx"):
    try:
      df_alat = pd.read_excel("master_alat_bss.xlsx")
      df_alat.columns = df_alat.columns.str.replace("\xa0", " ").str.strip()
      if len(df_alat.columns) >= 2:
        col_a1 = df_alat.columns[1]
        list_alat_opt = (
            df_alat[col_a1].dropna().astype(str).str.strip().tolist()
        )
    except Exception:
      pass

  if f"val_ppn_kbk_{idx}" not in st.session_state:
    st.session_state[f"val_ppn_kbk_{idx}"] = 0.0
  if f"val_pph_kbk_{idx}" not in st.session_state:
    st.session_state[f"val_pph_kbk_{idx}"] = 0.0

  with st.container():
    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown(
          "<br>📅 **Tanggal Pembayaran / Keluar**", unsafe_allow_html=True
      )
    with c2:
      tgl = st.date_input(
          "Tanggal",
          datetime.now(),
          label_visibility="collapsed",
          key=f"tgl_kbk_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🧾 **Nomor Bukti / Ref Internal**", unsafe_allow_html=True)
    with c2:
      no_bukti = st.text_input(
          "No Bukti",
          placeholder="Cth: BSS/BK/VIII/2026/001",
          label_visibility="collapsed",
          key=f"nobukti_kbk_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown(
          "<br>🏦 **Akun Kas / Rekening Bank Sumber**", unsafe_allow_html=True
      )
    with c2:
      bank_sumber = st.selectbox(
          "Pilih Kas/Bank",
          ["-- Pilih Akun Kas / Bank Sumber --"] + list_kas_bank_opt,
          key=f"bank_sumber_kbk_{idx}",
          label_visibility="collapsed",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown(
          "<br>🏢 **Penerima Pembayaran / Vendor**", unsafe_allow_html=True
      )
    with c2:
      sub_sup1, sub_sup2 = st.columns([3, 1])
      with sub_sup1:
        penerima_pilihan = st.selectbox(
            "Pilih Penerima",
            ["-- Pilih Penerima Pembayaran --"] + list_supplier_opt,
            key=f"penerima_sel_kbk_{idx}",
            label_visibility="collapsed",
        )
      with sub_sup2:
        tambah_penerima_baru = st.text_input(
            "Penerima Baru",
            placeholder="Ketik baru...",
            key=f"tambah_penerima_kbk_{idx}",
            label_visibility="collapsed",
        )

      lawan_transaksi_final = (
          penerima_pilihan
          if penerima_pilihan != "-- Pilih Penerima Pembayaran --"
          else ""
      )
      if tambah_penerima_baru.strip():
        lawan_transaksi_final = tambah_penerima_baru.strip()

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🏷️ **No. Referensi / Invoice Terkait**", unsafe_allow_html=True)
    with c2:
      no_invoice_ref = st.text_input(
          "No Referensi",
          placeholder="Cth: REF/EXPENSE/2026/001",
          label_visibility="collapsed",
          key=f"ref_kbk_{idx}",
      )

    # Business Unit
    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🏢 **Business Unit / Proyek**", unsafe_allow_html=True)
    with c2:
      sub_bu1, sub_bu2 = st.columns([3, 1])
      with sub_bu1:
        bu_pilihan = st.selectbox(
            "Business Unit",
            ["-- Pilih Business Unit --"] + list_bu_opt,
            label_visibility="collapsed",
            key=f"bu_kbk_{idx}",
        )
      with sub_bu2:
        tambah_bu_baru = st.text_input(
            "BU Baru",
            placeholder="Ketik baru...",
            key=f"tambah_bu_kbk_{idx}",
            label_visibility="collapsed",
        )
      bu_final = bu_pilihan if bu_pilihan != "-- Pilih Business Unit --" else ""
      if tambah_bu_baru.strip():
        bu_final = tambah_bu_baru.strip()

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>📦 **Jumlah (Volume / Qty)**", unsafe_allow_html=True)
    with c2:
      jumlah = st.number_input(
          "Jumlah",
          min_value=0.0,
          step=1.0,
          value=0.0,
          label_visibility="collapsed",
          key=f"jml_kbk_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>📏 **Satuan**", unsafe_allow_html=True)
    with c2:
      sub_sat1, sub_sat2 = st.columns([3, 1])
      with sub_sat1:
        satuan_pilihan = st.selectbox(
            "Pilih Satuan",
            ["-- Pilih Satuan --"] + st.session_state.master_satuan,
            label_visibility="collapsed",
            key=f"satuan_kbk_{idx}",
        )
      with sub_sat2:
        tambah_satuan_baru = st.text_input(
            "Tambah Satuan",
            placeholder="Baru...",
            label_visibility="collapsed",
            key=f"tambah_satuan_kbk_{idx}",
        )
      satuan_final = (
          satuan_pilihan if satuan_pilihan != "-- Pilih Satuan --" else ""
      )
      if tambah_satuan_baru.strip():
        satuan_clean = tambah_satuan_baru.strip().upper()
        satuan_final = satuan_clean
        if satuan_clean not in st.session_state.master_satuan:
          st.session_state.master_satuan.append(satuan_clean)

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🎯 **Peruntukan (Alokasi Alat / Unit)**", unsafe_allow_html=True)
    with c2:
      peruntukan_pilihan = st.selectbox(
          "Pilih Alat / Unit",
          ["-- Pilih Alokasi Alat / Unit --"] + list_alat_opt,
          label_visibility="collapsed",
          key=f"peruntukan_kbk_{idx}",
      )
      peruntukan_final = (
          peruntukan_pilihan
          if peruntukan_pilihan != "-- Pilih Alokasi Alat / Unit --"
          else "-"
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown(
          "<br><br>📝 **Uraian / Keterangan Pembayaran**", unsafe_allow_html=True
      )
    with c2:
      keterangan = st.text_area(
          "Keterangan",
          placeholder="Keterangan pengeluaran kas/bank keluar...",
          label_visibility="collapsed",
          key=f"ket_kbk_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>💰 **Nilai Dasar (DPP)**", unsafe_allow_html=True)
    with c2:
      dpp = st.number_input(
          "DPP",
          min_value=0.0,
          step=10000.0,
          format="%.2f",
          value=0.0,
          label_visibility="collapsed",
          key=f"val_dpp_kbk_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🏷️ **PPN (Pajak Pertambahan Nilai)**", unsafe_allow_html=True)
      pakai_ppn = st.checkbox("Gunakan PPN (11% Otomatis)", key=f"chk_ppn_kbk_{idx}")
    with c2:
      st.info(
          "💡 Centang PPN, pilih tarif PPh, lalu klik tombol hitung di bawah."
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>📉 **PPH (Pajak Penghasilan)**", unsafe_allow_html=True)
      pakai_pph = st.checkbox("Gunakan PPh", key=f"chk_pph_kbk_{idx}")
      tarif_pilihan = st.selectbox(
          "Tarif PPh",
          [0.01, 0.015, 0.0175, 0.02, 0.03, 0.04],
          format_func=lambda x: f"{x*100}%".replace(".0", ""),
          key=f"sel_tarif_kbk_{idx}",
          label_visibility="collapsed",
      )
    with c2:
      if st.button(
          "⚡ KLIK HITUNG PAJAK OTOMATIS",
          use_container_width=True,
          key=f"btn_hitung_kbk_{idx}",
      ):
        st.session_state[f"val_ppn_kbk_{idx}"] = (
            round(dpp * 0.11, 2) if pakai_ppn else 0.0
        )
        st.session_state[f"val_pph_kbk_{idx}"] = (
            round(dpp * tarif_pilihan, 2) if pakai_pph else 0.0
        )
        st.success("Kalkulasi PPN & PPh berhasil diterapkan!")
        st.rerun()

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🔹 **Nominal PPN**", unsafe_allow_html=True)
    with c2:
      ppn = st.number_input(
          "PPN",
          min_value=0.0,
          step=1000.0,
          format="%.2f",
          label_visibility="collapsed",
          key=f"val_ppn_kbk_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🔹 **Nominal PPh**", unsafe_allow_html=True)
    with c2:
      pph = st.number_input(
          "PPh",
          min_value=0.0,
          step=1000.0,
          format="%.2f",
          label_visibility="collapsed",
          key=f"val_pph_kbk_{idx}",
      )

    total_transaksi = (dpp + ppn) - pph

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>💵 **Total Nilai Pengeluaran**", unsafe_allow_html=True)
    with c2:
      st.markdown(f"### **Rp {total_transaksi:,.2f}**")

    st.divider()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
      if st.button(
          "💾 Simpan Data Kas Keluar",
          use_container_width=True,
          key=f"btn_save_kbk_{idx}",
      ):
        if total_transaksi > 0 and no_bukti and bu_final and lawan_transaksi_final:
          data_baru = {
              "Nomor Bukti": no_bukti,
              "Tanggal": tgl,
              "Sumber Transaksi": "Bank Keluar / Pembayaran",
              "Lawan Transaksi": lawan_transaksi_final,
              "No Invoice": no_invoice_ref,
              "Jatuh Tempo": "-",
              "Business Unit": bu_final,
              "Departemen Tujuan": departemen_tujuan,  # Menggunakan pilihan departemen keamanan
              "Jumlah": jumlah,
              "Satuan": satuan_final,
              "Peruntukan": peruntukan_final,
              "Keterangan": keterangan,
              "DPP": dpp,
              "PPN": ppn,
              "PPH": pph,
              "Total": total_transaksi,
              "Status Dokumen": f"Menunggu Approval {departemen_tujuan}",
              "Status Jurnal": "Belum Dijurnal",
          }
          df_existing = st.session_state.data_operasional
          if (
              not df_existing.empty
              and no_bukti in df_existing["Nomor Bukti"].values
          ):
            df_existing.loc[df_existing["Nomor Bukti"] == no_bukti] = (
                pd.DataFrame([data_baru]).values[0]
            )
            st.success(f"Nomor Bukti '{no_bukti}' berhasil diperbarui!")
          else:
            st.session_state.data_operasional = pd.concat(
                [df_existing, pd.DataFrame([data_baru])], ignore_index=True
            )
            st.success("Data kas keluar berhasil disimpan!")
        else:
          st.error(
              "Mohon lengkapi Nomor Bukti, Penerima, Business Unit, dan pastikan"
              " nilai nominal > 0."
          )

    with col_b2:
      if st.button(
          "➕ Simpan & Mulai Entri Baru",
          use_container_width=True,
          key=f"btn_save_new_kbk_{idx}",
      ):
        if total_transaksi > 0 and no_bukti and bu_final and lawan_transaksi_final:
          data_baru = {
              "Nomor Bukti": no_bukti,
              "Tanggal": tgl,
              "Sumber Transaksi": "Bank Keluar / Pembayaran",
              "Lawan Transaksi": lawan_transaksi_final,
              "No Invoice": no_invoice_ref,
              "Jatuh Tempo": "-",
              "Business Unit": bu_final,
              "Departemen Tujuan": departemen_tujuan,
              "Jumlah": jumlah,
              "Satuan": satuan_final,
              "Peruntukan": peruntukan_final,
              "Keterangan": keterangan,
              "DPP": dpp,
              "PPN": ppn,
              "PPH": pph,
              "Total": total_transaksi,
              "Status Dokumen": f"Menunggu Approval {departemen_tujuan}",
              "Status Jurnal": "Belum Dijurnal",
          }
          df_existing = st.session_state.data_operasional
          if (
              not df_existing.empty
              and no_bukti in df_existing["Nomor Bukti"].values
          ):
            df_existing.loc[df_existing["Nomor Bukti"] == no_bukti] = (
                pd.DataFrame([data_baru]).values[0]
            )
          else:
            st.session_state.data_operasional = pd.concat(
                [df_existing, pd.DataFrame([data_baru])], ignore_index=True
            )
          st.session_state.form_index_kbk += 1
          st.success("Tersimpan! Form diset ke entri baru.")
          st.rerun()
        else:
          st.error(
              "Mohon lengkapi Nomor Bukti, Penerima, Business Unit, dan pastikan"
              " nilai nominal > 0."
          )