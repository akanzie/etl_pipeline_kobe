---
trigger: always_on
---

# Rule 20 — Architecture (Layers / Dependencies / Responsibilities)

> Quy tắc ngắn để tuân theo ngay. Chi tiết → `docs/architecture/overview.md`.

## Layer Rules

- Dependency chỉ đi **một chiều**: UI → Application/Service → Infrastructure/Repository → Domain. Không được đảo ngược.
- Layer dưới **không được import** layer trên.
- Cross-cutting concerns (logging, auth, error handling) đặt ở Python decorator hoặc helper module riêng — không rải vào business logic hay UI.

## Responsibilities

| Layer | Vị trí | Được làm | Không được làm |
|-------|--------|----------|----------------|
| UI (Pages) | `pages/`, `src/ui/pages/`, `app.py` | Render widget, gọi Application, hiển thị kết quả | Business logic, trực tiếp query DB |
| Application | `src/application/` | Business logic, orchestration, validate input | Render Streamlit widget, trực tiếp query DB |
| Analytics / Query | `src/analytics/` | Build SQL/pure query helpers | IO, side effects |
| Infrastructure | `src/infrastructure/` | Data access (DB, file, API) | Business logic |
| Domain / Model | `src/domain/` | Data structure, Pydantic model, validation đơn giản | IO, side effects |
| Core / Excel | `src/core/`, `src/excel/` | Cross-cutting config/logging/exceptions và exporter base | Rải logic nghiệp vụ vào layer khác |

## Dependencies

- Không thêm dependency mới mà không ghi vào `spec-pack.md` trước (Rule 00).
- Ưu tiên dùng thư viện đã có trong project trước khi thêm mới.
- Không circular dependency giữa modules.

## Evidence

> **TBD** — Sẽ điền path file + đoạn code dẫn chứng khi có code inputs.
> Format: `<file>:<line-range> — <lý do rút ra rule>`
