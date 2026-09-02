# 00 — Tổng quan

## 1. Câu chuyện của luận văn (một đoạn)

Mạng lưới đường Đà Nẵng sau sáp nhập với Quảng Nam (7/2025) trở thành một đồ thị đô thị quy mô lớn chưa được phân tích một cách hệ thống. Dữ liệu hình học có sẵn từ OpenStreetMap nhưng **thiếu trọng số động** — tức là không biết đoạn đường nào thực sự đông vào giờ nào. Luận văn lấp khoảng trống đó bằng cách dùng thị giác máy tính đếm phương tiện từ camera/video thực địa, dùng số đếm ấy làm trọng số cho đồ thị, xử lý toàn bộ trên nền tảng dữ liệu lớn (Spark), rồi mô phỏng các kịch bản phân luồng bằng SUMO để định lượng mức cải thiện.

**Bốn con số là toàn bộ đóng góp khoa học:**

| # | Con số | Chứng minh điều gì | Xuất hiện ở |
|---|---|---|---|
| 1 | Mức tăng mAP sau khi fine-tune trên dữ liệu Đà Nẵng | Tồn tại khoảng cách miền giữa giao thông xe máy VN và mô hình huấn luyện trên dữ liệu phương Tây | Bài báo 1 |
| 2 | Sai số bộ đếm so với đếm tay (MAE/MAPE/**GEH**) | Số liệu đầu vào cho mô hình là đáng tin | Bài 1 + Bài 2 |
| **3** ⭐ | **Mức giảm sai số ước lượng thời gian hành trình khi dùng trọng số động từ số đếm, so với trọng số tĩnh của OSM — đối chứng độc lập bằng TomTom** | **Việc ghép hai nửa có giá trị thật, không phải hai đồ án dán vào nhau** | Bài báo 2 |
| 4 | Mức giảm tổng thời gian trễ trong kịch bản phân luồng | Hệ thống có giá trị ra quyết định thực tế | Bài báo 2 |

**Con số #3 là quan trọng nhất và dễ bị bỏ quên nhất.** Nó là bằng chứng duy nhất trả lời câu hỏi mà hội đồng chắc chắn sẽ hỏi: *"Vì sao phải ghép thị giác máy tính với đồ thị? Hai phần này liên quan gì đến nhau?"* Không có nó, bạn có hai đồ án rời. Nó tương ứng với **CH2** trong đề cương — xem [00b](00b-giai-doan-0-de-cuong.md) mục 3.2.

Nếu đến tuần 35 mà chưa có đủ bốn con số, kế hoạch đang trượt — bất kể giao diện đẹp đến đâu.

---

## 2. Kiến trúc hai tầng

```
┌─ TẦNG A — BATCH (chạy local / Colab, KHÔNG deploy) ────────────┐
│                                                                  │
│  Video, ảnh camera                                               │
│        │                                                         │
│        ├──> YOLOv11 fine-tuned + ByteTrack ──> đếm qua vạch ảo   │
│        │                                            │            │
│  OSM .pbf                                           │            │
│        │                                            v            │
│        └──> Đồ thị đã làm sạch ────> Spark: gán trọng số động   │
│                                       Spark: SSSP có trọng số    │
│                                       Spark: độ trung tâm        │
│                                            │                     │
│                                            v                     │
│                                    SUMO: kịch bản phân luồng     │
│                                            │                     │
└────────────────────────────────────────────┼─────────────────────┘
                                             v
                          ┌──────────────────────────────────┐
                          │  KHUNG NHÌN VẬT CHẤT HÓA         │
                          │  PMTiles · Parquet · SQLite      │
                          └──────────────┬───────────────────┘
                                         v
┌─ TẦNG B — SERVING (deploy công khai, free tier) ────────────────┐
│   FastAPI  ──  MapLibre GL + React  ──  URL công khai            │
└──────────────────────────────────────────────────────────────────┘
```

**Cách gọi tên trong luận văn:** kiến trúc Lambda — tách tầng xử lý theo lô (batch layer) và tầng phục vụ truy vấn (serving layer) qua các khung nhìn đã vật chất hóa (materialized views).

Đây là mẫu kiến trúc chuẩn, **không phải giải pháp tình thế vì thiếu máy chủ**. Tuyệt đối không viết trong luận văn theo kiểu "do hạn chế phần cứng nên em tính trước".

---

## 3. Dòng thời gian 53 tuần

> **Cập nhật 30/08/2026:** thêm **Giai đoạn 0 — đo đạc và viết đề cương (T1–T5)** ở đầu. Mọi giai đoạn sau dịch lùi 5 tuần. Xem [00b](00b-giai-doan-0-de-cuong.md).

```
Tháng   1    2    3    4    5    6    7    8    9   10   11   12   13
Tuần   1-5  6-9 10-13 14-17 18-21 22-25 26-29 30-33 34-37 38-41 42-45 46-49 50-53
       ─────────────────────────────────────────────────────────────────────────
GĐ0    █████                        ← đo đạc + viết đề cương, cổng G0
GĐ1         ████
GĐ2           ████████████
GĐ3                 ████████████
GĐ4                       ████████████
GĐ5                               ████████
GĐ6                                 ████████████
Bài 1                         ████████████
Bài 2                                     ████████████████
Luận văn                                       ████████████████████████
Bảo vệ                                                               ██
```

Chồng lấn là cố ý. Bốn quy tắc:

- **GĐ0 kết thúc bằng cổng G0** — không đầu tư gán nhãn quy mô lớn trước khi đề cương được thông qua. Nếu hội đồng yêu cầu đổi hướng, bạn mất 5 tuần chứ không phải 5 tháng.
- **Job TomTom chạy từ NGÀY 1 của GĐ0**, xuyên suốt cả 53 tuần. Đây là việc duy nhất thực sự khẩn.
- **GĐ2 (dữ liệu) chạy nền suốt 12 tuần** — quay video và gán nhãn là việc rời rạc, làm xen kẽ.
- **GĐ4 (đồ thị/Spark) không phụ thuộc GĐ3** — làm song song. Bí ở thị giác máy tính thì chuyển sang Spark, đừng ngồi chờ.

### Vì sao đo trước rồi mới viết đề cương

Bốn con số nền của đề tài này **chưa ai công bố** — số đỉnh/cạnh đồ thị Đà Nẵng mới, % cạnh thiếu thuộc tính, tỷ lệ mô hình gốc sót xe máy, và cổng dữ liệu mở thực tế có gì. Viết đề cương trước khi đo thì bốn chỗ đó sẽ là "dự kiến", và hội đồng sẽ hỏi đúng vào đó. Hai tuần đo đổi lấy một đề cương có bằng chứng thực nghiệm — đó là trao đổi có lời.

Nhưng **chỉ đo, không xây**. Xây hệ thống ba tháng rồi mới viết đề cương là sai ngược lại: bạn có thể sa lầy vào hướng GVHD không đồng ý.

---

## 4. Cột mốc bắt buộc (milestone gates)

Không được đi tiếp nếu chưa qua cổng.

| Cổng | Tuần | Điều kiện qua cổng |
|---|---|---|
| **G0 — Đề cương được thông qua** | **T5** | **Đề cương có 4 con số đo thật; GVHD duyệt; bảo vệ trước bộ môn.** Không gán nhãn quy mô lớn trước cổng này |
| **G1 — Xương sống** | T9 | `docker compose up` chạy được; URL công khai hiện bản đồ Đà Nẵng với dữ liệu giả |
| **G2 — Đường ống thông suốt** | T13 | Một video thật → mô hình → số đếm → ghi Parquet → hiện lên bản đồ. Kết quả xấu cũng được, miễn là **thông** |
| **G3 — Dữ liệu đủ** | T19 | ≥1.500 ảnh đã gán nhãn, chia **theo điểm quay**; ≥10 giờ video thô đã lưu trữ |
| **G4 — Con số #1 và #2** | T25 | Bảng mAP trước/sau fine-tune; bảng đối chứng đếm tay MAE/MAPE/GEH |
| **G5 — Con số #3 và #4** | T31 | SUMO đạt GEH<5 ở ≥85% điểm; ≥2 kịch bản có kiểm định thống kê; **CH2 đã trả lời** |
| **G6 — Sản phẩm hoàn chỉnh** | T35 | Web app công khai chạy dữ liệu thật, đủ 5 thao tác demo |
| **G7 — Bài báo 1 đã gửi** | T31 | Có mã số bản thảo |
| **G8 — Bản thảo luận văn đầy đủ** | T47 | 100% chương, đã gửi GVHD lần 1 |
| **G9 — Bảo vệ** | T51–53 | Đã in quyển, đã tổng duyệt ≥2 lần |

---

## 5. Sáu nguyên tắc bất di bất dịch

**1. Đường ống trước, chất lượng sau.**
Nối đủ 5 mắt xích ở T8 với kết quả tệ, còn hơn có một mô hình mAP 0.92 ở T20 mà chưa nối gì.

**2. Deploy khung rỗng ngay tháng đầu.**
CORS, biến môi trường, giới hạn RAM, dung lượng ảnh Docker — luôn phát sinh sự cố ngoài dự kiến. Xử lý chúng khi còn rảnh, không phải tuần trước bảo vệ.

**3. Bắt đầu thu chuỗi thời gian từ ngày đầu tiên.**
Dữ liệu tốc độ từ TomTom/HERE là dữ liệu quá khứ — **không mua lại được**. Mỗi ngày trì hoãn là một ngày dữ liệu mất vĩnh viễn. Đây là việc cần làm trước cả khi đọc xong kế hoạch này.

**4. Viết luận văn song song, không viết dồn.**
Kết thúc mỗi giai đoạn, viết ngay 3–8 trang nhật ký kỹ thuật: đã làm gì, tham số nào, kết quả ra sao, tại sao chọn cách đó. Đến T29 bạn *biên tập* thay vì *sáng tác*. Chi tiết kỹ thuật quên rất nhanh — sau 4 tháng bạn sẽ không nhớ nổi vì sao chọn `conf=0.35`.

**5. Mọi con số phải tái lập được bằng một lệnh.**
Mỗi bảng trong luận văn ứng với một script trong `experiments/` sinh ra một file CSV trong `results/`. Khi phản biện hỏi "số này ở đâu ra", bạn chạy lại được tại chỗ.

**6. Bảo vệ phạm vi tối thiểu bằng mọi giá.**
Xem mục 6. Khi trễ tiến độ, cắt bớt tính năng — không bao giờ cắt bớt phần đối chứng (validation). Một hệ thống ít tính năng nhưng có đối chứng đầy đủ thì bảo vệ được; ngược lại thì không.

---

## 6. Phạm vi tối thiểu vs phạm vi đầy đủ

Quyết định ranh giới này **ngay bây giờ**, đừng để nó tự xảy ra vào tháng cuối.

| Hạng mục | Tối thiểu (cam kết) | Đầy đủ (nếu thuận lợi) |
|---|---|---|
| Điểm quay | 6 | 12 |
| Ảnh gán nhãn | 1.500 | 3.000+ |
| Lớp phương tiện | 4 (xe máy, ô tô con, xe tải/khách, xe buýt) | 6 (+ xe đạp, người đi bộ) |
| Đồ thị | Đà Nẵng cũ (~30k đỉnh) | Đà Nẵng + Quảng Nam (~150k đỉnh) |
| Trọng số động | 3 khung giờ (sáng/trưa/chiều) | 24 khung giờ × ngày thường/cuối tuần |
| Spark | 3 node Docker trên 1 máy | 5 node thật hoặc cloud |
| Kịch bản SUMO | 2 | 4 |
| Web app | Bản đồ + định tuyến + biểu đồ | Thêm streaming, so sánh kịch bản trực tiếp |
| Bài báo | 1 đã gửi | 2 đã gửi, 1 đã chấp nhận |
| Dataset | Lưu nội bộ | Công bố Zenodo có DOI |

**Bản tối thiểu đủ để bảo vệ và đủ cho một bài báo.** Bám lấy nó trước, mở rộng sau.

---

## 7. Thứ tự ưu tiên khi trễ tiến độ

Khi phải cắt, cắt theo thứ tự này (cắt từ trên xuống):

1. Bài báo 2 (hoãn sang sau bảo vệ)
2. Công bố dataset lên Zenodo
3. Streaming thời gian thực → chuyển hoàn toàn sang batch
4. Kịch bản SUMO thứ 3 và 4
5. Mở rộng đồ thị sang Quảng Nam
6. Số điểm quay 12 → 6

**Không bao giờ cắt:** đối chứng đếm tay, bảng mAP trước/sau, hiệu chỉnh GEH của SUMO, và tính tái lập của repo. Đó là bốn thứ tạo nên tính khoa học của luận văn.
