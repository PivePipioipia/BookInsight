# 📖 HƯỚNG DẪN CHI TIẾT CHỈNH SỬA FILE app.py

## 📋 MỤC LỤC
1. [Tổng quan về file](#1-tổng-quan-về-file)
2. [Cấu hình cơ bản](#2-cấu-hình-cơ-bản)
3. [Tùy chỉnh màu sắc và theme](#3-tùy-chỉnh-màu-sắc-và-theme)
4. [Tùy chỉnh layout và spacing](#4-tùy-chỉnh-layout-và-spacing)
5. [Tùy chỉnh header](#5-tùy-chỉnh-header)
6. [Tùy chỉnh chat bubbles](#6-tùy-chỉnh-chat-bubbles)
7. [Tùy chỉnh input box](#7-tùy-chỉnh-input-box)
8. [Tùy chỉnh book cards](#8-tùy-chỉnh-book-cards)
9. [Cấu hình API](#9-cấu-hình-api)
10. [Tùy chỉnh logic hiển thị](#10-tùy-chỉnh-logic-hiển-thị)

---

## 1. TỔNG QUAN VỀ FILE

File `app.py` là ứng dụng Streamlit tạo giao diện chat để tìm kiếm sách. File được chia thành các phần chính:

- **Dòng 1-19**: Import thư viện và cấu hình trang
- **Dòng 21-272**: CSS tùy chỉnh (phần lớn nhất)
- **Dòng 274-291**: Header HTML
- **Dòng 293-299**: Cấu hình API URL
- **Dòng 301-314**: Quản lý session state (memory)
- **Dòng 316-353**: Hiển thị lịch sử chat
- **Dòng 355-367**: Hàm gọi API
- **Dòng 369-428**: Xử lý input từ người dùng

---

## 2. CẤU HÌNH CƠ BẢN

### 2.1. Thay đổi tiêu đề và icon (Dòng 15-19)

```python
st.set_page_config(
    page_title="BookInsight Chatbot",  # ← Sửa tiêu đề tab trình duyệt
    page_icon="📚",                    # ← Đổi emoji (ví dụ: "🔍", "💬", "📖")
    layout="wide",                     # ← "centered" = hẹp, "wide" = rộng
)
```

**Ví dụ:**
- Đổi icon: `page_icon="🔍"` (kính lúp)
- Đổi layout: `layout="centered"` (card hẹp ở giữa)

---

## 3. TÙY CHỈNH MÀU SẮC VÀ THEME

### 3.1. Thay đổi màu chủ đạo (Dòng 34-45)

Tất cả màu sắc được định nghĩa trong biến CSS `:root`. Chỉ cần sửa ở đây để đổi toàn bộ theme:

```css
:root {
    --bg: #f8f9fa;              /* ← Màu nền chính (xám nhạt) */
    --paper: #ffffff;            /* ← Màu nền card (trắng) */
    --ink: #1a1a1a;             /* ← Màu chữ chính (đen) */
    --muted: #6b7280;            /* ← Màu chữ phụ (xám) */
    --accent: #2563eb;           /* ← Màu nhấn (xanh dương) */
    --accent-light: #3b82f6;     /* ← Màu nhấn sáng hơn */
    --border: #e5e7eb;           /* ← Màu viền (xám nhạt) */
    --shadow-sm: rgba(0, 0, 0, 0.04);  /* ← Bóng đổ nhẹ */
    --shadow-md: rgba(0, 0, 0, 0.08);  /* ← Bóng đổ vừa */
    --shadow-lg: rgba(0, 0, 0, 0.12);  /* ← Bóng đổ đậm */
}
```

**Ví dụ đổi sang theme tối (dark mode):**
```css
:root {
    --bg: #0f172a;              /* Nền tối */
    --paper: #1e293b;          /* Card tối */
    --ink: #f1f5f9;            /* Chữ sáng */
    --muted: #94a3b8;           /* Chữ phụ sáng */
    --accent: #3b82f6;         /* Xanh sáng */
    --border: #334155;         /* Viền tối */
}
```

**Ví dụ đổi sang theme xanh lá:**
```css
:root {
    --accent: #10b981;         /* Xanh lá */
    --accent-light: #34d399;   /* Xanh lá nhạt */
}
```

**Cách tìm mã màu:**
- Dùng công cụ: https://htmlcolorcodes.com/
- Format: `#RRGGBB` (ví dụ: `#ff0000` = đỏ)
- Hoặc: `rgb(255, 0, 0)` hoặc `rgba(255, 0, 0, 0.5)` (có độ trong suốt)

---

## 4. TÙY CHỈNH LAYOUT VÀ SPACING

### 4.1. Độ rộng card chính (Dòng 64)

```css
max-width: 720px;  /* ← Đổi số này để thay đổi độ rộng */
```

**Ví dụ:**
- `600px` = hẹp hơn (tốt cho mobile)
- `800px` = rộng hơn
- `1000px` = rất rộng
- `90%` = chiếm 90% màn hình (responsive)

### 4.2. Khoảng cách card (Dòng 65)

```css
margin: 32px auto;  /* ← 32px = cách trên/dưới, auto = căn giữa */
```

**Ví dụ:**
- `16px auto` = cách trên/dưới ít hơn
- `48px auto` = cách trên/dưới nhiều hơn
- `0 auto` = không cách trên/dưới

### 4.3. Bo góc card (Dòng 68)

```css
border-radius: 20px;  /* ← Đổi số này để thay đổi độ tròn */
```

**Ví dụ:**
- `0` = vuông góc (không bo)
- `8px` = bo nhẹ
- `20px` = bo vừa (hiện tại)
- `999px` = tròn hoàn toàn (pill shape)

---

## 5. TÙY CHỈNH HEADER

### 5.1. Thay đổi tên app và mô tả (Dòng 284-285)

```html
<div class="title">BookInsight</div>  <!-- ← Sửa tên app -->
<div class="subtitle">RAG‑Fusion · Text‑to‑SQL · Memory</div>  <!-- ← Sửa mô tả -->
```

**Ví dụ:**
```html
<div class="title">Tìm Sách Thông Minh</div>
<div class="subtitle">AI · Tìm kiếm · Gợi ý</div>
```

### 5.2. Thay đổi trạng thái (Dòng 287)

```html
<div class="status">Online</div>  <!-- ← Sửa text hoặc xóa dòng này -->
```

**Ví dụ:**
- `"Đang hoạt động"`
- `"Sẵn sàng"`
- Hoặc xóa toàn bộ dòng để ẩn status

### 5.3. Thay đổi kích thước chữ header (Dòng 87)

```css
font-size: 20px;  /* ← Đổi số này */
```

**Ví dụ:**
- `18px` = nhỏ hơn
- `24px` = lớn hơn
- `28px` = rất lớn

### 5.4. Thay đổi padding header (Dòng 80)

```css
padding: 24px 28px;  /* ← 24px = trên/dưới, 28px = trái/phải */
```

**Ví dụ:**
- `16px 20px` = chật hơn
- `32px 40px` = rộng hơn

---

## 6. TÙY CHỈNH CHAT BUBBLES

### 6.1. Màu nền tin nhắn bot (Dòng 111)

```css
background: #f8f9fa;  /* ← Đổi màu nền tin nhắn từ bot */
```

**Ví dụ:**
- `#ffffff` = trắng
- `#e0f2fe` = xanh nhạt
- `#fef3c7` = vàng nhạt

### 6.2. Bo góc tin nhắn user (Dòng 126)

```css
border-radius: 16px;  /* ← Đổi độ tròn của bubble user */
```

**Ví dụ:**
- `8px` = bo nhẹ
- `20px` = bo nhiều
- `999px` = tròn hoàn toàn

### 6.3. Padding tin nhắn (Dòng 114, 127)

```css
padding: 20px 28px;  /* ← Tin nhắn bot: trên/dưới 20px, trái/phải 28px */
padding: 14px 18px;  /* ← Tin nhắn user: trên/dưới 14px, trái/phải 18px */
```

**Ví dụ:**
- `12px 16px` = chật hơn
- `24px 32px` = rộng hơn

---

## 7. TÙY CHỈNH INPUT BOX

### 7.1. Placeholder text (Dòng 370)

```python
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì về sách..."):  # ← Sửa text này
```

**Ví dụ:**
- `"Nhập câu hỏi của bạn..."`
- `"Tìm sách bạn muốn..."`
- `"Bạn cần gì?"`

### 7.2. Kích thước chữ input (Dòng 152)

```css
font-size: 15px !important;  /* ← Đổi số này */
```

**Ví dụ:**
- `14px` = nhỏ hơn
- `16px` = lớn hơn

### 7.3. Màu viền khi focus (Dòng 160)

```css
border-color: var(--accent) !important;  /* ← Dùng màu accent */
```

**Hoặc đổi sang màu cụ thể:**
```css
border-color: #10b981 !important;  /* Xanh lá */
```

### 7.4. Hiệu ứng glow khi focus (Dòng 162)

```css
box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
```

**Giải thích:**
- `0 0 0 3px` = không offset, blur 0, spread 3px
- `rgba(37, 99, 235, 0.1)` = màu xanh với độ trong suốt 10%

**Ví dụ:**
- `rgba(16, 185, 129, 0.15)` = xanh lá, đậm hơn
- `rgba(239, 68, 68, 0.1)` = đỏ nhạt

---

## 8. TÙY CHỈNH BOOK CARDS

### 8.1. Padding card (Dòng 174)

```css
padding: 20px;  /* ← Khoảng cách trong card */
```

**Ví dụ:**
- `16px` = chật hơn
- `24px` = rộng hơn
- `20px 24px` = trên/dưới 20px, trái/phải 24px

### 8.2. Khoảng cách giữa các card (Dòng 175)

```css
margin-bottom: 16px;  /* ← Cách dưới mỗi card */
```

**Ví dụ:**
- `12px` = gần nhau hơn
- `24px` = xa nhau hơn

### 8.3. Kích thước tiêu đề sách (Dòng 189)

```css
font-size: 18px;  /* ← Kích thước tiêu đề trong card */
```

**Ví dụ:**
- `16px` = nhỏ hơn
- `20px` = lớn hơn
- `22px` = rất lớn

### 8.4. Tỷ lệ cột ảnh/thông tin (Dòng 329, 399)

```python
col1, col2 = st.columns([1, 3])  # ← [1, 3] = ảnh 25%, thông tin 75%
```

**Ví dụ:**
- `[1, 2]` = ảnh 33%, thông tin 67%
- `[1, 4]` = ảnh 20%, thông tin 80%
- `[2, 3]` = ảnh 40%, thông tin 60%

### 8.5. Thêm/xóa thông tin hiển thị (Dòng 340-344, 411-415)

Hiện tại card hiển thị:
- Tiêu đề
- Tác giả
- Giá
- Rating
- RRF Score (nếu có)

**Để thêm thông tin mới, thêm dòng sau dòng 344 hoặc 415:**
```python
st.markdown(f"**Thể loại:** {book.get('category', 'N/A')}")
st.markdown(f"**Năm xuất bản:** {book.get('year', 'N/A')}")
```

**Để xóa thông tin, xóa dòng tương ứng:**
```python
# Xóa dòng này để ẩn giá:
# st.markdown(f"**Giá:** ${book.get('price', 0.0):.2f}")
```

---

## 9. CẤU HÌNH API

### 9.1. Thay đổi URL API (Dòng 299)

```python
API_URL = "http://127.0.0.1:8000/chat"  # ← Sửa URL này
```

**Ví dụ:**
- Local khác port: `"http://127.0.0.1:8080/chat"`
- Production: `"https://api.example.com/chat"`
- Với authentication: `"https://api.example.com/v1/chat"`

### 9.2. Thay đổi timeout (Dòng 360)

```python
response = requests.post(API_URL, json=payload, timeout=300)  # ← 300 giây = 5 phút
```

**Ví dụ:**
- `timeout=60` = 1 phút
- `timeout=600` = 10 phút
- `timeout=None` = không giới hạn (không khuyến khích)

### 9.3. Thay đổi user_id (Dòng 359)

```python
payload = {"user_id": "streamlit_user", "question": user_question}  # ← Sửa user_id
```

**Ví dụ:**
- `"user_123"`
- `f"user_{time.time()}"` (unique mỗi session)
- Hoặc lấy từ session state nếu có login

---

## 10. TÙY CHỈNH LOGIC HIỂN THỊ

### 10.1. Thay đổi tin nhắn chào mừng (Dòng 312)

```python
"content": "Xin chào! Tôi là BookInsight. Bạn muốn biết gì về sách hôm nay?"
```

**Ví dụ:**
- `"Chào bạn! Tôi có thể giúp gì?"`
- `"Xin chào! Hãy hỏi tôi về sách."`

### 10.2. Thay đổi text "Đang suy nghĩ" (Dòng 380)

```python
message_placeholder.markdown("🤔 Đang suy nghĩ...")  # ← Sửa text này
```

**Ví dụ:**
- `"⏳ Đang xử lý..."`
- `"🔍 Đang tìm kiếm..."`
- `"💭 Đang suy nghĩ..."`

### 10.3. Thay đổi text "Đây là các gợi ý..." (Dòng 326, 395)

```python
st.markdown("**Đây là các gợi ý tôi tìm thấy cho bạn:**")  # ← Sửa text này
```

**Ví dụ:**
- `"**Kết quả tìm kiếm:**"`
- `"**Các cuốn sách phù hợp:**"`
- `"**Gợi ý cho bạn:**"`

### 10.4. Thay đổi ảnh placeholder (Dòng 335, 406)

```python
st.image("https://placehold.co/150x220/262730/FAFAFA?text=No+Image", ...)
```

**Giải thích URL:**
- `150x220` = kích thước (width x height)
- `262730` = màu nền (hex, không có #)
- `FAFAFA` = màu chữ
- `No+Image` = text hiển thị

**Ví dụ:**
- `"https://placehold.co/200x300/000000/FFFFFF?text=No+Cover"` (đen trắng)
- Hoặc dùng ảnh local: `st.image("assets/no_image.png", ...)`

### 10.5. Thêm/xóa divider giữa các sách (Dòng 347, 418)

```python
st.divider()  # ← Xóa dòng này để bỏ đường kẻ
```

Hoặc thay đổi style divider ở dòng 214-219.

---

## 🎨 VÍ DỤ CÁC THEME PHỔ BIẾN

### Theme Xanh Dương (Mặc định)
```css
--accent: #2563eb;
--accent-light: #3b82f6;
```

### Theme Xanh Lá
```css
--accent: #10b981;
--accent-light: #34d399;
```

### Theme Tím
```css
--accent: #8b5cf6;
--accent-light: #a78bfa;
```

### Theme Đỏ/Cam
```css
--accent: #f59e0b;
--accent-light: #fbbf24;
```

### Theme Tối (Dark Mode)
```css
--bg: #0f172a;
--paper: #1e293b;
--ink: #f1f5f9;
--muted: #94a3b8;
--border: #334155;
--accent: #3b82f6;
```

---

## 🔧 CÁC THAY ĐỔI THƯỜNG GẶP

### Làm card rộng hơn
1. Dòng 64: Đổi `max-width: 720px` → `max-width: 900px`
2. Dòng 18: Đổi `layout="wide"` (nếu chưa)

### Làm chữ lớn hơn
1. Dòng 52: Đổi `font-size` trong các CSS selector
2. Dòng 87: Header title `font-size: 20px` → `24px`
3. Dòng 152: Input `font-size: 15px` → `18px`

### Thay đổi font chữ
1. Dòng 28: Đổi Google Fonts link (ví dụ: `family=Roboto`)
2. Dòng 51: Đổi `font-family` trong CSS

### Ẩn status badge
1. Dòng 287: Xóa hoặc comment dòng `<div class="status">Online</div>`

### Thay đổi màu accent toàn bộ
1. Dòng 39-40: Đổi `--accent` và `--accent-light`

---

## 📝 LƯU Ý KHI CHỈNH SỬA

1. **Backup file trước khi sửa**: Copy file `app.py` thành `app.py.backup`
2. **Test sau mỗi thay đổi**: Chạy `streamlit run app.py` để xem kết quả
3. **CSS cần `!important`**: Một số style cần `!important` để override Streamlit mặc định
4. **Format JSON**: Nếu sửa phần hiển thị JSON, đảm bảo format đúng
5. **API URL**: Đảm bảo backend đang chạy trước khi test

---

## 🆘 XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi: "Module not found"
- **Nguyên nhân**: Thiếu thư viện
- **Giải pháp**: Chạy `pip install streamlit requests`

### Lỗi: "Connection refused" khi gọi API
- **Nguyên nhân**: Backend chưa chạy hoặc URL sai
- **Giải pháp**: Kiểm tra URL ở dòng 299, đảm bảo backend đang chạy

### CSS không áp dụng
- **Nguyên nhân**: Cache trình duyệt
- **Giải pháp**: Refresh trang (Ctrl+F5) hoặc clear cache

### Giao diện bị lỗi layout
- **Nguyên nhân**: CSS conflict hoặc syntax error
- **Giải pháp**: Kiểm tra dấu ngoặc `{}`, dấu `;` trong CSS

---

## 📚 TÀI LIỆU THAM KHẢO

- **Streamlit Docs**: https://docs.streamlit.io/
- **CSS Variables**: https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
- **Color Picker**: https://htmlcolorcodes.com/
- **Google Fonts**: https://fonts.google.com/

---

**Chúc bạn chỉnh sửa thành công! 🎉**

