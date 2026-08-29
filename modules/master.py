import streamlit as st
import pandas as pd

def render_modul_0():
    st.subheader("Modul 0: Pengaturan Master Data Perusahaan")
    
    sub_modul = st.radio("Pilih Sub Menu Master:", ["Input Account / Kode Rekening", "Input Business Unit"], horizontal=True)
    st.divider()
    
    if sub_modul == "Input Account / Kode Rekening":
        st.markdown("### 📋 Daftar Kode Rekening (6 Digit)")
        df_tampil_coa = st.session_state.master_coa[["Kategori", "Sub Kategori", "Sub Account", "Nama Akun", "Kode Akun"]]
        st.dataframe(df_tampil_coa, use_container_width=True)
        
        st.divider()
        st.markdown("### Kelola Data Akun (Auto-Fill & Manual)")
        mode_coa = st.radio("Pilih Aksi Pengelolaan Akun", ["Tambah Akun Baru", "Koreksi / Edit / Hapus Akun yang Ada"], horizontal=True)
        
        if mode_coa == "Tambah Akun Baru":
            with st.form("form_tambah_akun"):
                st.info("💡 **Tips Auto-Fill:** Masukkan Kode Akun 6 digit (Contoh: `511103`) dan Nama Account. Kategori & Sub Kategori akan terisi otomatis!")
                col_1, col_2 = st.columns(2)
                with col_1:
                    kode_baru = st.text_input("Kode Akun (6 Digit)")
                with col_2:
                    nama_baru = st.text_input("Nama Account")
                
                kat_otomatis, subkat_otomatis, subacc_otomatis = "", "", ""
                if kode_baru and len(kode_baru) >= 1:
                    prefix = kode_baru[0]
                    if prefix == '1': kat_otomatis = "100000 - Aset Lancar"
                    elif prefix == '2': kat_otomatis = "200000 - Kewajiban"
                    elif prefix == '3': kat_otomatis = "300000 - Ekuitas"
                    elif prefix == '4': kat_otomatis = "400000 - Pendapatan"
                    elif prefix == '5':
                        kat_otomatis = "500000 BIAYA PROYEK"
                        if len(kode_baru) >= 3:
                            sub_p = kode_baru[1:3]
                            if sub_p == "11": subkat_otomatis = "510000 - PROYEK SEWA ALAT"
                            elif sub_p == "21" or sub_p == "22": subkat_otomatis = "520000 - DRILLING / SERVICES"
                            else: subkat_otomatis = f"5{sub_p}000 - PROYEK UMUM"
                        if len(kode_baru) >= 4:
                            subacc_p = kode_baru[:4] + "00"
                            if kode_baru[3] == '1': subacc_otomatis = f"{subacc_p} - UPAH LANGSUNG"
                            elif kode_baru[3] == '2': subacc_otomatis = f"{subacc_p} - TUNJANGAN-TUNJANGAN"
                            else: subacc_otomatis = f"{subacc_p} - SUPPLIES"

                col_3, col_4, col_5 = st.columns(3)
                with col_3: kat_baru = st.text_input("Kategori (Otomatis)", value=kat_otomatis)
                with col_4: subkat_baru = st.text_input("Sub Kategori (Otomatis)", value=subkat_otomatis)
                with col_5: subacc_baru = st.text_input("Sub Account (Otomatis)", value=subacc_otomatis)
                
                btn_save = st.form_submit_button("💾 Save (Simpan Akun)")
                if btn_save and kode_baru and nama_baru:
                    if kode_baru in st.session_state.master_coa['Kode Akun'].values:
                        st.error(f"Kode Akun {kode_baru} sudah ada!")
                    else:
                        df_b = pd.DataFrame([{
                            "Kode Akun": kode_baru, "Nama Akun": nama_baru.upper(), 
                            "Sub Account": subacc_baru, "Sub Kategori": subkat_baru, "Kategori": kat_baru
                        }])
                        st.session_state.master_coa = pd.concat([st.session_state.master_coa, df_b], ignore_index=True)
                        st.success(f"Akun {kode_baru} berhasil disimpan!")
                        st.rerun()
        else:
            if not st.session_state.master_coa.empty:
                pilih_kode_edit = st.selectbox("Pilih Kode Akun untuk Dipanggil Ulang", st.session_state.master_coa['Kode Akun'].tolist())
                if pilih_kode_edit:
                    data_akun_pilih = st.session_state.master_coa[st.session_state.master_coa['Kode Akun'] == pilih_kode_edit].iloc[0]
                    with st.form("form_edit_akun"):
                        ed_kat = st.text_input("Kategori", value=data_akun_pilih['Kategori'])
                        ed_subkat = st.text_input("Sub Kategori", value=data_akun_pilih['Sub Kategori'])
                        ed_subacc = st.text_input("Sub Account", value=data_akun_pilih['Sub Account'])
                        ed_nama = st.text_input("Nama Account", value=data_akun_pilih['Nama Akun'])
                        col_e1, col_e2 = st.columns(2)
                        with col_e1: btn_update = st.form_submit_button("🔄 Update Akun")
                        with col_e2: btn_delete = st.form_submit_button("🗑️ Delete Akun")
                        if btn_update:
                            st.session_state.master_coa.loc[st.session_state.master_coa['Kode Akun'] == pilih_kode_edit, ['Kategori', 'Sub Kategori', 'Sub Account', 'Nama Akun']] = [ed_kat, ed_subkat, ed_subacc, ed_nama.upper()]
                            st.success("Akun berhasil diperbarui!")
                            st.rerun()
                        if btn_delete:
                            st.session_state.master_coa = st.session_state.master_coa[st.session_state.master_coa['Kode Akun'] != pilih_kode_edit]
                            st.success("Akun berhasil dihapus!")
                            st.rerun()

    else:
        st.markdown("### 🏢 Daftar Business Unit / Proyek")
        st.dataframe(st.session_state.master_bu, use_container_width=True)
        with st.form("form_tambah_bu"):
            id_bu_baru = st.text_input("ID Business Unit (Cth: BU-05)")
            nama_bu_baru = st.text_input("Nama Business Unit (Cth: Proyek Slickline)")
            btn_save_bu = st.form_submit_button("💾 Save Business Unit")
            if btn_save_bu and id_bu_baru:
                df_bu_b = pd.DataFrame([{"ID BU": id_bu_baru, "Nama Business Unit": nama_bu_baru}])
                st.session_state.master_bu = pd.concat([st.session_state.master_bu, df_bu_b], ignore_index=True)
                st.success("Business Unit berhasil disimpan!")
                st.rerun()