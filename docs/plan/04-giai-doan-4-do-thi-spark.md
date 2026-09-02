# Giai đoạn 4 — Đồ thị và xử lý phân tán (Tuần 13–20)

> **Mục tiêu:** Biến đồ thị OSM tĩnh thành đồ thị có trọng số động, và chứng minh tầng xử lý phân tán là **cần thiết** chứ không phải trang trí.

Giai đoạn này chạy song song với GĐ3 và **không phụ thuộc vào nó** — dùng dữ liệu đếm giả lập cho đến khi GĐ3 xong. Khi bí ở YOLO thì chuyển sang đây, đừng ngồi chờ.

---

## 1. Câu hỏi phải trả lời được trước khi bắt đầu

> *"Đồ thị của bạn chỉ có 50.000 đỉnh. Một máy tính xách tay chạy `igraph` xử lý xong trong 2 giây. Vậy Spark để làm gì?"*

Đây là câu hỏi mà **cả phản biện luận văn lẫn reviewer bài báo đều sẽ hỏi**. Nếu không có câu trả lời, toàn bộ phần "dữ liệu lớn" của đề tài sụp đổ.

Câu trả lời trung thực và đúng: **khối lượng tính toán không nằm ở kích thước đồ thị, mà ở tích của các chiều.**

| Chiều | Quy mô |
|---|---|
| Đỉnh | ~50.000 (Đà Nẵng cũ) đến ~150.000 (sau sáp nhập) |
| Lát cắt thời gian | 24 giờ × 2 loại ngày = 48 đồ thị có trọng số khác nhau |
| Kịch bản phân luồng | 4 |
| Cặp điểm đi–đến cần định tuyến | 10.000+ |
| **Tổng số lần tính đường đi** | **10.000 × 48 × 4 ≈ 1,9 triệu** |

Cộng thêm:
- **Độ trung tâm trung gian (betweenness centrality)** trên 150k đỉnh — độ phức tạp O(|V||E|), thực sự không khả thi trên một máy, phải lấy mẫu và phân tán
- Chuỗi thời gian đếm xe: hàng chục triệu bản ghi cần tổng hợp theo nhiều chiều
- Khối lượng khung hình video đã xử lý: hàng trăm triệu

**Cách trình bày trong luận văn:** đừng giấu việc một đồ thị đơn lẻ có thể xử lý trên một máy. Nói thẳng ra, rồi chỉ ra ngưỡng mà cách đó sụp đổ — kèm số liệu thực nghiệm. Sự trung thực đó mạnh hơn nhiều so với việc cố thổi phồng quy mô dữ liệu. **Phải có một biểu đồ: thời gian chạy theo số lát cắt thời gian, đường một-máy vs đường Spark, và chỉ rõ điểm giao nhau.**

---

## 2. Làm sạch và làm giàu đồ thị (Tuần 13–14)

### 2.1 Chuẩn hoá

- Giữ thành phần liên thông mạnh lớn nhất (loại các đoạn cụt, đảo cô lập)
- Đơn giản hoá hình học nhưng **giữ nguyên topology** (`ox.simplify_graph`)
- Xử lý đường một chiều, cấm rẽ (`turn restrictions` từ quan hệ OSM)
- Gán `edge_id` ổn định — **quan trọng**: id này là khoá nối với dữ liệu đếm xe, phải bất biến giữa các lần chạy

### 2.2 Bổ khuyết thuộc tính — một đóng góp chính danh của luận văn

Phần lớn cạnh trong OSM Việt Nam thiếu `maxspeed` và `lanes`. Chiến lược 3 tầng:

1. **Có sẵn trong OSM** → dùng trực tiếp
2. **Suy luận theo luật** → bảng mặc định theo `highway=*` (motorway 80, trunk 60, primary 50, secondary 40, residential 30…), có điều chỉnh theo đô thị/ngoại thành
3. **Học từ dữ liệu** → dùng chuỗi thời gian tốc độ TomTom đã thu để **học tốc độ dòng tự do thực tế** theo loại đường: lấy phân vị 85 của tốc độ quan sát trong giờ thấp điểm

Tầng 3 là phần có giá trị nghiên cứu: nó cho ra một bảng tốc độ tự do **thực đo cho Đà Nẵng**, khác với giá trị mặc định của OSM. Báo cáo bảng so sánh giữa giá trị mặc định và giá trị thực đo — đây là một kết quả có thể trích dẫn.

### 2.3 Ánh xạ điểm đếm lên cạnh (map matching)

Mỗi `site_id` phải gắn vào đúng `edge_id`. Với vài chục điểm thì làm thủ công + kiểm tra trực quan là đủ và đáng tin hơn tự động. Ghi ra `data/site_edge_mapping.csv` với ảnh chụp màn hình minh chứng cho từng điểm.

---

## 3. Mô hình trọng số động (Tuần 15–16)

### 3.1 Từ số đếm sang thời gian di chuyển

Dùng **hàm BPR (Bureau of Public Roads)** — chuẩn mực trong kỹ thuật giao thông:

```
t = t0 * ( 1 + α * (V/C)^β )

t0 = chiều dài / tốc độ dòng tự do
V  = lưu lượng (PCU/giờ) từ pipeline thị giác
C  = năng lực thông hành của cạnh
α = 0.15, β = 4  (giá trị kinh điển; nên hiệu chỉnh lại cho VN)
```

**Vấn đề then chốt: xác định C (năng lực thông hành) cho giao thông hỗn hợp xe máy chi phối.** Giá trị trong sách giáo khoa phương Tây không áp dụng được. Cần tra TCVN, các nghiên cứu về giao thông xe máy ở Việt Nam/Đài Loan/Indonesia, và ghi rõ nguồn. Nếu hiệu chỉnh được α, β từ dữ liệu tốc độ TomTom của chính mình thì **đó là một đóng góp đáng kể của luận văn** — hồi quy quan hệ giữa lưu lượng quan sát và tốc độ quan sát.

### 3.2 Ngoại suy cho cạnh không có điểm đếm

Chỉ ~12 cạnh có số đếm thật, còn 150.000 cạnh thì không. Ba cách, nên làm cả ba và so sánh:

| Cách | Mô tả | Ưu/nhược |
|---|---|---|
| Theo lớp đường | Nhân lưu lượng trung bình của cạnh cùng `highway=*` | Đơn giản, thô |
| Theo trọng số không gian | Lan truyền từ điểm đếm gần nhất theo khoảng cách mạng lưới | Tốt hơn, vẫn thô |
| **Kiểm định bằng TomTom** | Dùng tốc độ TomTom trên các đoạn có dữ liệu để **kiểm chứng** giá trị ngoại suy | Đây là phần biến ước lượng thành có căn cứ |

Cách thứ ba là chỗ dữ liệu TomTom bạn thu từ tuần 1 phát huy giá trị — nó cho bạn ground truth trên hàng chục đoạn thay vì chỉ 12 điểm đếm.

---

## 4. Tính toán trên Spark (Tuần 17–19)

### 4.1 Cảnh báo kỹ thuật quan trọng về GraphFrames

**`GraphFrames.shortestPaths()` chỉ tính đường đi ngắn nhất KHÔNG TRỌNG SỐ (BFS theo số cạnh).** Nó không dùng được cho bài toán này, vì bạn cần đường nhanh nhất theo thời gian di chuyển.

Ba lựa chọn:

| Cách | Đánh giá |
|---|---|
| Pregel API của GraphX | Chỉ có Scala, không có Python |
| **Tự cài Bellman-Ford / delta-stepping bằng vòng lặp join trên DataFrame** | **Khuyến nghị** |
| Tính ngoài Spark bằng `igraph`, chỉ dùng Spark để song song hoá theo lát cắt thời gian | Phương án dự phòng hợp lệ |

**Cách khuyến nghị chính là điểm nối tuyệt đẹp về lại danh sách đề tài gốc:** cài đặt Bellman-Ford phân tán bằng các vòng lặp join chính là "nghiên cứu mô hình MapReduce cho thuật toán Bellman-Ford" — một trong các đề tài trong file gốc, nhưng ở đây nó có ứng dụng thật thay vì chỉ là bài tập.

Lưu ý triển khai bắt buộc:
- **Checkpoint sau mỗi 3–5 vòng lặp** để cắt lineage, nếu không Spark sẽ tràn bộ nhớ khi kế hoạch thực thi dài ra
- Phân vùng (partition) theo đỉnh nguồn để giảm shuffle
- Cache bảng cạnh, broadcast nếu đủ nhỏ

### 4.2 Các bài toán phân tích

| Bài toán | Cài đặt | Ý nghĩa giao thông |
|---|---|---|
| SSSP có trọng số, đa nguồn | Bellman-Ford lặp trên DataFrame | Định tuyến, ma trận thời gian |
| **Độ trung tâm trung gian (có lấy mẫu)** | Brandes trên tập nguồn lấy mẫu, phân tán theo nguồn | **Xác định đoạn đường trọng yếu** — kết quả có giá trị chính sách cao nhất |
| Độ trung tâm gần | Từ ma trận SSSP | Khả năng tiếp cận |
| Phát hiện cộng đồng (Louvain / LPA) | GraphFrames LPA | Phân vùng giao thông tự nhiên |
| Phân tích tính bền vững | Loại từng cạnh trọng yếu, đo mức tăng thời gian đi lại toàn mạng | **Kịch bản "nếu cầu X đóng"** — rất hấp dẫn |

Hai dòng in đậm là hai kết quả đáng giá nhất về mặt ứng dụng. Bản đồ độ trung tâm trung gian của Đà Nẵng theo từng khung giờ là một hình ảnh mạnh cho cả bài báo lẫn buổi bảo vệ.

### 4.3 Đo khả năng mở rộng — **bắt buộc, đây là phần chứng minh "Big Data"**

Thiết kế thí nghiệm:

| Trục biến thiên | Các mức |
|---|---|
| Số node Spark | 1, 2, 3, 5 |
| Kích thước đồ thị | Đà Nẵng cũ / +Quảng Nam / nhân bản × 2, × 4 để đẩy quy mô |
| Số lát cắt thời gian | 1, 6, 24, 48 |

Báo cáo: thời gian chạy, **tăng tốc (speedup)**, **hiệu suất song song (efficiency)**, và so sánh với đường cơ sở một máy (`igraph`/`NetworkX`).

Trung thực về kết quả: ở quy mô nhỏ, Spark **chậm hơn** một máy do chi phí khởi tạo và shuffle. Hãy chỉ rõ ngưỡng giao nhau. Một biểu đồ có điểm giao rõ ràng thuyết phục hơn nhiều so với việc chỉ khoe Spark nhanh.

### 4.4 Cấu hình cụm

Bản tối thiểu: 3 node Docker trên một máy (`docker-compose` với 1 master + 2 worker). Đủ để đo speedup, và hợp lệ về mặt học thuật nếu ghi rõ cấu hình.

Bản đầy đủ: 3–5 máy thật trong phòng lab, hoặc Spark trên Oracle Cloud Always Free (4 nhân ARM, 24GB RAM là đủ cho một cụm nhỏ thật).

---

## 5. Vật chất hoá kết quả cho tầng phục vụ (Tuần 20)

Xuất ra các khung nhìn mà web app sẽ đọc — xem hợp đồng dữ liệu chi tiết ở [B-kien-truc-ky-thuat.md](B-kien-truc-ky-thuat.md):

```
serving/
├── edges.pmtiles              # hình học + trọng số 24 khung giờ
├── edge_metrics.parquet       # betweenness, tốc độ, V/C theo giờ
├── site_counts.parquet        # chuỗi thời gian đếm xe
├── od_matrix.parquet          # thời gian đi lại giữa các cặp điểm chính
└── scenarios/                 # kết quả kịch bản (điền ở GĐ5)
```

Nguyên tắc: **tầng phục vụ chỉ đọc, không tính.** Mọi phép tính nặng đã xong ở tầng batch.

---

## Sản phẩm bàn giao của GĐ4

- [ ] `pipeline/graph/` — làm sạch, bổ khuyết thuộc tính, ánh xạ điểm đếm
- [ ] Bảng so sánh tốc độ tự do: mặc định OSM vs thực đo từ TomTom
- [ ] Mô hình BPR có tham số hiệu chỉnh cho điều kiện Đà Nẵng
- [ ] Cài đặt Bellman-Ford phân tán trên Spark, có checkpoint
- [ ] Bản đồ độ trung tâm trung gian theo khung giờ
- [ ] Phân tích tính bền vững — kịch bản đóng cạnh trọng yếu
- [ ] `results/scalability.csv` + biểu đồ có điểm giao nhau
- [ ] Các file trong `serving/` đã sinh
- [ ] `docs/nhat-ky/04-do-thi-spark.md` (~10 trang → chương 4 luận văn)

## Tiêu chí hoàn thành

Chạy được một lệnh sinh lại toàn bộ `serving/` từ dữ liệu thô. Và trả lời được bằng số liệu câu hỏi ở mục 1.

---

## Rủi ro giai đoạn này

| Rủi ro | Xử lý |
|---|---|
| **Spark tràn bộ nhớ ở vòng lặp Bellman-Ford** | Checkpoint thường xuyên hơn; tăng `spark.sql.shuffle.partitions`; giảm số nguồn mỗi lô |
| **Spark chậm hơn một máy ở mọi quy mô thử** | Đây là kết quả hợp lệ — hãy nhân bản đồ thị để đẩy quy mô lên và tìm cho ra điểm giao. Nếu không có điểm giao, chuyển luận điểm sang song song hoá theo lát cắt/kịch bản (embarrassingly parallel), vẫn hợp lệ |
| Không tìm được hệ số năng lực thông hành cho xe máy | Dùng giá trị từ nghiên cứu Đài Loan/Indonesia, ghi rõ nguồn và coi là hạn chế; hoặc hiệu chỉnh ngược từ dữ liệu TomTom |
| Ánh xạ điểm đếm lên cạnh sai | Kiểm tra trực quan từng điểm, lưu ảnh chụp màn hình làm minh chứng |
| Đồ thị sau sáp nhập quá lớn, máy không chịu nổi | Lùi về Đà Nẵng cũ cho các thí nghiệm chính, dùng đồ thị lớn chỉ cho phần đo scalability |
