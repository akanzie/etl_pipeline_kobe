---
trigger: always_on
---

# Rule 80 — Streamlit UI & UX Development

Bản hướng dẫn chuyên biệt cho việc phát triển giao diện người dùng bằng Streamlit, đảm bảo hiệu suất và trải nghiệm người dùng tốt nhất.

## Core UI Patterns
- **Layout Management**: Sử dụng `st.columns`, `st.tabs`, và `st.container` để tổ chức giao diện mạch lạc. Tránh lồng ghép quá sâu (> 3 cấp).
- **State Management**: Sử dụng `st.session_state` hiệu quả. Khởi tạo giá trị mặc định ngay đầu file hoặc trong một helper function.
- **Component Modularity**: Chia nhỏ giao diện thành các hàm riêng biệt (ví dụ: `render_header()`, `render_sidebar()`, `render_dashboard()`).

## Performance Optimization
- **Caching**: Sử dụng `@st.cache_data` cho các tác vụ IO/Data Loading và `@st.cache_resource` cho các kết nối DB hoặc model AI.
- **Fragments**: Sử dụng `@st.fragment` để cập nhật từng phần của giao diện mà không cần reload toàn bộ trang.
- **Data Heavy Ops**: Không để logic nặng trong callback của widget. Hãy xử lý data rồi mới update UI.

## UX Best Practices
- **Feedback**: Luôn có `st.spinner()` hoặc `st.status()` khi thực hiện các tác vụ tốn thời gian.
- **Validation**: Kiểm tra input ngay tại UI bằng `st.error()` hoặc `st.warning()` trước khi gửi xuống Application layer.
- **Theming**: Tuân thủ theme của dự án (màu sắc, font) đã cấu hình trong `.streamlit/config.toml`.
- **Empty States**: Hiển thị hướng dẫn hoặc placeholder khi chưa có dữ liệu để người dùng biết phải làm gì.

## SDD Layer Integration
- **Separation of Concerns**: Page trong Streamlit (`pages/*.py`) CHỈ làm nhiệm vụ render. Mọi business logic phải gọi qua `ApplicationService`.
- **Error Handling**: Sử dụng try-except tại UI layer để bắt các custom exceptions từ Service và hiển thị `st.error` thân thiện với người dùng.
- **Auth Guard**: Kiểm tra session auth ở dòng đầu tiên của mỗi page. Redirect về login nếu chưa authenticated.