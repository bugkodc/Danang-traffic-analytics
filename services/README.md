# Tầng phục vụ — web demo

Đây là **tầng serving** trong kiến trúc Lambda: chỉ đọc dữ liệu đã tính sẵn,
không chạy tính toán nặng. Xem `docs/plan/B-kien-truc-ky-thuat.md`.

## Chạy trên máy cá nhân

```bash
pip install -r services/requirements.txt
python -m uvicorn services.api.main:app --reload --port 8000
```

Mở http://localhost:8000

Nếu chưa có dữ liệu, chạy trước `cd ingest/tomtom && python collect.py`,
hoặc `git pull` để lấy dữ liệu GitHub Actions đã thu.

## Đang có gì

| Thao tác | Trạng thái |
|---|---|
| Bản đồ Đà Nẵng, các đoạn tô màu theo mức tắc | ✅ dữ liệu TomTom thật |
| Thanh trượt thời gian qua các lần đo | ✅ |
| Click đoạn → biểu đồ tốc độ theo thời gian | ✅ |
| Đường tốc độ dòng tự do làm mốc so sánh | ✅ |
| Định tuyến so sánh (ngắn nhất vs nhanh nhất) | ⏳ cần GĐ4 |
| So sánh kịch bản phân luồng | ⏳ cần GĐ5 |
| Panel video có bounding box | ⏳ cần GĐ3 |

Đây là 2/5 thao tác demo mục tiêu, xem `docs/plan/06-giai-doan-6-web-app-deploy.md`.

## API

| Endpoint | Trả về |
|---|---|
| `GET /api/tong-quan` | Số bản ghi, số đoạn, khoảng thời gian |
| `GET /api/thoi-diem` | Danh sách các thời điểm đo |
| `GET /api/doan?thoi_diem=...` | Trạng thái các đoạn tại một thời điểm |
| `GET /api/doan/{id}/chuoi-thoi-gian` | Lịch sử đo của một đoạn |
| `GET /api/theo-gio` | **Hồ sơ tốc độ trung bình theo giờ** — dạng dữ liệu sẽ thành trọng số động của cạnh đồ thị |

## Ngưỡng tô màu

| Mức | `speed_ratio` | Màu |
|---|---|---|
| 1 | ≥ 0,85 | Xanh — thông thoáng |
| 2 | 0,65–0,85 | Vàng — hơi đông |
| 3 | 0,45–0,65 | Cam — đông |
| 4 | < 0,45 | Đỏ — tắc |
