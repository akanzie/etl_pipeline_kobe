---
trigger: always_on
---

# Rule 40 — Testing (UT / IT / E2E / Naming / Mock Policy)

> Quy tắc ngắn để tuân theo ngay. Chi tiết → `docs/standards/testing.md`.

## Test Pyramid

| Loại | Scope | Tỷ lệ mục tiêu |
|------|-------|----------------|
| Unit Test (UT) | Một function/class, mock dependencies | ~70% |
| Integration Test (IT) | Nhiều layer thật, DB/infra thật hoặc in-memory | ~20% |
| E2E Test | Full flow qua API/UI | ~10% |

## Naming

- Test file: `test_<tên_module>.py` (ví dụ: `test_user_service.py`) — pytest convention bắt buộc.
- Test function: `test_<mô_tả_behavior>` — đủ để đọc mà không cần nhìn code.
- Ví dụ: `test_calculate_total_returns_zero_when_cart_is_empty`, `test_login_fails_when_password_is_wrong`.

## Mock Policy

- UT: mock **tất cả** external dependencies (DB, HTTP, file system) — dùng `unittest.mock` hoặc `pytest-mock`.
- IT: **không mock** DB — dùng SQLite in-memory hoặc DB thật với data fixture riêng.
- E2E (Streamlit): dùng `streamlit.testing.v1.AppTest` hoặc Playwright — không mock gì.
- Không mock module đang được test (tautology test).

## Coverage

- Minimum coverage: **TBD** (điền sau khi có config thực tế).
- Bắt buộc có test cho: happy path, error path, boundary values, security-sensitive paths.
- Không tăng coverage bằng cách test getter/setter vô nghĩa.

## CI

- Test phải pass trước khi merge — không skip test để unblock.
- Flaky test phải được quarantine và track trong issue, không bỏ qua.

## Evidence

> **TBD** — Sẽ điền path file + đoạn code dẫn chứng khi có code inputs.
> Format: `<file>:<line-range> — <lý do rút ra rule>`
