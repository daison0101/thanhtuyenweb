import streamlit as st
import pandas as pd
import sqlalchemy as sa

from database import (
    engine,
    employees_table,
    get_employees,
    get_departments,
    get_positions
)


def show():

    st.subheader("👨‍💼 Quản lý nhân viên")

    df = get_employees()
    departments = get_departments()
    positions = get_positions()

    # ================= HIỂN THỊ BẢNG =================

    if not df.empty:
        df_show = df.copy()
        df_show = df_show.rename(columns={
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

    else:
        st.info("Chưa có nhân viên")

    st.divider()

    # ================= THÊM NHÂN VIÊN =================

    st.subheader("➕ Thêm nhân viên")

    with st.form("add_emp"):

        name = st.text_input("Họ tên")
        email = st.text_input("Email")
        phone = st.text_input("Điện thoại")

        dep = st.selectbox(
            "Phòng ban",
            departments["ten_phong"] if not departments.empty else []
        )

        pos = st.selectbox(
            "Chức vụ",
            positions["ten_chuc_vu"] if not positions.empty else []
        )

        date = st.date_input("Ngày vào làm")

        submit = st.form_submit_button("Thêm nhân viên")

        if submit:

            if name == "":
                st.warning("Vui lòng nhập tên")
                return

            dep_id = int(
                departments[departments["ten_phong"] == dep]["id"].values[0]
            )

            pos_id = int(
                positions[positions["ten_chuc_vu"] == pos]["id"].values[0]
            )

            with engine.connect() as conn:

                conn.execute(
                    employees_table.insert().values(
                        ho_ten=name,
                        email=email,
                        dien_thoai=phone,
                        department_id=dep_id,
                        position_id=pos_id,
                        ngay_vao_lam=str(date)
                    )
                )

                conn.commit()

            get_employees.clear()

            st.success("Đã thêm nhân viên")

            st.rerun()

    st.divider()

    # ================= CẬP NHẬT NHÂN VIÊN =================

    if not df.empty:

        st.subheader("✏️ Cập nhật nhân viên")

        emp_id = st.selectbox("Chọn nhân viên cần sửa", df["id"])

        emp = df[df["id"] == emp_id].iloc[0]

        new_name = st.text_input("Họ tên", value=emp["ho_ten"])
        new_email = st.text_input("Email", value=emp["email"])
        new_phone = st.text_input("Điện thoại", value=emp["dien_thoai"])

        dep = st.selectbox("Phòng ban mới", departments["ten_phong"])
        pos = st.selectbox("Chức vụ mới", positions["ten_chuc_vu"])

        new_date = st.text_input("Ngày vào làm", value=emp["ngay_vao_lam"])

        if st.button("Cập nhật nhân viên"):

            dep_id = int(
                departments[departments["ten_phong"] == dep]["id"].values[0]
            )

            pos_id = int(
                positions[positions["ten_chuc_vu"] == pos]["id"].values[0]
            )

            with engine.connect() as conn:

                conn.execute(
                    employees_table.update()
                    .where(employees_table.c.id == emp_id)
                    .values(
                        ho_ten=new_name,
                        email=new_email,
                        dien_thoai=new_phone,
                        department_id=dep_id,
                        position_id=pos_id,
                        ngay_vao_lam=new_date
                    )
                )

                conn.commit()

            get_employees.clear()

            st.success("Cập nhật thành công")

            st.rerun()

    st.divider()

    # ================= XÓA NHÂN VIÊN =================

    if not df.empty:

        st.subheader("🗑 Xóa nhân viên")

        emp_delete = st.selectbox("Chọn nhân viên cần xóa", df["id"])

        if st.button("Xóa nhân viên"):

            with engine.connect() as conn:

                conn.execute(
                    employees_table.delete()
                    .where(employees_table.c.id == emp_delete)
                )

                conn.commit()

            get_employees.clear()

            st.success("Đã xóa nhân viên")

            st.rerun()