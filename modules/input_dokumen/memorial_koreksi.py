from datetime import datetime
import os
import pandas as pd
import streamlit as st


def render_memorial_koreksi():
  st.markdown("### 📝 Modul Khusus: Memorial / Koreksi Pembukuan")

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
        " dahulu di atas untuk membuka formulir memorial."
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

  if "form_index_mem" not in st.session_state:
    st.session_state.form_index_mem = 0

  idx = st.session_state.form_index_mem

  col_reset1, col_reset2 = st.columns([3, 1])
  with col_reset2:
    if st.button("🧹 Reset Form Memorial", use_container_width=True):
      st.session_state.form_index_mem += 1
      st.success("Form memorial berhasil dibersihkan!")
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

  list_coa_opt = []
  if os.path.exists("master_coa_bss.xlsx"):
    try:
      df_coa = pd.read_excel("master_coa_bss.xlsx")
      df_coa.columns = df_coa.columns.str.replace("\xa0", " ").str.strip()
      col_kode = df_coa.columns[0]
      col_nama = (
          df_coa.columns[1] if len(df_coa.columns) > 1 else df_coa.columns[0]
      )
      list_coa_opt = (
          df_coa[col_kode].astype(str).str.strip()
          + " - "
          + df_coa[col_nama].astype(str).str.strip()
      ).tolist()
    except Exception:
      pass
  if not list_coa_opt:
    list_coa_opt = ["611.01 - Biaya Umum", "211.01 - Hutang Lainnya"]

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
      st.markdown("<br>📅 **Tanggal Memorial**", unsafe_allow_html=True)
    with c2:
      tgl = st.date_input(
          "Tanggal",
          datetime.now(),
          label_visibility="collapsed",
          key=f"tgl_mem_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🧾 **Nomor Bukti / Slip Memorial**", unsafe_allow_html=True)
    with c2:
      no_bukti = st.text_input(
          "No Bukti",
          placeholder="Cth: BSS/MEM/VIII/2026/001",
          label_visibility="collapsed",
          key=f"nobukti_mem_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>📋 **Jenis Penyesuaian / Koreksi**", unsafe_allow_html=True)
    with c2:
      jenis_memorial = st.selectbox(
          "Jenis Memorial",
          [
              "Jurnal Penyesuaian (Adjustment)",
              "Koreksi Pembukuan / Kesalahan Catat",
              "Alokasi Biaya Internal",
              "Memorial Tutup Buku",
          ],
          key=f"jenis_mem_{idx}",
          label_visibility="collapsed",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🏢 **Pihak / Departemen Terkait**", unsafe_allow_html=True)
    with c2:
      pihak_terkait = st.text_input(
          "Pihak Terkait",
          placeholder="Cth: Bagian Akuntansi / Internal",
          key=f"pihak_mem_{idx}",
          label_visibility="collapsed",
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
            key=f"bu_mem_{idx}",
        )
      with sub_bu2:
        tambah_bu_baru = st.text_input(
            "BU Baru",
            placeholder="Ketik baru...",
            key=f"tambah_bu_mem_{idx}",
            label_visibility="collapsed",
        )
      bu_final = bu_pilihan if bu_pilihan != "-- Pilih Business Unit --" else ""
      if tambah_bu_baru.strip():
        bu_final = tambah_bu_baru.strip()

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>🎯 **Peruntukan (Alokasi Alat / Unit)**", unsafe_allow_html=True)
    with c2:
      peruntukan_pilihan = st.selectbox(
          "Pilih Alat / Unit",
          ["-- Pilih Alokasi Alat / Unit --"] + list_alat_opt,
          label_visibility="collapsed",
          key=f"peruntukan_mem_{idx}",
      )
      peruntukan_final = (
          peruntukan_pilihan
          if peruntukan_pilihan != "-- Pilih Alokasi Alat / Unit --"
          else "-"
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown(
          "<br><br>📝 **Uraian / Keterangan Memorial / Koreksi**",
          unsafe_allow_html=True,
      )
    with c2:
      keterangan = st.text_area(
          "Keterangan",
          placeholder="Alasan koreksi atau rincian jurnal penyesuaian...",
          label_visibility="collapsed",
          key=f"ket_mem_{idx}",
      )

    c1, c2 = st.columns([1, 2])
    with c1:
      st.markdown("<br>💰 **Nilai Nominal Koreksi / Penyesuaian**", unsafe_allow_html=True)
    with c2:
      nilai_memorial = st.number_input(
          "Nominal",
          min_value=0.0,
          step=10000.0,
          format="%.2f",
          value=0.0,
          label_visibility="collapsed",
          key=f"val_mem_{idx}",
      )

    st.divider()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
      if st.button(
          "💾 Simpan Data Memorial",
          use_container_width=True,
          key=f"btn_save_mem_{idx}",
      ):
        if nilai_memorial > 0 and no_bukti and bu_final and pihak_terkait:
          data_baru = {
              "Nomor Bukti": no_bukti,
              "Tanggal": tgl,
              "Sumber Transaksi": f"Memorial / Koreksi - {jenis_memorial}",
              "Lawan Transaksi": pihak_terkait,
              "No Invoice": "-",
              "Jatuh Tempo": "-",
              "Business Unit": bu_final,
              "Departemen Tujuan": departemen_tujuan,  # Menggunakan pilihan departemen keamanan
              "Jumlah": 1.0,
              "Satuan": "Lot",
              "Peruntukan": peruntukan_final,
              "Keterangan": keterangan,
              "DPP": nilai_memorial,
              "PPN": 0.0,
              "PPH": 0.0,
              "Total": nilai_memorial,
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
            st.success("Data memorial berhasil disimpan!")
        else:
          st.error(
              "Mohon lengkapi Nomor Bukti, Pihak Terkait, Business Unit, dan"
              " pastikan nilai nominal > 0."
          )

    with col_b2:
      if st.button(
          "➕ Simpan & Mulai Entri Baru",
          use_container_width=True,
          key=f"btn_save_new_mem_{idx}",
      ):
        if nilai_memorial > 0 and no_bukti and bu_final and pihak_terkait:
          data_baru = {
              "Nomor Bukti": no_bukti,
              "Tanggal": tgl,
              "Sumber Transaksi": f"Memorial / Koreksi - {jenis_memorial}",
              "Lawan Transaksi": pihak_terkait,
              "No Invoice": "-",
              "Jatuh Tempo": "-",
              "Business Unit": bu_final,
              "Departemen Tujuan": departemen_tujuan,
              "Jumlah": 1.0,
              "Satuan": "Lot",
              "Peruntukan": peruntukan_final,
              "Keterangan": keterangan,
              "DPP": nilai_memorial,
              "PPN": 0.0,
              "PPH": 0.0,
              "Total": nilai_memorial,
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
          st.session_state.form_index_mem += 1
          st.success("Tersimpan! Form diset ke entri baru.")
          st.rerun()
        else:
          st.error(
              "Mohon lengkapi Nomor Bukti, Pihak Terkait, Business Unit, dan"
              " pastikan nilai nominal > 0."
          )