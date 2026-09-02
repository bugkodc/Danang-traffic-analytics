# Chạy thu thập dữ liệu 24/24 mà không cần server

> Giải pháp: **GitHub Actions**. Job chạy trên hạ tầng GitHub, máy của bạn tắt vẫn thu dữ liệu bình thường. Chi phí: 0 đồng.

---

## Vì sao chọn GitHub Actions

| Tiêu chí | GitHub Actions | Oracle Cloud Free | Máy cá nhân |
|---|---|---|---|
| Chi phí | Miễn phí (repo công khai: **không giới hạn phút chạy**) | Miễn phí vĩnh viễn | Tiền điện + tiếng ồn |
| Cần bật máy | Không | Không | **Có** |
| Công cài đặt | ~20 phút | ~2 giờ (dựng VM, cron, firewall) | ~10 phút |
| Lưu trữ dữ liệu | Commit thẳng vào repo — **tự có bản sao lưu và lịch sử phiên bản** | Phải tự sao lưu | Phải tự sao lưu |
| Rủi ro mất dữ liệu | Rất thấp | Trung bình (Oracle có thể thu hồi tài nguyên nhàn rỗi) | Cao (ổ hỏng, quên bật) |

GitHub Actions thắng ở đúng điểm quan trọng nhất với bạn: **dữ liệu được commit vào git nên tự động có sao lưu và lịch sử**, không cần nhớ sao lưu thủ công hằng tuần.

---

## Cài đặt — 4 bước, khoảng 20 phút

### Bước 1 — Tạo API key MỚI

Key cũ đã lộ trong lịch sử chat. Vào **developer.tomtom.com** → xoá key cũ → tạo key mới.

### Bước 2 — Đẩy repo lên GitHub

```bash
cd "D:\Downloads\Thạc sĩ\BigData"
git init
git add .
git commit -m "khoi tao"
```

Tạo repo trên GitHub rồi:

```bash
git remote add origin https://github.com/<tai-khoan>/<ten-repo>.git
git branch -M main
git push -u origin main
```

**Nên để repo ở chế độ công khai (public):** repo công khai được **không giới hạn phút chạy Actions**, repo riêng tư chỉ có 2.000 phút/tháng — không đủ cho lịch chạy này. Dữ liệu tốc độ giao thông không nhạy cảm nên công khai không sao. API key vẫn được mã hoá trong Secrets, không lộ.

⚠️ Trước khi push, kiểm tra **không có file nào chứa API key**. Tạo `.gitignore` với ít nhất:

```
.env
*.key
__pycache__/
```

### Bước 3 — Nạp API key vào Secrets

Trên GitHub: **Settings → Secrets and variables → Actions → New repository secret**

- Name: `TOMTOM_API_KEY`
- Secret: dán key mới vào

Secret được mã hoá, không hiện trong log, người xem repo công khai không đọc được.

### Bước 4 — Bật và chạy thử

Vào tab **Actions** → chọn workflow *Thu thap du lieu TomTom* → bấm **Run workflow** để chạy tay một lần.

Nếu thành công, bạn sẽ thấy một commit mới kiểu `du lieu tomtom 2026-08-30 11:22 UTC` và file trong `tomtom/data/`.

Sau đó lịch tự động sẽ chạy. Kéo dữ liệu về máy bất cứ lúc nào bằng `git pull`.

---

## Lịch lấy mẫu — thiết kế và lý do

```
Cao điểm  VN 05:00–09:00 và 16:00–20:00  →  10 phút/lần
Còn lại                                   →  20 phút/lần
```

Tổng ~96 lần/ngày × 12 đoạn = **~1.152 request/ngày**, nằm trong hạn mức miễn phí 2.500/ngày, còn dư để mở rộng lên ~20 đoạn.

**Ba lý do thiết kế:**

1. **Dày hơn ở cao điểm** — đó là khoảng thời gian có biến động lớn nhất và cũng là khoảng bạn cần độ chính xác nhất cho kịch bản phân luồng. Ban đêm giao thông ổn định, lấy thưa không mất thông tin.

2. **Phút lẻ (3, 13, 23… và 7, 27, 47)** thay vì đầu giờ tròn. Hai tác dụng: tránh lúc GitHub Actions đông nghẹt nhất nên ít bị trễ, và **tạo độ lệch tự nhiên chống sai lệch hệ thống** do lấy mẫu trùng chu kỳ.

3. **Chấp nhận trễ.** GitHub có thể hoãn workflow theo lịch vài phút khi tải cao. Với mục đích dựng hồ sơ thống kê, độ trễ vài phút **không gây hại — thậm chí có lợi**, vì nó làm mẫu phân tán ngẫu nhiên hơn.

---

## Về câu hỏi "15 phút có đại diện được không"

Câu trả lời ngắn: **có**, vì ba lý do.

**1. TomTom không trả về ảnh chụp tức thời.** `currentSpeed` đã là giá trị tổng hợp từ nhiều xe thăm dò trong một cửa sổ thời gian gần đó, không phải tốc độ một chiếc xe tại đúng giây gọi API.

**2. Mục tiêu là hồ sơ thống kê, không phải phát hiện sự cố.** Bạn cần biết *"thứ Hai 17h30 đoạn này thường chạy bao nhiêu km/h"*, chứ không cần bắt từng vụ tắc. Sau 6 tháng, mỗi khung 15 phút của tuần có khoảng **26 mẫu độc lập** — thừa để ước lượng trung bình và độ biến động. Biến động ngẫu nhiên giữa hai lần gọi tự triệt tiêu qua số lần lặp.

**3. Các thang thời gian quan trọng đều dài hơn chu kỳ lấy mẫu:**

| Hiện tượng | Chu kỳ | Bắt được? |
|---|---|---|
| Chu kỳ đèn tín hiệu | 60–120 giây | Không — và không cần, trọng số cạnh là giá trị tổng hợp |
| Tắc do sự cố | 10–30 phút | Bắt được một phần |
| Đợt cao điểm | 1,5–2,5 giờ | **Bắt tốt — đây là thứ cần** |
| Chênh lệch ngày thường / cuối tuần | ngày | Bắt tốt |

**Và quan trọng nhất: TomTom không phải nguồn đo chính.** Nguồn chính là video tự quay có đếm tay đối chứng. TomTom giữ ba vai phụ, cả ba đều không đòi độ phân giải cao:

1. Bổ khuyết `maxspeed` thiếu trong OSM bằng tốc độ dòng tự do thực đo
2. Dựng hồ sơ tốc độ theo giờ để hiệu chỉnh hàm BPR
3. **Kiểm chứng chéo độc lập** cho mô phỏng SUMO — nguồn không tham gia hiệu chỉnh

Nếu sau này cần độ phân giải cao hơn cho một đoạn cụ thể, giảm số đoạn xuống và tăng tần suất lên 5 phút/lần cho riêng đoạn đó (đây cũng là giới hạn nhỏ nhất của cron trên GitHub Actions).

---

## Theo dõi

- Tab **Actions** trên GitHub hiện lịch sử mọi lần chạy; lần nào lỗi sẽ có dấu đỏ
- GitHub tự gửi email khi workflow thất bại
- Kiểm tra dữ liệu: `git pull` rồi chạy lệnh kiểm tra trong [README.md](README.md)

⚠️ **GitHub tự tắt workflow theo lịch nếu repo không có hoạt động nào trong 60 ngày.** Ở đây job commit dữ liệu liên tục nên điều kiện này luôn được thoả — không cần lo.

---

## Phương án dự phòng

| Nếu | Thì |
|---|---|
| Muốn toàn quyền kiểm soát, chạy thêm việc nặng | **Oracle Cloud Always Free** — 4 nhân ARM, 24GB RAM, miễn phí vĩnh viễn, chạy cron như máy chủ thật |
| Có Raspberry Pi ở nhà | Cắm điện, cài cron, tốn ~5W. Nhưng phụ thuộc điện và mạng nhà |
| Chỉ cần tạm thời | Để máy cá nhân bật với Task Scheduler — chấp nhận mất dữ liệu những lúc máy tắt |

Không nên dùng Google Colab (không chạy nền được) hay PythonAnywhere bản miễn phí (chỉ cho 1 tác vụ theo lịch mỗi ngày).
