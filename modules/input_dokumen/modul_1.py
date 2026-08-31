from datetime import datetime
import pandas as pd
import streamlit as st


def render_modul_1():
  # Inisialisasi state sesi verifikasi khusus di dalam Modul 1
  if "modul1_verified" not in st.session_state:
    st.session_state.modul1_verified = False
  if "modul1_dept" not in st.session_state:
    st.session_state.modul1_dept = None
  if "modul1_user" not in st.session_state:
    st.session_state.modul1_user = None

  st.subheader(
      "Modul 1: Penginputan Dokumen & Manajemen Persetujuan (Workflow)"
  )
  st.markdown("---")

  # =========================================================================
  # GERBANG VERIFIKASI AWAL (Mencocokkan dengan Database Kredensial Permanen)
  # =========================================================================
  if not st.session_state.modul1_verified:
    col_spacer1, col_box, col_spacer2 = st.columns([1, 2, 1])
    with col_box:
      st.markdown(
          "<h4 style='text-align: center; color: #1E3A8A;'>🔐 Verifikasi"
          " Akses Penginputan</h4>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; color: #64748B; font-size: 13px;'>Silakan"
          " pilih departemen dan masukkan Username atau Nama Lengkap terdaftar"
          " Anda.</p>",
          unsafe_allow_html=True,
      )

      with st.form("form_verifikasi_modul1_lokal"):
        dept_list = [
            "-- Pilih Departemen Tujuan --",
            "Operasional",
            "HRD",
            "Logistik",
            "Maintenance",
            "HSE",
            "Akuntansi",
            "Keuangan",
        ]
        pilih_dept = st.selectbox("Departemen Tujuan", dept_list)
        input_username = st.text_input(
            "Username / Nama Penginput",
            placeholder="Ketik username atau nama terdaftar...",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        btn_verif = st.form_submit_button(
            "🚀 Masuk ke Form Penginputan", use_container_width=True
        )

        if btn_verif:
          if pilih_dept == "-- Pilih Departemen Tujuan --":
            st.error("Mohon pilih Departemen Tujuan terlebih dahulu!")
          elif not input_username.strip():
            st.error("Username atau Nama penginput tidak boleh kosong!")
          else:
            clean_input = input_username.strip().lower()
            creds = st.session_state.get("credentials_dict", {})

            ditemukan = False
            nama_terverifikasi = ""

            for uname, details in creds.items():
              stored_user = str(uname).strip().lower()
              stored_name = str(details.get("name", "")).strip().lower()
              stored_dept = str(details.get("dept", "")).strip().lower()

              if clean_input == stored_user or clean_input == stored_name:
                if (
                    stored_dept == pilih_dept.lower()
                    or details.get("role") == "Programmer"
                    or "admin" in clean_input
                ):
                  ditemukan = True
                  nama_terverifikasi = details.get("name", input_username)
                  break

            if ditemukan:
              st.session_state.modul1_verified = True
              st.session_state.modul1_dept = pilih_dept
              st.session_state.modul1_user = nama_terverifikasi
              st.success(
                  f"Verifikasi sukses! Membuka akses untuk **{nama_terverifikasi}"
                  f" ({pilih_dept})**..."
              )
              st.rerun()
            else:
              st.error(
                  f"❌ Akses Ditolak: '{input_username}' tidak terdaftar atau"
                  f" tidak sesuai pada departemen **{pilih_dept}**."
              )
    return

  # Jika sudah terverifikasi, tampilkan info penginput aktif & tombol ganti sesi di atas
  col_info, col_out = st.columns([4, 1])
  with col_info:
    st.info(
        f"👤 Penginput Aktif: **{st.session_state.modul1_user}** | 🏢 Departemen"
        f" Tujuan: **{st.session_state.modul1_dept}**"
    )
  with col_out:
    if st.button("🔄 Ganti Sesi", use_container_width=True):
      st.session_state.modul1_verified = False
      st.session_state.modul1_dept = None
      st.session_state.modul1_user = None
      st.rerun()

  st.markdown("---")

  # Jalur import sub-modul dengan awalan modules.input_dokumen
  from modules.input_dokumen.gudang_persediaan import render_gudang_persediaan
  from modules.input_dokumen.invoice_penjualan import render_invoice_penjualan
  from modules.input_dokumen.kas_bank_keluar import render_kas_bank_keluar
  from modules.input_dokumen.kas_bank_masuk import render_kas_bank_masuk
  from modules.input_dokumen.memorial_koreksi import render_memorial_koreksi
  from modules.input_dokumen.pembelian_kredit import render_pembelian_kredit

  # Inisialisasi DataFrame utama dengan kolom pelacakan Tanggal Input & Approve
  if "data_operasional" not in st.session_state:
    st.session_state.data_operasional = pd.DataFrame(
        columns=[
            "Nomor Bukti",
            "Tanggal Transaksi",
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
            "Nama Penginput",
            "Tanggal Input",
            "Tanggal Approve",
        ]
    )

  # =========================================================================
  # FITUR SIDEBAR: RUANG DATA TERSIMPAN MANDIRI & PANGGIL ULANG (EDIT)
  # =========================================================================
  penginput_saat_ini = st.session_state.modul1_user

  with st.sidebar:
    st.markdown("---")
    st.markdown("### 📂 Data Tersimpan Anda")
    st.markdown(
        f"<p style='font-size:12px; color:#64748B;'>Privasi data milik:"
        f" <b>{penginput_saat_ini}</b></p>",
        unsafe_allow_html=True,
    )

    df_all_ops = st.session_state.data_operasional
    # Filter data HANYA milik user yang sedang aktif login
    if not df_all_ops.empty and "Nama Penginput" in df_all_ops.columns:
      df_user_milik_sendiri = df_all_ops[
          df_all_ops["Nama Penginput"].str.lower()
          == penginput_saat_ini.lower()
      ]
    else:
      df_user_milik_sendiri = pd.DataFrame(columns=df_all_ops.columns)

    if not df_user_milik_sendiri.empty:
      st.dataframe(
          df_user_milik_sendiri[
              [
                  "Nomor Bukti",
                  "Sumber Transaksi",
                  "Total",
                  "Status Dokumen",
                  "Tanggal Input",
              ]
          ],
          use_container_width=True,
      )

      st.markdown("---")
      st.markdown("#### 🔄 Panggil Ulang (Edit / Update)")
      list_bukti_user = df_user_milik_sendiri["Nomor Bukti"].tolist()
      pilih_edit_bukti = st.selectbox(
          "Pilih Nomor Bukti untuk Diedit", ["-- Pilih --"] + list_bukti_user
      )

      if pilih_edit_bukti != "-- Pilih --":
        if st.button(
            "📥 Muat Data ke Form Edit", use_container_width=True
        ):
          row_pilih = df_user_milik_sendiri[
              df_user_milik_sendiri["Nomor Bukti"] == pilih_edit_bukti
          ].iloc[0]
          st.session_state.edit_mode_active = True
          st.session_state.edit_data_temp = row_pilih.to_dict()
          st.success(
              f"Data **{pilih_edit_bukti}** berhasil dimuat. Silakan lakukan"
              " perubahan pada form utama."
          )
          st.rerun()
    else:
      st.info(
          "Belum ada data tersimpan yang Anda input. Data dari pengguna lain"
          " disembunyikan demi privasi."
      )

  # =========================================================================
  # NAVIGASI UTAMA MODUL 1
  # =========================================================================
  list_sumber_opsi = [
      "Kas Bank Masuk (Penerimaan Dana)",
      "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)",
      "Tagihan / Pembelian Kredit (Hutang Usaha)",
      "Kas Besar / Kas Proyek",
      "Kas Kecil (Petty Cash)",
      "Bank Keluar / Pembayaran",
      "Gudang",
      "Memorial / Koreksi",
  ]

  if st.session_state.get("edit_mode_active", False):
    st.warning(
        "⚠️ **MODE EDIT AKTIF:** Anda sedang memperbarui data dokumen dengan"
        f" Nomor Bukti: `{st.session_state.edit_data_temp.get('Nomor Bukti')}`."
        " Perubahan yang disimpan akan memperbarui data sebelumnya."
    )
    if st.button("❌ Batalkan Mode Edit"):
      st.session_state.edit_mode_active = False
      if "edit_data_temp" in st.session_state:
        del st.session_state.edit_data_temp
      st.rerun()

  sumber_transaksi = st.selectbox(
      "Pilih Sumber Dokumen untuk Diinput",
      list_sumber_opsi,
      key="selectbox_sumber_trx",
  )
  st.markdown("---")

  # Render form input dokumen sesuai pilihan
  if sumber_transaksi == "Tagihan / Pembelian Kredit (Hutang Usaha)":
    render_pembelian_kredit()
  elif (
      sumber_transaksi == "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)"
  ):
    render_invoice_penjualan()
  elif sumber_transaksi == "Kas Bank Masuk (Penerimaan Dana)":
    render_kas_bank_masuk()
  elif sumber_transaksi in [
      "Kas Besar / Kas Proyek",
      "Kas Kecil (Petty Cash)",
      "Bank Keluar / Pembayaran",
  ]:
    render_kas_bank_keluar()
  elif sumber_transaksi == "Gudang":
    render_gudang_persediaan()
  elif sumber_transaksi == "Memorial / Koreksi":
    render_memorial_koreksi()