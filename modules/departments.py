import streamlit as st
import pandas as pd
import sqlalchemy as sa
from database import engine, departments_table


def load_departments():
    with engine.connect() as conn:
        query = sa.select(departments_table)
        df = pd.read_sql(query, conn)
    return df


def show():

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

    st.dataframe(df_show, use_container_width=True)
    

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

        dep_id = st.selectbox("Chọn phòng ban", df["id"])

        selected = df[df["id"] == dep_id].iloc[0]

        new_name = st.text_input("Tên phòng ban mới", selected["ten_phong"])
        new_desc = st.text_area("Mô tả mới", selected["mo_ta"])

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

    st.markdown("### 🗑 Xóa phòng ban")

    if df.empty:
        st.info("Không có phòng ban để xóa")
    else:

        delete_id = st.selectbox("Chọn phòng ban cần xóa", df["id"])

        if st.button("Xóa phòng ban"):

            with engine.connect() as conn:

                conn.execute(
                    departments_table.delete()
                    .where(departments_table.c.id == delete_id)
                )

                conn.commit()

            st.success("Đã xóa phòng ban")
            st.rerun()