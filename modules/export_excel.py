import streamlit as st
import pandas as pd
import sqlalchemy as sa
import io

from database import engine, employees_table


def show():

    st.subheader("📥 Xuất dữ liệu Excel")

    with engine.connect() as conn:
        df = pd.read_sql(sa.select(employees_table), conn)

    st.dataframe(df)

    # ===== EXPORT EXCEL =====

    if st.button("Xuất Excel"):

        buffer = io.BytesIO()

        df.to_excel(buffer, index=False)

        st.download_button(
            label="📥 Download Excel",
            data=buffer.getvalue(),
            file_name="employees.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )