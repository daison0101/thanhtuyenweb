import streamlit as st
import pandas as pd
import sqlalchemy as sa
from database import engine, positions_table


# ================= LOAD DATA =================

def load_positions():
    with engine.connect() as conn:
        query = sa.select(positions_table)
        df = pd.read_sql(query, conn)
    return df


# ================= MAIN PAGE =================

def show():

    # ================= PHÂN QUYỀN =================
    role = st.session_state.get("role")

    if role not in ["admin", "hr"]:
        st.error("🚫 Bạn không có quyền truy cập trang này!")
        st.stop()

    st.subheader("📌 Quản lý chức vụ")

    df = load_positions()

    # ================= DANH SÁCH =================

    st.markdown("### 📋 Danh sách chức vụ")

    if df.empty:
        st.info("Chưa có chức vụ nào")
    else:

        df_show = df.rename(columns={
            "id": "ID",
            "ten_chuc_vu": "Tên chức vụ",
            "mo_ta": "Mô tả"
        })

        st.dataframe(df_show, use_container_width=True)

    st.divider()

    # ================= THÊM CHỨC VỤ =================

    st.markdown("### ➕ Thêm chức vụ")

    with st.form("add_position"):

        name = st.text_input("Tên chức vụ")
        desc = st.text_area("Mô tả")

        submit = st.form_submit_button("Thêm chức vụ")

        if submit:

            if name.strip() == "":
                st.warning("Vui lòng nhập tên chức vụ")
                return

            with engine.connect() as conn:

                conn.execute(
                    positions_table.insert().values(
                        ten_chuc_vu=name,
                        mo_ta=desc
                    )
                )

                conn.commit()

            st.success("Thêm chức vụ thành công")
            st.rerun()

    st.divider()

    # ================= CẬP NHẬT CHỨC VỤ =================

    st.markdown("### ✏️ Cập nhật chức vụ")

    if df.empty:
        st.info("Không có dữ liệu để chỉnh sửa")

    else:

        pos_id = st.selectbox(
            "Chọn chức vụ",
            df["id"],
            format_func=lambda x: df[df["id"] == x]["ten_chuc_vu"].values[0]
        )

        selected = df[df["id"] == pos_id].iloc[0]

        new_name = st.text_input("Tên chức vụ mới", selected["ten_chuc_vu"])
        new_desc = st.text_area("Mô tả mới", selected["mo_ta"])

        if st.button("Cập nhật chức vụ"):

            if new_name.strip() == "":
                st.warning("Tên chức vụ không được để trống")
                return

            with engine.connect() as conn:

                conn.execute(
                    positions_table.update()
                    .where(positions_table.c.id == pos_id)
                    .values(
                        ten_chuc_vu=new_name,
                        mo_ta=new_desc
                    )
                )

                conn.commit()

            st.success("Cập nhật thành công")
            st.rerun()

    st.divider()

    # ================= XÓA CHỨC VỤ =================

    # ❌ CHỈ ADMIN MỚI ĐƯỢC XÓA
    if role == "admin":

        st.markdown("### 🗑 Xóa chức vụ")

        if df.empty:
            st.info("Không có chức vụ để xóa")

        else:

            delete_id = st.selectbox(
                "Chọn chức vụ cần xóa",
                df["id"],
                format_func=lambda x: df[df["id"] == x]["ten_chuc_vu"].values[0]
            )

            if st.button("Xóa chức vụ"):

                with engine.connect() as conn:

                    conn.execute(
                        positions_table.delete()
                        .where(positions_table.c.id == delete_id)
                    )

                    conn.commit()

                st.success("Đã xóa chức vụ")
                st.rerun()