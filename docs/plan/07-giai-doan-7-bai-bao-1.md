# Giai đoạn 7 — Bài báo 1: Thị giác máy tính (Tuần 17–26)

> **Tiêu đề dự kiến:** *Fine-tuning YOLOv11 for Motorcycle-Dominant Mixed Traffic: A Vehicle Counting Dataset and Benchmark from Da Nang, Vietnam*

Bài này viết được ngay sau GĐ3, không cần chờ GĐ4–GĐ5. Đó là lý do nó đi trước.

---

## 1. Luận điểm của bài (một câu)

> Các mô hình phát hiện phương tiện huấn luyện trên dữ liệu giao thông phương Tây suy giảm đáng kể trên giao thông hỗn hợp do xe máy chi phối ở Việt Nam; chúng tôi định lượng khoảng cách miền này, công bố bộ dữ liệu đầu tiên cho Đà Nẵng, và cho thấy fine-tune với lượng dữ liệu khiêm tốn thu hẹp phần lớn khoảng cách đó.

Ba đóng góp tuyên bố:
1. **Bộ dữ liệu** `DaNang-Traffic-2026` có DOI, chia tập theo điểm quay
2. **Định lượng domain gap** — có phân tầng theo điều kiện (mưa/đêm/mật độ cao)
3. **Đường ống đếm đã đối chứng** bằng đếm tay theo chuẩn GEH của ngành giao thông

Đóng góp 1 và 3 là thứ khiến bài này khác với hàng nghìn bài "áp dụng YOLO đếm xe". Nhấn mạnh chúng.

---

## 2. Chọn nơi gửi

| Venue | Loại | Đánh giá |
|---|---|---|
| **IAENG *Engineering Letters*** | Tạp chí, Scopus | Nhận bài quanh năm, quy trình vừa phải — đích chính |
| **IAENG *IJCS*** | Tạp chí, Scopus | Tương tự, hợp với phần đồ thị hơn → để dành cho bài 2 |
| **FAIR** | Hội thảo quốc gia VN | Uy tín tốt trong nước, kỷ yếu có ISBN; phù hợp nếu lịch khớp |
| KSE / RIVF / NICS / SoICT | Hội thảo IEEE tại VN | Có kỷ yếu IEEE Xplore — **uy tín cao hơn IAENG**, đáng cân nhắc nghiêm túc |
| ACIIDS | Hội thảo Springer LNAI | Khu vực châu Á, chất lượng khá |
| IEEE Access | Tạp chí Q1 | Uy tín cao nhưng phí xuất bản lớn (~$2.000) |

**Hai lưu ý cần kiểm tra trước khi gửi:**

1. **Xác minh tình trạng chỉ mục Scopus của venue tại thời điểm gửi.** Danh mục Scopus thay đổi và có tạp chí bị ngừng chỉ mục. Tra cứu trực tiếp trên trang Scopus Sources.
2. **Kiểm tra quy định của trường** về việc bài báo được tính cho luận văn: một số chương trình yêu cầu tạp chí thuộc một hạng quartile nhất định hoặc hội thảo có kỷ yếu IEEE/Springer. Hỏi rõ trước khi bỏ công.

Nếu trường chấp nhận, một hội thảo IEEE tại Việt Nam (KSE, RIVF, NICS, SoICT) thường là lựa chọn cân bằng tốt hơn giữa uy tín và khả năng được nhận.

---

## 3. Bố cục và mốc thời gian

| Tuần | Việc | Đầu ra |
|---|---|---|
| T17–18 | Khảo sát tài liệu — 40–60 bài | File Zotero/Mendeley + bảng tổng hợp |
| T19 | Dàn ý chi tiết + chốt các bảng/hình | Danh sách bảng-hình trước khi viết chữ nào |
| T20–21 | Viết Phương pháp + Bộ dữ liệu | 4–5 trang |
| T22 | Viết Thực nghiệm + Kết quả | 3–4 trang |
| T23 | Viết Mở đầu + Liên quan | 2–3 trang |
| T24 | Viết Thảo luận + Kết luận + Tóm tắt | 1–2 trang |
| T25 | Rà soát, biên tập ngôn ngữ, định dạng theo mẫu | Bản hoàn chỉnh |
| T26 | Giáo viên hướng dẫn duyệt → **GỬI** | Mã bản thảo |

**Quy tắc:** chốt danh sách bảng và hình *trước* khi viết câu nào. Bài báo là các bảng biểu được nối bằng văn xuôi, không phải ngược lại.

---

## 4. Danh sách bảng và hình bắt buộc

| Mã | Nội dung | Nguồn |
|---|---|---|
| Bảng 1 | Thống kê bộ dữ liệu: ảnh/lớp, ảnh/điểm, theo thời tiết và khung giờ | GĐ2 |
| Bảng 2 | So sánh với các bộ dữ liệu giao thông hiện có | Khảo sát |
| **Bảng 3** | **B0/B1/B2 — mAP50, mAP50-95, AP từng lớp, FPS** | **Con số #1** |
| Bảng 4 | Đánh giá phân tầng theo điều kiện | GĐ3 |
| Bảng 5 | Thí nghiệm loại trừ: `imgsz`, augmentation | GĐ3 |
| **Bảng 6** | **Đối chứng đếm: MAE, MAPE, GEH** | **Con số #2** |
| Hình 1 | Bản đồ 12 điểm quay + ảnh mẫu | GĐ2 |
| Hình 2 | Sơ đồ đường ống phát hiện → bám vết → đếm | |
| Hình 3 | Ảnh định tính: B0 sót xe vs B2 phát hiện đúng | **Hình thuyết phục nhất** |
| Hình 4 | Phân tích lỗi — 6 trường hợp sai điển hình | GĐ3 |
| Hình 5 | Đường cong huấn luyện / ma trận nhầm lẫn | |

Hình 3 là hình quan trọng nhất về mặt trực quan: hai ảnh cùng cảnh, một bên mô hình gốc bỏ sót hàng chục xe máy, một bên mô hình của bạn bắt hết. Nó truyền tải luận điểm nhanh hơn mọi bảng số.

---

## 5. Khảo sát tài liệu — nhóm theo 4 mảng

1. **Phát hiện phương tiện bằng học sâu** — dòng YOLO, RT-DETR, các bài so sánh
2. **Đếm xe và bám vết** — DeepSORT, ByteTrack, đếm qua vạch/vùng, AI City Challenge
3. **Giao thông hỗn hợp / xe máy chi phối** — nghiên cứu từ Việt Nam, Đài Loan, Indonesia, Ấn Độ. **Đây là mảng quan trọng nhất để định vị đóng góp**
4. **Bộ dữ liệu giao thông** — MIO-TCD, UA-DETRAC, VisDrone, BDD100K, AI City

Nguồn: Google Scholar, Semantic Scholar, IEEE Xplore, arXiv. Ưu tiên bài 2022 trở lại đây; giữ vài bài kinh điển làm nền.

Tuyệt đối tránh: trích dẫn bài mình chưa đọc, và trích dẫn từ danh sách do công cụ AI sinh ra mà không kiểm chứng — trích dẫn sai hoặc không tồn tại là lỗi nghiêm trọng, bị phát hiện dễ và hậu quả nặng.

---

## 6. Lời khuyên viết bài

**Phần Mở đầu — công thức 4 đoạn:**
1. Bối cảnh: đô thị hoá, tắc nghẽn, nhu cầu dữ liệu giao thông ở Việt Nam
2. Khoảng trống: giao thông xe máy chi phối khác căn bản; mô hình và bộ dữ liệu hiện có không phù hợp; **chưa có bộ dữ liệu công khai cho Đà Nẵng**
3. Đóng góp: liệt kê 3 gạch đầu dòng
4. Cấu trúc bài

**Cách nói về hạn chế:** nêu thẳng trong phần Thảo luận — số điểm quay hạn chế, chỉ một thành phố, chưa thử nghiệm ban đêm sâu, thiết bị quay là điện thoại. Reviewer luôn tìm ra hạn chế; bạn nêu trước thì đó là sự chín chắn, họ tìm ra trước thì đó là điểm yếu.

**Ngôn ngữ:** viết câu ngắn. Nếu tiếng Anh không phải thế mạnh, dùng công cụ hỗ trợ ngữ pháp rồi nhờ người rà lại, nhưng **giữ nội dung khoa học là của mình**. Reviewer phân biệt được văn xuôi trống rỗng và văn xuôi có nội dung.

**Định dạng:** dùng đúng mẫu của venue ngay từ đầu (đã có `FAIR2026_IEEE_a4.docx` trong thư mục gốc). Đừng viết bằng định dạng khác rồi chuyển đổi vào phút chót.

---

## 7. Sau khi gửi

- Thời gian chờ phản hồi: vài tuần đến vài tháng tuỳ venue
- **Không ngồi chờ.** Chuyển ngay sang GĐ8 và viết luận văn
- Khi có phản biện: trả lời **từng ý một** trong bảng phản hồi, lịch sự, kể cả với nhận xét bạn không đồng ý. Nếu không đồng ý, giải thích bằng lý lẽ và dữ liệu
- Nếu bị từ chối: đọc kỹ nhận xét, sửa, gửi venue khác. **Bị từ chối là chuyện bình thường**, không phải dấu hiệu bài dở. Chuẩn bị sẵn danh sách venue thứ hai và thứ ba từ trước

## Sản phẩm bàn giao

- [ ] Bản thảo hoàn chỉnh đúng định dạng venue
- [ ] Đủ 6 bảng, 5 hình
- [ ] Thư mục tài liệu 40–60 mục, đã đọc thật
- [ ] Giáo viên hướng dẫn đã duyệt
- [ ] **Đã gửi, có mã bản thảo** (cổng G7, T26)
- [ ] Bộ dữ liệu đã lên Zenodo, có DOI, trích dẫn trong bài
