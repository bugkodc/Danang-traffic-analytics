# Giai đoạn 0 — Đo đạc và viết đề cương (Tuần 1–5)

> **Nguyên tắc:** Đo trước, viết sau. Nhưng chỉ đo đúng những gì cần để viết.

Giai đoạn này trả lời câu hỏi "setup trước hay viết đề cương trước". Đáp án: **2 tuần đo đạc → 3 tuần viết**. Không phải xây hệ thống ba tháng rồi mới viết, cũng không phải viết chay từ tài liệu.

---

## Vì sao phải đo trước

Đề cương chỉ mạnh khi có số liệu cụ thể. Với đề tài này, các số liệu nền **chưa ai công bố** — bạn phải tự đo:

| Con số | Ai đã công bố? | Hệ quả nếu không đo |
|---|---|---|
| Số đỉnh/cạnh đồ thị Đà Nẵng mới | Không ai | Không biện minh được quy mô dữ liệu lớn |
| % cạnh thiếu `maxspeed`/`lanes` | Không ai | Không định lượng được khối lượng làm sạch |
| Tỷ lệ YOLO gốc sót xe máy tại Đà Nẵng | Không ai | Không chứng minh được khoảng cách miền tồn tại |
| Cổng dữ liệu mở thực tế có gì | Không ai | Không biết phải tự thu bao nhiêu |

Bốn dòng này là bốn cái chân của đề cương. Thiếu chúng thì đề cương toàn chữ "dự kiến", và hội đồng sẽ hỏi đúng vào đó.

---

## NGÀY 1 — Việc không thể trì hoãn

### 0.1 Khởi động thu dữ liệu TomTom (2 giờ)

**Đây là việc duy nhất thực sự khẩn.** Dữ liệu tốc độ là dữ liệu quá khứ — không mua lại được. Mỗi ngày chờ là một ngày mất vĩnh viễn.

- Đăng ký API key TomTom Developer (Traffic Flow Segment Data, ~2.500 request/ngày miễn phí)
- Chọn 20–50 đoạn đường trên hành lang dự kiến, lấy toạ độ tâm đoạn
- Script gọi API mỗi 15 phút → `data/raw/speed/YYYY-MM-DD.parquet`
- Chạy nền bằng Task Scheduler

Đến lúc bảo vệ đề cương bạn đã có ~5 tuần dữ liệu; đến lúc bảo vệ luận văn có gần một năm. Đây sẽ là nguồn kiểm chứng chéo độc lập mạnh nhất của toàn bộ luận văn.

### 0.2 Đăng ký cổng dữ liệu mở (30 phút)

**opendata.danang.gov.vn** hoặc **congdulieu.vn** — đăng ký tự phục vụ, không cần công văn.

Checklist khi đăng nhập được (ghi ra `docs/khao-sat-opendata.md`):

- [ ] Lĩnh vực GTVT có 19 mục — **thực tế bao nhiêu mục đã có dữ liệu thật**, bao nhiêu mới chỉ có tên?
- [ ] Mục "dữ liệu camera giám sát giao thông" thuộc loại nào:
  - (a) Siêu dữ liệu — danh sách vị trí, toạ độ, hướng nhìn *(khả năng cao nhất)*
  - (b) Ảnh snapshot định kỳ
  - (c) Luồng video trực tiếp
  - (d) Dữ liệu đã xử lý — số đếm xe, tốc độ *(nếu có, thiết kế lại đề tài theo hướng tốt hơn)*
- [ ] Định dạng, có API không, tần suất cập nhật, cập nhật lần cuối khi nào
- [ ] Mục "mạng lưới xe buýt" và "luồng tuyến vận tải cố định" — **có định dạng GTFS không?**
- [ ] Danh mục phủ cả địa bàn Quảng Nam cũ hay chỉ Đà Nẵng cũ?

Hỗ trợ trực tiếp: **0236 1022** / **info@congdulieu.vn** — gọi hỏi nhanh hơn gửi văn bản nhiều.

**Số hiệu để trích dẫn:** Quyết định **804/QĐ-UBND ngày 05/03/2026**, do Phó Chủ tịch UBND TP Đà Nẵng Hồ Quang Bửu ký — danh mục dữ liệu mở gồm **14 lĩnh vực, 211 mục dữ liệu**, riêng GTVT & logistics **19 mục**. Sở KH&CN Đà Nẵng chủ trì. Mục tiêu 2026: hoàn thành tối thiểu 90%.

---

## TUẦN 1 — Đo đồ thị và chốt hành lang

### 1.1 Kéo đồ thị OSM và lập bảng thống kê

```python
import osmnx as ox
G = ox.graph_from_place("Đà Nẵng, Việt Nam", network_type="drive")
```

Nếu ranh giới sau sáp nhập chưa cập nhật trong OSM, dùng bbox thủ công và ghi rõ cách xác định phạm vi.

**Bảng phải có (Bảng 1 của đề cương):**

| Chỉ số | Đà Nẵng cũ | + Quảng Nam cũ |
|---|---|---|
| Số đỉnh | | |
| Số cạnh | | |
| Tổng chiều dài mạng (km) | | |
| Phân bố theo `highway=*` | | |
| **% cạnh thiếu `maxspeed`** | | |
| **% cạnh thiếu `lanes`** | | |
| Số thành phần liên thông | | |
| Số nút `highway=traffic_signals` | | |

Đo cả hai phạm vi — chênh lệch giữa hai cột là lập luận trực tiếp cho quy mô dữ liệu sau sáp nhập.

### 1.2 Chốt hành lang nghiên cứu

**Quan trọng: không làm cả thành phố.** Chuẩn mực là nghiên cứu một hành lang 3–5 km với 6–12 điểm đếm. Nhiều hơn thì không hiệu chỉnh SUMO nổi, không đếm tay đối chứng nổi, không sửa mạng bằng tay nổi.

Tiêu chí chọn hành lang:
- Có ít nhất một cầu qua sông (tạo điểm nghẽn tự nhiên → kịch bản phân luồng có ý nghĩa)
- Có 1–2 nút giao lớn
- Có chỗ đặt máy quay cao 5–8m: cầu vượt bộ hành, lan can cầu, tầng 2 quán cà phê, bãi đỗ xe trung tâm thương mại
- Nếu cổng dữ liệu cho danh sách vị trí camera: **ưu tiên hành lang có cụm camera sẵn**

Ghi ra `data/sites.csv`: `site_id, tên, lat, lon, mô tả góc quay, loại hình, ghi chú tiếp cận, có camera thành phố không`.

---

## TUẦN 2 — Thí nghiệm chẩn đoán

### 2.1 Quay thử

30 phút giờ cao điểm tại 1–2 điểm. Ghi lại: độ cao máy, góc nghiêng, độ phân giải, thời tiết, khung giờ.

*Mẹo tiết kiệm:* đặt một đêm khách sạn tầng cao nhìn xuống trục chính (300–500k ngoài mùa du lịch) → quay 6–8 giờ trải nhiều khung giờ từ góc lý tưởng, tuyệt đối ổn định.

### 2.2 Đo khoảng cách miền — **con số quan trọng nhất của đề cương**

Chạy hai mô hình gốc chưa fine-tune trên 50 khung hình ngẫu nhiên, đếm tay số xe máy thật, so sánh:

| Mô hình | Giấy phép | Tỷ lệ sót xe máy |
|---|---|---|
| YOLOv11m / YOLO26 (COCO) | AGPL-3.0 | |
| **RF-DETR** (COCO) | **Apache 2.0** | |

Kết quả quyết định toàn bộ phần sau:

| Tỷ lệ sót | Ý nghĩa | Hành động |
|---|---|---|
| < 15% | Khoảng cách miền nhỏ | Luận điểm yếu — chuyển trọng tâm sang đánh giá phân tầng theo điều kiện (mưa/đêm/mật độ cao) |
| **15–40%** | Khoảng cách rõ rệt | **Kịch bản lý tưởng.** Viết thẳng con số này vào đề cương |
| > 40% | Khoảng cách rất lớn | Kiểm tra lại góc quay/chất lượng video trước khi mừng |

Ghi ra `results/g0_baseline_gap.csv`. **Đây là bằng chứng thực nghiệm đầu tiên và mạnh nhất của đề cương** — nó biến câu "giao thông Việt Nam khác phương Tây" từ phỏng đoán thành số đo.

### 2.3 Chốt mô hình và bộ lớp phương tiện

Mô hình đề xuất: **RF-DETR** (Apache 2.0, backbone DINOv2, dẫn đầu benchmark RF100-VL về chuyển giao miền — mạnh nhất khi fine-tune dataset nhỏ ở miền lạ). Giữ YOLO làm mốc so sánh. Chi tiết ở [D](D-cong-nghe-va-huong-moi.md) mục 1.

Bộ lớp: 6 lớp `motorcycle, car, bus, truck, van, bicycle`; bản tối thiểu gộp còn 4. **Chốt xong không đổi** — đổi giữa chừng là gán nhãn lại từ đầu.

---

## TUẦN 3–5 — Viết đề cương

Dùng lại đúng cấu trúc đề cương cũ của bạn — GVHD đã quen định dạng đó và nó đạt chuẩn.

### 3.1 Định vị so với công trình đã có

**Bắt buộc trích dẫn và định vị rõ**, nếu không hội đồng tự tìm ra sẽ thành điểm trừ nặng:

| Công trình | Họ đã làm | Bạn khác ở đâu |
|---|---|---|
| **BigSUMO** (arXiv 2601.02286, 01/2026) | Spark/Hadoop + mô phỏng SUMO song song + scalability | Họ **không có thị giác máy tính**; bạn nối số đếm thực từ video vào |
| **Counting Mixed Traffic at Motorcycle-Dominated Intersections** (Springer IJITSR 2024) | Đếm xe giao lộ xe máy chi phối bằng CV | Họ dừng ở đếm; bạn đưa số đếm vào đồ thị và mô phỏng |
| **Toronto turning movement counts → SUMO** (arXiv 2508.10733) | Hiệu chỉnh SUMO từ số đếm | Họ dùng số đếm chính thức có sẵn; bạn tự sinh số đếm bằng CV |
| TGDT, OpenTwinMap, "Driving SUMO Towards Digital Twins" | Bản sao số từ OSM + CV + SUMO | Họ không có tầng phân tán và phân tích scalability |
| Spark shortest-path trên mạng đường Mỹ | Tính đường đi phân tán | Không gắn với dữ liệu quan trắc thực |

**Khoảng trống còn lại — viết đúng ba điều này, không tuyên bố quá:**

1. **Chuỗi bốn khâu chưa ai ghép**: thị giác máy tính → trọng số đồ thị → xử lý phân tán → mô phỏng kịch bản, trong một hệ thống khép kín có kiểm chứng ở từng khâu
2. **Đà Nẵng hoàn toàn trống** — không có công trình nào về phân tích mạng lưới giao thông Đà Nẵng bằng OSM; mạng lưới sau sáp nhập Quảng Nam (7/2025) chưa ai phân tích
3. **Bộ dữ liệu chưa tồn tại** — không có bộ dữ liệu ảnh giao thông Đà Nẵng công khai; các bài review về giám sát đô thị nêu đích danh khoảng trống "chưa có bộ dữ liệu đô thị công khai cho Đông Nam Á"

### 3.2 Câu hỏi nghiên cứu và giả thuyết

Làm theo đúng dạng Bảng 4 trong đề cương cũ:

| Mã | Câu hỏi nghiên cứu | H₀ / Hₐ | Kiểm định |
|---|---|---|---|
| **CH1** | Khoảng cách miền giữa mô hình huấn luyện trên dữ liệu phương Tây và giao thông xe máy Đà Nẵng lớn đến mức nào? | H₀: mAP không khác biệt giữa mô hình gốc và mô hình fine-tune | t bắt cặp / Wilcoxon trên các lần chia dữ liệu |
| **CH2** ⭐ | **Trọng số động từ số đếm thị giác có cải thiện độ chính xác ước lượng thời gian hành trình so với trọng số tĩnh của OSM không?** | H₀: sai số ước lượng so với TomTom không khác biệt | t bắt cặp trên các đoạn đường; RMSE/MAE |
| **CH3** | Ngưỡng quy mô nào thì xử lý phân tán vượt trội xử lý một máy? | H₀: thời gian chạy không khác biệt giữa Spark và một máy | ANOVA hai yếu tố (số node × quy mô) |
| **CH4** | Kịch bản phân luồng có giảm tổng thời gian trễ có ý nghĩa thống kê không? | H₀: trễ trung bình không khác giữa hiện trạng và kịch bản | t bắt cặp / Mann-Whitney trên ≥10 lần chạy seed |

**CH2 là câu hỏi quan trọng nhất.** Nó là câu hỏi duy nhất chứng minh việc ghép hai nửa có giá trị — chứ không phải hai đồ án dán vào nhau. Và nó kiểm chứng được bằng dữ liệu TomTom bạn đang thu từ ngày 1. Đặt nó làm trục của đề cương.

### 3.3 Mục tiêu SMART

- **MT1.** Xây dựng đồ thị đường Đà Nẵng đã làm sạch và bổ khuyết thuộc tính, công bố bảng tốc độ dòng tự do thực đo thay cho giá trị mặc định OSM
- **MT2.** Xây dựng bộ dữ liệu `DaNang-Traffic` ≥1.500 ảnh gán nhãn ≥4 lớp, chia tập **theo điểm quay**, công bố có DOI
- **MT3.** Fine-tune RF-DETR đạt mAP50 ≥ [đặt ngưỡng theo kết quả tuần 2] và **định lượng khoảng cách miền** so với mô hình gốc
- **MT4.** Đường ống đếm xe đạt **GEH < 5 tại ≥85% điểm đếm** so với đếm tay
- **MT5.** Chứng minh trọng số động cải thiện ước lượng thời gian hành trình so với trọng số tĩnh, đối chứng độc lập bằng TomTom (CH2)
- **MT6.** Cài đặt SSSP có trọng số phân tán trên Spark, xác định **ngưỡng quy mô** mà xử lý phân tán vượt trội một máy
- **MT7.** Hiệu chỉnh SUMO đạt chuẩn GEH và định lượng ≥2 kịch bản phân luồng có kiểm định thống kê
- **MT8.** Triển khai hệ thống web công khai với đủ 5 thao tác demo

Viết MT3 theo hướng **"định lượng khoảng cách"** chứ không phải **"đạt mAP ≥ X"** — đây là bài học rút từ MT3 của đề cương cũ: đừng cam kết một con số cải thiện mà bạn chưa đo được.

### 3.4 Phạm vi — nói rõ cái KHÔNG làm

- Không xây hệ thống camera mới
- Không mô phỏng vi mô toàn thành phố — **giới hạn ở một hành lang 3–5 km**
- Không triển khai vận hành thực tế; dừng ở nguyên mẫu và đánh giá ngoại tuyến
- Không dùng mô hình ngôn ngữ lớn / VLM
- Không thử nghiệm can thiệp giao thông ngoài đời — chỉ mô phỏng

Mục này bảo vệ bạn ở buổi bảo vệ. Đề cương cũ của bạn viết rất tốt phần này, giữ nguyên cách viết.

### 3.5 Đạo đức và pháp lý

- **Nghị định 13/2023/NĐ-CP** về bảo vệ dữ liệu cá nhân — không lưu ảnh có khuôn mặt/biển số nhận dạng được; pipeline chỉ ghi bounding box + nhãn + mốc thời gian
- Làm mờ biển số và khuôn mặt trong mọi ảnh minh hoạ
- Rà soát bộ dữ liệu trước khi công bố lên Zenodo
- Tuân thủ điều khoản TomTom/HERE; tránh Google Directions cho lưu trữ dài hạn
- Không dùng flycam nếu chưa có phép bay

### 3.6 Bối cảnh chính sách — dùng cho phần lý do chọn đề tài

Bốn văn bản năm 2026 cho thấy đề tài nằm đúng dòng chính sách quốc gia:

| Văn bản | Nội dung |
|---|---|
| **QĐ 456/QĐ-TTg ngày 20/3/2026** | Đề án Trung tâm dữ liệu, quản lý, giám sát, xử lý vi phạm và điều hành giao thông 2026–2030, tầm nhìn 2050 |
| **QĐ 502/QĐ-TTg 2026** | Kết nối, chia sẻ dữ liệu camera giám sát với CSDL quốc gia |
| **QCVN 11:2026/BCA** | Quy chuẩn kỹ thuật quốc gia về camera giám sát |
| **QĐ 804/QĐ-TTg ngày 06/5/2026** | Danh mục bộ dữ liệu phục vụ phát triển **trí tuệ nhân tạo** — củng cố lập luận cho đóng góp bộ dữ liệu |
| **QĐ 804/QĐ-UBND ngày 05/3/2026** (Đà Nẵng) | Danh mục dữ liệu mở: 14 lĩnh vực, 211 mục, GTVT 19 mục gồm camera giám sát |

*Cẩn thận kẻo nhầm: 804/QĐ-**TTg** (Thủ tướng, dữ liệu AI) khác 804/QĐ-**UBND** (Đà Nẵng, dữ liệu mở) — trùng số, khác cấp.*

Bối cảnh hạ tầng để trích: Đà Nẵng có **gần 170 camera tại 71 điểm/tuyến**; IOC khai trương 8/2023.

---

## Sản phẩm bàn giao của GĐ0

- [ ] Job TomTom **đang chạy**, đã có ≥3 tuần dữ liệu
- [ ] `docs/khao-sat-opendata.md` — kết quả khảo sát cổng dữ liệu mở
- [ ] Bảng thống kê đồ thị OSM, **cả hai phạm vi** (Đà Nẵng cũ / + Quảng Nam)
- [ ] Hành lang nghiên cứu đã chốt + `data/sites.csv` 6–12 điểm đã khảo sát thực địa
- [ ] `results/g0_baseline_gap.csv` — **tỷ lệ sót xe máy của RF-DETR và YOLO gốc**
- [ ] Mô hình và bộ lớp phương tiện đã chốt
- [ ] **Đề cương hoàn chỉnh**, có 4 con số thật thay vì "dự kiến"

## Cổng G0 — điều kiện sang GĐ1

Đề cương được GVHD thông qua và bảo vệ trước bộ môn. **Không đầu tư vào gán nhãn quy mô lớn trước khi qua cổng này** — nếu hội đồng yêu cầu đổi hướng, bạn chỉ mất 5 tuần thay vì 5 tháng.

---

## Rủi ro giai đoạn này

| Rủi ro | Xử lý |
|---|---|
| **Tỷ lệ sót xe máy quá thấp (<15%)** → luận điểm yếu | Phát hiện ngay tuần 2, còn kịp đổi trọng tâm sang đánh giá phân tầng theo điều kiện, hoặc sang bài toán đếm thay vì phát hiện |
| Cổng dữ liệu mở không có gì dùng được | Đã lường trước — tự quay là xương sống. Ghi kết quả khảo sát vào đề cương như một đóng góp nhỏ (hiện trạng dữ liệu mở giao thông Đà Nẵng) |
| Ranh giới Đà Nẵng mới chưa có trong OSM | Dùng bbox thủ công, ghi rõ trong đề cương |
| Không tìm được hành lang có đủ chỗ đặt máy | Khảo sát 2–3 hành lang ứng viên ngay tuần 1, đừng cược vào một cái |
| Viết đề cương lâu hơn 3 tuần | Dùng lại cấu trúc đề cương cũ — bạn đã có template đạt chuẩn, chỉ thay nội dung |
