import sqlalchemy as sa
import pandas as pd
import streamlit as st
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = sa.create_engine(DATABASE_URL)

metadata = sa.MetaData()

# ================= USERS =================

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String),
    sa.Column("password", sa.String),
    sa.Column("role", sa.String(20))  # ✅ THÊM ROLE
)

# ================= DEPARTMENTS =================

departments_table = sa.Table(
    "departments",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("ten_phong", sa.String),
    sa.Column("mo_ta", sa.String)
)

# ================= POSITIONS =================

positions_table = sa.Table(
    "positions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("ten_chuc_vu", sa.String),
    sa.Column("mo_ta", sa.String)
)

# ================= EMPLOYEES =================

employees_table = sa.Table(
    "employees",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("ho_ten", sa.String),
    sa.Column("email", sa.String),
    sa.Column("dien_thoai", sa.String),
    sa.Column("department_id", sa.Integer),
    sa.Column("position_id", sa.Integer),
    sa.Column("ngay_vao_lam", sa.String),
    sa.Column("user_id", sa.Integer)  # ✅ THÊM USER_ID
)

# ================= ATTENDANCE =================

attendance_table = sa.Table(
    "attendance",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("employee_id", sa.Integer),
    sa.Column("ngay", sa.String),
    sa.Column("check_in", sa.String),
    sa.Column("check_out", sa.String)
)

# ================= INIT DATABASE =================

def init_db():
    metadata.create_all(engine)

# ================= CACHE FUNCTIONS =================

@st.cache_data
def get_employees():

    query = """
    SELECT 
        e.id,
        e.ho_ten,
        e.email,
        e.dien_thoai,
        e.user_id,  -- ✅ THÊM CỘT NÀY
        d.ten_phong,
        p.ten_chuc_vu,
        e.ngay_vao_lam
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    LEFT JOIN positions p ON e.position_id = p.id
    ORDER BY e.id
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


@st.cache_data
def get_departments():
    with engine.connect() as conn:
        return pd.read_sql(sa.select(departments_table), conn)


@st.cache_data
def get_positions():
    with engine.connect() as conn:
        return pd.read_sql(sa.select(positions_table), conn)


@st.cache_data
def get_attendance():
    with engine.connect() as conn:
        return pd.read_sql(sa.select(attendance_table), conn)