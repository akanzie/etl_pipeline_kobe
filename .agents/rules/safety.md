---
trigger: always_on
---

# Rule 00 — Safety (Absolute, Non-overridable)

## Destructive Commands — NEVER execute
- `rm -rf` hoặc bất kỳ lệnh xóa đệ quy nào
- `git reset --hard` / `git clean -fd`
- Overwrite toàn bộ file mà không đọc trước
- Drop database / truncate table trên môi trường production
- Force push lên nhánh `main` / `master` / `release/*`

## Scope Guardrails
- Không implement tính năng ngoài spec-pack.md đã approve.
- Không tự thêm dependency mới mà không ghi vào spec-pack.md trước.
- Không thay đổi schema DB / API contract mà không có migration plan trong spec.

## Ambiguity Protocol
- Khi gặp điểm mơ hồ: tách thành **Open Issue** trong spec-pack.md, KHÔNG tự giả định.
- Format Open Issue:
  ```
  ### Open Issue #N
  **Câu hỏi:** <mô tả điểm mơ hồ>
  **Options:** <các lựa chọn có thể>
  **Owner:** <người quyết định>
  **Deadline:** <ngày cần trả lời>
  ```

## Data & Secret Safety
- Không log / commit secret, token, password.
- Không hardcode credential vào source code.
- File chứa secret phải nằm trong `.gitignore`.

### Sensitive File Patterns — NEVER read, write, or edit
Các pattern dưới đây bị cấm tuyệt đối (đã cấu hình trong `.claude/settings.json`):
```
.env  |  .env.*  |  secrets/**  |  credentials/**
*.pem  |  *.key  |  *.p12  |  *.keystore
*.pfx  |  *.cer  |  id_rsa  |  id_ed25519
```
Nếu cần làm việc với secret, chuyển sang Secret Manager hoặc `settings.local` — không bao giờ paste giá trị thật vào `docs/`.

## Approval Gate
- Mọi thay đổi file phải có explicit approval từ user trước khi thực thi.
- Chỉ exception duy nhất: tạo file mới trong thư mục `docs/changes/{{TICKET}}/` khi đang ở bước được approve rõ ràng.
