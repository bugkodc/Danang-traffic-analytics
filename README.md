# Da Nang Traffic Analytics

Hệ thống phân tích và phân luồng giao thông đô thị Đà Nẵng trên nền dữ liệu lớn — kết hợp đồ thị OpenStreetMap và đếm phương tiện bằng thị giác máy tính.

*A big-data system for urban traffic analysis and rerouting in Da Nang, Vietnam — combining OpenStreetMap road graphs with computer-vision vehicle counting.*

> Luận văn Thạc sĩ ngành Hệ thống thông tin — Khoa Toán–Tin học, Trường Đại học Sư phạm, Đại học Đà Nẵng.

---

## Kiến trúc

Kiến trúc Lambda — tách tầng xử lý theo lô và tầng phục vụ truy vấn:

```
┌─ TẦNG BATCH (chạy local / Colab) ───────────────────────────────┐
│  Video thực địa ──> RF-DETR + ByteTrack ──> đếm qua vạch ảo      │
│                                                   │              │
│  OSM .pbf ──> đồ thị đã làm sạch ──> Spark: trọng số động       │
│                                      Spark: SSSP có trọng số     │
│                                      Spark: độ trung tâm         │
│                                             │                    │
│                                    SUMO: kịch bản phân luồng     │
└─────────────────────────────────────────────┼────────────────────┘
                                              v
                        ┌──────────────────────────────────┐
                        │  KHUNG NHÌN VẬT CHẤT HOÁ         │
                        │  PMTiles · Parquet · DuckDB      │
                        └──────────────┬───────────────────┘
                                       v
┌─ TẦNG SERVING (deploy công khai) ───────────────────────────────┐
│         FastAPI  ──  MapLibre GL + React  ──  URL công khai      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Trạng thái

| Hợp phần | Trạng thái |
|---|---|
| Thu thập chuỗi thời gian tốc độ (TomTom) | ✅ **Đang chạy** — GitHub Actions, 24/24 |
| Đồ thị OSM Đà Nẵng | ⏳ Chưa bắt đầu |
| Bộ dữ liệu ảnh giao thông Đà Nẵng | ⏳ Chưa bắt đầu |
| Phát hiện & đếm phương tiện | ⏳ Chưa bắt đầu |
| Xử lý đồ thị phân tán (Spark) | ⏳ Chưa bắt đầu |
| Mô phỏng kịch bản (SUMO) | ⏳ Chưa bắt đầu |
| Web app | ⏳ Chưa bắt đầu |

---

## Cấu trúc thư mục

```
danang-traffic-analytics/
├── .github/workflows/      Lịch chạy tự động trên GitHub Actions
├── ingest/tomtom/          Thu thập tốc độ giao thông theo thời gian thực
│   └── data/*.parquet      ← DỮ LIỆU KHÔNG TÁI TẠO ĐƯỢC
├── docs/plan/              Kế hoạch triển khai 15 file — đọc docs/plan/README.md
└── CLAUDE.md               Bối cảnh dự án cho phiên làm việc mới
```

Các thư mục `vision/`, `graph/`, `sumo/`, `services/`, `experiments/`, `results/` sẽ được tạo khi tới giai đoạn tương ứng. Xem [docs/plan/B-kien-truc-ky-thuat.md](docs/plan/B-kien-truc-ky-thuat.md).

---

## Bắt đầu

### Thu thập dữ liệu tốc độ

Chạy tự động trên GitHub Actions, không cần máy chủ. Xem hướng dẫn cài đặt 4 bước tại [ingest/tomtom/CHAY-TREN-GITHUB.md](ingest/tomtom/CHAY-TREN-GITHUB.md).

Chạy tay ở máy cá nhân:

```bash
pip install -r requirements.txt
export TOMTOM_API_KEY=your_key_here
cd ingest/tomtom && python collect.py
```

Kiểm tra chất lượng các điểm đo sau mỗi lần sửa `segments.csv`:

```bash
cd ingest/tomtom && python kiem_tra_diem.py
```

---

## Kế hoạch triển khai

Toàn bộ kế hoạch nằm ở [docs/plan/](docs/plan/README.md) — 15 file, chia theo giai đoạn, mỗi giai đoạn có mục tiêu, danh sách công việc theo tuần, sản phẩm bàn giao và sổ rủi ro riêng.

Đang ở **Giai đoạn 0** — đo đạc lấy số liệu và viết đề cương: [docs/plan/00b-giai-doan-0-de-cuong.md](docs/plan/00b-giai-doan-0-de-cuong.md).

---

## Giấy phép

Mã nguồn: [MIT](LICENSE).

Bộ dữ liệu ảnh giao thông (khi công bố) sẽ dùng giấy phép riêng CC BY-NC 4.0.

Dữ liệu tốc độ trong `ingest/tomtom/data/` được thu thập qua TomTom Traffic API và chỉ sử dụng cho mục đích nghiên cứu phi thương mại, theo điều khoản của nhà cung cấp.
