# Tầng phục vụ — web demo (CesiumJS)

**Tầng serving** trong kiến trúc Lambda: chỉ đọc dữ liệu đã tính sẵn.
Xem `docs/plan/B-kien-truc-ky-thuat.md`.

## Chạy

```bash
pip install -r services/requirements.txt
python graph/xuat_geojson.py          # chỉ chạy 1 lần, sinh file bản đồ
python -m uvicorn services.api.main:app --reload --port 8000
```

Mở http://localhost:8000 — **chạy từ thư mục gốc repo**, không phải trong `services/`.

## Tải thư viện CesiumJS (1 lần)

Thư viện 20MB không commit lên git. Tải về:

```bash
curl -sL -o cesium.tgz https://registry.npmjs.org/cesium/-/cesium-1.126.0.tgz
tar -xzf cesium.tgz
mv package/Build/Cesium services/api/static/vendor/Cesium
rm -rf package cesium.tgz
```

## Vì sao chọn CesiumJS

| | CesiumJS | MapLibre |
|---|---|---|
| **Phát lại theo thời gian** | ✅ Đồng hồ + CZML dựng sẵn | ❌ Tự viết |
| **Animation xe chạy từ SUMO** | ✅ FCD → CZML gần như 1-1 | ⚠️ Tự dựng |
| Môi trường 3D | ✅ Quả cầu, camera nghiêng/bay | ⚠️ Chỉ đùn khối nhà |
| Nền bản đồ sẵn có | ❌ Tự cấp (ta đã có) | ✅ Đầy đủ |

Hai dòng đầu là lý do quyết định: đề tài cần **phát lại dữ liệu theo thời gian**,
và ở Giai đoạn 5 sẽ cần **animation xe chạy từ đầu ra SUMO**. Cesium được thiết
kế đúng cho việc đó. Chuyển đổi sau sẽ phải viết lại toàn bộ tầng hiển thị.

## Chạy hoàn toàn offline

**Không dùng Cesium ion, không token, không gọi ra ngoài lần nào.**
`Cesium.Ion.defaultAccessToken = undefined`.

Ảnh nền dùng bộ Natural Earth đóng gói sẵn trong thư viện. Mọi dữ liệu còn lại
là của chính luận văn:

| Lớp | Nguồn | Số lượng |
|---|---|---|
| Mạng lưới đường | `graph/xuat_geojson.py` từ đồ thị OSM | 31.096 đoạn |
| Sông, biển, hồ | cùng script | 491 vùng |
| Điểm đo | TomTom API | 12 điểm |

Đánh đổi: không có ảnh vệ tinh, không có địa hình cao độ, không có nhãn tên
đường. Với đề tài phân luồng giao thông thì không cần.

## Đang có gì

| Thao tác demo | Trạng thái |
|---|---|
| Bản đồ Đà Nẵng, điểm đo tô màu theo mức tắc | ✅ |
| Nghiêng 3D, xoay, bay camera | ✅ |
| Thanh trượt thời gian qua các lần đo | ✅ |
| Click điểm → biểu đồ tốc độ theo thời gian | ✅ |
| Định tuyến so sánh (ngắn nhất vs nhanh nhất) | ⏳ cần GĐ4 |
| **Animation xe chạy + so sánh kịch bản** | ⏳ **cần GĐ5 — dùng CZML** |
| Panel video có bounding box | ⏳ cần GĐ3 |

## API

| Endpoint | Trả về |
|---|---|
| `GET /api/tong-quan` | Số bản ghi, số đoạn, khoảng thời gian |
| `GET /api/thoi-diem` | Danh sách thời điểm đo |
| `GET /api/doan?thoi_diem=...` | Trạng thái các đoạn tại một thời điểm |
| `GET /api/doan/{id}/chuoi-thoi-gian` | Lịch sử đo của một đoạn |
| `GET /api/theo-gio` | **Hồ sơ tốc độ theo giờ** — sẽ thành trọng số động của cạnh |
| `GET /api/duong-chinh` | Mạng lưới đường (GeoJSON) |
| `GET /api/mat-nuoc` | Sông, biển, hồ (GeoJSON) |

## Ngưỡng tô màu

| Mức | `speed_ratio` | Màu |
|---|---|---|
| 1 | ≥ 0,85 | Xanh — thông thoáng |
| 2 | 0,65–0,85 | Vàng — hơi đông |
| 3 | 0,45–0,65 | Cam — đông |
| 4 | < 0,45 | Đỏ — tắc |
