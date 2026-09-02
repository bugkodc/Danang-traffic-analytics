# Giai đoạn 3 — Thị giác máy tính (Tuần 9–16)

> **Mục tiêu:** Sinh ra **con số #1** (mức tăng mAP sau fine-tune) và **con số #2** (sai số bộ đếm so với đếm tay). Đây là toàn bộ nội dung bài báo 1.

Điều kiện bắt đầu: đã có ≥1.000 ảnh gán nhãn (không cần chờ đủ 3.000 — bắt đầu sớm với ít dữ liệu, huấn luyện lại khi có thêm).

---

## 1. Thiết lập thí nghiệm

### 1.1 Đường cơ sở phải có (baseline)

Bài báo cần ít nhất 3 mốc so sánh, nếu không reviewer sẽ hỏi "so với cái gì?":

| Mốc | Mô tả | Vai trò |
|---|---|---|
| **B0** | Trọng số COCO gốc, không huấn luyện lại | Thể hiện domain gap thô |
| **B1** | Huấn luyện trên MIO-TCD hoặc UA-DETRAC (dữ liệu phương Tây) | Mốc "dữ liệu giao thông nhưng không phải VN" |
| **B1v** | Huấn luyện trên dataset VN công khai (Roboflow/Kaggle, xem [A](A-nguon-du-lieu.md) 3.1) | Mốc "dữ liệu VN nhưng không phải Đà Nẵng" |
| **B2** | B1 + fine-tune trên `DaNang-Traffic-2026` | **Mô hình đề xuất** |
| B3 *(tùy chọn)* | Huấn luyện từ đầu chỉ trên dữ liệu Đà Nẵng | Chứng minh pre-training có ích |

Khoảng cách B0 → B2 chính là **con số #1**. Khoảng cách B1 → B2 là phần thuyết phục nhất, vì nó tách bạch "nhờ dữ liệu Việt Nam" khỏi "nhờ dữ liệu giao thông nói chung". Mốc B1v mới thêm cho phép tách thêm một tầng nữa: "nhờ dữ liệu Đà Nẵng" khỏi "nhờ dữ liệu Việt Nam".

### 1.2 Biến thể kiến trúc — **đã cập nhật 30/08/2026**

Bối cảnh mô hình đã đổi đáng kể. Xem [D](D-cong-nghe-va-huong-moi.md) mục 1 để biết chi tiết. Tóm tắt quyết định:

| Mô hình | Giấy phép | Vai trò trong luận văn |
|---|---|---|
| **RF-DETR** | **Apache 2.0** | **Mô hình đề xuất** — backbone DINOv2, dẫn đầu benchmark RF100-VL về chuyển giao miền, mạnh nhất khi fine-tune dataset nhỏ ở miền lạ |
| **YOLO26** | AGPL-3.0 | Mốc so sánh — mới nhất của Ultralytics, tối ưu lượng tử hoá, nhanh hơn 43% trên CPU so với YOLO11-n |
| **YOLOv11** | AGPL-3.0 | Mốc so sánh quen thuộc, cộng đồng lớn |
| RTMDet *(tuỳ chọn)* | MIT | Nếu muốn chiều "thông lượng cao, giấy phép thoáng" |

Ba lý do đổi mô hình đề xuất sang RF-DETR: (a) nó được thiết kế đúng cho tình huống dataset nhỏ ở miền lạ — chính là tình huống của bạn; (b) giấy phép Apache 2.0 không ràng buộc như AGPL nếu sau này muốn chuyển giao cho cơ quan quản lý; (c) bảng so sánh có thêm chiều giấy phép là bảng có nội dung.

**Nếu ngại rủi ro:** giữ YOLOv11 làm đường cơ sở đã quen và **thêm** RF-DETR làm mô hình đề xuất. Chi phí thêm khoảng 2–3 ngày.

**Thêm một mục ngắn về giấy phép trong luận văn** (AGPL-3.0 của Ultralytics vs Apache 2.0/MIT). Rất ít học viên để ý, và nó thể hiện tư duy triển khai hệ thống — đúng chất ngành Hệ thống thông tin.

### 1.2b Thí nghiệm liên thành phố — **bổ sung, ưu tiên cao**

Đây là nâng cấp novelty lớn nhất với chi phí thấp nhất. Chi tiết ở [D](D-cong-nghe-va-huong-moi.md) mục 2.1.

| Huấn luyện trên | Kiểm thử trên | mAP | Ý nghĩa |
|---|---|---|---|
| Phương Tây (MIO-TCD/UA-DETRAC) | Đà Nẵng | | Khoảng cách miền lớn nhất |
| TP.HCM (camera công khai + dataset VN) | Đà Nẵng | | Khoảng cách **liên thành phố trong nước** |
| Đà Nẵng | TP.HCM | | Chiều ngược lại |
| TP.HCM + Đà Nẵng | Đà Nẵng | | Lợi ích của gộp dữ liệu |

Bảng này biến bài báo từ *"fine-tune YOLO cho Đà Nẵng"* thành *"định lượng khoảng cách miền liên thành phố trong giao thông xe máy chi phối Đông Nam Á"* — chủ đề đang có track riêng ở AI City Challenge 2026, và trùng đúng khoảng trống mà các bài review nêu ra: **chưa có bộ dữ liệu đô thị công khai cho Đông Nam Á**.

Công thêm: ~1 tuần (chủ yếu là thu ảnh TP.HCM từ cổng camera công khai).

### 1.3 Tăng cường dữ liệu (augmentation)

Ultralytics có sẵn mosaic, mixup, HSV, scale, flip. Cần cân nhắc riêng cho bài toán này:

- **Bật mạnh:** scale (xe máy xa/gần chênh lệch lớn), HSV (ngược sáng, đèn đường)
- **Cẩn thận với flip ngang:** giao thông VN đi bên phải — lật ngang tạo cảnh không tồn tại. Vẫn nên bật vì lợi ích tổng thể lớn hơn, nhưng phải thử nghiệm cả hai và **báo cáo kết quả** — đây là một chi tiết nhỏ nhưng cho thấy sự cẩn trọng.
- **Copy-paste augmentation** cho lớp thiếu mẫu (xe buýt thường ít)

Chạy một thí nghiệm loại trừ (ablation) về augmentation → thêm một bảng cho bài báo.

---

## 2. Huấn luyện

### 2.1 Cấu hình khởi điểm

```
imgsz: 960          # cao hơn mặc định 640 vì xe máy là vật thể nhỏ
epochs: 100-150
batch: theo VRAM
optimizer: AdamW
patience: 30
cos_lr: True
```

`imgsz=960` là điều chỉnh quan trọng nhất cho bài toán này. Chạy một thí nghiệm loại trừ với 640 / 960 / 1280 và đưa vào bài — nó chứng minh bạn hiểu bản chất bài toán vật thể nhỏ chứ không chỉ chạy lệnh mặc định.

### 2.2 Hạ tầng huấn luyện

- Máy cá nhân có GPU: tốt nhất, chủ động
- **Kaggle**: 30 giờ GPU/tuần miễn phí, phiên 12 giờ — đủ cho hầu hết lần chạy
- **Colab free**: hay bị ngắt, chỉ dùng thử nghiệm nhanh
- Luôn ghi checkpoint ra Google Drive/ổ ngoài để phiên bị ngắt không mất

### 2.3 Ghi nhận thí nghiệm

Dùng Weights & Biases (miễn phí cho tài khoản học thuật) hoặc ít nhất là bảng CSV kỷ luật. Mỗi lần chạy ghi: mã lần chạy, cấu hình, dữ liệu phiên bản nào, mAP50, mAP50-95, AP từng lớp, thời gian huấn luyện.

**Không được để tình trạng "kết quả tốt nhất mà không nhớ chạy bằng cấu hình gì".**

---

## 3. Đánh giá phát hiện

### 3.1 Bảng chính của bài báo

| Mô hình | mAP50 | mAP50-95 | AP xe máy | AP ô tô | AP xe buýt | AP xe tải | FPS | Giấy phép |
|---|---|---|---|---|---|---|---|---|
| B0 · YOLOv11m (COCO) | | | | | | | | AGPL-3.0 |
| B0 · RF-DETR (COCO) | | | | | | | | Apache 2.0 |
| B1 · + MIO-TCD | | | | | | | | |
| B1v · + dataset VN công khai | | | | | | | | |
| **B2 · RF-DETR + Đà Nẵng (đề xuất)** | | | | | | | | Apache 2.0 |
| B2 · YOLO26 + Đà Nẵng | | | | | | | | AGPL-3.0 |

**AP của lớp xe máy là cột quan trọng nhất** — nó là hiện thân của luận điểm domain gap.

### 3.2 Đánh giá phân tầng — đây là chỗ ăn điểm

Đừng chỉ báo cáo một con số tổng. Tách theo điều kiện:

| Điều kiện | mAP50 B0 | mAP50 B2 | Mức cải thiện |
|---|---|---|---|
| Ban ngày, nắng | | | |
| **Mưa** | | | |
| **Chạng vạng / đêm** | | | |
| Mật độ thấp | | | |
| **Mật độ cao (tắc)** | | | |
| Ngược sáng | | | |

Bảng này thường cho thấy mức cải thiện ở điều kiện khó lớn hơn nhiều so với điều kiện dễ — đó là một phát hiện có nội dung, không chỉ là một con số.

### 3.3 Phân tích lỗi

Chọn 100 trường hợp sai điển hình, phân loại nguyên nhân: che khuất, vật thể quá nhỏ, nhầm lớp, hộp trùng lặp, mờ do chuyển động. Kèm 4–6 ảnh minh hoạ trong bài báo.

Phần này khiến bài báo trông như nghiên cứu chứ không như báo cáo kỹ thuật.

---

## 4. Bám vết và đếm

### 4.1 Bám vết

Dùng **ByteTrack** (mặc định trong Ultralytics, mạnh với vật thể bị che). So sánh với BoT-SORT nếu có thời gian.

Vấn đề đặc thù của giao thông xe máy: xe máy đi sát nhau, ID hay bị hoán đổi (ID switch). Cần chỉnh:
- `track_high_thresh`, `track_low_thresh`: hạ xuống so với mặc định vì độ tin cậy phát hiện xe máy thấp hơn
- `track_buffer`: tăng để giữ vết qua các đoạn bị che

Báo cáo chỉ số MOTA / IDF1 nếu gán được nhãn bám vết cho một đoạn ngắn (30 giây cũng đủ).

### 4.2 Đếm qua vạch ảo

Thuật toán: với mỗi vết, xét dấu của tích có hướng giữa vector vạch và vị trí tâm hộp qua các khung liên tiếp; đổi dấu = đã cắt vạch. Ghi lại hướng cắt để tách chiều.

Chi tiết dễ sai, phải xử lý:
- **Chống đếm trùng:** một vết chỉ được đếm một lần cho mỗi vạch
- **Vết đứt đoạn:** nếu ID bị mất rồi tạo lại giữa chừng, đối tượng bị đếm 2 lần → cần khoảng thời gian tối thiểu giữa hai lần đếm của các ID gần nhau về không gian
- **Xe dừng đè lên vạch:** dao động qua lại gây đếm nhiều lần → yêu cầu khoảng cách di chuyển tối thiểu
- **Gán lớp cho vết:** lấy lớp xuất hiện nhiều nhất trong toàn bộ vết, không lấy lớp ở khung cắt vạch

### 4.3 Đối chứng với đếm tay — **con số #2**

| Điểm | Điều kiện | Đếm tay | Hệ thống | Sai số | MAPE | **GEH** |
|---|---|---|---|---|---|---|
| site_03 | Sáng, nắng | | | | | |
| site_07 | Chiều, mưa | | | | | |
| … | | | | | | |

Ba chỉ số phải báo cáo:
- **MAE** — sai số tuyệt đối trung bình
- **MAPE** — sai số phần trăm
- **GEH** — chỉ số chuẩn của ngành kỹ thuật giao thông:

```
GEH = sqrt( 2(M-C)^2 / (M+C) )     M = số đếm mô hình, C = số đếm thực
```

**Chuẩn ngành: GEH < 5 ở ≥85% điểm đếm** thì mô hình được coi là hiệu chỉnh đạt. Dùng đúng chỉ số này thay vì chỉ dùng MAE cho thấy bạn nắm chuẩn mực của lĩnh vực ứng dụng — chi tiết nhỏ nhưng tạo khác biệt lớn với reviewer, và nó nối thẳng sang khâu hiệu chỉnh SUMO ở GĐ5.

---

## 5. Đầu ra cho các giai đoạn sau

Sản phẩm cuối của GĐ3 phải là một file Parquet theo đúng hợp đồng dữ liệu ở [B-kien-truc-ky-thuat.md](B-kien-truc-ky-thuat.md):

```
counts.parquet
  site_id, edge_id, timestamp_15min, direction,
  vehicle_class, count, pcu, confidence_mean
```

**PCU (Passenger Car Unit)** là cột quan trọng — quy đổi các loại xe về đơn vị xe con tương đương để tính lưu lượng. Hệ số quy đổi cho điều kiện Việt Nam: xe máy ~0.25–0.3, ô tô con 1.0, xe buýt/xe tải ~2.0–2.5. Trích dẫn nguồn (TCVN hoặc HCM — Highway Capacity Manual bản điều chỉnh cho giao thông hỗn hợp) và ghi rõ hệ số đã dùng.

Không có bước quy đổi PCU thì không nối được sang mô hình giao thông ở GĐ4–GĐ5.

---

## Sản phẩm bàn giao của GĐ3

- [ ] `models/yolo-danang-v1.pt` + file cấu hình huấn luyện
- [ ] `results/detection_comparison.csv` — bảng B0/B1/B2 (**con số #1**)
- [ ] `results/detection_stratified.csv` — đánh giá theo điều kiện
- [ ] `results/error_analysis.md` + ảnh minh hoạ
- [ ] `results/ablation_imgsz.csv`, `results/ablation_aug.csv`
- [ ] `results/counting_validation.csv` — MAE/MAPE/GEH (**con số #2**)
- [ ] `pipeline/vision/` chạy được: video vào → `counts.parquet` ra
- [ ] `docs/nhat-ky/03-thi-giac.md` (~10 trang → thành chương 3 luận văn)

## Tiêu chí qua cổng G4 (T20)

Con số #1 và #2 đã có, tái lập được bằng script trong `experiments/`. Nếu mức tăng mAP < 5 điểm thì domain gap yếu — xem mục rủi ro.

---

## Rủi ro giai đoạn này

| Rủi ro | Xử lý |
|---|---|
| **Mức tăng mAP quá nhỏ (<5 điểm)** — luận điểm bài báo sụp | Chuyển trọng tâm sang đánh giá phân tầng: mức cải thiện ở điều kiện mưa/đêm/mật độ cao thường vẫn lớn, đó mới là câu chuyện. Hoặc chuyển góc bài báo sang bài toán *đếm* thay vì *phát hiện*. |
| Quá khớp (overfit) do ít dữ liệu | Tăng augmentation, đóng băng lớp đầu, giảm số epoch, dùng mô hình nhỏ hơn (`yolo11s`) |
| Hoán đổi ID nhiều, đếm sai nghiêm trọng | Chỉnh ngưỡng ByteTrack; đặt vạch đếm ở vùng ít che khuất nhất; cân nhắc đếm theo vùng thay vì theo vạch |
| Hết quota GPU miễn phí | Giảm `imgsz` xuống 640 cho các lần thử, chỉ dùng 960 cho lần chạy cuối; giảm số biến thể so sánh |
| Kết quả không tái lập được giữa các lần chạy | Cố định seed, ghi lại phiên bản thư viện vào `requirements.txt` với số hiệu chính xác |
