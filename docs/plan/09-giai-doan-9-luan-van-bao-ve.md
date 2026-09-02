# Giai đoạn 9 — Luận văn và bảo vệ (Tuần 29–48)

> **Nguyên tắc chi phối:** đến T29 bạn **biên tập**, không **sáng tác**. Nếu đã viết nhật ký kỹ thuật đều đặn sau mỗi giai đoạn, 60–70% nội dung đã có sẵn.

---

## 1. Nguồn gốc từng chương

Bảng này là lý do phải viết nhật ký từ T4. Nếu bạn đã làm đúng, giai đoạn này nhẹ nhàng; nếu không, đây sẽ là 5 tháng khủng hoảng.

| Chương | Nội dung | Trang | Nguồn |
|---|---|---|---|
| 1 | Mở đầu: bối cảnh, vấn đề, mục tiêu, phạm vi, đóng góp | 8–10 | Viết mới |
| 2 | Tổng quan: dữ liệu lớn, đồ thị đường, phát hiện đối tượng, mô phỏng giao thông | 20–25 | Gộp khảo sát của **cả hai bài báo** |
| 3 | Dữ liệu và phương pháp thu thập | 15–18 | `nhat-ky/02-du-lieu.md` |
| 4 | Phát hiện và đếm phương tiện | 18–22 | `nhat-ky/03-thi-giac.md` + bài báo 1 |
| 5 | Mô hình đồ thị và xử lý phân tán | 18–22 | `nhat-ky/04-do-thi-spark.md` + bài báo 2 |
| 6 | Mô phỏng kịch bản phân luồng | 12–15 | `nhat-ky/05-sumo.md` |
| 7 | Kiến trúc và triển khai hệ thống | 10–12 | `nhat-ky/06-he-thong.md` |
| 8 | Kết luận và hướng phát triển | 5–6 | Viết mới |
| | Phụ lục: bảng số liệu, mã nguồn chính, ảnh màn hình | 10–20 | |
| | **Tổng** | **~110–140** | |

**Kiểm tra ngay:** quy định của trường về số trang, cấu trúc chương, quy cách trình bày và định dạng trích dẫn. Mỗi trường mỗi khác, và sửa định dạng ở cuối tốn nhiều thời gian vô ích.

---

## 2. Mốc thời gian

| Tuần | Việc | Đầu ra |
|---|---|---|
| T29–30 | Dựng khung, gộp nhật ký vào các chương, thống nhất ký hiệu và thuật ngữ | Bản nháp 0 |
| T31–33 | Viết chương 2 (tổng quan) — chương tốn công nhất, viết mới nhiều nhất | Chương 2 xong |
| T34–36 | Hoàn thiện chương 3, 4 | |
| T37–39 | Hoàn thiện chương 5, 6, 7 | |
| T40–41 | Viết chương 1 và 8 (viết sau cùng — lúc này mới biết mình đã làm được gì) | |
| **T42** | **Nộp GVHD bản đầy đủ lần 1** | **Cổng G8** |
| T43–44 | Sửa theo góp ý; rà số liệu; kiểm tra trùng lặp | |
| T45 | Hoàn thiện định dạng, mục lục, danh mục bảng/hình, tài liệu tham khảo | |
| T46 | In quyển, nộp; chuẩn bị slide | |
| T47 | **Tổng duyệt lần 1 và lần 2** | |
| T48 | **Bảo vệ** | |

Chương 1 và 8 viết sau cùng — đây là kinh nghiệm chuẩn. Bạn không thể viết phần mở đầu thuyết phục khi chưa biết kết quả cuối cùng là gì.

---

## 3. Những chỗ hội đồng sẽ đào

Chuẩn bị sẵn câu trả lời có số liệu cho từng câu:

| Câu hỏi | Chuẩn bị |
|---|---|
| **"Big data ở chỗ nào? 50k đỉnh có gì lớn?"** | Bảng tích các chiều + biểu đồ speedup có điểm giao. Xem [08](08-giai-doan-8-bai-bao-2.md) mục 4 |
| **"Số đếm của em có đúng không?"** | Bảng đối chứng đếm tay, MAE/MAPE/GEH, và nói rõ sai số con người giữa hai lần bạn tự đếm |
| **"Sao không dùng Spark cho phần YOLO?"** | Giải thích kiến trúc Lambda: suy luận video là tác vụ GPU theo lô, đã song song hoá theo video; Spark dùng cho tầng phân tích |
| **"Kết quả mô phỏng có tin được không?"** | Chuẩn hiệu chỉnh GEH<5 ở ≥85% điểm + kiểm chứng chéo độc lập bằng TomTom |
| **"Chỉ 6–12 điểm quay cho cả thành phố?"** | Thừa nhận là hạn chế; nói rõ cách ngoại suy và cách đã kiểm chứng ngoại suy bằng TomTom; đề xuất mở rộng |
| **"Hệ thống này ai dùng, dùng thế nào?"** | Kịch bản sử dụng cụ thể cho cơ quan quản lý giao thông; nếu đã liên hệ được Sở thì nêu ra |
| **"Đóng góp mới so với các nghiên cứu đã có?"** | Ba con số + bộ dữ liệu có DOI + tính khép kín của chuỗi lập luận |
| **"Xe máy mô phỏng thế nào? SUMO đâu có mô hình xe máy VN?"** | Mô hình sublane, tham số `vType`, và thừa nhận đây là hạn chế đã biết của lĩnh vực |

**Nguyên tắc trả lời:** không có số liệu thì nói "em chưa đo được điều đó" thay vì đoán. Hội đồng chấp nhận sự trung thực, không chấp nhận bịa.

---

## 4. Slide bảo vệ (~20 slide / 20 phút)

| Slide | Nội dung |
|---|---|
| 1 | Tên đề tài, học viên, GVHD |
| 2 | Vấn đề: một ảnh tắc đường Đà Nẵng + một câu hỏi |
| 3 | Khoảng trống: dữ liệu OSM có hình học nhưng không có lưu lượng |
| 4 | Mục tiêu và đóng góp — 3 gạch đầu dòng |
| 5 | **Sơ đồ khung tổng thể** — slide quan trọng nhất |
| 6–7 | Dữ liệu: bản đồ điểm quay, thống kê bộ dữ liệu |
| 8–10 | Phát hiện & đếm: **con số #1**, **con số #2**, ảnh so sánh trực quan |
| 11–13 | Đồ thị & Spark: bản đồ độ trung tâm, **biểu đồ speedup** |
| 14–16 | Mô phỏng: hiệu chỉnh GEH, **con số #3** |
| 17 | **DEMO TRỰC TIẾP** (3–4 phút) |
| 18 | Hạn chế — nêu trước khi bị hỏi |
| 19 | Hướng phát triển |
| 20 | Kết luận + link demo + DOI dataset |

**Về phần demo:** đặt ở slide 17, sau khi đã trình bày hết số liệu. Nếu demo hỏng, bạn đã trình bày xong phần khoa học và chỉ mất một mục nhỏ. Nếu demo ở đầu và hỏng, bạn mất bình tĩnh cho cả buổi.

Ba lớp dự phòng cho demo — xem [06](06-giai-doan-6-web-app-deploy.md) mục 6. Chuẩn bị cả ba.

---

## 5. Danh sách kiểm tra trước khi nộp

**Nội dung**
- [ ] Mọi số liệu trong quyển tái lập được bằng script trong `experiments/`
- [ ] Mọi bảng/hình đều được nhắc đến trong văn bản
- [ ] Ký hiệu toán học và thuật ngữ nhất quán toàn quyển
- [ ] Thuật ngữ tiếng Anh có bảng đối chiếu, dùng thống nhất
- [ ] Chương 2 có tổng hợp và bình luận, **không phải liệt kê bài này bài kia**

**Trích dẫn**
- [ ] Mọi tài liệu trong danh mục đều được trích dẫn trong bài và ngược lại
- [ ] **Đã đọc thật mọi tài liệu mình trích dẫn**
- [ ] Không có trích dẫn nào do công cụ AI sinh ra mà chưa kiểm chứng tồn tại
- [ ] Đã chạy kiểm tra trùng lặp theo yêu cầu của trường

**Hình thức**
- [ ] Đúng mẫu trình bày của trường
- [ ] Mục lục, danh mục bảng, danh mục hình, danh mục viết tắt
- [ ] Hình đủ độ phân giải khi in đen trắng (kiểm tra bằng cách in thử)
- [ ] Bản đồ và biểu đồ phân biệt được khi không có màu

**Sản phẩm kèm theo**
- [ ] Đĩa/USB mã nguồn hoặc link repo
- [ ] Link demo còn sống
- [ ] DOI bộ dữ liệu
- [ ] Xác nhận bài báo đã gửi/đã nhận

---

## 6. Tuần bảo vệ

- Tổng duyệt **ít nhất 2 lần**, bấm giờ, có người nghe và đặt câu hỏi
- Nhờ một người ngoài chuyên ngành nghe thử — nếu họ nắm được vấn đề và kết quả, bài trình bày đạt
- Kiểm tra demo mỗi ngày trong tuần bảo vệ
- Chuẩn bị sẵn quyển có đánh dấu trang để tra nhanh khi bị hỏi số liệu
- In dự phòng slide ra giấy

---

## Rủi ro giai đoạn này

| Rủi ro | Xử lý |
|---|---|
| **Không viết nhật ký từ đầu → phải sáng tác lại từ số 0** | Rủi ro lớn nhất. Phòng ngừa từ T4, không có cách chữa ở T29. Nếu đã lỡ: dành trọn T29–T31 tái dựng lại từ commit log và kết quả trong `results/` |
| Quên chi tiết kỹ thuật của giai đoạn trước | Đọc lại `experiments/` và commit log; chạy lại script để lấy số liệu |
| GVHD phản hồi chậm | Nộp từng chương ngay khi xong, không dồn đến T42 |
| Kết quả không đẹp như kỳ vọng | Kết quả trung thực có giải thích tốt vẫn bảo vệ được. Đừng sửa số liệu — đó là ranh giới không được vượt qua |
| Trượt tiến độ đến sát hạn | Áp dụng thứ tự cắt giảm ở [00-tong-quan.md](00-tong-quan.md) mục 7. Cắt tính năng, không cắt phần đối chứng |
