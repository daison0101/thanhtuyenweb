import streamlit as st
import pandas as pd
import sqlalchemy as sa
import os
from google.genai import Client

from database import (
    engine,
    employees_table,
    departments_table,
    attendance_table
)

# ================= API KEY =================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Thiếu GEMINI_API_KEY trong file .env")
    st.stop()

client = Client(api_key=api_key)

# ================= LOAD DATA =================

def load_data():

    with engine.connect() as conn:

        emp_query = sa.select(employees_table)
        dep_query = sa.select(departments_table)
        att_query = sa.select(attendance_table)

        employees = pd.read_sql(emp_query, conn)
        departments = pd.read_sql(dep_query, conn)
        attendance = pd.read_sql(att_query, conn)

    return employees, departments, attendance


# ================= PAGE =================

def show():

    st.subheader("🧠 AI Phân tích nhân sự")
    st.caption("AI phân tích dữ liệu nhân sự và đưa ra nhận xét")

    employees, departments, attendance = load_data()

    if employees.empty:
        st.warning("⚠ Chưa có dữ liệu nhân viên")
        return

    st.divider()

    # ================= BASIC STATS =================

    total_emp = len(employees)
    total_dep = len(departments)

    col1, col2 = st.columns(2)

    col1.metric("Tổng nhân viên", total_emp)
    col2.metric("Số phòng ban", total_dep)

    st.divider()

    # ================= JOIN PHÒNG BAN =================

    emp_dep = employees.merge(
        departments,
        left_on="department_id",
        right_on="id",
        how="left"
    )

    # ================= NHÂN VIÊN THEO PHÒNG =================

    dep_count = (
        emp_dep.groupby("ten_phong")
        .size()
        .reset_index(name="Số nhân viên")
        .sort_values(by="Số nhân viên", ascending=False)
    )

    st.markdown("### 📊 Nhân viên theo phòng ban")
    st.bar_chart(dep_count.set_index("ten_phong"))

    st.divider()

    # ================= JOIN CHẤM CÔNG + NHÂN VIÊN =================

    attendance_emp = attendance.merge(
        employees,
        left_on="employee_id",
        right_on="id",
        how="left"
    )

    # ================= THỐNG KÊ CHẤM CÔNG =================

    attendance_count = (
        attendance_emp.groupby("ho_ten")
        .size()
        .reset_index(name="Số ngày chấm công")
    )

    attendance_count = attendance_count.rename(columns={
        "ho_ten": "Nhân viên"
    })

    st.markdown("### 🕒 Thống kê chấm công")
    st.dataframe(attendance_count)

    st.divider()

    # ================= HIỂN THỊ NHÂN VIÊN =================

    employees_show = emp_dep.rename(columns={
        "id_x": "ID",
        "ho_ten": "Họ tên",
        "email": "Email",
        "dien_thoai": "Điện thoại",
        "ten_phong": "Phòng ban",
        "position_id": "Chức vụ",
        "ngay_vao_lam": "Ngày vào làm"
    })

    employees_show = employees_show[
        ["ID", "Họ tên", "Email", "Điện thoại", "Phòng ban", "Chức vụ", "Ngày vào làm"]
    ]

    # ================= HIỂN THỊ PHÒNG BAN =================

    departments_show = departments.rename(columns={
        "id": "ID",
        "ten_phong": "Tên phòng ban",
        "mo_ta": "Mô tả"
    })

    # ================= HIỂN THỊ CHẤM CÔNG =================

    attendance_show = attendance_emp.rename(columns={
        "id_x": "ID",
        "ho_ten": "Nhân viên",
        "ngay": "Ngày",
        "check_in": "Giờ vào",
        "check_out": "Giờ ra"
    })

    attendance_show = attendance_show[
        ["ID", "Nhân viên", "Ngày", "Giờ vào", "Giờ ra"]
    ]

    # ================= SHOW TABLE =================

    with st.expander("📋 Dữ liệu nhân viên"):
        st.dataframe(employees_show)

    with st.expander("🏢 Dữ liệu phòng ban"):
        st.dataframe(departments_show)

    with st.expander("🕒 Dữ liệu chấm công"):
        st.dataframe(attendance_show)

    st.divider()

    # ================= AI ANALYSIS =================

    if st.button("🤖 Phân tích dữ liệu bằng AI"):

        with st.spinner("AI đang phân tích dữ liệu..."):

            prompt = f"""
Bạn là chuyên gia quản trị nhân sự.

Dữ liệu công ty:

Tổng nhân viên: {total_emp}

Nhân viên theo phòng ban:
{dep_count.to_string(index=False)}

Thống kê chấm công:
{attendance_count.to_string(index=False)}

Hãy phân tích:

1. Tình hình nhân sự chung
2. Phòng ban đông nhân viên nhất
3. Nhận xét dữ liệu chấm công
4. Vấn đề tiềm ẩn
5. Đề xuất cải thiện quản lý nhân sự

Trả lời bằng tiếng Việt.
"""

            try:

                response = client.models.generate_content(
                    model="models/gemini-3-flash-preview",
                    contents=prompt
                )

                result = response.text

            except Exception as e:

                result = f"❌ Lỗi AI: {e}"

        st.divider()

        st.markdown("### 📊 Kết quả phân tích AI")
        st.markdown(result)