import streamlit as st
import pandas as pd
import io
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import streamlit.components.v1 as components

def render_modul_0():
    # CSS Khusus agar saat mencetak, hanya area laporan master akun yang muncul
    st.markdown("""
        <style>
            @media print {
                body * {
                    visibility: hidden;
                }
                #printable-report, #printable-report * {
                    visibility: visible;
                }
                #printable-report {
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 100%;
                    background: white !important;
                }
                [data-testid="stSidebar"], header, footer, .stButton {
                    display: none !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("Modul 0: Pengaturan Master Akun (Chart of Accounts & Business Unit)")
    
    tab1, tab2 = st.tabs(["📁 Master Akun (COA)", "🏢 Business Unit (BU)"])
    
    with tab1:
        st.markdown("### Daftar Master Akun & Pengelolaan COA")
        
        if not st.session_state.master_coa.empty:
            st.markdown("#### 📋 Tabel Master Akun Aktif")
            st.dataframe(st.session_state.master_coa, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 📥 Ekspor & Cetak Data Master Akun")
            
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            
            with col_ex1:
                # Tombol Download Excel Cantik & Bergaris
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    st.session_state.master_coa.to_excel(writer, index=False, sheet_name='Master_COA')
                    
                output.seek(0)
                from openpyxl import load_workbook
                wb = load_workbook(output)
                ws = wb.active
                
                header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
                data_font = Font(name="Calibri", size=11, color="000000")
                thin_border = Border(
                    left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'),
                    top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9')
                )
                
                for col in range(1, ws.max_column + 1):
                    cell = ws.cell(row=1, column=col)
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = thin_border
                ws.row_dimensions[1].height = 25
                
                for row in range(2, ws.max_row + 1):
                    ws.row_dimensions[row].height = 20
                    for col in range(1, ws.max_column + 1):
                        cell = ws.cell(row=row, column=col)
                        cell.font = data_font
                        cell.border = thin_border
                        cell.alignment = Alignment(vertical="center", horizontal="left" if col > 1 else "center")
                
                for col in ws.columns:
                    max_len = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        if cell.value:
                            max_len = max(max_len, len(str(cell.value)))
                    ws.column_dimensions[col_letter].width = max(max_len + 4, 15)
                
                final_output = io.BytesIO()
                wb.save(final_output)
                excel_data = final_output.getvalue()
                
                st.download_button(
                    label="📥 Download File Excel (Cantik & Bergaris)",
                    data=excel_data,
                    file_name="Master_COA_PT_BSS_Professional.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
            with col_ex2:
                if 'show_preview' not in st.session_state:
                    st.session_state.show_preview = False
                
                if st.button("👁️ Preview Dokumen Resmi", use_container_width=True):
                    st.session_state.show_preview = not st.session_state.show_preview
                    st.rerun()
                    
            with col_ex3:
                # Tombol Print Khusus yang memicu fungsi cetak browser langsung
                print_button_html = """
                <button onclick="parent.window.print();" style="
                    width: 100%; 
                    background-color: #ffffff; 
                    color: #31333F; 
                    padding: 0.5rem 0.75rem; 
                    border: 1px solid #d6d6d8; 
                    border-radius: 0.3rem; 
                    cursor: pointer; 
                    font-weight: 500;
                    font-family: Source Sans Pro, sans-serif;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                ">
                    🖨️ Cetak / Print Dokumen
                </button>
                """
                components.html(print_button_html, height=45)

        # --- AREA LAPORAN KODE REKENING KHUSUS (BERSIH DARI DASHBOARD) ---
        if st.session_state.get('show_preview', False):
            st.markdown("---")
            
            # Kontainer khusus laporan dengan ID 'printable-report'
            report_html = f"""
            <div id="printable-report" style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #cccccc; color: #000000; font-family: Arial, sans-serif;">
                <h2 style="text-align: center; margin-bottom: 5px; color: #1F4E78;">PT BANGGAI SENTRAL SULAWESI</h2>
                <h4 style="text-align: center; margin-top: 0px; margin-bottom: 25px; color: #444444;">LAPORAN MASTER KODE REKENING (CHART OF ACCOUNTS)</h4>
                <hr style="border: 1px solid #1F4E78; margin-bottom: 20px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <thead>
                        <tr style="background-color: #1F4E78; color: white;">
                            <th style="border: 1px solid #b0b0b0; padding: 8px; text-align: center;">Kode Akun</th>
                            <th style="border: 1px solid #b0b0b0; padding: 8px; text-align: left;">Nama Akun</th>
                            <th style="border: 1px solid #b0b0b0; padding: 8px; text-align: left;">Sub Account</th>
                            <th style="border: 1px solid #b0b0b0; padding: 8px; text-align: left;">Sub Kategori</th>
                            <th style="border: 1px solid #b0b0b0; padding: 8px; text-align: left;">Kategori</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for _, row in st.session_state.master_coa.iterrows():
                report_html += f"""
                        <tr>
                            <td style="border: 1px solid #d0d0d0; padding: 6px; text-align: center;">{row['Kode Akun']}</td>
                            <td style="border: 1px solid #d0d0d0; padding: 6px; text-align: left;">{row['Nama Akun']}</td>
                            <td style="border: 1px solid #d0d0d0; padding: 6px; text-align: left;">{row.get('Sub Account', '')}</td>
                            <td style="border: 1px solid #d0d0d0; padding: 6px; text-align: left;">{row.get('Sub Kategori', '')}</td>
                            <td style="border: 1px solid #d0d0d0; padding: 6px; text-align: left;">{row.get('Kategori', '')}</td>
                        </tr>
                """
                
            report_html += f"""
                    </tbody>
                </table>
                <p style="font-size: 11px; color: #555; margin-top: 25px; text-align: right;">Dicetak dari Sistem Akuntansi Terintegrasi PT BSS</p>
            </div>
            """
            
            components.html(report_html, height=600, scrolling=True)

            if st.button("❌ Tutup Preview Dokumen"):
                st.session_state.show_preview = False
                st.rerun()

        st.markdown("---")
        st.markdown("#### 🔄 Panggil Ulang Akun untuk Diedit atau Dihapus")
        
        if not st.session_state.master_coa.empty:
            list_kode_akun = st.session_state.master_coa['Kode Akun'].tolist()
            pilih_akun_edit = st.selectbox("Pilih Kode Akun yang Ingin Dikoreksi", list_kode_akun)
            
            if pilih_akun_edit:
                row_akun = st.session_state.master_coa[st.session_state.master_coa['Kode Akun'] == pilih_akun_edit].iloc[0]
                
                with st.form("form_koreksi_akun"):
                    st.info(f"Sedang mengedit Akun: **{pilih_akun_edit}**")
                    
                    edit_nama_akun = st.text_input("Nama Account (Variabel)", value=row_akun['Nama Akun'])
                    edit_sub_acc = st.text_input("Sub Account", value=row_akun.get('Sub Account', ''))
                    edit_sub_kat = st.text_input("Sub Kategori", value=row_akun.get('Sub Kategori', ''))
                    edit_kat = st.text_input("Kategori", value=row_akun.get('Kategori', ''))
                    
                    col_k1, col_k2 = st.columns(2)
                    with col_k1: btn_update = st.form_submit_button("💾 Update / Simpan Perubahan", use_container_width=True)
                    with col_k2: btn_hapus = st.form_submit_button("🗑️ Hapus Akun Ini", use_container_width=True)
                    
                    if btn_update:
                        st.session_state.master_coa.loc[st.session_state.master_coa['Kode Akun'] == pilih_akun_edit, ['Nama Akun', 'Sub Account', 'Sub Kategori', 'Kategori']] = [edit_nama_akun, edit_sub_acc, edit_sub_kat, edit_kat]
                        st.success(f"Akun **{pilih_akun_edit}** berhasil diperbarui!")
                        st.rerun()
                        
                    if btn_hapus:
                        st.session_state.master_coa = st.session_state.master_coa[st.session_state.master_coa['Kode Akun'] != pilih_akun_edit]
                        st.success(f"Akun **{pilih_akun_edit}** berhasil dihapus dari master!")
                        st.rerun()
        else:
            st.info("Belum ada data master akun.")

        st.divider()
        # --- FORM TAMBAH AKUN BARU ---
        with st.form("form_tambah_akun", clear_on_submit=True):
            st.markdown("#### ➕ Tambah / Daftarkan Akun Baru")
            c1, c2 = st.columns(2)
            with c1:
                input_no_akun = st.text_input("Nomor Akun (Cth: 5133.001 atau 5137.001)")
            with c2:
                input_nama_akun = st.text_input("Nama Account (Variabel / Bebas Diedit)")
                
            submitted = st.form_submit_button("➕ Tambahkan ke Master Akun")
            
            if submitted:
                if input_no_akun and input_nama_akun:
                    kode_bersih = input_no_akun.strip()
                    
                    kategori_1, kategori_2, sub_kategori = "", "", ""
                    p1 = kode_bersih[0] if len(kode_bersih) > 0 else ""
                    if p1 == '1': kategori_1 = "1 - Aktiva"
                    elif p1 == '2': kategori_1 = "2 - Hutang"
                    elif p1 == '3': kategori_1 = "3 - Ekuitas"
                    elif p1 == '4': kategori_1 = "4 - Pendapatan"
                    elif p1 == '5': kategori_1 = "5 - Harga Pokok Penjualan"
                    elif p1 == '6': kategori_1 = "6 - Beban Usaha"
                    elif p1 == '7': kategori_1 = "7 - Pendapatan / Beban Lain-Lain"
                    elif p1 == '8': kategori_1 = "8 - Ekuitas / Deviden"
                    elif p1 == '9': kategori_1 = "9 - Beban / Gain-Loss"
                    
                    p2 = kode_bersih[:2] if len(kode_bersih) >= 2 else ""
                    if p2 == '11': kategori_2 = "11 - Aktiva Lancar"
                    elif p2 == '12': kategori_2 = "12 - Aktiva Tetap / Lainnya"
                    elif p2 == '13': kategori_2 = "13 - Aktiva Tetap / Akumulasi"
                    elif p2 == '21': kategori_2 = "21 - Hutang Lancar"
                    elif p2 == '22': kategori_2 = "22 - Hutang Jangka Panjang"
                    elif p2 == '31': kategori_2 = "31 - Modal"
                    elif p2 == '32': kategori_2 = "32 - Laba Ditahan"
                    elif p2 == '41': kategori_2 = "41 - Pendapatan Proyek GS"
                    elif p2 == '42': kategori_2 = "42 - Pendapatan Proyek CR"
                    elif p2 == '51': kategori_2 = "51 - Harga Pokok Proyek GS"
                    elif p2 == '52': kategori_2 = "52 - Harga Pokok Proyek CR"
                    elif p2 == '53': kategori_2 = "53 - Harga Pokok Proyek Bengkel"
                    elif p2 == '62': kategori_2 = "62 - Beban Administrasi"
                    elif p2 == '71': kategori_2 = "71 - Pendapatan Lain-lain"
                    elif p2 == '72': kategori_2 = "72 - Biaya Lain-lain"
                    elif p2 == '75': kategori_2 = "75 - Pajak Penghasilan"
                    elif p2 == '88': kategori_2 = "88 - Deviden"
                    elif p2 == '91': kategori_2 = "91 - Gain or Loss IDR"

                    p3 = kode_bersih[:3] if len(kode_bersih) >= 3 else ""
                    if p3 == '111': sub_kategori = "111 - Kas"
                    elif p3 == '112': sub_kategori = "112 - Bank"
                    elif p3 == '113': sub_kategori = "113 - Investasi Jk Pendek"
                    elif p3 == '114': sub_kategori = "114 - Piutang Usaha"
                    elif p3 == '115': sub_kategori = "115 - Uang Muka Pembelian"
                    elif p3 == '116': sub_kategori = "116 - Piutang Lain"
                    elif p3 == '117': sub_kategori = "117 - Persediaan Barang"
                    elif p3 == '118': sub_kategori = "118 - Uang Muka Biaya / Pajak"
                    elif p3 == '121': sub_kategori = "121 - Investasi Jangka Panjang"
                    elif p3 == '131': sub_kategori = "131 - Harga Peroleh Aktiva Tetap"
                    elif p3 == '132': sub_kategori = "132 - Akumulasi Penyusutan"
                    elif p3 == '211': sub_kategori = "211 - Hutang Bank"
                    elif p3 == '212': sub_kategori = "212 - Hutang Usaha"
                    elif p3 == '213': sub_kategori = "213 - Pendapatan Diterima Dimuka"
                    elif p3 == '214': sub_kategori = "214 - Hutang Pajak"
                    elif p3 == '215': sub_kategori = "215 - Hutang Biaya"
                    elif p3 == '216': sub_kategori = "216 - Hutang Lain-Lain"
                    elif p3 == '221': sub_kategori = "221 - Kewajiban Jangka Panjang"
                    elif p3 == '311': sub_kategori = "311 - Modal"
                    elif p3 == '321': sub_kategori = "321 - Laba Ditahan"
                    elif p3 == '411': sub_kategori = "411 - Penjualan Barang Dagangan"
                    elif p3 == '412': sub_kategori = "412 - Pendapatan Jasa Tronton"
                    elif p3 == '413': sub_kategori = "413 - Pendapatan Proyek Jasa Umum"
                    elif p3 == '421': sub_kategori = "421 - Pendapatan Proyek Konstruksi"
                    elif p3 == '511': sub_kategori = "511 - Harga Pokok Pengadaan Barang"
                    elif p3 == '512': sub_kategori = "512 - Harga Pokok Operasional Tronton"
                    elif p3 == '513': sub_kategori = "513 - Harga Pokok Proyek Jasa Umum"
                    elif p3 == '514': sub_kategori = "514 - Biaya Lain-Lain Proyek"
                    elif p3 == '621': sub_kategori = "621 - Beban Administrasi Karyawan"
                    elif p3 == '622': sub_kategori = "622 - Suplies Kantor"
                    elif p3 == '623': sub_kategori = "623 - Jasa Pihak Ketiga"
                    elif p3 == '624': sub_kategori = "624 - Biaya Transportasi"
                    elif p3 == '625': sub_kategori = "625 - Biaya Umum Kantor"
                    elif p3 == '626': sub_kategori = "626 - Pemeliharaan Aktiva"
                    elif p3 == '627': sub_kategori = "627 - Iuran, Pungutan & Sumbangan"
                    elif p3 == '628': sub_kategori = "628 - Penyusutan Aktiva"
                    elif p3 == '629': sub_kategori = "629 - Beban Adm Lain-Lain"
                    elif p3 == '710': sub_kategori = "710 - Pendapatan Lain-lain"
                    elif p3 == '720': sub_kategori = "720 - Biaya Lain-lain"
                    elif p3 == '750': sub_kategori = "750 - Pajak Penghasilan"
                    elif p3 == '880': sub_kategori = "880 - Deviden"
                    elif p3 == '910': sub_kategori = "910 - Realize / Unrealize Gain or Loss IDR"

                    data_baru = {
                        "Kode Akun": kode_bersih,
                        "Nama Akun": input_nama_akun,
                        "Sub Account": sub_kategori,
                        "Sub Kategori": kategori_2,
                        "Kategori": kategori_1
                    }
                    
                    st.session_state.master_coa = pd.concat([
                        st.session_state.master_coa, pd.DataFrame([data_baru])
                    ], ignore_index=True)
                    
                    st.success(f"Akun **{input_no_akun} - {input_nama_akun}** berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Mohon lengkapi Nomor Akun dan Nama Account.")

    with tab2:
        st.markdown("### Daftar Business Unit (BU) / Proyek")
        if not st.session_state.master_bu.empty:
            st.dataframe(st.session_state.master_bu, use_container_width=True)
        else:
            st.info("Belum ada data Business Unit.")