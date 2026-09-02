# Bối cảnh dự án — Luận văn Thạc sĩ Hệ thống thông tin

> File này được Claude Code tự động đọc khi mở phiên mới. Mục đích: một phiên chat mới hiểu ngay đang làm gì, đã quyết định gì, và tiếp theo phải làm gì — không cần giải thích lại từ đầu.
>
> **Cập nhật lần cuối: 30/08/2026**

---

## 1. Người dùng và bối cảnh

- Học viên cao học **ngành Hệ thống thông tin**, Khoa Toán–Tin học, Trường ĐH Sư phạm – ĐH Đà Nẵng
- GVHD: **Nguyễn Trần Quốc Vinh**
- Có kỹ năng lập trình game (Unreal Engine 5, Unity) — hữu ích cho phần web/trực quan hoá, **không** hữu ích cho Spark/SUMO/kỹ thuật giao thông
- Giao tiếp bằng **tiếng Việt**

---

## 2. Đề tài đã chốt

> **Xây dựng hệ thống phân tích và phân luồng giao thông đô thị Đà Nẵng trên nền dữ liệu lớn: kết hợp đồ thị OpenStreetMap và đếm phương tiện bằng thị giác máy tính**

Chuỗi lập luận khép kín của đề tài:

```
Video thực địa → đếm xe (YOLO/RF-DETR, đối chứng GEH<5)
  → quy đổi PCU → trọng số cạnh qua hàm BPR
  → phân tích trên Spark (SSSP có trọng số, độ trung tâm, tính bền vững)
  → xác định đoạn/nút trọng yếu
  → thiết kế kịch bản can thiệp XUẤT PHÁT TỪ chính kết quả phân tích
  → mô phỏng SUMO đã hiệu chỉnh → định lượng mức cải thiện
```

### ⚠️ Câu hỏi chưa được trả lời

**Đề tài giao thông này là LUẬN VĂN hay là BÁO CÁO MÔN Big Data?** Người dùng chưa xác nhận. Điều này thay đổi quy mô rất lớn:

- **Nếu là luận văn**: dùng nguyên bộ plan 15 file, ~53 tuần
- **Nếu là báo cáo môn học**: chỉ cần OSM + Spark + đo scalability, ~6–8 tuần, bỏ hẳn SUMO/gán nhãn/web app

**Hỏi lại người dùng trước khi tư vấn sâu.**

---

## 3. Lịch sử quyết định — đừng bàn lại

Ba đề tài đã được cân nhắc và loại/chọn. **Không mở lại các cuộc thảo luận này** trừ khi người dùng chủ động nêu.

| Đề tài | Kết quả | Lý do |
|---|---|---|
| 10 đề tài trong `Các đề tài nội dung chính.pptx` (BFS/K-means/max-flow/Bellman-Ford trên MapReduce, YOLO sâm Ngọc Linh, bệnh mắt…) | **Loại** | Hadoop MapReduce đã lỗi thời; dữ liệu Facebook không lấy được; sâm Ngọc Linh không tiếp cận được vườn; bệnh mắt cạnh tranh quá cao và YOLO sai công cụ |
| **Cảnh báo sớm nguy cơ không đạt học phần** (có đề cương 31 trang đã viết, file `PPLNCKH/.../PPLNCKH_DoNgocQuangLuan_51UHTTT.pdf`) | **Không chọn** | Dù an toàn hơn nhiều và đã có đề cương, người dùng vẫn chốt đề tài giao thông |
| **Giao thông Đà Nẵng** | ✅ **ĐÃ CHỐT** | Novelty rộng hơn, đúng trục Big Data, khoảng trống địa lý thật |

Đề cương cảnh báo sớm đã viết vẫn còn giá trị nếu người dùng đổi ý — nó được đánh giá là **trên mức trung bình khá rõ**, đặc biệt phần kiểm định thống kê (Bảng 8) vượt chuẩn thông thường của lĩnh vực.

---

## 4. Trạng thái hiện tại

### ✅ Đã xong

- **Bộ kế hoạch 15 file trong `docs/plan/`** — xem `docs/plan/README.md` để biết mục lục
- **Job thu dữ liệu TomTom đã viết và chạy thử thành công** trong `ingest/tomtom/`
  - `collect.py` — gọi API, ghi Parquet theo ngày, có log
  - `kiem_tra_diem.py` — kiểm tra chất lượng điểm đo, phát hiện trùng đoạn
  - `segments.csv` — **12 điểm đã dò và kiểm chứng, đạt 12/12**
  - Đã thu 2 lần vào `ingest/tomtom/data/2026-08-30.parquet`

- **GitHub Actions workflow đã viết** — `.github/workflows/thu-thap-tomtom.yml`
  - Người dùng **không có server chạy 24/24**, nên job chạy trên hạ tầng GitHub, miễn phí
  - Lịch thích ứng: cao điểm (VN 05–09h, 16–20h) 10 phút/lần; còn lại 20 phút/lần
  - Phút lẻ (3,13,23… / 7,27,47) là cố ý: tránh giờ GitHub đông + tạo độ lệch chống sai lệch hệ thống
  - Dữ liệu commit thẳng vào repo → tự có sao lưu và lịch sử phiên bản
  - Hướng dẫn 4 bước ở `ingest/tomtom/CHAY-TREN-GITHUB.md`

### ⏳ Đang chờ người dùng làm

1. **Đẩy repo lên GitHub (để PUBLIC) + nạp secret `TOMTOM_API_KEY`** → bật workflow. Repo công khai mới có phút chạy Actions không giới hạn; repo riêng tư chỉ 2.000 phút/tháng, không đủ
2. **Đổi API key TomTom** — key cũ đã lộ trong lịch sử chat, phải tạo key mới trước khi push
3. **Đăng ký `opendata.danang.gov.vn`** — checklist 6 mục ở `docs/plan/00b-giai-doan-0-de-cuong.md` mục 0.2

### ❌ Chưa bắt đầu

Toàn bộ Giai đoạn 0 trở đi: kéo đồ thị OSM, chốt hành lang nghiên cứu, quay thử, đo tỷ lệ sót xe máy, viết đề cương.

---

## 5. Việc tiếp theo ngay

Theo `docs/plan/00b-giai-doan-0-de-cuong.md`:

| Thứ tự | Việc | Thời gian |
|---|---|---|
| 1 | Đặt lịch job TomTom chạy tự động | 15 phút |
| 2 | Đăng ký cổng dữ liệu mở, khảo sát danh mục GTVT | 30 phút |
| 3 | **Kéo đồ thị OSM Đà Nẵng, lập bảng thống kê** (số đỉnh/cạnh, % thiếu `maxspeed`/`lanes`) | 1 ngày |
| 4 | Khảo sát thực địa, chốt hành lang 3–5 km + 6–12 điểm quay | 2 ngày |
| 5 | Quay thử 30 phút, **đo tỷ lệ sót xe máy của RF-DETR và YOLO gốc** | 2 ngày |
| 6 | Viết đề cương với 4 con số đo được | 3 tuần |

**Người dùng đã yêu cầu script kéo đồ thị OSM (việc số 3) — đó là việc tiếp theo cần làm khi họ báo.**

---

## 6. Sự thật đã kiểm chứng — dùng lại, đừng tìm lại

### Cổng dữ liệu mở Đà Nẵng

- **Quyết định 804/QĐ-UBND ngày 05/03/2026**, ký bởi Phó Chủ tịch UBND TP **Hồ Quang Bửu**
- **14 lĩnh vực, 211 mục dữ liệu**; riêng **GTVT & logistics: 19 mục**, gồm mạng lưới xe buýt, luồng tuyến vận tải cố định, **và dữ liệu camera giám sát giao thông**
- Cơ quan chủ trì: **Sở Khoa học và Công nghệ Đà Nẵng**. Mục tiêu 2026: hoàn thành ≥90%
- Cổng: `opendata.danang.gov.vn` / `congdulieu.vn` — **đăng ký tự phục vụ, KHÔNG cần công văn**
- ⚠️ Nhưng cổng đang yêu cầu đăng nhập và trang dịch vụ dữ liệu báo "đang cập nhật" → **nằm trong danh mục ≠ tải được hôm nay**
- Hỗ trợ: **0236 1022** / `info@congdulieu.vn`
- ⚠️ Đừng nhầm với **804/QĐ-TTg ngày 06/5/2026** (Thủ tướng, dữ liệu cho AI) — trùng số, khác cấp

### Camera

| Phạm vi | Số lượng |
|---|---|
| Đà Nẵng (ranh giới cũ) | **Gần 170 camera tại 71 điểm/tuyến** |
| QL1A qua Quảng Trị–Huế–Đà Nẵng | 80 camera / 224 km (hệ thống quốc lộ, CSGT quản lý) |
| Quảng Nam cũ | Không có số liệu công khai |
| Đà Nẵng mới sau sáp nhập | **Chưa ai công bố** — có thể thành một câu hỏi khảo sát của luận văn |

- `camera.0511.vn` — **đang tạm đóng để nâng cấp**, kiểm tra lại định kỳ
- `giaothong.hochiminhcity.gov.vn/map.aspx` — cổng TP.HCM đang mở, dùng để bổ sung dữ liệu huấn luyện
- IOC Đà Nẵng khai trương 8/2023

**Reframe quan trọng:** luận văn chỉ cần **6–12 điểm đếm trên một hành lang**, không cần 170 camera. Câu hỏi đúng là *"có 6–12 camera cùng hành lang, truy cập được, góc đủ cao không"*.

### Bối cảnh chính sách 2026 (dùng cho chương mở đầu)

- **QĐ 456/QĐ-TTg 20/3/2026** — Đề án Trung tâm dữ liệu, giám sát, điều hành giao thông 2026–2030
- **QĐ 502/QĐ-TTg 2026** — kết nối dữ liệu camera với CSDL quốc gia
- **QCVN 11:2026/BCA** — quy chuẩn kỹ thuật camera giám sát
- **QĐ 804/QĐ-TTg 06/5/2026** — danh mục dữ liệu phục vụ phát triển AI

---

## 7. Kiểm tra trùng lặp đã làm — novelty còn lại rất hẹp

**Đã tra cứu kỹ. Từng thành phần của đề tài đều đã được công bố:**

| Công trình | Phủ mảng nào |
|---|---|
| **BigSUMO** (arXiv 2601.02286, 01/2026) | Spark/Hadoop + SUMO song song + scalability — **không có thị giác máy tính** |
| **Counting Mixed Traffic at Motorcycle-Dominated Intersections** (Springer IJITSR 2024) | Đếm xe giao lộ xe máy chi phối bằng CV |
| Toronto turning movement → SUMO (arXiv 2508.10733) | Hiệu chỉnh SUMO từ số đếm |
| Intersection analysis with CV + SUMO (Oxford ITI), DeepSIGNAL-ITS | CV + SUMO tích hợp |
| TGDT, OpenTwinMap, "Driving SUMO Towards Digital Twins" | Bản sao số từ OSM + CV + SUMO |
| Parallel Shortest Path on Spark (US road network) | Đồ thị phân tán |
| AI-based traffic counting Vietnam; Vehicle Detection in Vietnam's Complex Urban Traffic | Góc "xe máy Việt Nam" **đã đông** |

**Ba điều còn lại — chỉ tuyên bố đúng ba điều này, không hơn:**

1. **Chuỗi bốn khâu chưa ai ghép**: CV → trọng số đồ thị → xử lý phân tán → mô phỏng, trong một hệ thống khép kín có kiểm chứng ở từng khâu
2. **Đà Nẵng hoàn toàn trống** — tra cứu không ra công trình nào về mạng lưới giao thông Đà Nẵng bằng OSM; mạng sau sáp nhập Quảng Nam (7/2025) chưa ai phân tích
3. **Bộ dữ liệu chưa tồn tại** — chưa có dataset ảnh giao thông Đà Nẵng công khai; các bài review nêu đích danh khoảng trống *"chưa có bộ dữ liệu đô thị công khai cho Đông Nam Á"*

⚠️ **Lĩnh vực này xuất bản rất nhanh.** Đặt cảnh báo Google Scholar và rà lại mỗi tháng.

---

## 8. Quyết định kỹ thuật đã chốt

| Quyết định | Nội dung | Lý do |
|---|---|---|
| **Phạm vi** | **Nghiên cứu hành lang 3–5 km, 6–12 điểm đếm** — KHÔNG làm cả thành phố | Nhiều hơn thì không hiệu chỉnh SUMO nổi, không đếm tay đối chứng nổi |
| **Mô hình phát hiện** | **RF-DETR** (Apache 2.0, backbone DINOv2) làm mô hình đề xuất; YOLOv11/YOLO26 làm mốc so sánh | RF-DETR dẫn đầu benchmark RF100-VL về chuyển giao miền — mạnh nhất khi fine-tune dataset nhỏ ở miền lạ. YOLO Ultralytics là **AGPL-3.0**, ràng buộc thật nếu chuyển giao |
| **Kiến trúc** | **Lambda**: tầng batch (Spark/YOLO/SUMO, chạy local) + tầng serving (FastAPI + DuckDB + PMTiles, deploy công khai) | Gọi đúng tên kiến trúc, **không** trình bày như giải pháp tình thế vì thiếu máy chủ |
| **Chia tập dữ liệu** | **Theo điểm quay**, KHÔNG chia ngẫu nhiên | Chia ngẫu nhiên làm khung cùng video nằm cả train lẫn test → mAP bị thổi phồng, kết quả vô giá trị |
| **Nguồn dữ liệu chính** | Tự quay (khách sạn tầng cao / cầu vượt bộ hành) + TomTom + xe thăm dò GPS | Không cần xin phép ai; công văn không nằm trên đường găng |

### Bốn con số là toàn bộ đóng góp khoa học

| # | Con số | Chứng minh |
|---|---|---|
| 1 | Mức tăng mAP sau fine-tune trên dữ liệu Đà Nẵng | Tồn tại khoảng cách miền |
| 2 | Sai số bộ đếm vs đếm tay (MAE/MAPE/**GEH**) | Dữ liệu đầu vào đáng tin |
| **3** ⭐ | **Mức giảm sai số ước lượng thời gian hành trình khi dùng trọng số động vs trọng số tĩnh OSM, đối chứng bằng TomTom** | **Việc ghép hai nửa có giá trị thật** |
| 4 | Mức giảm tổng thời gian trễ trong kịch bản SUMO | Giá trị ra quyết định |

**Con số #3 quan trọng nhất và dễ bị bỏ quên nhất** — nó là bằng chứng duy nhất trả lời câu hội đồng chắc chắn hỏi: *"Vì sao phải ghép thị giác máy tính với đồ thị?"* Không có nó → hai đồ án rời.

---

## 9. Ba bẫy kỹ thuật đã biết trước

1. **`GraphFrames.shortestPaths()` KHÔNG hỗ trợ trọng số** — chỉ chạy BFS theo số cạnh. Phải tự cài Bellman-Ford bằng vòng lặp join trên DataFrame, **bắt buộc checkpoint mỗi 3–5 vòng** để cắt lineage, nếu không Spark tràn bộ nhớ.
2. **SUMO mặc định mô phỏng theo làn** — sai bản chất với xe máy Việt Nam. Phải bật **sublane model** (`--lateral-resolution`) và định nghĩa `vType` riêng (`width=0.8`, `latAlignment="arbitrary"`).
3. **Câu hỏi "Big Data ở đâu?"** — đồ thị 50k đỉnh chạy được trên một laptop. Phải trả lời bằng tích các chiều (cặp OD × lát cắt thời gian × kịch bản ≈ 1,9 triệu lần tính SSSP) + độ trung tâm trung gian O(|V||E|), và **đưa biểu đồ speedup có điểm giao** với đường một-máy. Thừa nhận thẳng, đừng thổi phồng.

---

## 10. Cấu trúc thư mục

```
danang-traffic-analytics/          ← REPO GIT (thu muc lam viec chinh)
├── CLAUDE.md                      ← file nay
├── README.md                      gioi thieu repo, cong khai
├── requirements.txt
├── .github/workflows/             lich chay tu dong tren GitHub Actions
│   └── thu-thap-tomtom.yml
├── ingest/tomtom/                 job thu du lieu toc do, DANG CHAY
│   ├── collect.py, kiem_tra_diem.py, segments.csv
│   ├── README.md, CHAY-TREN-GITHUB.md
│   └── data/*.parquet             ← DU LIEU KHONG TAI TAO DUOC
└── docs/plan/                     15 file ke hoach, doc docs/plan/README.md truoc
    ├── 00-tong-quan.md            dong thoi gian 53 tuan, 4 con so, 9 cong
    ├── 00b-giai-doan-0-de-cuong.md    ← DANG O DAY: do dac + viet de cuong
    ├── 01..09-giai-doan-*.md      cac giai doan trien khai
    ├── A-nguon-du-lieu.md         nguon du lieu da kiem chung + checklist phap ly
    ├── B-kien-truc-ky-thuat.md    cay repo, hop dong du lieu, so sanh nen tang deploy
    ├── C-quan-ly-rui-ro.md        so rui ro
    └── D-cong-nghe-va-huong-moi.md    mo hinh 2026, huong nghien cuu nong

D:\Downloads\Thac si\BigData\    ← CHI LA TAI LIEU THAM KHAO, khong phai repo
├── Cac de tai noi dung chinh.pptx     danh sach 10 de tai goc cua mon hoc
├── FAIR2026_IEEE_a4.docx              mau dinh dang bai bao
└── EL_34_*.pdf, IJCS_53_*.pdf         bai mau IAENG (venue dich tham khao)
                                        ^ CO BAN QUYEN - khong commit len repo
```

---

## 11. Cách làm việc với người dùng

- **Trả lời bằng tiếng Việt.**
- Người dùng đánh giá cao **sự thẳng thắn về rủi ro** — đã nhiều lần yêu cầu kiểm tra trùng lặp, độ khó thực tế, và tính khả thi trước khi đầu tư. Đừng tô hồng.
- Khi tư vấn novelty: **luôn tra cứu công trình đã có trước**, đừng khẳng định "cái này mới" từ trí nhớ. Đã có tiền lệ: góc "xe máy Việt Nam" ban đầu được đánh giá là novelty mạnh, tra kỹ thì hoá ra đã đông.
- Ưu tiên **việc làm được ngay** hơn là bàn luận dài. Người dùng thường hỏi "vậy tôi cần làm gì trước tiên".

### Những điều KHÔNG nên làm

- ❌ Đừng khuyên gửi công văn xin dữ liệu camera như việc ưu tiên — nó không nằm trên đường găng, tự quay mới là xương sống
- ❌ Đừng khuyên mở rộng phạm vi ra cả thành phố — đã chốt nghiên cứu hành lang
- ❌ Đừng đề xuất chuyển sang VLM/foundation model — mất trục dữ liệu lớn, cạnh tranh quá cao
- ❌ Đừng để người dùng gán nhãn quy mô lớn trước khi đề cương được thông qua (cổng G0)
- ❌ Đừng commit API key vào git
