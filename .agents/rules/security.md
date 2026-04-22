---
trigger: always_on
---

# Rule 30 — Security (Input Validation / Authorization / Logs / PII)

> Quy tắc ngắn để tuân theo ngay. Chi tiết → `docs/standards/security.md`.

## Input Validation

- Validate **tất cả** input từ user / external API tại UI layer (trước khi gọi Service) hoặc trong Service.
- Dùng **Pydantic** để validate data model — không validate thủ công bằng if/else chuỗi dài.
- Khi input không hợp lệ: hiển thị `st.error()` / `st.warning()` tại UI, raise exception có message rõ ràng tại Service; không để stack trace lộ ra màn hình người dùng.

## Authorization

- Kiểm tra authorization **trước** khi thực hiện bất kỳ business logic nào.
- Với Streamlit: kiểm tra `st.session_state` đã có thông tin auth chưa ngay đầu mỗi page — nếu chưa, redirect về login.
- Không tin tưởng dữ liệu nhạy cảm từ `st.session_state` nếu có thể bị user can thiệp — verify lại từ backend/token.
- Principle of least privilege: chỉ cấp quyền tối thiểu cần thiết.

## Logging & PII

- **Không log**: password, token, secret key, credit card, số CMND/passport, số điện thoại đầy đủ.
- Log đủ để debug (session ID dạng hash/masked, action, kết quả) — không log payload nguyên vẹn của sensitive fields.
- Dùng Python `logging` module với structured format — không dùng `print()` hoặc `st.write()` để debug trong production.

## Secrets

- Không hardcode credential, key, token vào source code (Rule 00 absolute).
- Dùng environment variable hoặc Secret Manager.
- File `.env` phải trong `.gitignore`.
- File cấu hình (`.cfg`, `.ini`) chứa credentials phải trong `.gitignore`; chỉ commit template với giá trị rỗng.

## Evidence

> **TBD** — Sẽ điền path file + đoạn code dẫn chứng khi có code inputs.
> Format: `<file>:<line-range> — <lý do rút ra rule>`
