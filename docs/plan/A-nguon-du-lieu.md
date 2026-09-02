# Phụ lục A — Danh mục nguồn dữ liệu

> **Cập nhật 30/08/2026** — mục 2 đã được viết lại sau khi kiểm chứng các nguồn công khai. Thay đổi lớn nhất: **dữ liệu camera giám sát giao thông đã nằm trong Danh mục dữ liệu mở chính thức của Đà Nẵng**, nên cách tiếp cận đúng là qua cổng dữ liệu mở chứ không phải công văn xin phép.

---

## 1. Đồ thị đường (chắc chắn có, miễn phí)

| Nguồn | Cách lấy | Ghi chú |
|---|---|---|
| **OSMnx** | `ox.graph_from_place("Đà Nẵng, Việt Nam", network_type="drive")` | Nhanh nhất; ra thẳng `networkx` có `length`, `maxspeed`, `oneway`, `lanes` |
| **Geofabrik** | `download.geofabrik.de` → Asia → Vietnam | File `.osm.pbf` toàn quốc; cắt bằng `osmium extract --bbox` |
| **Overpass API** | Query theo `highway=*` và bbox | Khi chỉ cần một phần |
| **BBBike extract** | Vẽ bbox tuỳ ý, nhận file qua email | Tiện khi vùng không trùng ranh giới hành chính |

**Lưu ý ranh giới:** sau sáp nhập tỉnh 7/2025, Đà Nẵng đã hợp nhất với Quảng Nam. Kiểm tra quan hệ ranh giới trong OSM; nếu chưa cập nhật thì dùng bbox thủ công và ghi rõ trong luận văn.

---

## 2. Nguồn công khai đã kiểm chứng (30/08/2026)

### 2.1 ⭐ Cổng dữ liệu mở Đà Nẵng — nguồn quan trọng nhất

**https://opendata.danang.gov.vn** (và tên miền phụ **https://congdulieu.vn**)

- Do Sở TT&TT Đà Nẵng vận hành, hoạt động từ 10/2019
- **Đăng ký tài khoản tự phục vụ** (email, tên đăng nhập, mật khẩu, số điện thoại) hoặc đăng nhập bằng tài khoản EGOV — **không cần công văn, không cần giấy giới thiệu**
- Cung cấp dữ liệu qua nhiều kênh: web, **API**, SMS, Zalo

**Việc cần làm ngay:** đăng ký tài khoản và duyệt hết danh mục dữ liệu lĩnh vực giao thông. Đây là việc 30 phút và có thể thay đổi hoàn toàn kế hoạch thu thập dữ liệu của bạn.

### 2.2 ⭐ Danh mục dữ liệu mở — đòn bẩy pháp lý

**Số hiệu chính xác để trích dẫn (đã kiểm chứng 30/08/2026):**

> **Quyết định số 804/QĐ-UBND ngày 05/03/2026**, do Phó Chủ tịch UBND TP Đà Nẵng **Hồ Quang Bửu** ký, ban hành Danh mục dữ liệu mở thành phố Đà Nẵng.
>
> **Tổng: 14 lĩnh vực, 211 mục dữ liệu.**
> **Lĩnh vực Giao thông vận tải & logistics: 19 mục**, gồm dữ liệu mạng lưới xe buýt, dữ liệu luồng tuyến vận tải cố định, **và dữ liệu camera giám sát giao thông**.
>
> Cơ quan chủ trì: **Sở Khoa học và Công nghệ Đà Nẵng**.
> Lộ trình: trong năm 2026 các đơn vị hoàn thành tối thiểu **90%** khối lượng dữ liệu thuộc phạm vi quản lý.

*(Quyết định này thay cho bản công bố 12/5/2023 do ông Lê Trung Chinh ký. Dùng số hiệu 804/QĐ-UBND khi viết văn bản và khi trích trong luận văn.)*

⚠️ **Cẩn thận kẻo nhầm số hiệu:** 804/QĐ-**UBND** (Đà Nẵng, dữ liệu mở) khác 804/QĐ-**TTg** ngày 06/5/2026 (Thủ tướng, danh mục bộ dữ liệu phục vụ phát triển AI). Trùng số, khác cấp, cả hai đều liên quan đến đề tài.

### 2.2b ⚠️ Nằm trong danh mục KHÔNG có nghĩa là tải được hôm nay

Đã thử truy cập ngày 30/08/2026:

| Cổng | Tình trạng |
|---|---|
| opendata.danang.gov.vn | Chỉ hiện form đăng nhập/đăng ký; không xem được danh mục nếu chưa có tài khoản |
| congdulieu.vn/dich-vu-du-lieu | *"Trang bạn yêu cầu đang được cập nhật. Vui lòng thử lại sau"* |
| camera.0511.vn | Vẫn tạm đóng để nâng cấp |

**Số camera thực sự dùng được cho nghiên cứu: chưa xác nhận được, có thể là 0.** Danh mục là *cam kết sẽ cung cấp*, không phải *đã cung cấp*; mốc 90% là mục tiêu của cả năm 2026.

Khi đăng nhập được, xác định "dữ liệu camera" thuộc loại nào — giá trị chênh nhau rất xa:

| Loại | Giá trị |
|---|---|
| (a) Siêu dữ liệu: vị trí, toạ độ, hướng nhìn | **Khả năng cao nhất.** Không đếm xe được, nhưng rất tốt để chọn điểm quay và vẽ bản đồ hạ tầng |
| (b) Ảnh snapshot định kỳ | Tốt — poll được, xây dataset được |
| (c) Luồng video trực tiếp | Rất tốt |
| (d) Dữ liệu đã xử lý: số đếm, tốc độ | **Vàng** — thiết kế lại đề tài theo hướng tốt hơn |

Đặt kỳ vọng ở mức (a). Hỗ trợ trực tiếp: **0236 1022** / **info@congdulieu.vn** — gọi hỏi nhanh hơn gửi văn bản.

**Reframe quan trọng:** kể cả được cấp toàn bộ, một luận văn thạc sĩ **không dùng nổi 170 camera**. Thiết kế nghiên cứu hành lang chỉ cần 6–12 điểm đếm. Câu hỏi thật không phải *"Đà Nẵng có bao nhiêu camera"* mà là *"có 6–12 camera nào cùng một hành lang, truy cập được, góc đủ cao để đếm xe máy không"*.

**Ý nghĩa thực tiễn — điều này thay đổi tư thế của bạn:**

Trước: *"Em xin phép được truy cập camera giao thông để làm luận văn."* → xin một ân huệ, dễ bị từ chối.

Sau: *"Theo Quyết định ban hành Danh mục dữ liệu mở TP Đà Nẵng ngày 12/5/2023, dữ liệu camera giám sát giao thông thuộc danh mục dữ liệu mở lĩnh vực GTVT. Đề nghị Quý cơ quan hướng dẫn thủ tục khai thác dữ liệu này qua Cổng dữ liệu mở phục vụ nghiên cứu."* → viện dẫn văn bản của chính thành phố, đề nghị hướng dẫn thủ tục.

Văn bản thứ hai có tỷ lệ được phản hồi cao hơn hẳn, vì nó không đặt cán bộ tiếp nhận vào thế phải quyết định cho hay không cho, mà chỉ yêu cầu hướng dẫn quy trình đã có sẵn.

**Trước khi gửi:** tra cứu số hiệu quyết định chính xác trên Cổng thông tin điện tử TP Đà Nẵng (danang.gov.vn) và trích dẫn đúng số hiệu.

### 2.3 Hệ thống camera thực tế (số liệu dùng cho luận văn)

| Phạm vi | Số camera |
|---|---|
| **Đà Nẵng (ranh giới cũ)** | **Gần 170 camera tại 71 điểm/tuyến**, phủ các trục trọng yếu |
| QL1A qua Quảng Trị–Huế–Đà Nẵng | 80 camera trên 224 km — hệ thống quốc lộ do CSGT quản lý, khác hệ thống thành phố |
| Quảng Nam cũ | ⚠️ Không tìm được số liệu công khai |
| **Đà Nẵng mới (sau sáp nhập)** | ⚠️ Chưa có số liệu công bố — **một câu hỏi khảo sát của chính luận văn** |

- Trung tâm Giám sát điều hành thông minh (**IOC**) khai trương **8/2023**: IOC cấp thành phố + OC quận/phường + OC chuyên ngành (OC giao thông, OC an ninh), 15 dịch vụ đô thị thông minh
- Hệ thống có tích hợp AI: nhận dạng biển số, đo tốc độ, phát hiện vi phạm kể cả thiếu sáng

### 2.3b Bối cảnh chính sách 2026 — dùng cho chương mở đầu

Bốn văn bản cho thấy đề tài nằm đúng dòng chính sách quốc gia đang triển khai:

| Văn bản | Nội dung |
|---|---|
| **QĐ 456/QĐ-TTg ngày 20/3/2026** | Đề án Trung tâm dữ liệu, quản lý, giám sát, xử lý vi phạm và điều hành giao thông 2026–2030, tầm nhìn 2050 |
| **QĐ 502/QĐ-TTg 2026** | Kết nối, chia sẻ dữ liệu camera giám sát an ninh với CSDL quốc gia |
| **QCVN 11:2026/BCA** | Quy chuẩn kỹ thuật quốc gia về camera giám sát |
| **QĐ 804/QĐ-TTg ngày 06/5/2026** | Danh mục bộ dữ liệu phục vụ phát triển **trí tuệ nhân tạo** — củng cố lập luận cho đóng góp bộ dữ liệu |

### 2.4 Cổng camera công khai — tình trạng hiện tại

| Cổng | Tình trạng (30/08/2026) | Ghi chú |
|---|---|---|
| **camera.0511.vn** | ⚠️ **Tạm đóng công khai để nâng cấp hệ thống** | Trước đây xem được không cần đăng nhập. **Kiểm tra lại định kỳ** — có thể mở lại |
| **giaothong.hochiminhcity.gov.vn/map.aspx** | ✅ Hoạt động, công khai | Cổng camera TP.HCM; nhiều ứng dụng bên thứ ba lấy nguồn từ đây |
| **opencctv.org/cameras/vietnam** | ✅ ~1.400 camera VN | Chặn truy cập tự động (403); xem bằng trình duyệt được |
| **worldcam.eu** — Da Nang Traffic | ⚠️ Không hoạt động | Vì lấy nguồn từ camera.0511.vn |

**Chiến lược dùng camera TP.HCM:** cổng TP.HCM đang mở và ổn định. Dùng ảnh từ đó để **huấn luyện** mô hình (giao thông hỗn hợp xe máy Việt Nam nói chung), còn Đà Nẵng là **vùng case study** với dữ liệu tự quay. Đây là cách chia hợp lệ về mặt khoa học và phải nói rõ trong bài — nó thậm chí còn mạnh hơn, vì cho phép bạn kiểm tra khả năng khái quát hoá liên thành phố (xem [D](D-cong-nghe-va-huong-moi.md) — đây đang là chủ đề nóng).

**Cách lấy luồng ảnh từ một cổng camera bất kỳ:** mở trang trên trình duyệt → DevTools → tab Network → lọc `.jpg` hoặc `.m3u8` → lấy URL snapshot → poll bằng `requests` mỗi 2–5 giây. Ổn định hơn RTSP nhiều và nhẹ băng thông.

### 2.5 Dữ liệu giao thông công cộng

- **danangbus.vn** — danh sách tuyến, danh sách trạm dừng, bản đồ mạng lưới xe buýt
- Ứng dụng **DanaBus** — thông tin tuyến và trạm
- Dữ liệu mạng lưới xe buýt nằm trong Danh mục dữ liệu mở (mục 2.2) → hỏi định dạng **GTFS** khi liên hệ; nếu có GTFS thì đây là dữ liệu rất giá trị cho mô hình mạng lưới

---

## 3. Bộ dữ liệu ảnh công khai

### 3.1 Dữ liệu Việt Nam (dùng để pre-train, tiết kiệm công gán nhãn)

| Bộ | Quy mô | Nguồn |
|---|---|---|
| **Vietnamese vehicle** (Roboflow Universe) | ~1.547 ảnh, lớp car/bus/truck/motorcycle | `universe.roboflow.com/car-classification/vietnamese-vehicle` |
| **Vietnamese Vehicles Dataset** (Kaggle) | Xe phổ biến VN theo nhiều thời điểm trong ngày, TP.HCM | `kaggle.com/datasets/duongtran1909/vietnamese-vehicles-dataset` |
| **Vietnamese bike and motorbike** (Kaggle) | Phân loại xe đạp/xe máy VN | `kaggle.com/datasets/nqa112/vietnamese-bike-and-motorbike` |
| **Smart city cars detection** (Roboflow) | Giao thông VN | `universe.roboflow.com/vietnam-vehical/smart-city-cars-detection-gzxjr` |

Các bộ này **không thay thế được** dữ liệu Đà Nẵng của bạn (quy mô nhỏ, chủ yếu TP.HCM, chất lượng nhãn không đồng đều), nhưng dùng làm bước pre-train trung gian rất tốt — và làm **mốc so sánh B1** trong bảng thí nghiệm ở [GĐ3](03-giai-doan-3-thi-giac-may-tinh.md).

### 3.2 Dữ liệu quốc tế

| Dataset | Quy mô | Dùng để |
|---|---|---|
| **MIO-TCD** | ~786k ảnh camera giao thông cố định | Pre-train — đúng góc nhìn camera treo cao |
| **UA-DETRAC** | Video có nhãn bám vết | Benchmark phát hiện + tracking |
| **VisDrone** | Góc nhìn drone, mật độ dày, vật thể nhỏ | Gần với giao thông xe máy VN |
| **AI City Challenge** | Nhiều track, dữ liệu công khai | Phương pháp tham chiếu; xem [D](D-cong-nghe-va-huong-moi.md) |
| **BDD100K** | 100k video lái xe | Đa dạng điều kiện, góc nhìn từ xe |
| **Roboflow Universe** | Cộng đồng | Tìm khoá `vietnam traffic`, `motorbike` |

---

## 4. Dữ liệu đối chứng (ground truth)

### 4.1 Đếm tay
5 đoạn video 15 phút, đếm 2 lần, ghi cả độ lệch giữa 2 lần. ~8–10 giờ công. Xem [GĐ2](02-giai-doan-2-du-lieu.md) mục 3.

### 4.2 API tốc độ giao thông — bắt đầu thu từ ngày đầu tiên

| API | Hạn mức miễn phí | Lấy được gì |
|---|---|---|
| **TomTom Traffic Flow Segment Data** | ~2.500 request/ngày | Tốc độ hiện tại vs tốc độ dòng tự do trên từng đoạn |
| **HERE Traffic API** | Có free tier | Tương tự, kèm mức tắc nghẽn — nguồn thứ hai |
| **Mapbox Directions** | Free tier rộng | Thời gian hành trình có tính giao thông |

**Cảnh báo pháp lý:** tránh Google Directions API cho lưu trữ dài hạn — điều khoản của Google hạn chế cache. TomTom/HERE dễ thở hơn cho nghiên cứu; vẫn phải đọc điều khoản và ghi rõ trong luận văn.

**Uber Movement đã đóng cửa** — đừng mất thời gian tìm.

### 4.3 Xe thăm dò (floating car) — không cần xin phép ai
Tự chạy xe qua tuyến nghiên cứu với điện thoại ghi GPS. Cho ra thời gian hành trình thực đo trên hàng chục cạnh mỗi chuyến — chính là trọng số đồ thị cần dùng. Là phương pháp chuẩn trong kỹ thuật giao thông, có tài liệu để trích dẫn.

---

## 5. Dữ liệu ngữ cảnh

| Nguồn | Lấy gì | Dùng để |
|---|---|---|
| OSM POI | Trường, chợ, bệnh viện, KCN, khách sạn | Giải thích điểm phát sinh chuyến đi |
| **WorldPop** / Meta HRSL | Mật độ dân số lưới ~100m | Thay ma trận OD khi không có khảo sát hộ gia đình |
| **Open-Meteo** | Lịch sử mưa/nhiệt theo giờ, miễn phí, không cần key | Biến giải thích — Đà Nẵng mưa mùa rất mạnh |
| Lịch sự kiện | DIFF, lễ tết, khai giảng | Case study "ngày bất thường" |
| TCVN / nghiên cứu khu vực | Hệ số PCU, năng lực thông hành cho xe máy | Tham số mô hình BPR |

---

## 6. Checklist pháp lý và đạo đức

- [ ] Camera công cộng: chỉ dùng phi thương mại, phục vụ nghiên cứu; trích dẫn nguồn
- [ ] **Không lưu ảnh gốc có khuôn mặt hoặc biển số nhận dạng được** — lưu ý **Nghị định 13/2023/NĐ-CP** về bảo vệ dữ liệu cá nhân. Pipeline chỉ ghi bounding box + nhãn lớp + mốc thời gian
- [ ] Ảnh minh hoạ trong luận văn/bài báo: làm mờ biển số và khuôn mặt
- [ ] Ảnh trong bộ dữ liệu công bố: rà soát kỹ trước khi đưa lên Zenodo
- [ ] **Không dùng flycam** nếu chưa có phép bay
- [ ] Khi quay nơi công cộng: mang giấy giới thiệu, không cản trở giao thông, không hướng máy vào nhà dân
- [ ] Nếu nhờ người thân/bạn bè ghi GPS: có văn bản đồng ý, ẩn danh hoá, cắt bỏ điểm đầu/cuối gần nhà
- [ ] Đọc và tuân thủ điều khoản mọi API sử dụng
- [ ] Giấy phép bộ dữ liệu công bố: đề xuất CC BY-NC 4.0

---

## 7. Ước lượng quy mô dữ liệu (dùng cho phần biện minh "Big Data")

| Nguồn | Ước lượng |
|---|---|
| Video thô (bản đầy đủ) | 36 giờ @ 1080p ≈ 150–250 GB |
| Khung hình xử lý | 12 điểm × 25fps × 12h × 30 ngày ≈ **390 triệu khung** |
| Chuỗi thời gian đếm xe | 12 điểm × 4 hướng × 6 lớp × 5 phút × 1 năm ≈ **30 triệu bản ghi** |
| Chuỗi tốc độ TomTom | 50 đoạn × 96 điểm/ngày × 365 ngày ≈ **1,75 triệu bản ghi** |
| Tính toán định tuyến | 10.000 cặp OD × 48 lát cắt × 4 kịch bản ≈ **1,9 triệu lần tính SSSP** |
| Độ trung tâm trung gian | O(\|V\|\|E\|) trên 150k đỉnh — không khả thi trên một máy |

Hai dòng cuối là chỗ Spark thực sự cần thiết. Xem [GĐ4](04-giai-doan-4-do-thi-spark.md) mục 1.

---

## 8. Thứ tự ưu tiên thu thập (đã cập nhật)

| Ưu tiên | Nguồn | Cần xin phép? | Thời gian | Khi nào |
|---|---|---|---|---|
| **1** | **TomTom API — bắt đầu thu chuỗi thời gian** | Không | 2 giờ | **NGÀY 1, không chờ gì** |
| **2** | Đăng ký **opendata.danang.gov.vn**, duyệt danh mục GTVT | Không | 30 phút | Ngày 1 |
| **3** | Kéo đồ thị OSM, lập bảng thống kê | Không | 1 ngày | Tuần 1 |
| **4** | Tải các dataset VN công khai (Roboflow, Kaggle) | Không | 1 giờ | Tuần 1 |
| **5** | Khảo sát thực địa, chốt hành lang + 6–12 điểm | Không | 2 ngày | Tuần 1 |
| **6** | Quay thử + đo tỷ lệ sót xe máy của mô hình gốc | Không | 2 ngày | Tuần 2 |
| **7** | Tự quay video đủ bộ (khách sạn/cầu vượt) | Không | 4 ngày | **Sau cổng G0** |
| **8** | Xe thăm dò GPS trên hành lang | Không | 3 buổi | Sau G0 |
| 9 | Kiểm tra camera.0511.vn mở lại chưa | Không | 5 phút/tuần | Định kỳ |
| 10 | Văn bản đề nghị hướng dẫn khai thác dữ liệu mở (mục 2.2) | — | 4–8 tuần chờ | Tuỳ chọn |

Việc 1–6 là nội dung [Giai đoạn 0](00b-giai-doan-0-de-cuong.md) — đo đạc lấy số liệu cho đề cương. Không việc nào cần xin phép ai.

**Việc 7 trở đi chỉ làm sau khi đề cương được thông qua (cổng G0).** Đừng gán nhãn quy mô lớn trước đó — nếu hội đồng yêu cầu đổi hướng, bạn mất 5 tuần chứ không phải 5 tháng.

Việc 10 là phần thưởng thêm, không nằm trên đường găng.
