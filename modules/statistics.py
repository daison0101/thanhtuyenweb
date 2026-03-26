import streamlit as st
import pandas as pd
import sqlalchemy as sa
import plotly.express as px

from database import (
    engine,
    employees_table,
    departments_table,
    positions_table,
    attendance_table
)


# ================= LOAD DATA =================

def load_employees():
    with engine.connect() as conn:
        df = pd.read_sql(sa.select(employees_table), conn)
    return df


def load_departments():
    with engine.connect() as conn:
        df = pd.read_sql(sa.select(departments_table), conn)
    return df


def load_positions():
    with engine.connect() as conn:
        df = pd.read_sql(sa.select(positions_table), conn)
    return df


def load_attendance():
    with engine.connect() as conn:
        df = pd.read_sql(sa.select(attendance_table), conn)
    return df


# ================= MAIN =================

def show():

    st.subheader("📊 Thống kê nhân sự")

    employees = load_employees()
    departments = load_departments()
    positions = load_positions()
    attendance = load_attendance()

    # ================= KPI =================

    st.markdown("### 📌 Tổng quan")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👨‍💼 Nhân viên", len(employees))
    col2.metric("🏢 Phòng ban", len(departments))
    col3.metric("📌 Chức vụ", len(positions))
    col4.metric("🕒 Bản ghi chấm công", len(attendance))

    st.divider()

    # ================= NHÂN VIÊN THEO PHÒNG BAN =================

    st.markdown("### 📊 Nhân viên theo phòng ban")

    if not employees.empty and not departments.empty:

        df = employees.merge(
            departments,
            left_on="department_id",
            right_on="id",
            how="left"
        )

        df["ten_phong"] = df["ten_phong"].fillna("Chưa phân")

        chart_data = df.groupby("ten_phong").size().reset_index(name="Số nhân viên")

        fig = px.bar(
            chart_data,
            x="ten_phong",
            y="Số nhân viên",
            title="Số nhân viên theo phòng ban"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ================= NHÂN VIÊN THEO CHỨC VỤ =================

    st.markdown("### 📊 Nhân viên theo chức vụ")

    if not employees.empty and not positions.empty:

        df = employees.merge(
            positions,
            left_on="position_id",
            right_on="id",
            how="left"
        )

        df["ten_chuc_vu"] = df["ten_chuc_vu"].fillna("Chưa phân")

        chart_data = df.groupby("ten_chuc_vu").size().reset_index(name="Số nhân viên")

        fig = px.pie(
            chart_data,
            names="ten_chuc_vu",
            values="Số nhân viên",
            title="Tỷ lệ nhân viên theo chức vụ"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ================= THỐNG KÊ CHẤM CÔNG =================

    st.markdown("### 📊 Thống kê chấm công")

    if not attendance.empty:

        attendance["ngay"] = pd.to_datetime(attendance["ngay"])

        chart = attendance.groupby("ngay").size().reset_index(name="Số lần chấm công")

        fig = px.line(
            chart,
            x="ngay",
            y="Số lần chấm công",
            title="Số lần chấm công theo ngày"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ================= BẢNG NHÂN VIÊN =================

    st.markdown("### 📋 Dữ liệu nhân viên")

    if employees.empty:

        st.info("Chưa có dữ liệu nhân viên")

    else:

        df = employees.merge(
            departments,
            left_on="department_id",
            right_on="id",
            how="left"
        ).merge(
            positions,
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

        st.dataframe(df_show, use_container_width=True)