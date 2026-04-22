---
trigger: always_on
---

# Rule 10 — Style (Naming / Structure / Formatting)

> Quy tắc ngắn để tuân theo ngay. Chi tiết → `docs/standards/coding.md`.

## Naming

- **Files / Modules**: `snake_case` (ví dụ: `user_service.py`, `order_repository.py`).
- **Classes**: `PascalCase` (ví dụ: `UserService`, `OrderDto`).
- **Functions / Variables**: `snake_case` (ví dụ: `get_user_by_id`, `total_price`).
- **Constants**: `UPPER_SNAKE_CASE` (ví dụ: `MAX_RETRY_COUNT`).
- **Test files**: `test_<tên_module>.py` (ví dụ: `test_user_service.py`) — theo pytest convention.
- **Streamlit pages**: `snake_case`, đặt trong thư mục `pages/` (ví dụ: `pages/order_list.py`).

## Structure

- Mỗi file chỉ chứa một concern chính (single-responsibility).
- Không để dead code, commented-out code trong commit.
- Import order: stdlib → third-party → internal (theo thứ tự này, cách nhau blank line).
- Tách UI logic (Streamlit widgets) ra khỏi business logic — không viết lẫn lộn trong cùng một hàm.

## Formatting

- Formatter: **Black** (chuẩn, không tự điều chỉnh config).
- Linter: **Ruff** hoặc **Flake8**.
- Max line length: **88** (Black default) — không dùng 120.
- Không commit code có linting error.

## Evidence

> **TBD** — Sẽ điền path file + đoạn code dẫn chứng khi có code inputs.
> Format: `<file>:<line-range> — <lý do rút ra rule>`
