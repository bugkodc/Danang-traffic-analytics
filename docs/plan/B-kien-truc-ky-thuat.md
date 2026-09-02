# Phụ lục B — Kiến trúc kỹ thuật

## 1. Cây thư mục repo

```
danang-traffic/
├── docker-compose.yml
├── README.md                       # mô tả, ảnh màn hình, link demo, cách chạy
├── requirements.txt                # ghim số hiệu phiên bản chính xác
│
├── data/                           # KHÔNG commit (.gitignore)
│   ├── raw/
│   │   ├── osm/                    # .osm.pbf
│   │   ├── video/                  # + manifest.csv
│   │   └── speed/                  # YYYY-MM-DD.parquet từ TomTom
│   ├── interim/                    # khung hình đã trích, nhãn nháp
│   ├── processed/                  # dataset đã gán nhãn, đồ thị đã làm sạch
│   ├── ground_truth/               # manual_counts.csv
│   ├── sites.csv
│   └── site_edge_mapping.csv
│
├── pipeline/
│   ├── ingest/                     # thu thập tốc độ, poll camera, trích khung
│   ├── vision/                     # YOLO, ByteTrack, đếm qua vạch
│   ├── graph/                      # OSM, làm sạch, BPR, job Spark
│   └── sumo/                       # netconvert, hiệu chỉnh, kịch bản
│
├── services/
│   ├── api/                        # FastAPI + DuckDB
│   └── web/                        # React + MapLibre GL
│
├── serving/                        # đầu ra tầng batch, đầu vào tầng serving
│   ├── edges.pmtiles
│   ├── edge_metrics.parquet
│   ├── site_counts.parquet
│   ├── od_matrix.parquet
│   └── scenarios/
│
├── experiments/                    # MỖI BẢNG TRONG LUẬN VĂN = 1 SCRIPT Ở ĐÂY
│   ├── exp01_baseline_gap.py
│   ├── exp02_detection_comparison.py
│   ├── exp03_stratified_eval.py
│   ├── exp04_ablation_imgsz.py
│   ├── exp05_counting_validation.py
│   ├── exp06_scalability.py
│   └── exp07_scenarios.py
│
├── results/                        # CSV kết quả — CÓ commit vào git
├── models/                         # trọng số (dùng Git LFS hoặc để ngoài)
└── docs/
    ├── nhat-ky/                    # viết sau MỖI giai đoạn
    ├── huong-dan-gan-nhan.md
    └── figures/
```

**Quy tắc vàng:** mỗi bảng trong luận văn ứng với đúng một script trong `experiments/` sinh ra đúng một file trong `results/`. Khi phản biện hỏi "số này ở đâu ra", bạn chạy lại được tại chỗ.

---

## 2. Hợp đồng dữ liệu giữa các tầng

Chốt các schema này sớm và **không đổi**. Đây là giao diện giữa các giai đoạn — thay đổi giữa chừng gây phá vỡ dây chuyền.

### 2.1 `counts.parquet` — đầu ra GĐ3, đầu vào GĐ4 & GĐ5

```
site_id            string      # khoá tới sites.csv
edge_id            int64       # khoá tới đồ thị, qua site_edge_mapping.csv
ts_15min           timestamp   # đã gộp về khoảng 15 phút
direction          string      # 'N','S','E','W' hoặc mã hướng rẽ
vehicle_class      string      # motorcycle|car|bus|truck|van|bicycle
count              int32       # số xe thô
pcu                float32     # đã quy đổi xe con tương đương
confidence_mean    float32     # độ tin cậy trung bình của phát hiện
```

### 2.2 `edges.parquet` — đồ thị đã làm giàu

```
edge_id            int64
u, v               int64       # đỉnh đầu/cuối
geometry           WKB         # LineString
length_m           float32
highway            string      # loại đường OSM
lanes              int8        # có thể suy luận
maxspeed_osm       float32     # từ OSM, có thể null
freeflow_speed     float32     # THỰC ĐO từ TomTom - đóng góp của luận văn
capacity_pcu_h     float32     # năng lực thông hành
oneway             bool
```

### 2.3 `edge_metrics.parquet` — kết quả phân tích, đầu vào tầng serving

```
edge_id            int64
hour               int8        # 0-23
daytype            string      # weekday|weekend
volume_pcu         float32     # lưu lượng ước lượng
travel_time_s      float32     # từ hàm BPR
vc_ratio           float32     # V/C - mức bão hoà
betweenness        float32     # độ trung tâm trung gian
congestion_level   int8        # 0-4, dùng để tô màu bản đồ
```

Cột `congestion_level` tính sẵn ở tầng batch để phía client chỉ việc tra bảng màu — đây là mẹo giúp thanh trượt thời gian mượt hoàn toàn.

---

## 3. `docker-compose.yml` — bố cục

```yaml
services:
  api:            # FastAPI + DuckDB, mount serving/ chỉ đọc
  web:            # React build tĩnh, phục vụ qua nginx
  spark-master:   # chỉ bật khi chạy tầng batch (profile: batch)
  spark-worker:   # scale 2-4 node để đo speedup
```

Dùng **Docker Compose profiles** để tách: `docker compose up` chỉ bật `api` + `web` (tầng serving, nhẹ); `docker compose --profile batch up` mới bật cụm Spark. Nhờ vậy người khác clone repo về chạy demo được ngay mà không cần cụm Spark.

---

## 4. Ngăn xếp công nghệ

| Tầng | Công nghệ | Lý do |
|---|---|---|
| Thị giác | Ultralytics YOLOv11 + ByteTrack | Chuẩn hiện hành, tài liệu tốt, xuất ONNX dễ |
| Đồ thị | OSMnx + NetworkX (một máy) / **PySpark + GraphFrames** (phân tán) | Xem cảnh báo mục 5 |
| Đối chứng một máy | `igraph` | Nhanh hơn NetworkX nhiều, dùng làm đường cơ sở đo speedup |
| Mô phỏng | **SUMO** + `routeSampler.py` | Mã nguồn mở, chuẩn học thuật, có mô hình sublane cho xe máy |
| Lưu trữ | Parquet + **DuckDB** | Không cần server CSDL; nhanh cho truy vấn phân tích; dữ liệu chỉ đọc |
| Bản đồ | **PMTiles** + MapLibre GL | Một file, host tĩnh, không cần tile server |
| API | FastAPI | Nhẹ, tự sinh tài liệu OpenAPI |
| Frontend | React + Recharts | |
| Theo dõi thí nghiệm | Weights & Biases (free học thuật) | Tránh mất dấu cấu hình |

---

## 5. Ba bẫy kỹ thuật đã biết trước

### 5.1 `GraphFrames.shortestPaths()` KHÔNG hỗ trợ trọng số

Nó chỉ chạy BFS theo số cạnh. Bài toán này cần đường nhanh nhất theo thời gian di chuyển.

**Giải pháp:** tự cài Bellman-Ford bằng vòng lặp join trên DataFrame. **Bắt buộc checkpoint sau mỗi 3–5 vòng lặp** để cắt lineage — nếu không Spark sẽ tràn bộ nhớ khi kế hoạch thực thi dài ra.

Đây cũng chính là điểm nối về đề tài "MapReduce cho Bellman-Ford" trong danh sách gốc, nhưng có ứng dụng thật.

### 5.2 Chia tập theo điểm quay, KHÔNG chia ngẫu nhiên

Chia ngẫu nhiên làm các khung từ cùng một video nằm cả ở train lẫn test → mô hình đã thấy nền cảnh → **mAP bị thổi phồng, kết quả vô giá trị**.

```
train: site_01..site_08    val: site_09, site_10    test: site_11, site_12
```

### 5.3 SUMO mặc định mô phỏng theo làn — sai bản chất với xe máy VN

Phải bật **sublane model** (`--lateral-resolution`) và định nghĩa `vType` riêng cho xe máy (`width=0.8`, `minGap` nhỏ, `latAlignment="arbitrary"`). Nếu bỏ qua, kết quả mô phỏng sai về bản chất và phản biện sẽ chỉ ra.

---

## 6. Bảng so sánh nền tảng triển khai

| Nền tảng | Chi phí | Ngủ? | Đánh giá |
|---|---|---|---|
| **Hugging Face Spaces (Docker)** | Miễn phí | Có | Nhanh nhất, URL vĩnh viễn — khuyến nghị nếu ưu tiên gọn |
| **Oracle Cloud Always Free** | Miễn phí vĩnh viễn | Không | 4 nhân ARM + 24GB RAM, mạnh nhất — khuyến nghị nếu muốn hệ thống thật |
| Fly.io | Free allowance | Cấu hình được | Có volume, Docker |
| Vercel + Supabase | Miễn phí | Không | Frontend nhanh, PostGIS 500MB |
| Railway | ~$5/tháng | Không | An toàn nhất cho tháng bảo vệ |
| Render free | Miễn phí | **Có, 15 phút** | Cold start ~50s — rủi ro khi demo |
| VPS Việt Nam | ~100–200k/tháng | Không | Tên miền `.vn`, ping thấp |

---

## 7. Quy ước git

- Nhánh `main` luôn chạy được; giữ một nhánh `stable` đã kiểm chứng cho ngày bảo vệ
- Commit `results/*.csv` — đây là số liệu của luận văn, phải có lịch sử
- **Không commit** `data/` và `models/` (dùng Git LFS hoặc lưu ngoài)
- Gắn tag ở mỗi cột mốc: `g1-nen-mong`, `g4-con-so-1-2`, `g6-san-pham`, `bao-ve`
- Repo private lúc đầu, chuyển public trước khi gửi bài báo
