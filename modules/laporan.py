import streamlit as st
import pandas as pd

def render_modul_3():
    st.subheader("Modul 3: Output Laporan Keuangan Dinamis")
    df_jrn = st.session_state.data_jurnal
    if not df_jrn.empty:
        st.dataframe(df_jrn, use_container_width=True)
    else:
        st.info("Belum ada data jurnal untuk menampilkan laporan.")