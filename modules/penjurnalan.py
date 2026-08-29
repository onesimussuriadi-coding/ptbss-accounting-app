import streamlit as st
import pandas as pd
from datetime import datetime

def render_modul_2():
    st.subheader("Modul 2: Proses Penjurnalan Akuntansi")
    df_op = st.session_state.data_operasional
    if not df_op.empty:
        st.dataframe(df_op, use_container_width=True)
    else:
        st.warning("Belum ada dokumen operasional untuk dijurnal.")