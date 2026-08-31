from datetime import datetime
import os
import pandas as pd
import streamlit as st


def render_kas_bank_masuk():
  st.markdown("### 📥 Modul Khusus: Kas & Bank Masuk (Penerimaan Dana)")

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
        " dahulu di atas untuk membuka formulir kas/bank masuk."
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

  if "form_index_kbm" not in st.session_state:
    st.session_state.form_index_kbm = 0

  idx = st.session_state.form_index_kbm

  col_reset1, col_reset2 = st.columns([3, 1])
  with col_reset2:
    if st.button("🧹 Reset Form Kas Masuk", use_container_width=True):
      st.session_state.form_index_kbm += 1
      st.success("Form kas masuk berhasil dibersihkan!")
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

  list_pelanggan_opt = []
  if os.path.exists("master_pelanggan_bss.xlsx"):
    try:
      df_pel = pd.read_excel("master_pelanggan_bss.xlsx")
      df_pel.columns = df_pel.columns.str.replace("\xa0", " ").str.strip()
      col_target = (
          df_pel.columns[1] if len(df_pel.columns) > 1 else df_pel.columns[0]
      )
      list_pelanggan_opt = (
          df_pel[col_target].dropna().astype(str).str.strip().tolist()
      )
    except Exception:
      pass
  if not list_pelanggan_opt:
    list_pelanggan_opt = ["Pelanggan / Pihak Ketiga Umum"]

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

  with st.container():
    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>📅 **Tanggal Penerimaan**", unsafe_allow_html=True)
    with c2:
      tgl = st.date_input(
          "Tanggal",
          datetime.now(),
          label_visibility="collapsed",
          key=f"tgl_kbm_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🧾 **Nomor Bukti / Ref Internal**", unsafe_allow_html=True)
    with c2:
      no_bukti = st.text_input(
          "No Bukti",
          placeholder="Cth: BSS/BM/VIII/2026/001",
          label_visibility="collapsed",
          key=f"nobukti_kbm_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown(
          "<br>🏦 **Akun Kas / Rekening Bank Penerima**", unsafe_allow_html=True
      )
    with c2:
      bank_penerima = st.selectbox(
          "Pilih Kas/Bank",
          ["-- Pilih Akun Kas / Bank --"] + list_kas_bank_opt,
          key=f"bank_terima_kbm_{idx}",
          label_visibility="collapsed",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>👥 **Pihak Ketiga / Pelanggan**", unsafe_allow_html=True)
    with c2:
      sub_cust1, sub_cust2 = st.columns([3, 1])
      with sub_cust1:
        pelanggan_pilihan = st.selectbox(
            "Pilih Pelanggan",
            ["-- Pilih Pelanggan --"] + list_pelanggan_opt,
            key=f"pihak_ketiga_kbm_{idx}",
            label_visibility="collapsed",
        )
      with sub_cust2:
        tambah_pelanggan_baru = st.text_input(
            "Pelanggan Baru",
            placeholder="Ketik baru...",
            key=f"tambah_pelanggan_kbm_{idx}",
            label_visibility="collapsed",
        )

      lawan_transaksi_final = (
          pelanggan_pilihan if pelanggan_pilihan != "-- Pilih Pelanggan --" else ""
      )
      if tambah_pelanggan_baru.strip():
        lawan_transaksi_final = tambah_pelanggan_baru.strip()

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>📑 **Jenis Penerimaan**", unsafe_allow_html=True)
    with c2:
      jenis_terima = st.radio(
          "Jenis Penerimaan",
          [
              "Pelunasan Tagihan (Berdasarkan Invoice)",
              "Penerimaan Tunai / Non-Invoice (Input Manual)",
          ],
          key=f"jenis_terima_kbm_{idx}",
          label_visibility="collapsed",
      )

    no_invoice_final = "-"
    suggested_dpp = 0.0
    if jenis_terima == "Pelunasan Tagihan (Berdasarkan Invoice)":
      c1, c2 = st.columns([1, 2])
      with c1:
        st.markdown("<br>🏷️ **Nomor Invoice Tagihan**", unsafe_allow_html=True)
      with c2:
        if not st.session_state.data_operasional.empty:
          df_op = st.session_state.data_operasional
          mask_cust = (df_op["Lawan Transaksi"] == lawan_transaksi_final) & (
              df_op["No Invoice"] != "-"
          )
          inv_tercatat = df_op[mask_cust]["No Invoice"].unique().tolist()
        else:
          inv_tercatat = []
        list_inv_opsi = (
            inv_tercatat if inv_tercatat else ["Belum ada invoice tercatat"]
        )
        list_inv_opsi.append("INV-Lainnya (Manual)")

        pilih_inv = st.selectbox(
            "Pilih Invoice",
            ["-- Pilih Invoice --"] + list_inv_opsi,
            key=f"pilih_inv_kbm_{idx}",
            label_visibility="collapsed",
        )
        if (
            pilih_inv == "INV-Lainnya (Manual)"
            or "Belum ada invoice" in pilih_inv
        ):
          no_invoice_final = st.text_input(
              "Ketik Nomor Invoice Manual",
              placeholder="Cth: INV/BSS/2026/001",
              key=f"inv_manual_kbm_{idx}",
          )
        else:
          no_invoice_final = (
              pilih_inv if pilih_inv != "-- Pilih Invoice --" else ""
          )
          if not st.session_state.data_operasional.empty:
            matched_row = st.session_state.data_operasional[
                st.session_state.data_operasional["No Invoice"]
                == no_invoice_final
            ]
            if not matched_row.empty:
              suggested_dpp = float(matched_row.iloc[0]["Total"])
    else:
      no_invoice_final = "NON-INVOICE (Penerimaan Langsung)"

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
            key=f"bu_kbm_{idx}",
        )
      with sub_bu2:
        tambah_bu_baru = st.text_input(
            "BU Baru",
            placeholder="Ketik baru...",
            key=f"tambah_bu_kbm_{idx}",
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
          key=f"jml_kbm_{idx}",
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
            key=f"satuan_kbm_{idx}",
        )
      with sub_sat2:
        tambah_satuan_baru = st.text_input(
            "Tambah Satuan",
            placeholder="Baru...",
            label_visibility="collapsed",
            key=f"tambah_satuan_kbm_{idx}",
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
          key=f"peruntukan_kbm_{idx}",
      )
      peruntukan_final = (
          peruntukan_pilihan
          if peruntukan_pilihan != "-- Pilih Alokasi Alat / Unit --"
          else "-"
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br><br>📝 **Uraian / Keterangan**", unsafe_allow_html=True)
    with c2:
      keterangan = st.text_area(
          "Keterangan",
          placeholder="Keterangan penerimaan dana kas/bank masuk...",
          label_visibility="collapsed",
          key=f"ket_kbm_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>💰 **Nomor Penerimaan (Total)**", unsafe_allow_html=True)
    with c2:
      if suggested_dpp > 0:
        st.info(f"💡 Total tagihan invoice terpilih: **Rp {suggested_dpp:,.2f}**")
      total_transaksi = st.number_input(
          "Nomor",
          min_value=0.0,
          step=10000.0,
          format="%.2f",
          value=suggested_dpp,
          label_visibility="collapsed",
          key=f"val_tot_kbm_{idx}",
      )

    st.divider()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
      if st.button(
          "💾 Simpan Data Kas Masuk",
          use_container_width=True,
          key=f"btn_save_kbm_{idx}",
      ):
        if total_transaksi > 0 and no_bukti and bu_final and lawan_transaksi_final:
          data_baru = {
              "Nomor Bukti": no_bukti,
              "Tanggal": tgl,
              "Sumber Transaksi": "Kas Bank Masuk (Penerimaan Dana)",
              "Lawan Transaksi": lawan_transaksi_final,
              "No Invoice": no_invoice_final,
              "Jatuh Tempo": "-",
              "Business Unit": bu_final,
              "Departemen Tujuan": departemen_tujuan,  # Menggunakan pilihan departemen keamanan
              "Jumlah": jumlah,
              "Satuan": satuan_final,
              "Peruntukan": peruntukan_final,
              "Keterangan": keterangan,
              "DPP": total_transaksi,
              "PPN": 0.0,
              "PPH": 0.0,
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
            st.success("Data kas masuk berhasil disimpan!")
        else:
          st.error(
              "Mohon lengkapi Nomor Bukti, Lawan Transaksi, Business Unit, dan"
              " pastikan nominal > 0."
          )

    with col_b2:
      if st.button(
          "➕ Simpan & Mulai Entri Baru",
          use_container_width=True,
          key=f"btn_save_new_kbm_{idx}",
      ):
        if total_transaksi > 0 and no_bukti and bu_final and lawan_transaksi_final:
          data_baru = {
              "Nomor Bukti": no_bukti,
              "Tanggal": tgl,
              "Sumber Transaksi": "Kas Bank Masuk (Penerimaan Dana)",
              "Lawan Transaksi": lawan_transaksi_final,
              "No Invoice": no_invoice_final,
              "Jatuh Tempo": "-",
              "Business Unit": bu_final,
              "Departemen Tujuan": departemen_tujuan,
              "Jumlah": jumlah,
              "Satuan": satuan_final,
              "Peruntukan": peruntukan_final,
              "Keterangan": keterangan,
              "DPP": total_transaksi,
              "PPN": 0.0,
              "PPH": 0.0,
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
          st.session_state.form_index_kbm += 1
          st.success("Tersimpan! Form diset ke entri baru.")
          st.rerun()
        else:
          st.error(
              "Mohon lengkapi Nomor Bukti, Lawan Transaksi, Business Unit, dan"
              " pastikan nominal > 0."
          )