"""
BOOKINSIGHT CHATBOT - STREAMLIT APP
Ứng dụng chat tìm kiếm sách sử dụng RAG-Fusion, Text-to-SQL và Memory
"""

import streamlit as st 
import requests        
import json            
import time           
from pathlib import Path
import re

st.set_page_config(
    page_title="BookInsight Chatbot",  
    page_icon="📚",                    
    layout="centered", # 'centered' = hẹp ở giữa, 'wide' = rộng toàn màn hình
)


st.markdown(
    """
<!-- Load font Inter từ Google Fonts-->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* ===== BIẾN MÀU SẮC CHỦ ĐẠO =====
       Thay đổi các giá trị này để đổi theme màu của app
       Format: #RRGGBB hoặc rgb(r, g, b) hoặc rgba(r, g, b, alpha)
    */
    :root {
    --bg: #E0FFFF;              
    --paper: #FFF9F1;           
    --ink: #3a3a3a;             
    --muted: #8b7355;          
    --accent: #c8b99c;         
    --accent-light: #d4c4a8;    
    --border: #e6d3a3;          
    --shadow-sm: rgba(139, 115, 85, 0.08);
    --shadow-md: rgba(139, 115, 85, 0.12);
    --shadow-lg: rgba(139, 115, 85, 0.16);
}
    
    [data-testid="stAppViewContainer"] {
        background: var(--bg);                    
        color: var(--ink);                        
        font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-weight: 400;                         
        line-height: 1.6;                        
    }
    
   
    [data-testid="stAppViewBlockContainer"] > div:first-child {
        max-width: 720px;                       
        margin: 32px auto;                      
        background: #4682B4;               
        border: 1px solid var(--border);          
        border-radius: 20px;                      
        box-shadow: 0 1px 3px var(--shadow-sm), 0 4px 12px var(--shadow-md);  
        overflow: hidden;                         
        padding: 0;                              
    }
    

    .chat-header {
        background: #4682B4;               
        border-bottom: 1px solid var(--border);   
        padding: 24px 28px;                       
        display: flex;                           
        align-items: center;                      
        justify-content: space-between;          
    }
    .chat-header .title {
        font-weight: 600;                        
        font-size: 20px;                          
        letter-spacing: -0.01em;                 
        color: #ffffff;                        
        margin: 0;                               
    }
    .chat-header .subtitle {
        font-size: 13px;                          
        color: #ffffff;                      
        font-weight: 400;                        
        margin-top: 4px;                          
    }
    .chat-header .status {
        background: #f0f9ff;                     
        color: var(--accent);                     
        padding: 6px 12px;                        
        border-radius: 20px;                      
        font-size: 12px;                          
        font-weight: 500;                         
    }
    
    [data-testid="stChatMessage"] {
        background: #f8f9fa;                      
        border: 1px solid #3A7080;               
        border-radius: 16px;                      
        padding: 20px 28px;                        
        box-shadow: none;                         
        margin: 0;                                
    }
    

    [data-testid="stChatMessage"] div[data-testid="stChatMessageContentUser"] {
        background: #4682B4;                
        color: var(--ink);                       
        border: 1px solid var(--border);           
        border-radius: 16px;                      
        padding: 14px 18px;                       
        margin: 8px 0;                            
        box-shadow: 0 1px 2px var(--shadow-sm);  
    }
    
    [data-testid="stChatMessage"] div[data-testid="stChatMessageContent"] {
        color: var(--ink);                        
        padding: 0;                               
    }
    /* Giới hạn kích thước ảnh hiển thị trong bong bóng chat */
    [data-testid="stChatMessage"] img {
        max-width: 180px;
        border-radius: 8px;
        margin: 6px 0;
    }
    

    [data-testid="stChatInput"] {
        background: #87CEEB;                
        border-top: 1px solid var(--border);      
        border-radius: 0;                          
        padding: 20px 28px;                       
        box-shadow: none;                         
    }

    [data-testid="stChatInput"] textarea {
        color: var(--ink) !important;             
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;               
        border: none !important; 
        border-radius: 12px !important;           
        padding: 12px 16px !important;            
        background: #fafafa !important;           
    }

    [data-testid="stChatInput"] textarea:focus,
    [data-testid="stChatInput"] textarea:focus-visible,
    [data-testid="stChatInput"] textarea:active {
        border: none !important;                  
        background: var(--paper) !important;      
        box-shadow: none !important;               
        outline: none !important;                 
    }

    [data-testid="stChatInput"] button {
        color: #A0A0A0 !important;                
    }
    [data-testid="stChatInput"] button:hover {
        color: #4682B4 !important;                
    }
    [data-testid="stChatInput"] button svg {
        fill: #A0A0A0 !important;                 
    }
    [data-testid="stChatInput"] button:hover svg {
        fill: #4682B4 !important;                 
    }
    

    .book-card {
        background: var(--paper);                
        border: 1px solid var(--border);         
        border-radius: 16px;                     
        padding: 20px;                            
        margin-bottom: 16px;                      
        box-shadow: 0 1px 3px var(--shadow-sm);  
        transition: box-shadow 0.2s ease;         
    }

    .book-card:hover {
        box-shadow: 0 4px 12px var(--shadow-md);  
    }

    .book-card h3, .book-card h2, .book-card h4 {
        color: var(--ink);                        
        font-weight: 600;                         
        margin-top: 0;                            
        margin-bottom: 12px;                    
        font-size: 18px;                         
        letter-spacing: -0.01em;                 
    }

    .book-card p {
        color: var(--muted);                      
        font-size: 14px;                         
        margin: 4px 0;                            
    }

    .book-card strong {
        color: var(--ink);                        
        font-weight: 600;                        
    }
    
    [data-testid="stImage"] img {
        border-radius: 12px;                     
        border: 1px solid var(--border);          
        box-shadow: 0 2px 8px var(--shadow-sm);  
    }
    

    [data-testid="stDivider"] hr {
        border: none;                             
        height: 1px;                             
        background: var(--border);                 
        margin: 24px 0;                           
    }
    
 
    [data-testid="stCaptionContainer"] p {
        color: var(--muted);                      
        font-size: 12px;                         
    }
    
    [data-testid="stHeading"] h1,
    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3 {
        color: var(--ink);                        
        font-weight: 600;                        
        letter-spacing: -0.02em;                
    }
    

    ::-webkit-scrollbar {
        height: 8px;                              
    }
    ::-webkit-scrollbar-thumb {
        background: #d1d5db;                      
        border-radius: 4px;                       
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;                     
    }
    ::-webkit-scrollbar-track {
        background: transparent;                 
    }
    
    .main .block-container {
        padding-top: 0;                          
        padding-bottom: 0;                       
    }
    
    .stMarkdown {
        margin-bottom: 0;                         
    }
</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="chat-header">
  <div>
    <div class="title">BookInsight</div>
    <div class="subtitle">RAG‑Fusion · Text‑to‑SQL · Memory</div>
  </div>
  <div class="status">Online</div>
</div>
""",
    unsafe_allow_html=True,  
)


def render_text_with_inline_images(text: str) -> None:
    text = re.sub(
        r"(?<!\!)\[([^\]]*)\]\((https?://[^)]+\.(?:png|jpe?g|gif|webp)(?:\?[^\)]*)?)\)",
        r"![\1](\2)",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"(?<!\()(?P<url>https?://[^\s)']+\.(?:png|jpe?g|gif|webp)(?:\?[^\s)']*)?)",
        r"![Image](\g<url>)",
        text,
        flags=re.IGNORECASE,
    )
    # 3) Render markdown (ảnh sẽ theo CSS ở trên để giới hạn kích thước)
    st.markdown(text)

API_URL = "http://127.0.0.1:8000/chat"


if "messages" not in st.session_state:
    st.session_state.messages = []  
    
    st.session_state.messages.append({
        "role": "assistant",  # "assistant" = bot, "user" = người dùng
        "content": "Hello! I'm BookInsight. What would you like to explore about books today?"
    })

for message in st.session_state.messages:
    avatar_path = "assets/user_avatar.jpg" if message["role"] == "user" else "assets/assistant_avatar.jpg"
    fallback_emoji = "👤" if message["role"] == "user" else "🤖"
    resolved_avatar = avatar_path if Path(avatar_path).exists() else fallback_emoji
    with st.chat_message(message["role"], avatar=resolved_avatar):
    
        try:
            books = json.loads(message["content"])
            if isinstance(books, list) and all(isinstance(b, dict) for b in books):
                st.markdown("**Đây là các gợi ý tôi tìm thấy cho bạn:**")
                for book in books:
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if book.get("main_images"):
                            st.image(book.get("main_images"), caption=book.get("title"), width=180)
                        else:
                            st.image("https://placehold.co/150x220/262730/FAFAFA?text=No+Image", caption=book.get("title"), width=180)
                    
                    with col2:
                        st.markdown('<div class="book-card">', unsafe_allow_html=True)
                        st.subheader(book.get("title", "Không có tiêu đề"))
                        st.markdown(f"**Tác giả:** {book.get('author_name', 'Unknown')}")
                        st.markdown(f"**Giá:** ${book.get('price', 0.0):.2f}")
                        st.markdown(f"**Rating:** {book.get('average_rating', 0)} ({book.get('rating_number', 0)} reviews)")
                        if "rrf_score" in book:
                            st.caption(f"Độ liên quan (RRF Score): {book.get('rrf_score', 0):.4f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.divider() 
            else:
                render_text_with_inline_images(message["content"])
        except (json.JSONDecodeError, TypeError):
            render_text_with_inline_images(message["content"])


def call_agent_api(user_question):
    try:
        payload = {"user_id": "streamlit_user", "question": user_question}
        response = requests.post(API_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            return response.json()["answer"]
        else:
            return f"Lỗi từ API: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Lỗi kết nối đến Backend: {e}\n(Hãy đảm bảo server FastAPI đang chạy!)"

if prompt := st.chat_input("Ask me anything about books..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    user_avatar_path = "assets/user_avatar.jpg"
    user_avatar = user_avatar_path if Path(user_avatar_path).exists() else "👤"
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)

    assistant_avatar_path = "assets/assistant_avatar.jpg"
    assistant_avatar = assistant_avatar_path if Path(assistant_avatar_path).exists() else "🤖"
    with st.chat_message("assistant", avatar=assistant_avatar):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        full_response = call_agent_api(prompt)
        try:
            books = json.loads(full_response)
            
            if isinstance(books, list) and all(isinstance(b, dict) for b in books):
                message_placeholder.empty() 
                st.markdown("**Đây là các gợi ý tôi tìm thấy cho bạn:**")
                
                for book in books:
                    col1, col2 = st.columns([1, 3]) # Chia cột 1:3
                    
                    with col1: 
                        if book.get("main_images"):
                            st.image(book.get("main_images"), caption=book.get("title"), width=180)
                        else:
                            st.image("https://placehold.co/150x220/262730/FAFAFA?text=No+Image", caption=book.get("title"), width=180)
                    
                    with col2: 
                        st.markdown('<div class="book-card">', unsafe_allow_html=True)
                        st.subheader(book.get("title", "Không có tiêu đề"))
                        st.markdown(f"**Tác giả:** {book.get('author_name', 'Unknown')}")
                        st.markdown(f"**Giá:** ${book.get('price', 0.0):.2f}")
                        st.markdown(f"**Rating:** {book.get('average_rating', 0)} ({book.get('rating_number', 0)} reviews)")
                        if "rrf_score" in book:
                            st.caption(f"Độ liên quan (RRF Score): {book.get('rrf_score', 0):.4f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.divider() 
            else:
                message_placeholder.empty()
                render_text_with_inline_images(full_response)
                
        except (json.JSONDecodeError, TypeError):
            message_placeholder.empty()
            render_text_with_inline_images(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

