# Giai đoạn 5 — Mô phỏng kịch bản phân luồng (Tuần 19–24)

> **Mục tiêu:** Sinh ra **con số #3** — mức giảm tổng thời gian trễ khi áp dụng kịch bản phân luồng.

## Vì sao giai đoạn này không thể bỏ

Tên đề tài có chữ **"phân luồng"**. Nếu chỉ dừng ở quan sát và định tuyến, bạn có một hệ thống *giám sát* giao thông, và phản biện sẽ hỏi đúng câu: *"Vậy phân luồng ở đâu?"*

Bạn không thể ra ngoài đời cấm một con đường để thử nghiệm. Chuẩn mực học thuật cho tình huống này là **mô phỏng vi mô đã hiệu chỉnh bằng dữ liệu thực**. Đó chính là điều SUMO làm, và cũng là điều biến số đếm xe của bạn từ "một con số" thành "một công cụ ra quyết định".

---

## 1. Dựng mạng lưới SUMO (Tuần 19–20)

### 1.1 Chuyển đổi từ OSM

```bash
netconvert --osm-files danang.osm \
           --output-file danang.net.xml \
           --geometry.remove --roundabouts.guess \
           --ramps.guess --junctions.join \
           --tls.guess-signals --tls.discard-simple --tls.join
```

**Phạm vi:** đừng mô phỏng toàn thành phố. Chọn một **vùng nghiên cứu 3–5 km²** bao trọn các điểm đếm của bạn. Mô phỏng vi mô toàn Đà Nẵng vừa không chạy nổi vừa không hiệu chỉnh được (không đủ điểm đếm để hiệu chỉnh).

Đề xuất vùng: khu vực bao quanh 4–6 điểm đếm liền kề nhau, có ít nhất một cầu qua sông và một nút giao lớn — để kịch bản phân luồng có ý nghĩa.

### 1.2 Sửa mạng bằng tay — công đoạn không tránh được

Mạng sinh tự động từ OSM luôn có lỗi. Dùng **netedit** (GUI của SUMO) để sửa:
- Nút giao bị tách/gộp sai
- Làn xe và các hướng rẽ được phép
- Chu kỳ đèn tín hiệu (OSM chỉ có vị trí đèn, không có chu kỳ — phải đi thực địa bấm giờ ở 3–5 nút chính)
- Đường một chiều bị ngược

Dự trù **3–5 ngày công** cho riêng việc này. Đây là lý do phải giới hạn phạm vi vùng nghiên cứu.

### 1.3 Mô hình hoá xe máy — vấn đề đặc thù quan trọng nhất

SUMO mặc định mô phỏng theo làn, trong khi xe máy Việt Nam **không đi theo làn**. Nếu bỏ qua, kết quả mô phỏng sai về bản chất.

Các cách xử lý, nên thử và báo cáo so sánh:

| Cách | Mô tả |
|---|---|
| **`sublane model`** (khuyến nghị) | Bật `--lateral-resolution`, cho phép xe chiếm một phần làn và đi song song nhau — mô phỏng được hành vi len lỏi |
| Định nghĩa `vType` riêng cho xe máy | `width=0.8`, `minGap` nhỏ, `latAlignment="arbitrary"`, `impatience` cao |
| Quy đổi PCU | Đơn giản hoá: thay xe máy bằng số xe con tương đương. Kém chính xác nhưng nhanh, dùng làm đường cơ sở so sánh |

**Việc mô hình hoá đúng hành vi xe máy trong SUMO tự nó là một đóng góp của luận văn** và là một mục hấp dẫn trong bài báo 2 — vì đây là hạn chế được thừa nhận rộng rãi của các mô hình giao thông áp dụng cho Đông Nam Á.

---

## 2. Hiệu chỉnh bằng dữ liệu thật (Tuần 21–22) — bước quyết định

Đây là bước phân biệt một mô phỏng nghiêm túc với một mô phỏng đồ chơi.

### 2.1 Sinh nhu cầu đi lại từ số đếm

Dùng **`routeSampler.py`** (công cụ chuẩn của SUMO cho việc sinh tuyến khớp với dữ liệu đếm):

```bash
# 1. sinh tập tuyến ứng viên
python randomTrips.py -n danang.net.xml -r candidates.rou.xml \
       -e 3600 --fringe-factor 10

# 2. lấy mẫu tuyến sao cho khớp số đếm thực tế
python routeSampler.py -r candidates.rou.xml \
       --edgedata-files counts.xml \
       -o calibrated.rou.xml
```

Đầu vào `counts.xml` chính là `counts.parquet` từ GĐ3 đã quy đổi PCU — **đây là mắt xích nối hai nửa của luận văn**. Nếu mắt xích này không tồn tại, hội đồng sẽ thấy ngay đó là hai đồ án ghép lại.

### 2.2 Tiêu chí hiệu chỉnh đạt

Dùng lại **GEH** đã dùng ở GĐ3:

> **Chuẩn ngành: GEH < 5 tại ≥85% điểm đếm.**

Lặp: chạy mô phỏng → so số đếm mô phỏng với số đếm thật → chỉnh nhu cầu → chạy lại. Ghi lại bảng GEH qua từng vòng lặp — bảng này là bằng chứng cho thấy mô hình đáng tin.

Nếu sau nhiều vòng vẫn không đạt, nguyên nhân thường là: mạng lưới sai (rẽ bị cấm nhầm), chu kỳ đèn sai, hoặc năng lực thông hành đặt sai vì mô hình xe máy chưa đúng.

### 2.3 Kiểm chứng chéo bằng nguồn độc lập

Hiệu chỉnh bằng số đếm rồi **kiểm chứng bằng tốc độ TomTom** — một nguồn hoàn toàn độc lập không tham gia hiệu chỉnh. So sánh tốc độ mô phỏng với tốc độ TomTom trên cùng đoạn, cùng khung giờ.

Đây là kiểm chứng mạnh nhất bạn có thể làm và là chỗ dữ liệu thu từ tuần 1 trả công lớn nhất. Rất ít luận văn thạc sĩ có kiểm chứng chéo độc lập.

---

## 3. Thiết kế kịch bản (Tuần 23)

Mỗi kịch bản phải: (a) khả thi ngoài đời, (b) xuất phát từ một vấn đề đã quan sát được trong dữ liệu của bạn.

| # | Kịch bản | Xuất phát từ | Ưu tiên |
|---|---|---|---|
| **S0** | Hiện trạng | Đường cơ sở | Bắt buộc |
| **S1** | Cấm rẽ trái tại nút giao có V/C cao nhất | Nút do chính dữ liệu của bạn chỉ ra | Bắt buộc |
| **S2** | Tối ưu chu kỳ đèn tại 2–3 nút trọng yếu | Kết quả độ trung tâm trung gian ở GĐ4 | Nên có |
| S3 | Một chiều hoá một cặp tuyến song song | Phân tích mạng lưới | Tuỳ chọn |
| S4 | Đóng một cầu (mô phỏng sự cố/bảo trì) | Phân tích tính bền vững ở GĐ4 | Tuỳ chọn — **hấp dẫn nhất khi trình bày** |

Bản tối thiểu: S0 + S1 + S2.

Điểm cộng lớn: mỗi kịch bản đều **bắt nguồn từ một kết quả phân tích ở GĐ4**, chứ không phải nghĩ ra tuỳ tiện. Đó là chuỗi lập luận khép kín: đếm xe → trọng số đồ thị → xác định điểm nghẽn → đề xuất can thiệp → định lượng hiệu quả.

---

## 4. Chỉ số đánh giá (Tuần 24)

| Chỉ số | Đơn vị | Ý nghĩa |
|---|---|---|
| **Tổng thời gian trễ** | xe·giờ | **Chỉ số chính — con số #3** |
| Thời gian hành trình trung bình | giây | Trải nghiệm người dùng |
| Tốc độ trung bình mạng lưới | km/h | |
| Chiều dài hàng chờ tối đa | m | Rủi ro tắc lan truyền |
| Số điểm dừng trung bình | lần/xe | Chỉ báo tiêu hao nhiên liệu |
| Phát thải CO₂/NOx | kg | SUMO có sẵn mô hình HBEFA — **thêm chiều môi trường, rất được ưa chuộng khi bình duyệt** |

### Điều bắt buộc về phương pháp: chạy nhiều lần với seed khác nhau

Mô phỏng vi mô có tính ngẫu nhiên. **Chạy mỗi kịch bản ≥10 lần với seed khác nhau**, báo cáo trung bình ± độ lệch chuẩn, và kiểm định thống kê sự khác biệt giữa S0 và các kịch bản (t-test hoặc Mann-Whitney).

Rất nhiều bài báo bỏ qua bước này và bị phản biện bắt lỗi. Làm đúng sẽ là điểm mạnh của bạn.

**Cảnh báo diễn giải:** nếu S1 cho kết quả *xấu hơn* S0, đó vẫn là một kết quả hợp lệ và thú vị (nghịch lý Braess — thêm/bớt đường có thể làm giao thông tệ đi). Đừng cố ép ra kết quả đẹp. Một kết quả âm được giải thích tốt có giá trị khoa học cao hơn một kết quả dương bị gò.

---

## Sản phẩm bàn giao của GĐ5

- [ ] `danang.net.xml` — mạng SUMO vùng nghiên cứu đã sửa tay
- [ ] `vTypes.xml` — mô hình xe máy dùng sublane
- [ ] Báo cáo hiệu chỉnh: bảng GEH qua từng vòng lặp, đạt chuẩn ≥85% GEH<5
- [ ] Kiểm chứng chéo với tốc độ TomTom
- [ ] ≥2 (tối thiểu) hoặc 4 kịch bản, mỗi kịch bản ≥10 lần chạy
- [ ] `results/scenarios.csv` — bảng chỉ số đầy đủ + kiểm định thống kê (**con số #3**)
- [ ] Video/ảnh minh hoạ mô phỏng cho buổi bảo vệ
- [ ] `docs/nhat-ky/05-sumo.md` (~8 trang → chương 5 luận văn)

## Tiêu chí qua cổng G5 (T26)

Mô hình đạt chuẩn hiệu chỉnh GEH, và có ít nhất một kịch bản cho kết quả khác biệt có ý nghĩa thống kê so với hiện trạng.

---

## Rủi ro giai đoạn này

| Rủi ro | Mức | Xử lý |
|---|---|---|
| **Không đạt chuẩn GEH** | Cao | Thu hẹp vùng nghiên cứu; kiểm tra lại cấm rẽ và chu kỳ đèn; nới tiêu chí xuống GEH<7 và **ghi rõ là hạn chế** thay vì giấu |
| Sửa mạng bằng tay tốn hơn dự kiến nhiều | Cao | Thu hẹp vùng còn 1–2 km²; chấp nhận 3 điểm đếm thay vì 6 |
| Mô hình sublane chạy quá chậm | Trung bình | Giảm `--lateral-resolution`; rút ngắn thời gian mô phỏng còn 1 giờ cao điểm; giảm số lần lặp seed xuống 5 |
| Học SUMO tốn thời gian | Trung bình | **Bắt đầu học SUMO từ T15**, làm một ví dụ đồ chơi trước khi bước vào mạng thật |
| Kết quả kịch bản không có ý nghĩa thống kê | Trung bình | Tăng số lần chạy; chọn can thiệp mạnh tay hơn; báo cáo trung thực kết quả không có ý nghĩa — đó vẫn là phát hiện |
