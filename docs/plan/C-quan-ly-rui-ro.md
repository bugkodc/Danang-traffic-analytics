# Phụ lục C — Sổ rủi ro

Rà lại file này **mỗi tháng một lần**. Đánh dấu rủi ro nào đã hết, rủi ro nào đang hiện thực hoá.

---

## 1. Rủi ro nghiêm trọng (có thể làm hỏng đề tài)

### R1 — Không thu đủ dữ liệu video/gán nhãn đúng hạn
**Xác suất: Cao · Ảnh hưởng: Cao**

*Dấu hiệu sớm:* hết T8 mà chưa có 500 ảnh gán nhãn.

*Phòng ngừa:* bắt đầu quay từ T3, gán nhãn xen kẽ mỗi ngày một ít thay vì dồn.

*Ứng phó:* hạ xuống 1.500 ảnh và 4 lớp; dùng nhãn nháp từ mô hình rồi chỉ sửa; nhờ người phụ 2–3 buổi; giảm số điểm quay từ 12 xuống 6.

---

### R2 — Không có mức tăng mAP đáng kể sau fine-tune
**Xác suất: Trung bình · Ảnh hưởng: Cao (luận điểm bài báo 1 sụp)**

*Dấu hiệu sớm:* thí nghiệm chẩn đoán ở T3 cho tỷ lệ sót xe máy < 15%.

*Ứng phó — theo thứ tự:*
1. Chuyển trọng tâm sang **đánh giá phân tầng** — mức cải thiện ở điều kiện mưa/đêm/mật độ cao thường vẫn lớn, và đó mới là câu chuyện đáng kể
2. Chuyển góc bài báo từ bài toán *phát hiện* sang bài toán *đếm* — sai số đếm luỹ tích thường lớn hơn sai số phát hiện đơn khung
3. Nhấn mạnh đóng góp bộ dữ liệu thay vì đóng góp mô hình

Rủi ro này phát hiện được từ **T3**. Đó là lý do thí nghiệm chẩn đoán ở [GĐ1](01-giai-doan-1-nen-mong.md) mục 3.2 phải làm sớm.

---

### R3 — Không đạt chuẩn hiệu chỉnh GEH cho mô phỏng SUMO
**Xác suất: Cao · Ảnh hưởng: Cao (con số #3 không có)**

*Nguyên nhân thường gặp:* mạng lưới sai (cấm rẽ nhầm), chu kỳ đèn sai, mô hình xe máy chưa đúng, vùng nghiên cứu quá rộng so với số điểm đếm.

*Ứng phó:*
1. Thu hẹp vùng nghiên cứu xuống 1–2 km²
2. Đi thực địa bấm giờ chu kỳ đèn ở các nút chính
3. Kiểm tra lại mô hình sublane cho xe máy
4. **Nới tiêu chí xuống GEH<7 và ghi rõ là hạn chế** — trung thực về việc không đạt chuẩn ngành tốt hơn nhiều so với giấu

---

### R4 — Không viết nhật ký kỹ thuật, đến T29 phải sáng tác lại từ đầu
**Xác suất: Cao · Ảnh hưởng: Cao**

Đây là rủi ro **âm thầm nhất** vì không có dấu hiệu cho đến khi quá muộn.

*Phòng ngừa — cách duy nhất:* kết thúc mỗi giai đoạn viết ngay 5–10 trang. Đặt lịch nhắc.

*Ứng phó nếu đã lỡ:* dành trọn T29–T31 tái dựng từ commit log, `experiments/` và `results/`. Chạy lại script để lấy lại số liệu. Chấp nhận mất khoảng 3 tuần.

---

### R5 — Không nối được hai nửa hệ thống (thị giác và đồ thị)
**Xác suất: Trung bình · Ảnh hưởng: Rất cao**

Đây là **rủi ro đặc thù của đề tài ghép**, và là điều hội đồng sẽ dò tìm. Nếu hai nửa không nối, bạn có hai đồ án rời chứ không có một luận văn.

*Phòng ngừa:* nguyên tắc "đường ống thông ở T8"; chốt hợp đồng dữ liệu `counts.parquet` sớm và không đổi; thao tác demo số 3 và 4 phải hoạt động.

*Dấu hiệu sớm:* hết T12 mà `site_edge_mapping.csv` vẫn chưa có.

---

## 2. Rủi ro trung bình

| Mã | Rủi ro | Ứng phó |
|---|---|---|
| R6 | **Spark chậm hơn một máy ở mọi quy mô thử được** | Nhân bản đồ thị để đẩy quy mô, tìm cho ra điểm giao. Nếu vẫn không có, chuyển luận điểm sang song song hoá theo lát cắt thời gian và kịch bản — vẫn hợp lệ về mặt học thuật |
| R7 | Hết quota GPU miễn phí | Giảm `imgsz` xuống 640 cho các lần thử, chỉ dùng 960 cho lần chạy cuối; giảm số biến thể so sánh |
| R8 | Không được cấp dữ liệu camera từ Sở | **Đã hạ mức (30/08/2026):** dữ liệu camera nằm trong Danh mục dữ liệu mở của thành phố → tiếp cận qua opendata.danang.gov.vn thay vì công văn. Xem [A](A-nguon-du-lieu.md) mục 2.2. Kể cả không có, tự quay vẫn là xương sống |
| R8b | **camera.0511.vn đang tạm đóng để nâng cấp** | Kiểm tra lại hàng tuần. Trong lúc chờ, dùng cổng camera công khai TP.HCM cho dữ liệu huấn luyện + tự quay cho Đà Nẵng — cách chia này còn tạo ra bảng thí nghiệm liên thành phố có giá trị (xem [D](D-cong-nghe-va-huong-moi.md) 2.1) |
| R8c | Chọn sai mô hình, lạc hậu khi bảo vệ | Đọc [D](D-cong-nghe-va-huong-moi.md) mục 1 trước khi chốt. Thử RF-DETR trên 200 ảnh đầu, quyết định **trước** khi gán nhãn xong |
| R9 | Mưa kéo dài không quay được | Đảo lịch sang gán nhãn; **video mưa là dữ liệu quý** — cứ quay |
| R10 | Học SUMO tốn nhiều thời gian hơn dự kiến | Bắt đầu học từ T15 với một ví dụ đồ chơi, trước khi vào mạng thật |
| R11 | Bài báo bị từ chối | Bình thường. Chuẩn bị sẵn danh sách venue thứ hai và thứ ba từ trước khi gửi lần đầu |
| R12 | Deploy hỏng ngày bảo vệ | Ba lớp dự phòng: bản local, video demo, ping giữ ấm. Xem [GĐ6](06-giai-doan-6-web-app-deploy.md) mục 6 |
| R13 | Ổ cứng/thẻ nhớ hỏng, mất video | Sao lưu ổ ngoài + cloud **ngay trong ngày quay**. Video mất là không quay lại được cùng điều kiện |
| R14 | GVHD phản hồi chậm | Nộp từng chương ngay khi xong, không dồn đến T42 |
| R15 | Venue bị ngừng chỉ mục Scopus | Kiểm tra trên Scopus Sources **tại thời điểm gửi**, không tin danh sách cũ |

---

## 3. Rủi ro thấp nhưng cần biết

| Mã | Rủi ro | Ghi chú |
|---|---|---|
| R16 | Ranh giới Đà Nẵng sau sáp nhập chưa có trong OSM | Dùng bbox thủ công, ghi rõ trong luận văn |
| R17 | Bị nhắc nhở khi quay nơi công cộng | Mang giấy giới thiệu; chọn vị trí không cản trở; tránh hướng vào nhà dân |
| R18 | TomTom hết hạn mức miễn phí | Giảm số đoạn hoặc giãn chu kỳ lên 20–30 phút; bổ sung HERE |
| R19 | Đồ thị sau sáp nhập quá lớn cho máy cá nhân | Dùng Đà Nẵng cũ cho thí nghiệm chính, đồ thị lớn chỉ để đo scalability |
| R20 | Không tìm được hệ số PCU/năng lực thông hành cho xe máy VN | Dùng nguồn từ Đài Loan/Indonesia/Ấn Độ, ghi rõ nguồn, coi là hạn chế |

---

## 4. Ranh giới không được vượt qua

Đây không phải rủi ro mà là quy tắc. Vi phạm những điều này có thể dẫn đến hủy kết quả luận văn:

- **Không sửa số liệu** để kết quả đẹp hơn. Kết quả trung thực có giải thích tốt vẫn bảo vệ được
- **Không trích dẫn tài liệu chưa đọc.** Đặc biệt: không dùng danh mục tài liệu do công cụ AI sinh ra mà chưa kiểm chứng từng mục có thật
- **Không sao chép văn bản** từ nguồn khác, kể cả từ bài báo của chính mình, mà không diễn đạt lại và trích dẫn
- **Không công bố ảnh có thể định danh cá nhân** trong bộ dữ liệu hoặc luận văn
- **Không thu thập dữ liệu vi phạm điều khoản dịch vụ** của bên cung cấp

---

## 5. Bảng theo dõi hàng tháng

Sao chép bảng này vào nhật ký mỗi tháng:

| Tháng | Cổng gần nhất | Đạt? | Rủi ro đang hiện thực hoá | Hành động điều chỉnh |
|---|---|---|---|---|
| T1 | G1 (T4) | | | |
| T2 | G2 (T8) | | | |
| T3 | G3 (T14) | | | |
| T4 | | | | |
| T5 | G4 (T20) | | | |
| T6 | G5/G7 (T26) | | | |
| T7 | G6 (T30) | | | |
| T8 | | | | |
| T9 | | | | |
| T10 | G8 (T42) | | | |
| T11 | | | | |
| T12 | G9 (T46–48) | | | |

**Quy tắc:** nếu trễ một cổng quá 2 tuần, áp dụng ngay thứ tự cắt giảm ở [00-tong-quan.md](00-tong-quan.md) mục 7. Đừng hy vọng "tháng sau bù được" — trong thực tế điều đó gần như không xảy ra.
