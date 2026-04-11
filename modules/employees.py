import streamlit as st
import pandas as pd
import sqlalchemy as sa

from database import (
    engine,
    employees_table,
    users_table,
    get_employees,
    get_departments,
    get_positions
)


# ================= LOAD USERS =================
def load_users():
    with engine.connect() as conn:
        return pd.read_sql(sa.select(users_table), conn)


def show():

    # ================= PHÂN QUYỀN =================
    role = st.session_state.get("role")

    if role not in ["admin", "hr"]:
        st.error("🚫 Bạn không có quyền truy cập trang này!")
        st.stop()

    st.subheader("👨‍💼 Quản lý nhân viên")

    # ✅ THÔNG BÁO SAU KHI XÓA
    if "deleted_success" in st.session_state and st.session_state.deleted_success:
        st.success("✅ Đã xóa nhân viên")
        st.session_state.deleted_success = False

    df = get_employees()
    departments = get_departments()
    positions = get_positions()
    users = load_users()

    # ================= 🔎 SEARCH =================
    st.markdown("### 🔎 Tìm kiếm nhân viên")

    col1, col2, col3 = st.columns(3)

    name_filter = col1.text_input("Tên nhân viên")

    dep_options = ["Tất cả"]
    if not departments.empty:
        dep_options += departments["ten_phong"].tolist()

    dep_filter = col2.selectbox("Phòng ban", dep_options)

    pos_options = ["Tất cả"]
    if not positions.empty:
        pos_options += positions["ten_chuc_vu"].tolist()

    pos_filter = col3.selectbox("Chức vụ", pos_options)

    # ================= FILTER =================
    filtered_df = df.copy()

    if name_filter:
        filtered_df = filtered_df[
            filtered_df["ho_ten"].str.contains(name_filter, case=False, na=False)
        ]

    if dep_filter != "Tất cả":
        filtered_df = filtered_df[
            filtered_df["ten_phong"] == dep_filter
        ]

    if pos_filter != "Tất cả":
        filtered_df = filtered_df[
            filtered_df["ten_chuc_vu"] == pos_filter
        ]

    st.divider()

    # ================= TABLE =================
    st.markdown("### 📋 Danh sách nhân viên")

    if not filtered_df.empty:
        df_show = filtered_df.copy()
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
        st.success(f"Tìm thấy {len(filtered_df)} nhân viên")
    else:
        st.warning("Không tìm thấy nhân viên phù hợp")

    st.divider()

    # ================= ADD =================
    st.subheader("➕ Thêm nhân viên")

    with st.form("add_emp"):

        name = st.text_input("Họ tên")
        email = st.text_input("Email")
        phone = st.text_input("Điện thoại")

        if users.empty:
            st.warning("Chưa có tài khoản user!")
            return

        user_map = dict(zip(users["username"], users["id"]))
        selected_user = st.selectbox("Tài khoản (user)", list(user_map.keys()))

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

            if name.strip() == "":
                st.warning("Vui lòng nhập tên")
                return

            dep_id = int(
                departments[departments["ten_phong"] == dep]["id"].values[0]
            )

            pos_id = int(
                positions[positions["ten_chuc_vu"] == pos]["id"].values[0]
            )

            user_id = int(user_map[selected_user])

            existing = df[df["user_id"] == user_id]

            if not existing.empty:
                st.error("❌ User này đã được gán cho nhân viên khác!")
                return

            with engine.connect() as conn:
                conn.execute(
                    employees_table.insert().values(
                        ho_ten=name,
                        email=email,
                        dien_thoai=phone,
                        department_id=dep_id,
                        position_id=pos_id,
                        ngay_vao_lam=str(date),
                        user_id=user_id
                    )
                )
                conn.commit()

            get_employees.clear()
            st.success("✅ Đã thêm nhân viên")
            st.rerun()

    st.divider()

    # ================= UPDATE =================
    if not df.empty:

        st.subheader("✏️ Cập nhật nhân viên")

        emp_id = int(st.selectbox("Chọn nhân viên cần sửa", df["id"]))
        emp = df[df["id"] == emp_id].iloc[0]

        new_name = st.text_input("Họ tên", value=emp["ho_ten"])
        new_email = st.text_input("Email", value=emp["email"])
        new_phone = st.text_input("Điện thoại", value=emp["dien_thoai"])

        dep = st.selectbox("Phòng ban mới", departments["ten_phong"])
        pos = st.selectbox("Chức vụ mới", positions["ten_chuc_vu"])

        new_date = st.text_input("Ngày vào làm", value=emp["ngay_vao_lam"])

        if st.button("Cập nhật nhân viên"):

            dep_id = int(departments[departments["ten_phong"] == dep]["id"].values[0])
            pos_id = int(positions[positions["ten_chuc_vu"] == pos]["id"].values[0])

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
            st.success("✅ Cập nhật thành công")
            st.rerun()

    st.divider()

    # ================= DELETE =================
    if role == "admin" and not df.empty:

        st.subheader("🗑 Xóa nhân viên")

        emp_delete = int(st.selectbox("Chọn nhân viên cần xóa", df["id"]))
        emp_name = df[df["id"] == emp_delete]["ho_ten"].values[0]

        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False

        if st.button("Xóa nhân viên"):
            st.session_state.confirm_delete = True

        if st.session_state.confirm_delete:

            st.warning(f"⚠️ Bạn có chắc chắn muốn xóa: **{emp_name}** không?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Xác nhận xóa"):
                    with engine.connect() as conn:
                        conn.execute(
                            employees_table.delete()
                            .where(employees_table.c.id == emp_delete)
                        )
                        conn.commit()

                    get_employees.clear()
                    st.session_state.confirm_delete = False
                    st.session_state.deleted_success = True
                    st.rerun()

            with col2:
                if st.button("❌ Hủy"):
                    st.session_state.confirm_delete = False
                    st.info("Đã hủy thao tác xóa")
