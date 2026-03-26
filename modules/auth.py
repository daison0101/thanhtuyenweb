import streamlit as st
import sqlalchemy as sa
import bcrypt

from database import engine, users_table


def login_page():

    # ===== INIT SESSION =====
    if "login" not in st.session_state:
        st.session_state.login = False

    if "role" not in st.session_state:
        st.session_state.role = None

    if "username" not in st.session_state:
        st.session_state.username = None

    st.subheader("🔐 Đăng nhập hệ thống")

    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])

    # ================= LOGIN =================
    with tab1:

        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):

            with engine.connect() as conn:

                query = sa.select(users_table).where(
                    users_table.c.username == username
                )

                user = conn.execute(query).fetchone()

            if user:

                stored_password = user.password.encode()

                if bcrypt.checkpw(password.encode(), stored_password):

                    # ===== LƯU SESSION =====
                    st.session_state.user_id = user.id
                    st.session_state.login = True
                    st.session_state.username = user.username

                    # ⚠️ QUAN TRỌNG: lấy role từ DB
                    st.session_state.role = user.role if "role" in user._mapping else "user"

                    st.success(f"Đăng nhập thành công ({st.session_state.role})")
                    st.rerun()

                else:
                    st.error("Sai mật khẩu")

            else:
                st.error("Tài khoản không tồn tại")

    # ================= REGISTER =================
    with tab2:

        new_user = st.text_input("Tạo username", key="reg_user")
        new_pass = st.text_input("Tạo password", type="password", key="reg_pass")

        if st.button("Register", key="reg_btn"):

            if new_user == "" or new_pass == "":
                st.warning("Vui lòng nhập đầy đủ")
                return

            with engine.connect() as conn:

                # kiểm tra user tồn tại
                check_query = sa.select(users_table).where(
                    users_table.c.username == new_user
                )

                existing = conn.execute(check_query).fetchone()

                if existing:
                    st.error("Username đã tồn tại")
                    return

                # hash password
                hashed_password = bcrypt.hashpw(
                    new_pass.encode(),
                    bcrypt.gensalt()
                ).decode()

                # ===== MẶC ĐỊNH ROLE = user =====
                conn.execute(
                    users_table.insert().values(
                        username=new_user,
                        password=hashed_password,
                        role="user"   # 👈 thêm dòng này
                    )
                )

                conn.commit()

            st.success("Tạo tài khoản thành công")