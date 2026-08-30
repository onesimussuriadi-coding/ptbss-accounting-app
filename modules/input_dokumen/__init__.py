import streamlit as st
import pandas as pd

def render_modul_1():
    # Lazy import di dalam fungsi untuk mencegah circular import
    from modules.input_dokumen.pembelian_kredit import render_pembelian_kredit
    from modules.input_dokumen.invoice_penjualan import render_invoice_penjualan
    from modules.input_dokumen.kas_bank_masuk import render_kas_bank_masuk
    from modules.input_dokumen.kas_bank_keluar import render_kas_bank_keluar
    from modules.input_dokumen.gudang_persediaan import render_gudang_persediaan
    from modules.input_dokumen.memorial_koreksi import render_memorial_koreksi

    st.subheader("Modul 1: Penginputan Dokumen & Manajemen Persetujuan (Workflow)")

    dept_pilihan_input = st.selectbox(
        "Pilih Departemen Tujuan Dokumen (Wajib Sesuai Hierarki)",
        ["-- Pilih Departemen Tujuan --", "Operasional", "HRD", "Logistik", "Maintenance", "HSE", "Akuntansi", "Keuangan"],
        key="selectbox_dept_tujuan_input"
    )
    st.markdown("---")

    if 'data_operasional' not in st.session_state:
        st.session_state.data_operasional = pd.DataFrame(columns=[
            "Nomor Bukti", "Tanggal", "Sumber Transaksi", "Lawan Transaksi", 
            "No Invoice", "Jatuh Tempo", "Business Unit", "Departemen Tujuan", "Jumlah", "Satuan", "Peruntukan", "Keterangan", 
            "DPP", "PPN", "PPH", "Total", "Status Dokumen", "Status Jurnal"
        ])

    list_sumber_opsi = [
        "Kas Bank Masuk (Penerimaan Dana)", 
        "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)",
        "Tagihan / Pembelian Kredit (Hutang Usaha)",
        "Kas Besar / Kas Proyek", 
        "Kas Kecil (Petty Cash)", 
        "Bank Keluar / Pembayaran",
        "Gudang", 
        "Memorial / Koreksi"
    ]

    menu_tab = st.radio(
        "Pilih Menu Navigasi Modul:",
        ["📝 Form Penginputan Dokumen", "📂 Data Tersimpan & Approval (Pusat Kendali)"],
        horizontal=True,
        key="nav_modul_1"
    )

    if menu_tab == "📝 Form Penginputan Dokumen":
        sumber_transaksi = st.selectbox("Pilih Sumber Dokumen", list_sumber_opsi, key="selectbox_sumber_trx")
        st.markdown("---")

        if sumber_transaksi == "Tagihan / Pembelian Kredit (Hutang Usaha)":
            render_pembelian_kredit()
        elif sumber_transaksi == "Penerbitan Invoice / Tagihan Penjualan (Piutang Usaha)":
            render_invoice_penjualan()
        elif sumber_transaksi == "Kas Bank Masuk (Penerimaan Dana)":
            render_kas_bank_masuk()
        elif sumber_transaksi in ["Kas Besar / Kas Proyek", "Kas Kecil (Petty Cash)", "Bank Keluar / Pembayaran"]:
            render_kas_bank_keluar()
        elif sumber_transaksi == "Gudang":
            render_gudang_persediaan()
        elif sumber_transaksi == "Memorial / Koreksi":
            render_memorial_koreksi()
    else:
        st.markdown("### 📂 Pusat Kendali Dokumen & Persetujuan Berjenjang (Workflow)")
        if not st.session_state.data_operasional.empty:
            df_pusat = st.session_state.data_operasional.copy()
            st.dataframe(df_pusat, use_container_width=True)
        else:
            st.info("Belum ada data dokumen operasional yang tersimpan di dalam sistem.")