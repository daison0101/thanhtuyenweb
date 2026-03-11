import streamlit as st
import os
from google.genai import Client

# ================= INIT =================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Thiếu GEMINI_API_KEY trong .env")
    st.stop()

client = Client(api_key=api_key)


# ================= MAIN =================

def show():

    st.subheader("🤖 AI Chatbot HR")
    st.caption("Hỏi AI về nhân sự, tuyển dụng, luật lao động...")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ================= HIỂN THỊ CHAT =================

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Nhập câu hỏi...")

    if prompt:

        # hiển thị user
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # ================= AI =================

        with st.chat_message("assistant"):

            with st.spinner("AI đang suy nghĩ..."):

                try:

                    # tạo context từ lịch sử chat
                    history = ""

                    for m in st.session_state.messages:
                        history += f"{m['role']}: {m['content']}\n"

                    response = client.models.generate_content(
                        model="models/gemini-3-flash-preview",
                        contents=f"""
Bạn là trợ lý AI quản lý nhân sự cho một website HR.

Nhiệm vụ:
- Trả lời về quản lý nhân viên
- Tuyển dụng
- Luật lao động
- Quản trị nhân sự

Luôn trả lời bằng tiếng Việt.
Trả lời ngắn gọn, rõ ràng.

Lịch sử chat:
{history}

Câu hỏi mới:
{prompt}
"""
                    )

                    answer = response.text if response.text else "AI không có phản hồi."

                except Exception as e:

                    answer = f"❌ Lỗi AI: {e}"

                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    st.divider()

    if st.button("🗑 Xóa lịch sử chat"):
        st.session_state.messages = []
        st.rerun()