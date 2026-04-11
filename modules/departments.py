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

    # ✅ THÔNG BÁO SAU KHI XÓA
    if "deleted_dep_success" in st.session_state and st.session_state.deleted_dep_success:
        name = st.session_state.get("deleted_dep_name", "")
        st.success(f"✅ Đã xóa phòng ban: {name}")
        st.session_state.deleted_dep_success = False

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

    # ================= THÊM =================
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

    # ================= UPDATE =================
    st.markdown("### ✏️ Cập nhật phòng ban")

    if df.empty:
        st.info("Không có dữ liệu để chỉnh sửa")
    else:
        dep_map = dict(zip(df["ten_phong"], df["id"]))

        selected_dep = st.selectbox("Chọn phòng ban", list(dep_map.keys()))
        dep_id = dep_map[selected_dep]

        selected = df[df["id"] == dep_id].iloc[0]

        new_name = st.text_input("Tên phòng ban mới", value=selected["ten_phong"])
        new_desc = st.text_area("Mô tả mới", value=selected["mo_ta"])

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

    # ================= DELETE =================
    if role == "admin":

        st.markdown("### 🗑 Xóa phòng ban")

        if df.empty:
            st.info("Không có phòng ban để xóa")
        else:

            # 👉 HIỂN THỊ ID - TÊN
            dep_options = df.apply(
                lambda x: f"{x['id']} - {x['ten_phong']}", axis=1
            ).tolist()

            selected = st.selectbox("Chọn phòng ban cần xóa", dep_options)

            dep_id = int(selected.split(" - ")[0])
            dep_name = selected.split(" - ")[1]

            # INIT STATE
            if "confirm_delete_dep" not in st.session_state:
                st.session_state.confirm_delete_dep = False

            if "deleted_dep_name" not in st.session_state:
                st.session_state.deleted_dep_name = ""

            # CLICK XÓA
            if st.button("Xóa phòng ban"):
                st.session_state.confirm_delete_dep = True

            # POPUP
            if st.session_state.confirm_delete_dep:

                st.warning(f"⚠️ Bạn có chắc chắn muốn xóa:\n\nID: {dep_id} - {dep_name} ?")

                col1, col2 = st.columns(2)

                # XÁC NHẬN
                with col1:
                    if st.button("✅ Xác nhận xóa"):
                        with engine.connect() as conn:
                            conn.execute(
                                departments_table.delete()
                                .where(departments_table.c.id == dep_id)
                            )
                            conn.commit()

                        st.session_state.confirm_delete_dep = False
                        st.session_state.deleted_dep_success = True
                        st.session_state.deleted_dep_name = f"{dep_id} - {dep_name}"

                        st.rerun()

                # HỦY
                with col2:
                    if st.button("❌ Hủy"):
                        st.session_state.confirm_delete_dep = False
                        st.info("Đã hủy thao tác xóa")
