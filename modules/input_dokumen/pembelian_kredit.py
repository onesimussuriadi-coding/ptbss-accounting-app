from datetime import datetime
import os
import pandas as pd
import streamlit as st


def render_pembelian_kredit():
  st.markdown("### 📝 Form Entri: Tagihan / Pembelian Kredit (Hutang Usaha)")
  st.markdown(
      "Gunakan form ini untuk mencatat transaksi pembelian atau penerimaan"
      " tagihan kredit dari pemasok/vendor."
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
        " dahulu di atas untuk membuka formulir pembelian kredit."
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

  if "form_index_pembelian" not in st.session_state:
    st.session_state.form_index_pembelian = 0

  idx = st.session_state.form_index_pembelian

  # --- PEMBACAAN MASTER DATA DINAMIS (KONSISTEN DENGAN KAS KELUAR) ---
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

  # Tambahkan opsi pihak ketiga / manual
  list_supplier_opt.append("-- Ketik Nama Pemasok Lain / Pihak Ketiga --")

  # Pembacaan Alokasi Alat (Sesuai Pola Modul Kas Keluar - Kolom Ke-2 / Index 1)
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
  if not list_alat_opt:
    list_alat_opt = ["Operasional Umum", "Kendaraan Operasional", "Alat Berat"]

  if f"val_ppn_pembelian_{idx}" not in st.session_state:
    st.session_state[f"val_ppn_pembelian_{idx}"] = 0.0
  if f"val_pph_pembelian_{idx}" not in st.session_state:
    st.session_state[f"val_pph_pembelian_{idx}"] = 0.0

  with st.form(f"form_pembelian_kredit_kompak_{idx}", clear_on_submit=False):

    # Baris 1: Nomor Bukti & Business Unit
    c1, c2 = st.columns(2)
    with c1:
      l1, i1 = st.columns([1.2, 1.8])
      with l1:
        st.markdown("📌 **No. Bukti / Transaksi**")
      with i1:
        no_bukti = st.text_input(
            "No Bukti",
            placeholder="Cth: BKK-CR-2026-001",
            label_visibility="collapsed",
            key=f"nobukti_pk_{idx}",
        )
    with c2:
      l2, i2 = st.columns([1.2, 1.8])
      with l2:
        st.markdown("🏗️ **Business Unit / Proyek**")
      with i2:
        bu_pilihan = st.selectbox(
            "Business Unit",
            ["-- Pilih Business Unit --"] + list_bu_opt,
            label_visibility="collapsed",
            key=f"bu_pk_{idx}",
        )

    # Baris 2: Tanggal Transaksi & Departemen Tujuan (Terkunci / Menyesuaikan Security Gate)
    c3, c4 = st.columns(2)
    with c3:
      l3, i3 = st.columns([1.2, 1.8])
      with l3:
        st.markdown("📅 **Tanggal Transaksi**")
      with i3:
        tanggal_trx = st.date_input(
            "Tgl Trx",
            datetime.now(),
            label_visibility="collapsed",
            key=f"tgl_pk_{idx}",
        )
    with c4:
      l4, i4 = st.columns([1.2, 1.8])
      with l4:
        st.markdown("🎯 **Departemen Tujuan**")
      with i4:
        # Otomatis mengikuti pilihan dari security gate di atas
        st.text_input(
            "Dept Terkunci",
            value=departemen_tujuan,
            disabled=True,
            label_visibility="collapsed",
            key=f"dept_pk_{idx}",
        )

    # Baris 3: Pemasok / Vendor & No Invoice
    c5, c6 = st.columns(2)
    with c5:
      l5, i5 = st.columns([1.2, 1.8])
      with l5:
        st.markdown("🏢 **Pemasok / Vendor**")
      with i5:
        pemasok_pilihan = st.selectbox(
            "Pemasok",
            ["-- Pilih Pemasok --"] + list_supplier_opt,
            label_visibility="collapsed",
            key=f"pemasok_pk_{idx}",
        )
    with c6:
      l6, i6 = st.columns([1.2, 1.8])
      with l6:
        st.markdown("📄 **No. Invoice Supplier**")
      with i6:
        no_invoice = st.text_input(
            "Invoice",
            value="-",
            label_visibility="collapsed",
            key=f"inv_pk_{idx}",
        )

    # Input teks opsional jika memilih Pihak Ketiga
    pemasok_final = (
        pemasok_pilihan
        if pemasok_pilihan
        not in [
            "-- Pilih Pemasok --",
            "-- Ketik Nama Pemasok Lain / Pihak Ketiga --",
        ]
        else ""
    )
    if pemasok_pilihan == "-- Ketik Nama Pemasok Lain / Pihak Ketiga --":
      pemasok_manual = st.text_input(
          "✍️ Masukkan Nama Pemasok / Pihak Ketiga Lainnya:",
          placeholder="Ketik nama vendor di sini...",
          key=f"manual_sup_pk_{idx}",
      )
      if pemasok_manual.strip():
        pemasok_final = pemasok_manual.strip()

    # Baris 4: Jatuh Tempo & Qty / Satuan
    c7, c8 = st.columns(2)
    with c7:
      l7, i7 = st.columns([1.2, 1.8])
      with l7:
        st.markdown("⏳ **Jatuh Tempo Hutang**")
      with i7:
        jatuh_tempo = st.date_input(
            "Jatuh Tempo",
            datetime.now(),
            label_visibility="collapsed",
            key=f"tempo_pk_{idx}",
        )
    with c8:
      l8, i8 = st.columns([1.2, 1.8])
      with l8:
        st.markdown("📦 **Qty & Satuan**")
      with i8:
        qc, sc = st.columns([1, 1.3])
        with qc:
          jumlah = st.number_input(
              "Qty",
              min_value=0.0,
              value=1.0,
              step=1.0,
              label_visibility="collapsed",
              key=f"qty_pk_{idx}",
          )
        with sc:
          satuan_pilihan = st.selectbox(
              "Sat",
              ["Satuan"] + st.session_state.master_satuan,
              label_visibility="collapsed",
              key=f"sat_pk_{idx}",
          )
        satuan_final = (
            satuan_pilihan if satuan_pilihan != "Satuan" else "Unit"
        )

    # Baris 5: Alokasi Alat (Dibaca persis dari Kolom Master Alat)
    c9, c10 = st.columns(2)
    with c9:
      l9, i9 = st.columns([1.2, 1.8])
      with l9:
        st.markdown("🔧 **Alokasi Alat / Unit**")
      with i9:
        peruntukan_pilihan = st.selectbox(
            "Alat",
            ["-- Pilih Alokasi Alat --"] + list_alat_opt,
            label_visibility="collapsed",
            key=f"alat_pk_{idx}",
        )
        peruntukan_final = (
            peruntukan_pilihan
            if peruntukan_pilihan != "-- Pilih Alokasi Alat --"
            else "-"
        )

    st.markdown("---")

    # Uraian / Keterangan Transaksi di Atas Nilai Keuangan
    st.markdown("##### 📝 Uraian / Keterangan Transaksi")
    keterangan = st.text_area(
        "Keterangan",
        placeholder="Tuliskan keterangan detail pembelian kredit di sini...",
        height=70,
        label_visibility="collapsed",
        key=f"ket_pk_{idx}",
    )

    st.markdown("---")

    # Rincian Nilai Keuangan
    st.markdown("#### 💰 Rincian Nilai Keuangan")
    rf1, rf2, rf3 = st.columns(3)
    with rf1:
      st.markdown("**DPP / Nilai Pokok (Rp)**")
      dpp_val = st.number_input(
          "DPP",
          min_value=0.0,
          value=0.0,
          step=10000.0,
          format="%.2f",
          label_visibility="collapsed",
          key=f"dpp_pk_{idx}",
      )
    with rf2:
      st.markdown("**PPN (Rp)**")
      ppn_val = st.number_input(
          "PPN",
          min_value=0.0,
          value=0.0,
          step=1000.0,
          format="%.2f",
          label_visibility="collapsed",
          key=f"ppn_pk_{idx}",
      )
    with rf3:
      st.markdown("**PPh (Rp)**")
      pph_val = st.number_input(
          "PPh",
          min_value=0.0,
          value=0.0,
          step=1000.0,
          format="%.2f",
          label_visibility="collapsed",
          key=f"pph_pk_{idx}",
      )

    total_val = (dpp_val + ppn_val) - pph_val
    st.markdown(f"### **Total Tagihan Bersih: Rp {total_val:,.2f}**")
    st.markdown("<br>", unsafe_allow_html=True)

    # Tombol Aksi Lengkap
    b1, b2, b3, b4 = st.columns(4)
    with b1:
      submitted = st.form_submit_button("💾 Simpan", use_container_width=True)
    with b2:
      btn_edit = st.form_submit_button("✏️ Edit", use_container_width=True)
    with b3:
      btn_tambah = st.form_submit_button("➕ Baris", use_container_width=True)
    with b4:
      btn_refresh = st.form_submit_button("🔄 Refresh", use_container_width=True)

    if btn_refresh:
      st.session_state.form_index_pembelian += 1
      st.success("Form berhasil di-refresh!")
      st.rerun()

    if submitted:
      if (
          not no_bukti
          or not pemasok_final
          or not bu_pilihan
          or bu_pilihan == "-- Pilih Business Unit --"
      ):
        st.error("Mohon lengkapi Nomor Bukti, Business Unit, dan Pemasok!")
      else:
        data_baru = {
            "Nomor Bukti": no_bukti,
            "Tanggal": str(tanggal_trx),
            "Sumber Transaksi": "Tagihan / Pembelian Kredit (Hutang Usaha)",
            "Lawan Transaksi": pemasok_final,
            "No Invoice": no_invoice,
            "Jatuh Tempo": str(jatuh_tempo),
            "Business Unit": bu_pilihan,
            "Departemen Tujuan": departemen_tujuan,  # Menggunakan departemen dari security gate
            "Jumlah": jumlah,
            "Satuan": satuan_final,
            "Peruntukan": peruntukan_final,
            "Keterangan": keterangan,
            "DPP": dpp_val,
            "PPN": ppn_val,
            "PPH": pph_val,
            "Total": total_val,
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
          st.success(f"Dokumen **{no_bukti}** berhasil diperbarui!")
        else:
          st.session_state.data_operasional = pd.concat(
              [df_existing, pd.DataFrame([data_baru])], ignore_index=True
          )
          st.success(f"Dokumen **{no_bukti}** berhasil disimpan!")