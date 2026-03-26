import streamlit as st
import pdfplumber
import os
from google.genai import Client

# ================= API KEY =================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Thiếu GEMINI_API_KEY")
    st.stop()

client = Client(api_key=api_key)


# ================= READ PDF =================

def read_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            content = page.extract_text()

            if content:
                text += content + "\n"

    return text


# ================= PAGE =================

def show():

    st.subheader("📄 AI Sàng lọc CV")
    st.caption("Upload CV để AI đánh giá ứng viên")

    uploaded_file = st.file_uploader(
        "Upload CV (PDF)",
        type=["pdf"]
    )

    if uploaded_file:

        st.success("CV đã upload")
        st.write("Tên file:", uploaded_file.name)

        # đọc pdf
        with st.spinner("Đang đọc CV..."):

            cv_text = read_pdf(uploaded_file)

        # giới hạn token
        cv_text = cv_text[:12000]

        st.divider()

        with st.expander("📑 Nội dung CV"):

            st.code(cv_text[:5000])

        st.divider()

        if st.button("🤖 Phân tích CV bằng AI"):

            with st.spinner("AI đang phân tích..."):

                prompt = f"""
Bạn là chuyên gia tuyển dụng nhân sự (HR).

Phân tích CV sau:

{cv_text}

Hãy trả lời theo cấu trúc:

1. Tóm tắt ứng viên
2. Kỹ năng chính
3. Kinh nghiệm làm việc
4. Điểm mạnh
5. Điểm yếu
6. Mức độ phù hợp công việc (1-10)
7. Đề xuất tuyển dụng (Có / Không)

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

            st.markdown("### 📊 Kết quả phân tích")

            st.markdown(result)