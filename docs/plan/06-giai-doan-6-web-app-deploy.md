# Giai đoạn 6 — Web app và triển khai (Tuần 21–28)

> **Mục tiêu:** Sản phẩm mà hội đồng nhìn thấy. Một URL công khai, mở được trên điện thoại, chạy dữ liệu thật.

Khung deploy đã dựng từ **Tuần 2** (GĐ1). Giai đoạn này chỉ bơm dữ liệu thật và hoàn thiện giao diện. Nếu đến T21 mà chưa có URL công khai chạy dữ liệu giả, bạn đã bỏ qua nguyên tắc số 2 và cần quay lại làm ngay.

---

## 1. Năm thao tác demo — thiết kế ngược từ buổi bảo vệ

Toàn bộ giao diện chỉ cần phục vụ đúng 5 thao tác này. Mọi tính năng khác là tuỳ chọn.

| # | Thao tác | Hội đồng thấy gì | Chứng minh phần nào |
|---|---|---|---|
| 1 | Kéo thanh trượt thời gian 0h→24h | Mạng lưới đổi màu xanh/vàng/đỏ — thành phố "thở" | Trọng số động (GĐ4) |
| 2 | Click một nút giao | Biểu đồ đếm xe theo giờ, tách 4–6 loại phương tiện | Pipeline thị giác (GĐ3) |
| 3 | **Chọn điểm đi – điểm đến** | Hai tuyến chồng nhau: ngắn nhất *theo khoảng cách* vs nhanh nhất *theo lưu lượng thực đo* | **Hai nửa đã nối vào nhau** |
| 4 | **Bấm "Chạy kịch bản"** | Bảng trước/sau: thời gian trễ giảm bao nhiêu %, hàng chờ ngắn đi bao nhiêu | **Giá trị ra quyết định (GĐ5)** |
| 5 | Mở panel video | Khung hình có bounding box, số đếm nhảy theo thời gian | Tính xác thực của dữ liệu |

**Thao tác 3 và 4 là hai thao tác ăn điểm.** Chúng chứng minh đây là một hệ thống chứ không phải hai đồ án ghép lại — và đó chính là rủi ro lớn nhất của đề tài ghép mà hội đồng sẽ dò tìm.

---

## 2. Kiến trúc tầng phục vụ

### 2.1 Nguyên tắc

**Tầng phục vụ chỉ đọc, không tính.** Không có Spark, không có GPU, không suy luận video trực tiếp. Mọi phép tính nặng đã xong ở tầng batch và được vật chất hoá thành file.

Gọi tên trong luận văn: **kiến trúc Lambda, tách tầng batch và tầng serving qua khung nhìn vật chất hoá.** Đây là mẫu kiến trúc chuẩn — trình bày nó như một quyết định thiết kế, không phải như một lời xin lỗi vì thiếu máy chủ.

### 2.2 Thành phần

```
Trình duyệt
   │  MapLibre GL  +  React  +  Recharts
   │
   ├─── danang.pmtiles  (static, HTTP range request — không cần tile server)
   │
   └─── FastAPI
            └─── DuckDB đọc trực tiếp Parquet   (đơn giản nhất, khuyến nghị)
                 hoặc PostgreSQL + PostGIS      (nếu cần truy vấn không gian phức tạp)
```

**Khuyến nghị dùng DuckDB đọc Parquet** thay vì dựng PostgreSQL: không cần server cơ sở dữ liệu, truy vấn phân tích nhanh, triển khai đơn giản, dữ liệu chỉ đọc nên không cần tính giao dịch. Với quy mô dữ liệu này (vài trăm MB), DuckDB nhanh hơn Postgres và tốn ít công vận hành hơn nhiều.

### 2.3 API tối thiểu

```
GET /api/edges?hour=8&daytype=weekday    -> trọng số, V/C, mức tắc theo cạnh
GET /api/site/{id}/counts?date=...       -> chuỗi thời gian đếm xe
GET /api/route?from=..&to=..&hour=8      -> 2 tuyến: ngắn nhất & nhanh nhất
GET /api/scenarios                        -> danh sách kịch bản
GET /api/scenario/{id}/compare            -> bảng chỉ số trước/sau
GET /api/centrality?hour=8                -> top đoạn đường trọng yếu
```

Định tuyến ở thao tác 3: với các cặp điểm đã tính sẵn thì tra bảng. Nếu muốn cho phép chọn tuỳ ý, chạy Dijkstra bằng `igraph` ngay trong API — trên 50k đỉnh chỉ mất vài chục mili-giây, hoàn toàn khả thi ở tầng serving.

---

## 3. Lựa chọn nền tảng triển khai

| Nền tảng | Chi phí | Ưu | Nhược |
|---|---|---|---|
| **Hugging Face Spaces (Docker)** | Miễn phí | Dựng nhanh nhất, URL vĩnh viễn, quen thuộc với giới học thuật | Ngủ khi không dùng, RAM giới hạn |
| **Oracle Cloud Always Free** | Miễn phí vĩnh viễn | 4 nhân ARM + 24GB RAM — mạnh nhất; chạy được cả Docker Compose | Tốn công cấu hình, cần biết Linux |
| Fly.io | Free allowance | Có volume, Docker, cấu hình được để không ngủ | Quota hẹp |
| Vercel + Supabase | Miễn phí | Frontend rất nhanh, PostGIS sẵn 500MB | Tách hai nơi, phức tạp hơn |
| Railway | ~$5/tháng | **Không ngủ** — an toàn nhất cho ngày bảo vệ | Mất phí |
| Render free | Miễn phí | Đơn giản | **Ngủ sau 15 phút, khởi động lại ~50 giây** — rủi ro cao khi demo |
| VPS Việt Nam | ~100–200k/tháng | Tên miền `.vn`, ping thấp | Tự quản trị |

**Khuyến nghị:** Hugging Face Spaces nếu ưu tiên nhanh gọn; Oracle Cloud Always Free nếu muốn một hệ thống thật sự và không ngại cấu hình. Trong tháng bảo vệ, cân nhắc bỏ ~$5 cho Railway để chắc chắn không bị ngủ.

**Tên miền:** tuỳ chọn. Một tên miền `.site`/`.tech`/`.io.vn` giá vài chục nghìn đến vài trăm nghìn/năm làm sản phẩm trông chỉn chu hơn hẳn khi đưa link vào bài báo.

---

## 4. Tối ưu hiệu năng bản đồ

Với ~120.000 cạnh, đây là chỗ dễ hỏng nhất về trải nghiệm.

- **PMTiles là bắt buộc**, không gửi GeoJSON thô. Một file duy nhất, host tĩnh, MapLibre đọc qua HTTP range request.
- Trọng số 24 khung giờ nhúng thẳng vào thuộc tính tile (24 cột số) → **đổi giờ chỉ cần đổi biểu thức tô màu phía client, không gọi API** → thanh trượt mượt tuyệt đối. Đây là mẹo quan trọng nhất cho thao tác demo số 1.
- Đơn giản hoá hình học theo mức zoom (`tippecanoe` làm sẵn)
- Ở zoom thấp chỉ hiện đường trục (`motorway`, `trunk`, `primary`)

## 5. Panel video (thao tác 5)

**Không** suy luận video trực tiếp trên server — không có GPU và không cần thiết.

Cách làm: kết xuất sẵn 3–4 clip 30–60 giây đã vẽ bounding box, vạch đếm và bộ đếm chạy, xuất MP4 nén. Nhúng vào trang. Nhẹ, luôn chạy, và trông y hệt thời gian thực.

*Tuỳ chọn nâng cao:* Hugging Face Spaces có hạn mức ZeroGPU miễn phí — có thể làm chức năng "tải video lên để đếm thử". Chỉ làm nếu còn dư thời gian; nó gây ấn tượng nhưng không thiết yếu.

---

## 6. Ba lớp dự phòng cho ngày bảo vệ

Mạng phòng bảo vệ hỏng, free tier ngủ đông, cold start 50 giây trong khi hội đồng đang nhìn — chuyện xảy ra thường xuyên.

1. **Bản local chạy song song:** `docker compose up`, mở sẵn ở một tab khác
2. **Video demo 3 phút đã quay sẵn:** nếu cả hai hỏng vẫn trình bày trọn vẹn
3. **Ping giữ ấm:** nếu dùng free tier có ngủ, đặt cron ping mỗi 10 phút trong suốt tuần bảo vệ, và mở trang trước 15 phút

Chuẩn bị cả ba. Chi phí thấp, và mất một buổi bảo vệ vì lỗi mạng là điều không sửa được.

---

## 7. Tính tái lập của repo (một sản phẩm độc lập)

Trước khi gửi bài báo, chuyển repo sang public và đảm bảo:

- `README.md`: mô tả, ảnh chụp màn hình, link demo, hướng dẫn cài đặt
- `docker compose up` chạy được trên máy sạch, một lệnh duy nhất
- `requirements.txt` ghim số hiệu phiên bản chính xác
- `experiments/` — mỗi bảng trong luận văn có một script tương ứng
- `results/` — commit các file CSV kết quả vào git
- Trích dẫn bộ dữ liệu (DOI Zenodo) và giấy phép

Đưa link repo và link demo vào bài báo. Reviewer của IAENG và các hội thảo đều đánh giá cao tính tái lập, và nó là thứ phân biệt bài của bạn với các bài chỉ có bảng số.

---

## Sản phẩm bàn giao của GĐ6

- [ ] **URL công khai chạy dữ liệu thật**, mở được trên điện thoại
- [ ] Đủ 5 thao tác demo hoạt động
- [ ] Thanh trượt thời gian mượt (đổi màu phía client, không gọi API)
- [ ] Panel video với clip đã kết xuất sẵn
- [ ] Repo public, `docker compose up` chạy trên máy sạch
- [ ] Video demo dự phòng 3 phút
- [ ] Bản local đã kiểm tra trên máy khác
- [ ] `docs/nhat-ky/06-he-thong.md` (~6 trang → chương kiến trúc hệ thống)

## Tiêu chí qua cổng G6 (T30)

Đưa link cho một người không liên quan đến đề tài, không hướng dẫn gì, và họ tự khám phá được cả 5 thao tác. Nếu họ lúng túng, vấn đề nằm ở giao diện chứ không ở người dùng.

---

## Rủi ro giai đoạn này

| Rủi ro | Xử lý |
|---|---|
| **Sa đà làm đẹp giao diện** | Đặt hạn mức cứng: 5 thao tác là đủ. Con số #1, #2, #3 mới quyết định bài báo, giao diện chỉ quyết định điểm demo |
| Free tier hết RAM khi tải PMTiles lớn | PMTiles nên đặt ở static hosting/CDN tách khỏi API; tăng mức đơn giản hoá hình học |
| Deploy hỏng vào phút chót | Đã phòng bằng nguyên tắc "deploy khung rỗng từ T2"; luôn giữ nhánh `stable` đã kiểm chứng |
| Bản đồ lag trên điện thoại | Giảm số cạnh hiển thị ở zoom thấp; kiểm tra thật trên điện thoại từ sớm, đừng chỉ thử trên máy tính |
