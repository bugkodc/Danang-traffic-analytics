# Thu thập dữ liệu tốc độ giao thông — TomTom

> **Việc quan trọng nhất phải chạy sớm nhất.** Dữ liệu tốc độ là dữ liệu quá khứ — không mua lại được. Mỗi ngày trì hoãn là một ngày mất vĩnh viễn khỏi luận văn.

Job này phục vụ **con số #3** của luận văn: chứng minh trọng số động từ số đếm thị giác cho ước lượng thời gian hành trình tốt hơn trọng số tĩnh của OSM, đối chứng bằng một nguồn độc lập. Xem [../plan/00-tong-quan.md](../plan/00-tong-quan.md).

---

## Ba bước cài đặt (~30 phút)

### Bước 1 — Lấy API key

1. Vào **developer.tomtom.com**, đăng ký tài khoản miễn phí
2. Tạo một App mới, bật sản phẩm **Traffic Flow Segment Data**
3. Sao chép API key

Hạn mức miễn phí ~2.500 request/ngày. Với 12 đoạn × 4 lần/giờ × 24 giờ = 1.152 request/ngày — nằm gọn trong hạn mức, vẫn còn dư để mở rộng lên ~20 đoạn.

### Bước 2 — Cài thư viện và chạy thử

```bash
pip install requests pandas pyarrow
```

Đặt biến môi trường rồi chạy thử một lần:

```bash
set TOMTOM_API_KEY=dan_key_cua_ban_vao_day
python collect.py
```

Nếu thành công, log hiện dòng kiểu `Ghi 12/12 doan -> 2026-08-30.parquet (tong 12 ban ghi trong ngay)` và có file trong `data/`.

### Bước 3 — Đặt lịch chạy mỗi 15 phút

Mở **Task Scheduler** (Windows) → Create Task:

| Mục | Giá trị |
|---|---|
| General | Đặt tên `TomTom Traffic Collector`; tick **Run whether user is logged on or not** |
| Triggers | New → Daily, lặp lại **mỗi 15 phút**, thời lượng **Indefinitely** |
| Actions | Program: `python`<br>Arguments: `collect.py`<br>Start in: `D:\Downloads\Thạc sĩ\BigData\tomtom` |
| Conditions | Bỏ tick *Start the task only if the computer is on AC power* |

Đặt `TOMTOM_API_KEY` ở cấp hệ thống: `System Properties → Environment Variables → System variables → New`.

---

## Kiểm tra hằng tuần (2 phút)

```bash
python -c "import pandas as pd, glob; f=sorted(glob.glob('data/*.parquet')); print(len(f),'ngay'); d=pd.read_parquet(f[-1]); print(d.groupby('segment_id').size())"
```

Nếu file của ngày hôm qua rỗng hoặc thiếu ngày → job đã chết, xem `collect.log`.

---

## Kiểm tra chất lượng điểm đo

**Mỗi khi thêm hoặc sửa điểm trong `segments.csv`, chạy lại:**

```bash
python kiem_tra_diem.py
```

Script gọi API một lần cho mỗi điểm và báo cáo phân lớp đường (FRC), tốc độ dòng tự do, **độ dài đoạn thực tế**, và **phát hiện hai điểm rơi vào cùng một đoạn**.

Ba lỗi nó bắt được — đều đã xảy ra ở bộ toạ độ mẫu ban đầu:

| Lỗi | Ví dụ thật đã gặp |
|---|---|
| **Hai điểm cùng một đoạn** | Võ Nguyên Giáp và Phạm Văn Đồng cách nhau 1,7 km nhưng cùng trả về một đoạn dài 14,6 km → lãng phí một slot |
| **Đoạn quá dài (>3 km)** | Nguyễn Văn Linh trả về đoạn 12,4 km → giá trị trung bình bị pha loãng, không phản ánh tắc cục bộ |
| **Đoạn quá ngắn / đường nhỏ** | Lê Duẩn rơi vào một đoạn 207 m có tốc độ tự do 12 km/h → là ngõ nhỏ, không phải trục chính |

Bộ toạ độ hiện tại trong `segments.csv` **đã dò và kiểm chứng, đạt 12/12**, độ dài đoạn từ 351 m đến 2.742 m.

Nguyên tắc khi chọn điểm mới:

- Đặt ở **giữa đoạn**, tránh đúng nút giao — API trả dữ liệu của đoạn chứa điểm đó
- Nhắm đoạn dài **300 m – 3 km**; dài hơn thì giá trị bị pha loãng
- FRC3–FRC4 là mức bình thường của trục đô thị Việt Nam trong dữ liệu TomTom
- Ưu tiên các đoạn trên **hành lang nghiên cứu** sẽ chốt ở Tuần 1
- Giữ vài đoạn "đối chứng" ngoài hành lang
- Tăng lên ~20 đoạn vẫn trong hạn mức miễn phí

**Chưa chốt hành lang cũng cứ để job chạy với 12 điểm hiện tại.** Thêm hoặc đổi điểm sau lúc nào cũng được; dữ liệu của những ngày đã trôi qua thì không.

---

## Dữ liệu thu được

Mỗi bản ghi một đoạn một thời điểm:

| Cột | Ý nghĩa |
|---|---|
| `ts_local`, `ts_utc` | Thời điểm đo (giờ VN và UTC) |
| `segment_id`, `ten`, `lat`, `lon` | Định danh đoạn |
| `frc` | Phân lớp chức năng đường của TomTom |
| `current_speed` | Tốc độ hiện tại (km/h) |
| `freeflow_speed` | **Tốc độ dòng tự do — dùng để bổ khuyết `maxspeed` thiếu trong OSM** |
| `current_travel_time`, `freeflow_travel_time` | Thời gian đi qua đoạn (giây) |
| `speed_ratio` | `current/freeflow` — càng nhỏ càng tắc |
| `confidence` | Độ tin cậy của TomTom |

Ba công dụng trong luận văn:

1. **Bổ khuyết thuộc tính OSM** — `freeflow_speed` thực đo thay cho giá trị mặc định, cho ra một bảng tốc độ dòng tự do riêng cho Đà Nẵng (GĐ4 mục 2.2)
2. **Hiệu chỉnh hàm BPR** — hồi quy quan hệ giữa lưu lượng quan sát và tốc độ quan sát
3. **Kiểm chứng chéo độc lập** — nguồn *không* tham gia hiệu chỉnh, dùng để kiểm chứng mô phỏng SUMO (GĐ5 mục 2.3). Đây là kiểm chứng mạnh nhất của toàn bộ luận văn.

---

## Sao lưu

Thư mục `data/` là tài sản không tái tạo được. Sao chép lên Google Drive/OneDrive **mỗi tuần**. Mất nó là mất vĩnh viễn.
