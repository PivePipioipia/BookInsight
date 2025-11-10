"""
==========================================
BOOKINSIGHT CHATBOT - STREAMLIT APP
==========================================
Ứng dụng chat tìm kiếm sách sử dụng RAG-Fusion, Text-to-SQL và Memory
"""

# ========== 1. IMPORT THƯ VIỆN ==========
import streamlit as st  # Framework để tạo web app
import requests         # Để gọi API từ backend FastAPI
import json            # Để parse JSON response từ API
import time            # (Chưa dùng, có thể xóa nếu không cần)

# ========== 2. CẤU HÌNH TRANG WEB ==========
st.set_page_config(
    page_title="BookInsight Chatbot",  # Tiêu đề hiển thị trên tab trình duyệt
    page_icon="📚",                    # Icon hiển thị trên tab (có thể đổi emoji khác)
    layout="wide",                     # 'centered' = hẹp ở giữa, 'wide' = rộng toàn màn hình
)

# ========== 3. CSS TÙY CHỈNH - PHONG CÁCH MODERN MINIMALIST ==========
# Phần này định nghĩa toàn bộ style (màu sắc, font, spacing) cho ứng dụng
# Bạn có thể chỉnh sửa các biến CSS ở :root để thay đổi màu sắc chủ đạo

st.markdown(
    """
<!-- Load font Inter từ Google Fonts (font chữ hiện đại, dễ đọc) -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* ===== BIẾN MÀU SẮC CHỦ ĐẠO =====
       Thay đổi các giá trị này để đổi theme màu của app
       Format: #RRGGBB hoặc rgb(r, g, b) hoặc rgba(r, g, b, alpha)
    */
    :root {
    --bg: #E0FFFF;              /* Nền be nhạt */
    --paper: #FFF9F1;           /* Card trắng */
    --ink: #3a3a3a;             /* Chữ đen nhẹ */
    --muted: #8b7355;           /* Chữ phụ be đậm */
    --accent: #c8b99c;          /* Màu nhấn be trung bình */
    --accent-light: #d4c4a8;    /* Màu nhấn be nhạt */
    --border: #e6d3a3;          /* Viền be nhạt */
    --shadow-sm: rgba(139, 115, 85, 0.08);
    --shadow-md: rgba(139, 115, 85, 0.12);
    --shadow-lg: rgba(139, 115, 85, 0.16);
}
    
    /* ===== NỀN CHUNG CỦA ỨNG DỤNG ===== */
    [data-testid="stAppViewContainer"] {
        background: var(--bg);                    /* Dùng màu nền từ biến --bg */
        color: var(--ink);                        /* Màu chữ mặc định */
        font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-weight: 400;                         /* Độ đậm chữ: 300=nhẹ, 400=normal, 600=đậm, 700=rất đậm */
        line-height: 1.6;                         /* Khoảng cách giữa các dòng (1.6 = 160%) */
    }
    
    /* ===== KHUNG NỘI DUNG TRUNG TÂM (CARD CHÍNH) =====
       Đây là container chứa toàn bộ nội dung chat
       - max-width: giới hạn độ rộng tối đa (720px = ~70% màn hình)
       - margin: 32px auto = cách trên/dưới 32px, căn giữa trái/phải
       - border-radius: bo góc (20px = rất tròn)
       - box-shadow: tạo bóng đổ để card nổi lên
    */
    [data-testid="stAppViewBlockContainer"] > div:first-child {
        max-width: 720px;                        /* Độ rộng tối đa (có thể đổi: 600px, 800px, 1000px) */
        margin: 32px auto;                       /* Cách trên/dưới 32px, căn giữa */
        background: #4682B4;                /* Nền trắng */
        border: 1px solid var(--border);          /* Viền mỏng màu xám */
        border-radius: 20px;                      /* Bo góc (có thể đổi: 12px, 16px, 24px) */
        box-shadow: 0 1px 3px var(--shadow-sm), 0 4px 12px var(--shadow-md);  /* Bóng đổ 2 lớp */
        overflow: hidden;                         /* Ẩn phần tràn ra ngoài */
        padding: 0;                               /* Không padding (để header/content tự quản lý) */
    }
    
    /* ===== HEADER CHAT (PHẦN ĐẦU TRANG) =====
       Hiển thị tên app và trạng thái
    */
    .chat-header {
        background: #4682B4;                /* Nền trắng */
        border-bottom: 1px solid var(--border);   /* Đường kẻ dưới */
        padding: 24px 28px;                       /* Khoảng cách trong (trên/dưới: 24px, trái/phải: 28px) */
        display: flex;                            /* Dùng flexbox để căn chỉnh */
        align-items: center;                      /* Căn giữa theo chiều dọc */
        justify-content: space-between;           /* Căn 2 phần tử ra 2 đầu (trái/phải) */
    }
    .chat-header .title {
        font-weight: 600;                         /* Chữ đậm vừa */
        font-size: 20px;                          /* Kích thước chữ (có thể đổi: 18px, 22px, 24px) */
        letter-spacing: -0.01em;                 /* Khoảng cách chữ (âm = chữ sát nhau hơn) */
        color: #ffffff;                        /* Màu chữ đen */
        margin: 0;                                /* Bỏ margin mặc định */
    }
    .chat-header .subtitle {
        font-size: 13px;                          /* Chữ nhỏ hơn */
        color: #ffffff;                      /* Màu xám */
        font-weight: 400;                         /* Chữ bình thường */
        margin-top: 4px;                          /* Cách trên 4px */
    }
    .chat-header .status {
        background: #f0f9ff;                      /* Nền xanh nhạt */
        color: var(--accent);                     /* Chữ xanh đậm */
        padding: 6px 12px;                        /* Khoảng cách trong */
        border-radius: 20px;                      /* Bo góc tròn (pill shape) */
        font-size: 12px;                          /* Chữ nhỏ */
        font-weight: 500;                         /* Chữ đậm vừa */
    }
    
    /* ===== BONG BÓNG CHAT - ASSISTANT (BOT) =====
       Tin nhắn từ phía bot/assistant
    */
    [data-testid="stChatMessage"] {
        background: #f8f9fa;                      /* Nền xám rất nhạt */
        border: 1px solid #3A7080;                /* Viền xanh đậm */
        border-radius: 16px;                      /* Bo góc 16px */
        padding: 20px 28px;                        /* Khoảng cách trong */
        box-shadow: none;                         /* Không bóng đổ */
        margin: 0;                                /* Không margin */
    }
    
    /* ===== BONG BÓNG CHAT - USER (NGƯỜI DÙNG) =====
       Tin nhắn từ phía người dùng (hiển thị bên phải)
    */
    [data-testid="stChatMessage"] div[data-testid="stChatMessageContentUser"] {
        background: #4682B4;                /* Nền trắng */
        color: var(--ink);                        /* Chữ đen */
        border: 1px solid var(--border);           /* Viền xám nhạt */
        border-radius: 16px;                      /* Bo góc (có thể đổi: 12px, 20px) */
        padding: 14px 18px;                       /* Khoảng cách trong */
        margin: 8px 0;                            /* Cách trên/dưới 8px */
        box-shadow: 0 1px 2px var(--shadow-sm);   /* Bóng đổ nhẹ */
    }
    
    /* ===== NỘI DUNG ASSISTANT ===== */
    [data-testid="stChatMessage"] div[data-testid="stChatMessageContent"] {
        color: var(--ink);                        /* Màu chữ đen */
        padding: 0;                               /* Không padding */
    }
    
    /* ===== Ô NHẬP LIỆU CHAT (INPUT BOX) =====
       Ô textarea để người dùng nhập câu hỏi
    */
    [data-testid="stChatInput"] {
        background: #87CEEB;                /* Nền trắng */
        border-top: 1px solid var(--border);       /* Đường kẻ trên */
        border-radius: 0;                          /* Không bo góc */
        padding: 20px 28px;                       /* Khoảng cách trong */
        box-shadow: none;                         /* Không bóng đổ */
    }
    /* Style cho textarea bên trong */
    [data-testid="stChatInput"] textarea {
        color: var(--ink) !important;             /* Màu chữ (dùng !important để override) */
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;               /* Kích thước chữ (có thể đổi: 14px, 16px) */
        border: none !important;  /* Viền xám */
        border-radius: 12px !important;           /* Bo góc */
        padding: 12px 16px !important;            /* Khoảng cách trong */
        background: #fafafa !important;           /* Nền xám rất nhạt */
    }
    /* Style khi focus vào textarea (khi click vào) */
    [data-testid="stChatInput"] textarea:focus,
    [data-testid="stChatInput"] textarea:focus-visible,
    [data-testid="stChatInput"] textarea:active {
        border: none !important;                  /* Bỏ viền khi focus */
        background: var(--paper) !important;      /* Nền trắng khi focus */
        box-shadow: none !important;               /* Bỏ hiệu ứng glow */
        outline: none !important;                 /* Bỏ outline mặc định */
    }
    /* Style cho biểu tượng nút gửi (send button icon) */
    [data-testid="stChatInput"] button {
        color: #A0A0A0 !important;                /* Màu biểu tượng gửi (có thể đổi: #4682B4, #2563eb, #10b981) */
    }
    [data-testid="stChatInput"] button:hover {
        color: #4682B4 !important;                /* Màu khi hover (có thể đổi) */
    }
    [data-testid="stChatInput"] button svg {
        fill: #A0A0A0 !important;                 /* Màu fill của icon SVG */
    }
    [data-testid="stChatInput"] button:hover svg {
        fill: #4682B4 !important;                 /* Màu khi hover */
    }
    
    /* ===== THẺ SÁCH (BOOK CARD) =====
       Card hiển thị thông tin từng cuốn sách
       Class này được dùng trong Python code: st.markdown('<div class="book-card">')
    */
    .book-card {
        background: var(--paper);                /* Nền trắng */
        border: 1px solid var(--border);          /* Viền xám */
        border-radius: 16px;                     /* Bo góc */
        padding: 20px;                            /* Khoảng cách trong (có thể đổi: 16px, 24px) */
        margin-bottom: 16px;                      /* Cách dưới 16px (khoảng cách giữa các card) */
        box-shadow: 0 1px 3px var(--shadow-sm);   /* Bóng đổ nhẹ */
        transition: box-shadow 0.2s ease;         /* Hiệu ứng chuyển đổi mượt (0.2s) */
    }
    /* Hiệu ứng khi hover chuột vào card */
    .book-card:hover {
        box-shadow: 0 4px 12px var(--shadow-md);  /* Bóng đổ đậm hơn khi hover */
    }
    /* Style cho tiêu đề trong card (h2, h3, h4) */
    .book-card h3, .book-card h2, .book-card h4 {
        color: var(--ink);                        /* Màu chữ đen */
        font-weight: 600;                         /* Chữ đậm */
        margin-top: 0;                            /* Không cách trên */
        margin-bottom: 12px;                     /* Cách dưới 12px */
        font-size: 18px;                          /* Kích thước chữ (có thể đổi: 16px, 20px) */
        letter-spacing: -0.01em;                 /* Chữ sát nhau hơn */
    }
    /* Style cho đoạn văn trong card */
    .book-card p {
        color: var(--muted);                      /* Màu xám */
        font-size: 14px;                          /* Chữ nhỏ */
        margin: 4px 0;                            /* Cách trên/dưới 4px */
    }
    /* Style cho chữ in đậm (strong) trong card */
    .book-card strong {
        color: var(--ink);                        /* Màu đen */
        font-weight: 600;                         /* Chữ đậm */
    }
    
    /* ===== ẢNH BÌA SÁCH ===== */
    [data-testid="stImage"] img {
        border-radius: 12px;                      /* Bo góc (có thể đổi: 8px, 16px) */
        border: 1px solid var(--border);          /* Viền xám */
        box-shadow: 0 2px 8px var(--shadow-sm);   /* Bóng đổ nhẹ */
    }
    
    /* ===== ĐƯỜNG KẺ NGĂN CÁCH (DIVIDER) =====
       Dùng st.divider() trong Python để tạo đường kẻ
    */
    [data-testid="stDivider"] hr {
        border: none;                             /* Không viền */
        height: 1px;                              /* Độ dày 1px */
        background: var(--border);                 /* Màu xám */
        margin: 24px 0;                           /* Cách trên/dưới 24px */
    }
    
    /* ===== CAPTION (CHÚ THÍCH) =====
       Dùng st.caption() trong Python
    */
    [data-testid="stCaptionContainer"] p {
        color: var(--muted);                      /* Màu xám */
        font-size: 12px;                          /* Chữ rất nhỏ */
    }
    
    /* ===== HEADING (TIÊU ĐỀ) =====
       Dùng st.header(), st.subheader() trong Python
    */
    [data-testid="stHeading"] h1,
    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3 {
        color: var(--ink);                        /* Màu đen */
        font-weight: 600;                         /* Chữ đậm */
        letter-spacing: -0.02em;                 /* Chữ sát nhau */
    }
    
    /* ===== SCROLLBAR (THANH CUỘN) =====
       Tùy chỉnh thanh cuộn cho đẹp hơn
    */
    ::-webkit-scrollbar {
        width: 8px;                               /* Độ rộng thanh cuộn (có thể đổi: 6px, 10px) */
        height: 8px;                              /* Độ cao (cho scrollbar ngang) */
    }
    ::-webkit-scrollbar-thumb {
        background: #d1d5db;                      /* Màu thanh cuộn (xám) */
        border-radius: 4px;                       /* Bo góc */
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;                      /* Màu đậm hơn khi hover */
    }
    ::-webkit-scrollbar-track {
        background: transparent;                  /* Nền trong suốt */
    }
    
    /* ===== TỐI ƯU SPACING =====
       Loại bỏ padding/margin không cần thiết
    */
    .main .block-container {
        padding-top: 0;                           /* Bỏ padding trên */
        padding-bottom: 0;                        /* Bỏ padding dưới */
    }
    
    .stMarkdown {
        margin-bottom: 0;                         /* Bỏ margin dưới */
    }
</style>
""",
    unsafe_allow_html=True,
)

# ========== 4. HEADER GIAO DIỆN (PHẦN ĐẦU TRANG) ==========
# Hiển thị tên app, mô tả và trạng thái
# Bạn có thể thay đổi:
#   - "BookInsight" → tên app khác
#   - "RAG‑Fusion · Text‑to‑SQL · Memory" → mô tả khác
#   - "Online" → "Offline", "Đang hoạt động", v.v.
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
    unsafe_allow_html=True,  # Cho phép chạy HTML (cần thiết cho custom HTML)
)

# ========== 5. CẤU HÌNH API BACKEND ==========
# URL của FastAPI backend server
# Nếu backend chạy ở port khác hoặc domain khác, sửa ở đây
# Ví dụ:
#   - Local: "http://127.0.0.1:8000/chat"
#   - Production: "https://api.example.com/chat"
API_URL = "http://127.0.0.1:8000/chat"

# ========== 6. QUẢN LÝ TRÍ NHỚ (MEMORY/SESSION STATE) ==========
# Streamlit dùng session_state để lưu dữ liệu giữa các lần render
# "messages" là list chứa lịch sử chat: [{"role": "user/assistant", "content": "..."}, ...]
# 
# Kiểm tra nếu chưa có "messages" trong session_state (lần đầu load trang)
if "messages" not in st.session_state:
    st.session_state.messages = []  # Khởi tạo list rỗng
    
    # Thêm tin nhắn chào mừng từ assistant
    st.session_state.messages.append({
        "role": "assistant",  # "assistant" = bot, "user" = người dùng
        "content": "Xin chào! Tôi là BookInsight. Bạn muốn biết gì về sách hôm nay?"
    })
    # Bạn có thể thay đổi nội dung tin nhắn chào mừng ở đây

# --- 6. Hiển thị Lịch sử Chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # --- ⭐️ NÂNG CẤP HIỂN THỊ ⭐️ ---
        # Kiểm tra xem nội dung có phải là JSON list sách không
        try:
            # Cố gắng parse nội dung thành list
            books = json.loads(message["content"])
            if isinstance(books, list) and all(isinstance(b, dict) for b in books):
                # Nếu thành công, đây là list sách!
                st.markdown("**Đây là các gợi ý tôi tìm thấy cho bạn:**")
                for book in books:
                    # Dùng cột để hiển thị đẹp
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if book.get("main_images"):
                            st.image(book.get("main_images"), caption=book.get("title"), use_column_width=True)
                        else:
                            st.image("https://placehold.co/150x220/262730/FAFAFA?text=No+Image", caption=book.get("title"), use_column_width=True)
                    
                    with col2:
                        st.markdown('<div class="book-card">', unsafe_allow_html=True)
                        st.subheader(book.get("title", "Không có tiêu đề"))
                        st.markdown(f"**Tác giả:** {book.get('author_name', 'Unknown')}")
                        st.markdown(f"**Giá:** ${book.get('price', 0.0):.2f}")
                        st.markdown(f"**Rating:** {book.get('average_rating', 0)} ({book.get('rating_number', 0)} reviews)")
                        if "rrf_score" in book:
                            st.caption(f"Độ liên quan (RRF Score): {book.get('rrf_score', 0):.4f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.divider() # Kẻ vạch ngăn cách
            else:
                # Nó là JSON, nhưng không phải list sách
                st.markdown(message["content"])
        except (json.JSONDecodeError, TypeError):
            # Nếu không parse được (nó là text thường), cứ in ra
            st.markdown(message["content"])

# --- 7. Hàm để gọi API (Backend) ---
# (Hàm này giữ nguyên, không thay đổi)
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

# --- 8. Nhận Input từ Người dùng ---
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì về sách..."):
    
    # Thêm tin nhắn của user vào lịch sử và hiển thị
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Tạo tin nhắn "đang suy nghĩ"
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 Đang suy nghĩ...")
        
        # Gọi Backend (FastAPI)
        full_response = call_agent_api(prompt)
        
        # --- ⭐️ NÂNG CẤP HIỂN THỊ ⭐️ ---
        # Thay vì chỉ in ra `full_response`, chúng ta sẽ xử lý nó
        
        try:
            # Cố gắng parse xem nó có phải là list sách không
            books = json.loads(full_response)
            
            # Kiểm tra xem nó có phải là list các cuốn sách (dict) không
            if isinstance(books, list) and all(isinstance(b, dict) for b in books):
                message_placeholder.empty() # Xóa chữ "Đang suy nghĩ..."
                st.markdown("**Đây là các gợi ý tôi tìm thấy cho bạn:**")
                
                # Lặp qua và hiển thị từng cuốn sách
                for book in books:
                    col1, col2 = st.columns([1, 3]) # Chia cột 1:3
                    
                    with col1: # Cột ảnh
                        if book.get("main_images"):
                            st.image(book.get("main_images"), caption=book.get("title"), use_column_width=True)
                        else:
                            # Ảnh dự phòng nếu không có link
                            st.image("https://placehold.co/150x220/262730/FAFAFA?text=No+Image", caption=book.get("title"), use_column_width=True)
                    
                    with col2: # Cột thông tin
                        st.markdown('<div class="book-card">', unsafe_allow_html=True)
                        st.subheader(book.get("title", "Không có tiêu đề"))
                        st.markdown(f"**Tác giả:** {book.get('author_name', 'Unknown')}")
                        st.markdown(f"**Giá:** ${book.get('price', 0.0):.2f}")
                        st.markdown(f"**Rating:** {book.get('average_rating', 0)} ({book.get('rating_number', 0)} reviews)")
                        if "rrf_score" in book:
                            st.caption(f"Độ liên quan (RRF Score): {book.get('rrf_score', 0):.4f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.divider() # Kẻ vạch ngăn cách
            else:
                # Nó là JSON, nhưng không phải list sách (ví dụ: lỗi)
                message_placeholder.markdown(full_response)
                
        except (json.JSONDecodeError, TypeError):
            # Nếu không phải JSON (chỉ là text thường như "Đã lưu sở thích...")
            message_placeholder.markdown(full_response)
        
        # Thêm câu trả lời *thô* (raw) vào lịch sử
        st.session_state.messages.append({"role": "assistant", "content": full_response})

