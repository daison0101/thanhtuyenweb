import streamlit as st
import pandas as pd
import sqlalchemy as sa
from database import engine, departments_table


# ================= LOAD DATA =================

def load_departments():
    with engine.connect() as conn:
        query = sa.select(departments_table)
        df = pd.read_sql(query, conn)
    return df


# ================= PAGE =================

def show():

    # ================= PHÂN QUYỀN =================
    role = st.session_state.get("role")

    if role not in ["admin", "hr"]:
        st.error("🚫 Bạn không có quyền truy cập trang này!")
        st.stop()

    st.subheader("🏢 Quản lý phòng ban")

    df = load_departments()

    # ================= HIỂN THỊ DANH SÁCH =================

    st.markdown("### 📋 Danh sách phòng ban")

    if df.empty:
        st.info("Chưa có phòng ban nào")

    else:

        df_show = df.rename(columns={
            "id": "ID",
            "ten_phong": "Tên phòng ban",
            "mo_ta": "Mô tả"
        })

        st.dataframe(
            df_show,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ================= THÊM PHÒNG BAN =================

    st.markdown("### ➕ Thêm phòng ban")

    with st.form("add_department"):

        name = st.text_input("Tên phòng ban")
        desc = st.text_area("Mô tả")

        submit = st.form_submit_button("Thêm phòng ban")

        if submit:

            if name.strip() == "":
                st.warning("Vui lòng nhập tên phòng ban")
                return

            with engine.connect() as conn:

                conn.execute(
                    departments_table.insert().values(
                        ten_phong=name,
                        mo_ta=desc
                    )
                )

                conn.commit()

            st.success("Thêm phòng ban thành công")
            st.rerun()

    st.divider()

    # ================= CẬP NHẬT PHÒNG BAN =================

    st.markdown("### ✏️ Cập nhật phòng ban")

    if df.empty:

        st.info("Không có dữ liệu để chỉnh sửa")

    else:

        dep_map = dict(zip(df["ten_phong"], df["id"]))

        selected_dep = st.selectbox(
            "Chọn phòng ban",
            list(dep_map.keys())
        )

        dep_id = dep_map[selected_dep]

        selected = df[df["id"] == dep_id].iloc[0]

        new_name = st.text_input(
            "Tên phòng ban mới",
            value=selected["ten_phong"]
        )

        new_desc = st.text_area(
            "Mô tả mới",
            value=selected["mo_ta"]
        )

        if st.button("Cập nhật phòng ban"):

            if new_name.strip() == "":
                st.warning("Tên phòng ban không được để trống")
                return

            with engine.connect() as conn:

                conn.execute(
                    departments_table.update()
                    .where(departments_table.c.id == dep_id)
                    .values(
                        ten_phong=new_name,
                        mo_ta=new_desc
                    )
                )

                conn.commit()

            st.success("Cập nhật thành công")
            st.rerun()

    st.divider()

    # ================= XÓA PHÒNG BAN =================

    # ❌ CHỈ ADMIN MỚI ĐƯỢC XÓA
    if role == "admin":

        st.markdown("### 🗑 Xóa phòng ban")

        if df.empty:
            st.info("Không có phòng ban để xóa")

        else:

            dep_map = dict(zip(df["ten_phong"], df["id"]))

            delete_dep = st.selectbox(
                "Chọn phòng ban cần xóa",
                list(dep_map.keys())
            )

            delete_id = dep_map[delete_dep]

            if st.button("Xóa phòng ban"):

                with engine.connect() as conn:

                    conn.execute(
                        departments_table.delete()
                        .where(departments_table.c.id == delete_id)
                    )

                    conn.commit()

                st.success("Đã xóa phòng ban")
                st.rerun()