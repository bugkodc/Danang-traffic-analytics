# Phụ lục D — Công nghệ mới và hướng nghiên cứu đang nóng

> Khảo sát ngày **30/08/2026**. Mục đích: (a) chọn đúng công nghệ để không lạc hậu ngay khi bảo vệ, (b) tìm góc nâng novelty cho bài báo, (c) gợi ý đề tài thay thế nếu cần.

---

## 1. Mô hình phát hiện đối tượng — bức tranh 2026

Plan gốc viết YOLOv11. Cần cập nhật, vì bối cảnh đã đổi đáng kể.

| Mô hình | mAP (COCO) | Giấy phép | Ghi chú |
|---|---|---|---|
| **RF-DETR** | **>60** (đầu tiên vượt 60 ở thời gian thực) | **Apache 2.0** | Backbone **DINOv2** pre-train quy mô web; **dẫn đầu benchmark RF100-VL về chuyển giao miền** |
| **YOLO26** (2025) | 40.9 (n) – 57.5 (x) | AGPL-3.0 | Mới nhất của Ultralytics; hợp nhất 5 tác vụ; **nhanh hơn 43% trên CPU** so với YOLO11-n; thiết kế tối ưu cho lượng tử hoá |
| YOLOv12 | 40.6 (n) – 55.2 (x) | AGPL-3.0 | Lai CNN + self-attention; suy giảm mạnh khi lượng tử hoá |
| YOLOv11 | — | AGPL-3.0 | Ổn định, tài liệu tốt, cộng đồng lớn |
| RT-DETRv2 | — | Apache 2.0 | Deformable attention trong decoder |
| RTMDet | 52.8 | **MIT** | Vô địch về thông lượng thuần: 300+ FPS |

### Khuyến nghị cho đề tài của bạn

**Đổi mô hình đề xuất từ YOLOv11 sang RF-DETR, giữ YOLO làm mốc so sánh.** Ba lý do:

1. **RF-DETR được thiết kế đúng cho tình huống của bạn** — fine-tune trên dataset nhỏ, miền lạ. Backbone DINOv2 pre-train quy mô web nên chuyển giao rất tốt, và đó chính là lý do nó dẫn đầu RF100-VL, benchmark đo khả năng chuyển giao miền. Dataset Đà Nẵng của bạn chỉ 1.500–3.000 ảnh và là miền khác hẳn dữ liệu phương Tây — đây đúng là kịch bản RF-DETR mạnh nhất.

2. **Vấn đề giấy phép.** YOLOv8/v11/v12/26 của Ultralytics dùng **AGPL-3.0** — yêu cầu mở mã nguồn toàn bộ hệ thống dẫn xuất hoặc mua giấy phép thương mại. Với luận văn thì không sao, nhưng nếu bạn muốn công bố repo và nói về khả năng triển khai thực tế cho cơ quan quản lý, AGPL là ràng buộc thật. RF-DETR (Apache 2.0) và RTMDet (MIT) không có vấn đề này. **Đây là một đoạn đáng viết trong luận văn** — rất ít học viên để ý đến giấy phép, và nó thể hiện tư duy hệ thống.

3. **Bảng so sánh mạnh hơn.** So RF-DETR vs YOLO26 vs YOLOv11 trên dữ liệu Đà Nẵng, kèm cả chiều giấy phép và chiều tốc độ trên CPU, là một bảng có nội dung — thay vì chỉ "chúng tôi dùng YOLO".

**Cách sửa tối thiểu nếu ngại rủi ro:** giữ YOLOv11 làm đường cơ sở đã quen, **thêm RF-DETR làm mô hình đề xuất**. Ultralytics và RF-DETR đều có API huấn luyện tương tự nhau, chi phí thêm khoảng 2–3 ngày.

---

## 2. Ba hướng đang nóng, xếp theo mức độ phù hợp với bạn

### 2.1 ⭐ Khái quát hoá liên thành phố (cross-city generalization)

**Đây là hướng ăn khớp nhất với đề tài hiện tại, gần như không tốn thêm công.**

Bằng chứng cho thấy nó đang nóng:

- **AI City Challenge 2026** (lần thứ 10, tổ chức cùng ECCV 2026, 325 đội từ 26 quốc gia) có hẳn một track chính thức là **"cross-city object detection"**
- Bài review về VLM cho giám sát đô thị (arXiv 2510.12400) nêu đích danh khoảng trống: *"gần như không có đánh giá có cấu trúc về khả năng khái quát hoá qua các bối cảnh địa lý, văn hoá, hạ tầng"*, và chỉ ra thiên lệch của Cityscapes/BDD100K về các thành phố phương Tây thu nhập cao
- Cùng bài review ghi nhận: **chưa có bộ dữ liệu đô thị công khai cho Đông Nam Á**

**Cách khai thác — chỉ cần đổi cách đóng khung, không đổi công việc:**

Bạn vốn đã có dữ liệu TP.HCM (từ cổng camera công khai) và dữ liệu Đà Nẵng (tự quay). Chỉ cần thêm một bảng thí nghiệm:

| Huấn luyện trên | Kiểm thử trên | mAP |
|---|---|---|
| Phương Tây (MIO-TCD/UA-DETRAC) | Đà Nẵng | |
| TP.HCM | Đà Nẵng | |
| Đà Nẵng | TP.HCM | |
| TP.HCM + Đà Nẵng | Đà Nẵng | |

Bảng này biến bài báo từ *"chúng tôi fine-tune YOLO cho Đà Nẵng"* (đã có hàng nghìn bài tương tự) thành *"chúng tôi định lượng khoảng cách miền liên thành phố trong giao thông xe máy chi phối Đông Nam Á"* (đang là chủ đề nóng, có track riêng ở AI City Challenge). **Chi phí thêm: khoảng một tuần. Mức tăng novelty: rất lớn.**

Đây là khuyến nghị mạnh nhất trong toàn bộ phụ lục này.

### 2.2 Mô hình thị giác–ngôn ngữ (VLM) cho giám sát đô thị

Hướng nóng nhất về mặt học thuật năm 2026, nhưng **rủi ro cao hơn**.

Bối cảnh: mô hình nền tảng (foundation model) đã thay thế việc huấn luyện mô hình chuyên biệt trong phần lớn ứng dụng thương mại; VLM và MLLM cho phép hiểu ngữ nghĩa, suy luận nhân quả và đánh giá phản thực trên video giao thông. AI City Challenge 2026 có tới ba track liên quan: **suy luận bất thường giao thông (traffic anomaly reasoning)** — chuyển từ phát hiện nhị phân sang suy luận nhân quả; **captioning và VQA về an toàn giao thông**; **hiểu vi phạm giao thông qua camera mắt cá (fisheye)**.

Khoảng trống được nêu trong bài review, kèm mức độ phù hợp cho luận văn thạc sĩ:

| Khoảng trống | Việc có thể làm | Độ nặng |
|---|---|---|
| Không có protocol đánh giá chuẩn | Xây benchmark đánh giá tính bền vững của prompt cho vật thể đô thị | Vừa |
| Phụ thuộc mô hình quá lớn (GPT-4o, BLIP-2, InternVL2) | Chưng cất tri thức / lượng tử hoá VLM cho thiết bị biên | Vừa |
| Thiếu mô hình thời gian, chỉ dùng ảnh tĩnh | Đưa chuỗi khung hình vào VLM | Nặng |
| Không tích hợp GPS/độ sâu/âm thanh | Gắn GPS vào prompt để định vị | Vừa |
| **Chưa có dữ liệu đô thị Đông Nam Á** | **Chính là việc bạn đang làm** | — |

**Cách dùng nhẹ nhàng, ít rủi ro:** thêm một mục nhỏ vào luận văn — đánh giá **zero-shot** một mô hình mở từ vựng (YOLO-World, Grounding DINO, hoặc một VLM nhỏ) trên dữ liệu Đà Nẵng, so với mô hình đã fine-tune của bạn. Kết quả gần như chắc chắn là mô hình zero-shot kém hơn nhiều trên xe máy — và **đó là một kết quả có giá trị**, củng cố thêm luận điểm domain gap. Chi phí: 2–3 ngày. Đây là cách chạm vào chủ đề nóng mà không đánh cược cả luận văn.

**Không nên** chuyển hẳn luận văn sang VLM: cần GPU mạnh, cạnh tranh cực cao, và bạn mất đi phần dữ liệu lớn/đồ thị vốn là trục của chương trình.

### 2.3 Mạng nơ-ron đồ thị không–thời gian (ST-GNN) và bản sao số

Hướng này nối thẳng vào phần đồ thị của bạn.

Khoảng trống đang được nghiên cứu:
- Phần lớn phương pháp hiện tại là **transductive** — không dự đoán được cho đỉnh chưa từng thấy, phải huấn luyện lại cho mỗi cấu trúc đồ thị mới. Hướng **inductive** đang mở
- Khó trích xuất phụ thuộc thời gian **đa thang đo** (multi-scale)
- Phương pháp graph ODE còn hạn chế ở khởi tạo biểu diễn tiềm ẩn

Có công trình gần đây về **bản sao số dựa trên đồ thị thời gian cho hành lang giao thông đô thị (TGDT)** — trùng khớp đáng chú ý với thiết kế "nghiên cứu hành lang" của bạn.

Cũng đáng chú ý: có nghiên cứu về **nội suy lưu lượng giao thông toàn thành phố bằng ST-GNN** — tức là dùng GNN để ước lượng lưu lượng ở các cạnh **không có** điểm đếm, từ một số ít cạnh **có** điểm đếm.

**Đây chính xác là bài toán bạn đang gặp** ở [GĐ4](04-giai-doan-4-do-thi-spark.md) mục 3.2: chỉ có ~12 cạnh có số đếm thật nhưng cần ước lượng cho 150.000 cạnh. Plan hiện tại giải bằng luật heuristic (theo lớp đường, theo khoảng cách). **Thay heuristic bằng một ST-GNN nội suy là nâng cấp novelty lớn nhất có thể làm cho phần đồ thị**, và nó biến một điểm yếu (ít điểm đếm) thành chính đóng góp của bài.

Mức độ nặng: cần thêm khoảng 3–4 tuần và kiến thức PyTorch Geometric. Chỉ làm nếu GĐ3 và GĐ4 chạy đúng tiến độ.

---

## 3. Bảng quyết định — nên áp dụng gì

| Nâng cấp | Công thêm | Novelty tăng | Rủi ro | Khuyến nghị |
|---|---|---|---|---|
| **Thêm RF-DETR làm mô hình đề xuất** | 2–3 ngày | Trung bình | Thấp | ✅ **Làm** |
| **Bảng thí nghiệm liên thành phố TP.HCM ↔ Đà Nẵng** | ~1 tuần | **Cao** | Thấp | ✅ **Làm — ưu tiên cao nhất** |
| **Thêm mục bàn về giấy phép AGPL vs Apache** | 2 giờ | Thấp nhưng gây ấn tượng | Không | ✅ **Làm** |
| Đánh giá zero-shot mô hình mở từ vựng | 2–3 ngày | Trung bình | Thấp | ✅ Làm nếu kịp |
| ST-GNN nội suy lưu lượng thay heuristic | 3–4 tuần | **Rất cao** | Trung bình | ⚠️ Chỉ khi đúng tiến độ ở T20 |
| Chuyển hẳn sang VLM/foundation model | 2–3 tháng | Cao | **Rất cao** | ❌ Không — mất trục dữ liệu lớn |
| Đổi sang track AI City Challenge | — | Cao | **Rất cao** | ❌ Không — cạnh tranh với nhóm nghiên cứu lớn |

---

## 4. Ảnh hưởng lên tên đề tài và cách đóng khung

Nếu áp dụng hai mục ✅ đầu tiên, tên đề tài nên nhấn thêm chiều liên thành phố:

> *Xây dựng hệ thống phân tích và phân luồng giao thông đô thị trên nền dữ liệu lớn: khảo sát khoảng cách miền liên thành phố trong giao thông hỗn hợp xe máy chi phối và ứng dụng cho Đà Nẵng*

Và tiêu đề bài báo 1 đổi thành:

> *Cross-City Domain Gap in Motorcycle-Dominant Mixed Traffic: A Benchmark and Dataset from Vietnamese Cities*

Cách đóng khung này gắn trực tiếp vào hai điều đã được cộng đồng thừa nhận là khoảng trống: **thiếu bộ dữ liệu đô thị Đông Nam Á** và **thiếu đánh giá khái quát hoá liên bối cảnh địa lý**. Nó cũng khiến bài của bạn có thể so sánh và trích dẫn qua lại với dòng nghiên cứu cross-city detection đang hình thành quanh AI City Challenge.

Đóng góp không đổi, công việc gần như không đổi — chỉ đổi cách kể.

---

## 5. Việc cần làm để cập nhật

- [ ] Đọc bài review VLM cho giám sát đô thị (arXiv 2510.12400) — lấy phần khoảng trống làm căn cứ cho mục Liên quan
- [ ] Đọc báo cáo tổng kết AI City Challenge lần thứ 10 (arXiv 2608.17044) — xem cách track cross-city detection định nghĩa bài toán và chỉ số đánh giá
- [ ] Thử RF-DETR trên 200 ảnh đầu tiên, so với YOLOv11 — quyết định mô hình chính trước khi gán nhãn xong
- [ ] Kiểm tra tình trạng giấy phép và điều khoản của từng mô hình định dùng
- [ ] Thu thập song song một tập ảnh TP.HCM từ cổng camera công khai để phục vụ bảng liên thành phố

---

## Nguồn khảo sát

- [Best Object Detection Models 2026: RF-DETR, YOLOv12 & Beyond — Roboflow](https://blog.roboflow.com/best-object-detection-models/)
- [Towards General Urban Monitoring with Vision-Language Models: A Review, Evaluation, and a Research Agenda — arXiv 2510.12400](https://arxiv.org/html/2510.12400v1)
- [The 10th AI City Challenge — arXiv 2608.17044](https://arxiv.org/abs/2608.17044)
- [AI City Challenge 2026 — Track 1](https://www.aicitychallenge.org/2026-track1/)
- [Ultralytics YOLO Evolution: YOLO26, YOLO11, YOLOv8, YOLOv5 — arXiv 2510.09653](https://arxiv.org/pdf/2510.09653)
- [Computer Vision Trends in 2026 — viso.ai](https://viso.ai/deep-learning/computer-vision-trends-2026/)
- [Emerging Trends in GNN for Traffic Flow Prediction: A Survey — Springer](https://link.springer.com/article/10.1007/s11831-025-10286-9)
- [Spatio-temporal GNN for urban spaces: Interpolating citywide traffic volume — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0957417426007360)
- [TGDT: A Temporal Graph-based Digital Twin for Urban Traffic Corridors — arXiv 2504.18008](https://arxiv.org/pdf/2504.18008)
