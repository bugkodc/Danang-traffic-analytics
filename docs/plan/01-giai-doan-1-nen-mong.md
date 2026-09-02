# Giai đoạn 1 — Nền móng (Tuần 1–4)

> **Mục tiêu:** Kết thúc T4 phải có một hệ thống rỗng nhưng **hoàn chỉnh về mặt hạ tầng**, đã deploy công khai, và đã bắt đầu tích lũy dữ liệu không thể lấy lại được.

Đây là giai đoạn quan trọng nhất và cũng là giai đoạn hay bị coi nhẹ nhất. Mọi thứ làm ở đây đều là việc "không có kết quả để khoe" nhưng quyết định toàn bộ 44 tuần còn lại.

---

## Việc phải làm TRONG 48 GIỜ ĐẦU

Bốn việc này chặn tiến độ về sau, làm ngay trước khi đọc tiếp:

### 1. Khởi động thu thập chuỗi thời gian tốc độ

Dữ liệu tốc độ giao thông là dữ liệu quá khứ — **không mua lại được**. Mỗi ngày trì hoãn là một ngày mất vĩnh viễn.

- Đăng ký API key **TomTom Developer** (Traffic Flow Segment Data, ~2.500 request/ngày miễn phí)
- Chọn 20–50 đoạn đường trọng điểm, lấy toạ độ tâm đoạn
- Viết một script gọi API mỗi 15 phút, ghi ra `data/raw/speed/YYYY-MM-DD.parquet`
- Chạy nền bằng Task Scheduler (Windows) hoặc cron

Sau 6 tháng bạn sẽ có ~17.000 điểm đo/đoạn — đủ để làm ground truth cho toàn bộ luận văn. Chi phí: 0 đồng, 2 giờ công.

### 2. Đăng ký Cổng dữ liệu mở Đà Nẵng (30 phút — làm trước mọi thứ khác)

**https://opendata.danang.gov.vn** hoặc **https://congdulieu.vn**

Đăng ký tài khoản tự phục vụ bằng email/số điện thoại, hoặc đăng nhập bằng tài khoản EGOV. **Không cần công văn, không cần giấy giới thiệu.** Cổng cung cấp dữ liệu qua web, **API**, SMS và Zalo.

Sau khi đăng nhập, duyệt hết danh mục dữ liệu **lĩnh vực Giao thông vận tải** và ghi lại: có những bộ nào, định dạng gì, có API không, cập nhật đến thời điểm nào.

Vì sao đây là việc quan trọng nhất: theo **Quyết định ban hành Danh mục dữ liệu mở TP Đà Nẵng** (công bố 12/5/2023, thực hiện theo Nghị định 47/2020/NĐ-CP), lĩnh vực GTVT có **19 loại dữ liệu mở**, trong đó có **dữ liệu camera giám sát giao thông**, dữ liệu mạng lưới xe buýt và dữ liệu luồng tuyến vận tải cố định. Mục tiêu 2026: các đơn vị hoàn thành cung cấp ≥90% khối lượng dữ liệu thuộc phạm vi quản lý.

Nói cách khác: **dữ liệu bạn cần đã được thành phố công bố là dữ liệu mở.** Việc của bạn là tìm đúng cửa, không phải xin ân huệ.

### 3. Văn bản đề nghị hướng dẫn khai thác (chỉ khi cổng chưa có sẵn dữ liệu)

Nếu duyệt cổng mà chưa thấy dữ liệu camera, hãy gửi văn bản — nhưng **viết theo hướng viện dẫn, không phải xin phép**:

> *"Theo Quyết định ban hành Danh mục dữ liệu mở thành phố Đà Nẵng ngày 12/5/2023, dữ liệu camera giám sát giao thông thuộc danh mục dữ liệu mở lĩnh vực Giao thông vận tải. Đề nghị Quý cơ quan hướng dẫn thủ tục khai thác dữ liệu này qua Cổng dữ liệu mở phục vụ nghiên cứu khoa học phi thương mại."*

Khác biệt so với cách viết cũ: bạn không đặt cán bộ tiếp nhận vào thế phải quyết định cho hay không cho, mà chỉ đề nghị hướng dẫn một quy trình đã tồn tại. Tỷ lệ được phản hồi cao hơn hẳn.

Tra số hiệu quyết định chính xác trên danang.gov.vn trước khi gửi. Kèm cam kết: không lưu ảnh định danh cá nhân, tuân thủ **Nghị định 13/2023/NĐ-CP** về bảo vệ dữ liệu cá nhân.

**Quan trọng:** việc này **không nằm trên đường găng**. Nguồn tự quay vẫn là xương sống. Xem [A](A-nguon-du-lieu.md) mục 8 — sáu việc đầu trong thứ tự ưu tiên không cần xin phép ai và đủ để hoàn thành toàn bộ luận văn.

### 4. Tạo repo và commit đầu tiên

Khởi tạo cây thư mục theo [B-kien-truc-ky-thuat.md](B-kien-truc-ky-thuat.md), commit, push lên GitHub (private lúc đầu, chuyển public trước khi gửi bài báo).

---

## Tuần 1 — Đồ thị và khảo sát

### 1.1 Kéo đồ thị OSM Đà Nẵng

```python
import osmnx as ox
G = ox.graph_from_place("Đà Nẵng, Việt Nam", network_type="drive")
```

Nếu ranh giới hành chính sau sáp nhập chưa cập nhật trong OSM, dùng bbox thủ công hoặc `graph_from_polygon`.

**Số liệu bắt buộc phải ghi lại** (đây là bảng đầu tiên trong luận văn):

| Chỉ số | Cần đo |
|---|---|
| Số đỉnh, số cạnh | |
| Tổng chiều dài mạng (km) | |
| Phân bố theo `highway=*` (motorway/trunk/primary/…) | |
| **% cạnh thiếu `maxspeed`** | Dự kiến rất cao |
| **% cạnh thiếu `lanes`** | Dự kiến rất cao |
| Số thành phần liên thông | Nếu >1 phải xử lý |
| Số nút có `highway=traffic_signals` | |

Hai dòng in đậm là quan trọng nhất: chúng định lượng khối lượng công việc làm sạch dữ liệu, và bản thân việc bổ khuyết thuộc tính là một mục đóng góp chính danh trong luận văn.

### 1.2 Khảo sát thực địa chọn điểm quay

Đi thực tế, chọn 12 điểm (dùng 6 nếu theo phạm vi tối thiểu). Tiêu chí:

- Có chỗ đặt máy cao 5–8m và an toàn: cầu vượt bộ hành, tầng 2 quán cà phê, lan can cầu
- Đa dạng loại hình: nút giao nhiều tầng, cầu qua sông, trục xuyên tâm, tuyến ven biển, cửa ngõ sân bay
- Có điện hoặc quay được ≥30 phút bằng pin

**Gợi ý điểm khảo sát:** Ngã ba Huế (nút giao nhiều tầng), cầu Rồng, cầu Sông Hàn, cầu Trần Thị Lý, trục Nguyễn Văn Linh, Điện Biên Phủ, Ngô Quyền, Võ Nguyên Giáp (ven biển), khu vực cửa ngõ sân bay, Nguyễn Tri Phương.

Với mỗi điểm ghi vào `data/sites.csv`: `site_id, tên, lat, lon, mô tả góc quay, loại hình, ghi chú tiếp cận`.

---

## Tuần 2 — Khung phần mềm và deploy rỗng

### 2.1 Dựng cây repo

Theo [B-kien-truc-ky-thuat.md](B-kien-truc-ky-thuat.md). Tối thiểu:

```
├── docker-compose.yml
├── services/api/          # FastAPI
├── services/web/          # React + MapLibre
├── pipeline/vision/       # YOLO + tracking
├── pipeline/graph/        # OSM + Spark
├── pipeline/sumo/
├── experiments/           # mỗi bảng trong luận văn = 1 script ở đây
├── results/               # CSV kết quả, commit vào git
└── data/                  # KHÔNG commit, có .gitignore
```

### 2.2 Deploy khung rỗng — **cột mốc quan trọng nhất của giai đoạn**

Mục tiêu: một URL công khai, mở lên thấy bản đồ Đà Nẵng, các cạnh đường tô màu ngẫu nhiên, click vào cạnh hiện popup dữ liệu giả.

Chọn một nền tảng (xem so sánh ở [B-kien-truc-ky-thuat.md](B-kien-truc-ky-thuat.md)):
- **Hugging Face Spaces (Docker)** — nhanh nhất, miễn phí, URL vĩnh viễn
- **Oracle Cloud Always Free** — mạnh nhất (4 nhân ARM, 24GB RAM), tốn công cấu hình hơn

Xử lý ngay tại đây các vấn đề luôn phát sinh: CORS, biến môi trường, dung lượng ảnh Docker, giới hạn RAM, HTTPS.

### 2.3 Sinh PMTiles cho mạng đường

Với ~120k cạnh, **không** gửi GeoJSON thô xuống trình duyệt.

```bash
# GeoJSON -> MBTiles -> PMTiles
tippecanoe -o danang.mbtiles -zg --drop-densest-as-needed edges.geojson
pmtiles convert danang.mbtiles danang.pmtiles
```

PMTiles là một file duy nhất, host tĩnh, không cần tile server, MapLibre đọc trực tiếp qua HTTP range request. Toàn bộ mạng đường phục vụ miễn phí từ static hosting.

---

## Tuần 3 — Quay thử và kiểm chứng giả thuyết

### 3.1 Quay video thử

Ra 1–2 điểm đã chọn, quay 30 phút vào giờ cao điểm. Ghi lại: độ cao máy, góc nghiêng, độ phân giải, thời tiết, khung giờ.

### 3.2 Chạy YOLOv11 mặc định — thí nghiệm chẩn đoán

```python
from ultralytics import YOLO
model = YOLO("yolo11m.pt")   # trọng số COCO gốc, chưa fine-tune
```

Chọn 50 khung hình ngẫu nhiên, đếm tay số xe máy thật, so với số YOLO phát hiện.

**Con số này quyết định toàn bộ khối lượng công việc GĐ2–GĐ3:**

| Tỷ lệ sót xe máy | Ý nghĩa | Hành động |
|---|---|---|
| < 15% | Domain gap nhỏ | Cần ~1.000 ảnh gán nhãn; novelty bài báo yếu, phải tìm góc khác |
| 15–40% | Domain gap rõ rệt | ~2.000 ảnh; **đây là kịch bản lý tưởng cho bài báo** |
| > 40% | Domain gap rất lớn | ~3.000 ảnh; hạ độ cao máy hoặc đổi góc quay; kiểm tra lại chất lượng video |

Ghi kết quả vào `results/g1_baseline_gap.csv`. Đây là số liệu mở đầu của bài báo 1.

### 3.3 Chốt bộ lớp phương tiện

Đề xuất 6 lớp: `motorcycle`, `car`, `bus`, `truck`, `van`, `bicycle`. Bản tối thiểu gộp còn 4: `motorcycle`, `car`, `bus`, `truck`.

Chốt xong **không đổi nữa** — đổi lớp giữa chừng là gán nhãn lại từ đầu.

---

## Tuần 4 — Nối đường ống và qua cổng G1

### 4.1 Nối 5 mắt xích với dữ liệu tối giản

```
video thử → YOLO mặc định → ByteTrack → đếm qua 1 vạch ảo
    → ghi Parquet → API đọc → bản đồ hiện số đếm ở 1 điểm
```

Kết quả sẽ rất xấu. Không quan trọng. Quan trọng là **thông**.

### 4.2 Thiết lập nhật ký nghiên cứu

Tạo `docs/nhat-ky/` và viết ngay bài đầu tiên: bối cảnh đề tài, số liệu đồ thị OSM (mục 1.1), kết quả thí nghiệm chẩn đoán (mục 3.2). ~5 trang.

Từ đây, **kết thúc mỗi giai đoạn viết một bài**. Đến T29 bạn biên tập chứ không sáng tác.

---

## Sản phẩm bàn giao của GĐ1

- [ ] `data/raw/osm/danang.osm.pbf` + đồ thị đã tải, có bảng thống kê
- [ ] `data/sites.csv` — 6–12 điểm quay đã khảo sát thực địa
- [ ] Job thu thập tốc độ TomTom **đang chạy** và đã có ≥2 tuần dữ liệu
- [ ] **Đã đăng ký opendata.danang.gov.vn**, đã duyệt và ghi lại danh mục dữ liệu GTVT
- [ ] Đã tải các dataset giao thông VN công khai (Roboflow, Kaggle — xem [A](A-nguon-du-lieu.md) mục 3.1)
- [ ] *(Tuỳ chọn)* Văn bản đề nghị hướng dẫn khai thác dữ liệu mở đã gửi
- [ ] Repo GitHub + `docker compose up` chạy được
- [ ] **URL công khai hiện bản đồ Đà Nẵng**
- [ ] `results/g1_baseline_gap.csv` — tỷ lệ sót của YOLO mặc định
- [ ] Đường ống 5 mắt xích thông với dữ liệu tối giản
- [ ] `docs/nhat-ky/01-nen-mong.md` (~5 trang)

## Tiêu chí qua cổng G1

Mở URL công khai trên **điện thoại**, thấy bản đồ Đà Nẵng, click được vào một cạnh đường và hiện dữ liệu. Đồng thời `docker compose up` từ repo sạch chạy được trên máy khác.

Nếu chưa đạt, **không sang GĐ2**. Ngoại lệ duy nhất: GĐ2 phần quay video có thể bắt đầu song song từ T3 vì phụ thuộc thời tiết và lịch cá nhân.

---

## Rủi ro giai đoạn này

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Sa đà tinh chỉnh mô hình quá sớm | Hết T3 vẫn chưa deploy | Dừng, ép mình hoàn thành mục 2.2 trước |
| Ranh giới Đà Nẵng mới chưa có trong OSM | `graph_from_place` trả về vùng cũ | Dùng bbox thủ công; ghi rõ trong luận văn |
| Không tìm được chỗ đặt máy đủ cao | Video góc thấp, xe che nhau hoàn toàn | Đổi điểm; ưu tiên cầu vượt bộ hành; cân nhắc xin quay từ ban công nhà dân |
| TomTom free tier hết quota | API trả 403 | Giảm số đoạn hoặc giãn chu kỳ lên 20–30 phút; bổ sung HERE làm nguồn thứ hai |
