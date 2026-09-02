# Giai đoạn 8 — Bài báo 2: Dữ liệu lớn và đồ thị (Tuần 25–34)

> **Tiêu đề dự kiến:** *A Spark-Based Framework for Dynamic Urban Road Network Analysis Calibrated by Computer-Vision Traffic Counts: A Case Study of Da Nang, Vietnam*

Bài này là **bài quan trọng hơn về mặt học thuật** vì nó thể hiện toàn bộ hệ thống, và nó ứng với đúng trục "dữ liệu lớn" của chương trình. Viết sau khi GĐ4 và GĐ5 xong.

---

## 1. Luận điểm của bài (một câu)

> Đồ thị đường đô thị từ dữ liệu mở thiếu trọng số động phản ánh lưu lượng thực; chúng tôi đề xuất một khung xử lý phân tán trên Spark gắn số đếm phương tiện từ thị giác máy tính vào đồ thị OSM, phân tích ở quy mô nhiều lát cắt thời gian và nhiều kịch bản, rồi kiểm chứng bằng mô phỏng vi mô đã hiệu chỉnh theo chuẩn GEH.

Bốn đóng góp tuyên bố:
1. **Khung tích hợp** thị giác máy tính ↔ đồ thị ↔ mô phỏng, khép kín từ dữ liệu thô đến khuyến nghị
2. **Cài đặt SSSP có trọng số phân tán** trên Spark DataFrame (do GraphFrames không hỗ trợ) + phân tích khả năng mở rộng có chỉ rõ điểm giao
3. **Hiệu chỉnh tốc độ dòng tự do thực đo cho Đà Nẵng** thay cho giá trị mặc định của OSM
4. **Định lượng hiệu quả các kịch bản phân luồng** có kiểm định thống kê

---

## 2. Cấu trúc bài — trục lập luận phải khép kín

Đây là điểm mạnh nhất của bài, phải làm nổi bật ngay ở Hình 1:

```
Video thực địa
   → đếm xe (đã đối chứng GEH<5)
   → quy đổi PCU
   → trọng số cạnh qua hàm BPR
   → phân tích trên Spark: SSSP, độ trung tâm, tính bền vững
   → xác định đoạn/nút trọng yếu
   → thiết kế kịch bản can thiệp XUẤT PHÁT TỪ chính kết quả phân tích
   → mô phỏng SUMO đã hiệu chỉnh
   → định lượng mức cải thiện
```

Mỗi mũi tên phải có căn cứ trong bài. Chuỗi khép kín này là thứ phân biệt bài của bạn với các bài chỉ chạy thuật toán đồ thị trên dữ liệu OSM rồi dừng.

---

## 3. Danh sách bảng và hình bắt buộc

| Mã | Nội dung | Nguồn |
|---|---|---|
| Bảng 1 | Đặc trưng đồ thị: đỉnh, cạnh, phân bố loại đường, tỷ lệ thiếu thuộc tính | GĐ1 |
| Bảng 2 | **Tốc độ dòng tự do: mặc định OSM vs thực đo từ TomTom** | GĐ4 |
| Bảng 3 | Tham số BPR đã hiệu chỉnh + hệ số PCU cho giao thông xe máy | GĐ4 |
| **Bảng 4** | **Khả năng mở rộng: 1/2/3/5 node × các quy mô đồ thị × số lát cắt** | GĐ4 |
| Bảng 5 | Top-20 đoạn đường theo độ trung tâm trung gian, theo khung giờ | GĐ4 |
| Bảng 6 | Hiệu chỉnh SUMO: GEH qua từng vòng lặp | GĐ5 |
| Bảng 7 | Kiểm chứng chéo: tốc độ mô phỏng vs tốc độ TomTom | GĐ5 |
| **Bảng 8** | **Kết quả kịch bản: trễ, tốc độ, hàng chờ, phát thải — TB ± ĐLC + kiểm định** | **Con số #3** |
| **Hình 1** | **Sơ đồ khung tổng thể (trục lập luận ở mục 2)** | **Hình quan trọng nhất** |
| Hình 2 | Kiến trúc Lambda: tầng batch / tầng serving | |
| **Hình 3** | **Biểu đồ speedup có ĐIỂM GIAO với đường một-máy** | GĐ4 |
| Hình 4 | Bản đồ nhiệt độ trung tâm trung gian theo khung giờ | GĐ4 |
| Hình 5 | So sánh trực quan mạng lưới trước/sau kịch bản | GĐ5 |
| Hình 6 | Ảnh chụp màn hình hệ thống + link demo | GĐ6 |

---

## 4. Cách xử lý câu hỏi khó nhất

> *"Đồ thị 50.000 đỉnh — một laptop chạy xong trong 2 giây. Spark để làm gì?"*

**Đừng né. Đưa nó thành một mục riêng trong bài.** Cấu trúc trả lời:

1. Thừa nhận thẳng: một đồ thị đơn lẻ ở quy mô này xử lý được trên một máy
2. Chỉ ra khối lượng thật là tích các chiều: cặp OD × lát cắt thời gian × kịch bản ≈ 1,9 triệu lần tính đường đi, cộng độ trung tâm trung gian O(|V||E|)
3. **Đưa số liệu thực nghiệm** cho thấy đường một-máy và đường Spark cắt nhau ở đâu (Hình 3)
4. Kết luận có điều kiện: khung phân tán có lợi khi vượt ngưỡng X, và ngưỡng đó nằm trong phạm vi ứng dụng thực tế của bài toán quy hoạch giao thông đô thị

Sự trung thực này **mạnh hơn** việc cố thổi phồng quy mô dữ liệu. Reviewer nhìn ra ngay các con số bị làm màu, còn một phân tích có điểm giao rõ ràng thì thuyết phục và trích dẫn được.

---

## 5. Mốc thời gian

| Tuần | Việc |
|---|---|
| T25–26 | Khảo sát tài liệu mảng 2 (xem mục 6) |
| T27 | Dàn ý + chốt danh sách bảng/hình |
| T28–29 | Viết Phương pháp (khung, BPR, Spark, hiệu chỉnh) |
| T30–31 | Viết Thực nghiệm + Kết quả |
| T32 | Viết Mở đầu, Liên quan, Thảo luận |
| T33 | Rà soát, biên tập, định dạng |
| T34 | GVHD duyệt → **GỬI** |

Giai đoạn này chồng với việc viết luận văn (từ T29). Điều đó là cố ý và có lợi: **chương 4–5 của luận văn và bài báo 2 dùng chung phần lớn nội dung**. Viết một lần, dùng hai chỗ — nhưng nhớ diễn đạt lại, không sao chép nguyên khối giữa hai văn bản.

---

## 6. Khảo sát tài liệu — 4 mảng

1. **Xử lý đồ thị phân tán** — Pregel, GraphX, GraphFrames, delta-stepping, so sánh các nền tảng đồ thị
2. **Phân tích mạng lưới đô thị** — OSMnx, độ trung tâm trong mạng đường, tính bền vững mạng lưới
3. **Mô hình gán luồng giao thông** — hàm BPR, gán cân bằng người dùng, hiệu chỉnh mô hình, chuẩn GEH
4. **Thành phố thông minh / bản sao số giao thông** — các bài tích hợp cảm biến với mô hình mạng lưới

Mảng 1 là chỗ nối trực tiếp về danh sách đề tài gốc: cài Bellman-Ford phân tán chính là *"nghiên cứu mô hình MapReduce cho thuật toán Bellman-Ford"*, nhưng ở đây có ứng dụng thật thay vì chỉ là bài tập thuật toán. Nhấn mạnh điều này trong phần Liên quan.

---

## 7. Nơi gửi

- **IAENG *IJCS*** — đích chính, hợp chủ đề khoa học máy tính/hệ thống
- **KSE / RIVF / SoICT** (IEEE, Việt Nam) — uy tín cao hơn, đáng cân nhắc nếu lịch khớp
- *Journal of Big Data* (Springer, mở, có phí) — nếu có kinh phí
- *ISPRS International Journal of Geo-Information* (MDPI, Q2, có phí) — rất hợp chủ đề không gian
- *IEEE Access* — nếu có kinh phí và muốn Q1

Kiểm tra tình trạng chỉ mục Scopus tại thời điểm gửi và quy định của trường về hạng tạp chí, giống như đã lưu ý ở [bài báo 1](07-giai-doan-7-bai-bao-1.md).

---

## Sản phẩm bàn giao

- [ ] Bản thảo hoàn chỉnh
- [ ] Đủ 8 bảng, 6 hình
- [ ] Mục riêng trả lời câu hỏi "vì sao cần Spark", có số liệu
- [ ] Link demo công khai + repo public trong bài
- [ ] Đã gửi, có mã bản thảo

## Nếu trễ tiến độ

Bài báo 2 là hạng mục **đầu tiên bị cắt** theo thứ tự ưu tiên ở [00-tong-quan.md](00-tong-quan.md). Hoãn nó sang sau bảo vệ là quyết định hợp lý và thường xuyên xảy ra. Toàn bộ nội dung đã nằm sẵn trong chương 4–5 luận văn, nên viết lại thành bài báo sau khi bảo vệ chỉ tốn 2–3 tuần, trong điều kiện thảnh thơi hơn nhiều.

**Không được đánh đổi:** không bao giờ hy sinh tiến độ luận văn để kịp bài báo 2.
