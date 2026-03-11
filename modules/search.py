import streamlit as st
import pandas as pd
import sqlalchemy as sa

from database import (
    engine,
    employees_table,
    departments_table,
    positions_table
)


# ================= LOAD DATA =================

def load_data():

    with engine.connect() as conn:

        query = sa.select(
            employees_table.c.id,
            employees_table.c.ho_ten,
            employees_table.c.email,
            employees_table.c.dien_thoai,
            departments_table.c.ten_phong,
            positions_table.c.ten_chuc_vu
        ).join(
            departments_table,
            employees_table.c.department_id == departments_table.c.id,
            isouter=True
        ).join(
            positions_table,
            employees_table.c.position_id == positions_table.c.id,
            isouter=True
        )

        df = pd.read_sql(query, conn)

    return df


# ================= PAGE =================

def show():

    st.subheader("🔎 Tìm kiếm nhân viên")

    df = load_data()

    if df.empty:

        st.info("Chưa có dữ liệu nhân viên")
        return

    # ================= FILTER =================

    col1, col2, col3 = st.columns(3)

    name_filter = col1.text_input("Tên nhân viên")

    departments = ["Tất cả"] + sorted(df["ten_phong"].dropna().unique())
    dep_filter = col2.selectbox("Phòng ban", departments)

    positions = ["Tất cả"] + sorted(df["ten_chuc_vu"].dropna().unique())
    pos_filter = col3.selectbox("Chức vụ", positions)

    # ================= SEARCH LOGIC =================

    filtered = df.copy()

    if name_filter:

        filtered = filtered[
            filtered["ho_ten"].str.contains(name_filter, case=False, na=False)
        ]

    if dep_filter != "Tất cả":

        filtered = filtered[
            filtered["ten_phong"] == dep_filter
        ]

    if pos_filter != "Tất cả":

        filtered = filtered[
            filtered["ten_chuc_vu"] == pos_filter
        ]

    st.divider()

    # ================= RESULT =================

    st.markdown("### 📋 Kết quả tìm kiếm")

    if filtered.empty:

        st.warning("Không tìm thấy nhân viên phù hợp")

    else:

        df_show = filtered.rename(columns={
            "id": "ID",
            "ho_ten": "Họ tên",
            "email": "Email",
            "dien_thoai": "Điện thoại",
            "ten_phong": "Phòng ban",
            "ten_chuc_vu": "Chức vụ"
        })

        st.dataframe(df_show, use_container_width=True)

        st.success(f"Tìm thấy {len(filtered)} nhân viên")