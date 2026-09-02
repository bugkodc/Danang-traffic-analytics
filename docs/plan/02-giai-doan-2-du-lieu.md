# Giai đoạn 2 — Xây dựng bộ dữ liệu (Tuần 3–12)

> **Mục tiêu:** Tạo ra `DaNang-Traffic-2026` — bộ dữ liệu ảnh giao thông Đà Nẵng có gán nhãn, cùng kho video thô và chuỗi thời gian tốc độ.

Đây là giai đoạn tốn công nhất và ít thú vị nhất, nhưng **bộ dữ liệu là tài sản khoa học duy nhất còn sống sau khi bạn tốt nghiệp**. Nó cũng là thứ khiến bài báo của bạn khác với hàng nghìn bài "áp dụng YOLO để đếm xe" đã có.

Giai đoạn này chạy nền song song với GĐ1 và GĐ3 — quay video và gán nhãn là việc rời rạc, làm xen kẽ.

---

## 1. Kế hoạch quay video

### 1.1 Định lượng mục tiêu

| | Tối thiểu | Đầy đủ |
|---|---|---|
| Số điểm | 6 | 12 |
| Khung giờ/điểm | 3 (7h, 11h30, 17h) | 4 (+ 21h) |
| Thời lượng/lần | 20 phút | 30 phút |
| Số đợt | 2 (ngày thường + cuối tuần) | 3 (+ ngày mưa) |
| **Tổng video thô** | **~12 giờ** | **~36 giờ** |

### 1.2 Quy chuẩn quay (tuân thủ nghiêm — video không đạt chuẩn phải quay lại)

- **Độ cao:** 5–8m. Thấp hơn thì xe máy che nhau hoàn toàn, không tách được.
- **Góc nghiêng:** 30–45° so với phương ngang. Góc quá đứng mất thông tin loại xe, quá ngang thì che khuất.
- **Độ phân giải:** tối thiểu 1080p @ 25–30fps. 4K tốt hơn cho vật thể nhỏ nhưng nặng gấp 4 lần khi xử lý.
- **Cố định tuyệt đối:** dùng tripod hoặc kẹp. Camera rung làm hỏng toàn bộ khâu bám vết.
- **Vạch đếm phải nằm gọn trong khung**, cách mép ≥15% chiều cao ảnh để đối tượng được bám vết đủ lâu trước và sau khi qua vạch.

### 1.3 Siêu dữ liệu bắt buộc

Mỗi video ghi một dòng vào `data/raw/video/manifest.csv`:

```
video_id, site_id, ngày, giờ_bắt_đầu, thời_lượng, độ_phân_giải, fps,
thời_tiết, độ_cao_ước_lượng, góc_nghiêng, thiết_bị, ghi_chú
```

Thiếu siêu dữ liệu = video gần như vô dụng khi viết bài, vì bạn không giải thích được vì sao kết quả ở điểm này khác điểm kia.

### 1.4 Điều kiện đa dạng — đây là chỗ tạo giá trị khoa học

Cố ý thu thập cả các điều kiện khó, vì chính chúng làm nên đóng góp:

- **Trời mưa** (Đà Nẵng mưa nhiều từ tháng 9–12 — tận dụng đúng mùa bắt đầu luận văn)
- **Chạng vạng / ban đêm có đèn đường**
- **Ngược sáng** (buổi sáng hướng đông, chiều hướng tây)
- **Mật độ cực cao** (giờ tan tầm 17h–18h)

Một bộ dữ liệu chỉ có ảnh nắng đẹp giờ thấp điểm thì không nói lên điều gì.

---

## 2. Gán nhãn

### 2.1 Trích khung hình

Không lấy khung liên tiếp — chúng gần như trùng nhau và làm mô hình học vẹt.

```python
# lấy 1 khung mỗi 3–5 giây, tức mỗi ~100 khung
# 12 giờ video @ 25fps = 1.08 triệu khung -> trích ~10.000 khung -> chọn lọc 2.000-3.000
```

Chiến lược chọn lọc: ưu tiên khung đa dạng về mật độ và điều kiện, cân bằng giữa các điểm quay, và **cố ý lấy nhiều khung ở các trường hợp khó** (mưa, đêm, tắc đường).

### 2.2 Công cụ

| Công cụ | Ưu | Nhược |
|---|---|---|
| **Roboflow** (khuyến nghị) | Có gán nhãn tự động hỗ trợ, quản lý phiên bản, xuất trực tiếp định dạng YOLO, chia train/val/test | Free tier giới hạn số ảnh |
| **CVAT** (tự host) | Miễn phí không giới hạn, mạnh cho video | Phải tự cài, chậm hơn |
| **Label Studio** | Linh hoạt | Kém tối ưu cho bounding box số lượng lớn |

**Mẹo tăng tốc gấp 3:** dùng YOLO mặc định chạy trước để sinh nhãn nháp, rồi chỉ *sửa* thay vì vẽ từ đầu. Nhưng phải rà kỹ — mô hình sót xe máy chính là vấn đề bạn đang nghiên cứu, nên đừng tin nhãn nháp ở lớp đó.

### 2.3 Quy tắc gán nhãn — viết thành văn bản trước khi gán

Tạo `docs/huong-dan-gan-nhan.md` và tuân thủ tuyệt đối nhất quán. Các quyết định phải chốt trước:

- Xe bị che >50% thì có gán không? (**Đề xuất: có gán**, vì thực tế đường VN che khuất là thường trực)
- Xe máy chở 2–3 người: một hộp hay nhiều hộp? (**Đề xuất: một hộp bao cả xe và người**)
- Hộp bao gồm gương chiếu hậu? (**Đề xuất: không**)
- Xe ở rìa ảnh chỉ thấy một phần? (**Đề xuất: gán nếu thấy ≥30%**)
- Ranh giới `van` vs `truck` vs `car`? (Cần ví dụ ảnh minh hoạ cụ thể)
- Xe đỗ/dừng có gán không? (**Đề xuất: có gán, nhưng không tính vào số đếm qua vạch**)

Sự **nhất quán** quan trọng hơn sự "đúng". Một quy tắc kỳ lạ nhưng áp dụng đều còn tốt hơn quy tắc chuẩn áp dụng lung tung.

### 2.4 Kiểm tra chất lượng nhãn

Sau khi gán xong ~500 ảnh đầu, dừng lại và tự kiểm tra chéo: gán lại 50 ảnh ngẫu nhiên (không nhìn nhãn cũ), đo độ khớp bằng IoU và tỷ lệ trùng lớp. Nếu độ nhất quán thấp, sửa hướng dẫn rồi gán lại từ đầu — phát hiện sớm rẻ hơn nhiều so với phát hiện ở ảnh thứ 2.500.

Nếu có người thứ hai phụ gán nhãn, đo **hệ số đồng thuận giữa hai người** (Cohen's kappa) trên 100 ảnh chung. Con số này đưa vào bài báo, làm tăng đáng kể độ tin cậy của bộ dữ liệu.

### 2.5 Chia tập — chia theo ĐIỂM QUAY, không chia ngẫu nhiên

Đây là sai lầm phổ biến và nghiêm trọng nhất.

Nếu chia ngẫu nhiên, các khung từ cùng một video sẽ nằm cả ở train lẫn test → mô hình đã "thấy" nền cảnh đó → **mAP trên test bị thổi phồng, kết quả vô giá trị**.

```
train: site_01..site_08
val:   site_09, site_10
test:  site_11, site_12   <-- điểm quay hoàn toàn chưa thấy bao giờ
```

Với bản tối thiểu 6 điểm: train 4 / val 1 / test 1. Nói rõ cách chia này trong bài báo — reviewer sẽ đánh giá cao vì đa số bài không làm đúng.

---

## 3. Dữ liệu đếm tay (ground truth) — nhỏ nhưng không thể thiếu

Chọn **5 đoạn video 15 phút** ở các điểm và điều kiện khác nhau, đếm tay từng loại phương tiện qua vạch.

- Dùng phần mềm đếm thủ công hoặc bảng phím tắt, xem ở tốc độ 0.5×
- Mỗi đoạn đếm 2 lần cách nhau vài ngày, lấy trung bình, ghi lại độ lệch giữa 2 lần đếm của chính bạn (đây là "sai số con người" — con số hữu ích để so sánh)
- Ghi ra `data/ground_truth/manual_counts.csv`: `video_id, khoảng_thời_gian, hướng, lớp_xe, số_đếm`

Tổng công: khoảng 8–10 giờ. **Đây là 10 giờ có giá trị nhất trong toàn bộ luận văn** — không có bảng này thì không có con số #2, và không có con số #2 thì mọi kết quả phía sau không đứng vững.

---

## 4. Chuỗi thời gian tốc độ (chạy nền, đã khởi động từ GĐ1)

Kiểm tra hàng tuần:
- Job còn chạy không? (đặt cảnh báo nếu file ngày hôm qua rỗng)
- Dung lượng tích lũy hợp lý không?
- Đã có bao nhiêu ngày liên tục?

Đến T12 nên có ≥10 tuần dữ liệu × 20–50 đoạn × 96 điểm đo/ngày.

---

## 5. Dữ liệu ngữ cảnh (làm nhanh, 1–2 ngày)

| Nguồn | Lấy gì | Dùng để |
|---|---|---|
| OSM POI | Trường học, chợ, bệnh viện, khu công nghiệp, khách sạn | Giải thích điểm phát sinh chuyến đi |
| WorldPop / Meta HRSL | Mật độ dân số lưới ~100m | Thay thế ma trận OD khi không có khảo sát hộ gia đình |
| Open-Meteo (miễn phí, không cần key) | Lịch sử mưa/nhiệt độ theo giờ | Biến giải thích; Đà Nẵng mưa mùa rất mạnh |
| Lịch sự kiện | DIFF, lễ tết, khai giảng | Case study "ngày bất thường" — rất được đánh giá cao |

---

## 6. Đóng gói bộ dữ liệu

Cấu trúc chuẩn để có thể công bố:

```
DaNang-Traffic-2026/
├── images/{train,val,test}/
├── labels/{train,val,test}/       # định dạng YOLO
├── data.yaml
├── manifest.csv                   # ảnh -> site_id, thời tiết, khung giờ
├── sites.csv
├── manual_counts.csv
├── LICENSE                        # đề xuất CC BY-NC 4.0
└── README.md                      # thống kê, cách chia tập, quy tắc gán nhãn
```

**Công bố lên Zenodo để lấy DOI.** Chi phí: một buổi. Lợi ích: bộ dữ liệu trở thành mục "Đóng góp" chính danh, được trích dẫn độc lập, và làm nền cho một bài báo dạng dataset.

---

## Sản phẩm bàn giao của GĐ2

- [ ] ≥12 giờ video thô + `manifest.csv` đầy đủ siêu dữ liệu
- [ ] ≥1.500 (tối thiểu) hoặc ≥3.000 ảnh đã gán nhãn
- [ ] Chia tập **theo điểm quay**, không rò rỉ dữ liệu
- [ ] `docs/huong-dan-gan-nhan.md` + báo cáo kiểm tra độ nhất quán
- [ ] `manual_counts.csv` — 5 đoạn × 15 phút đếm tay
- [ ] ≥10 tuần chuỗi thời gian tốc độ
- [ ] Dữ liệu ngữ cảnh (POI, dân số, thời tiết)
- [ ] `docs/nhat-ky/02-du-lieu.md` (~8 trang — sẽ thành một chương của luận văn)

## Tiêu chí qua cổng G3 (T14)

Bảng thống kê bộ dữ liệu hoàn chỉnh: số ảnh/lớp, số ảnh/điểm, phân bố theo điều kiện thời tiết và khung giờ, số hộp trung bình mỗi ảnh. Nếu lớp nào < 200 mẫu thì hoặc gán bổ sung, hoặc gộp lớp đó.

---

## Rủi ro giai đoạn này

| Rủi ro | Mức | Xử lý |
|---|---|---|
| **Gán nhãn chậm hơn dự kiến** (rủi ro số 1) | Cao | Hạ mục tiêu xuống 1.500 ảnh và 4 lớp; dùng nhãn nháp từ mô hình; thuê/nhờ người phụ 2–3 buổi |
| Mưa kéo dài không quay được | Trung bình | Đảo lịch: gán nhãn ảnh cũ trong ngày mưa; đồng thời **video mưa là dữ liệu quý**, cứ quay |
| Bị hỏi/nhắc nhở khi quay nơi công cộng | Trung bình | Mang theo giấy giới thiệu của trường; chọn vị trí không cản trở; tránh quay vào nhà dân |
| Nhãn không nhất quán, phát hiện muộn | Cao | Bắt buộc kiểm tra chéo sau 500 ảnh đầu (mục 2.4) |
| Thẻ nhớ/ổ cứng hỏng | Trung bình | Sao lưu lên ổ ngoài + cloud **ngay trong ngày quay**. Video mất là không quay lại được cùng điều kiện |
