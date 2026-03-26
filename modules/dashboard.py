import streamlit as st
import pandas as pd
import sqlalchemy as sa

from database import (
    engine,
    employees_table,
    departments_table,
    positions_table,
    attendance_table
)

def show():

    st.subheader("📊 Dashboard nhân sự")

    with engine.connect() as conn:

        employees = pd.read_sql(sa.select(employees_table), conn)
        departments = pd.read_sql(sa.select(departments_table), conn)
        positions = pd.read_sql(sa.select(positions_table), conn)
        attendance = pd.read_sql(sa.select(attendance_table), conn)

    # ================= KPI =================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👨‍💼 Nhân viên", len(employees))
    col2.metric("🏢 Phòng ban", len(departments))
    col3.metric("📌 Chức vụ", len(positions))
    col4.metric("🕒 Chấm công", len(attendance))

    st.divider()

    # ================= EMPLOYEE TABLE =================

    st.subheader("👨‍💼 Nhân viên mới")

    if not employees.empty:

        df = employees.merge(
            departments[["id", "ten_phong"]],
            left_on="department_id",
            right_on="id",
            how="left"
        )

        df = df.merge(
            positions[["id", "ten_chuc_vu"]],
            left_on="position_id",
            right_on="id",
            how="left"
        )

        df_show = df.rename(columns={
            "ho_ten": "Họ tên",
            "email": "Email",
            "dien_thoai": "Điện thoại",
            "ten_phong": "Phòng ban",
            "ten_chuc_vu": "Chức vụ",
            "ngay_vao_lam": "Ngày vào làm"
        })

        df_show = df_show[
            ["id", "Họ tên", "Email", "Điện thoại", "Phòng ban", "Chức vụ", "Ngày vào làm"]
        ]

        st.dataframe(df_show.tail(5), use_container_width=True)

    else:

        st.info("Chưa có nhân viên")

    st.divider()

    # ================= CHART =================

    st.subheader("📈 Nhân viên theo phòng ban")

    if not employees.empty and not departments.empty:

        df_chart = employees.merge(
            departments,
            left_on="department_id",
            right_on="id",
            how="left"
        )

        chart = df_chart["ten_phong"].value_counts()

        st.bar_chart(chart)

    else:

        st.info("Chưa đủ dữ liệu")