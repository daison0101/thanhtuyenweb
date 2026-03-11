import streamlit as st
import pandas as pd
import sqlalchemy as sa
from datetime import date
from database import engine, attendance_table, employees_table


# ================= LOAD DATA =================

def load_attendance():

    with engine.connect() as conn:

        query = sa.select(
            attendance_table.c.id,
            employees_table.c.ho_ten,
            attendance_table.c.ngay,
            attendance_table.c.check_in,
            attendance_table.c.check_out
        ).join(
            employees_table,
            attendance_table.c.employee_id == employees_table.c.id
        )

        df = pd.read_sql(query, conn)

    return df


def load_employees():

    with engine.connect() as conn:

        query = sa.select(employees_table)

        df = pd.read_sql(query, conn)

    return df


# ================= MAIN =================

def show():

    st.subheader("🕒 Chấm công nhân viên")

    df = load_attendance()
    employees = load_employees()

    # ================= BẢNG =================

    st.markdown("### 📋 Bảng chấm công")

    if df.empty:

        st.info("Chưa có dữ liệu chấm công")

    else:

        df_show = df.rename(columns={
            "id": "ID",
            "ho_ten": "Nhân viên",
            "ngay": "Ngày",
            "check_in": "Check In",
            "check_out": "Check Out"
        })

        st.dataframe(df_show, use_container_width=True)

    st.divider()

    # ================= THÊM =================

    st.markdown("### ➕ Thêm chấm công")

    if employees.empty:

        st.warning("Chưa có nhân viên")

    else:

        with st.form("add_attendance"):

            emp_name = st.selectbox(
                "Nhân viên",
                employees["ho_ten"]
            )

            work_date = st.date_input(
                "Ngày",
                date.today()
            )

            check_in = st.time_input("Check In")
            check_out = st.time_input("Check Out")

            submit = st.form_submit_button("Lưu chấm công")

            if submit:

                emp_id = employees[
                    employees["ho_ten"] == emp_name
                ]["id"].values[0]

                with engine.connect() as conn:

                    conn.execute(
                        attendance_table.insert().values(
                            employee_id=int(emp_id),
                            ngay=str(work_date),
                            check_in=str(check_in),
                            check_out=str(check_out)
                        )
                    )

                    conn.commit()

                st.success("Chấm công thành công")

                st.rerun()

    st.divider()

    # ================= UPDATE =================

    st.markdown("### ✏️ Cập nhật chấm công")

    if not df.empty:

        att_id = st.selectbox(
            "Chọn bản ghi",
            df["id"],
            format_func=lambda x: f"{x} - {df[df['id']==x]['ho_ten'].values[0]}"
        )

        selected = df[df["id"] == att_id].iloc[0]

        new_checkin = st.text_input(
            "Check In",
            selected["check_in"]
        )

        new_checkout = st.text_input(
            "Check Out",
            selected["check_out"]
        )

        if st.button("Cập nhật"):

            with engine.connect() as conn:

                conn.execute(
                    attendance_table.update()
                    .where(attendance_table.c.id == att_id)
                    .values(
                        check_in=new_checkin,
                        check_out=new_checkout
                    )
                )

                conn.commit()

            st.success("Cập nhật thành công")

            st.rerun()

    st.divider()

    # ================= DELETE =================

    st.markdown("### 🗑 Xóa chấm công")

    if not df.empty:

        delete_id = st.selectbox(
            "Chọn bản ghi cần xóa",
            df["id"],
            format_func=lambda x: f"{x} - {df[df['id']==x]['ho_ten'].values[0]}"
        )

        if st.button("Xóa chấm công"):

            with engine.connect() as conn:

                conn.execute(
                    attendance_table.delete()
                    .where(attendance_table.c.id == delete_id)
                )

                conn.commit()

            st.success("Đã xóa")

            st.rerun()