# Kế hoạch triển khai luận văn & bài báo

**Đề tài:** Xây dựng hệ thống phân tích và phân luồng giao thông đô thị Đà Nẵng trên nền dữ liệu lớn — kết hợp đồ thị OpenStreetMap và đếm phương tiện bằng thị giác máy tính

**Ngành:** Hệ thống thông tin (Thạc sĩ)
**Ngày lập kế hoạch:** 30/08/2026

---

## Cách dùng bộ tài liệu này

Đọc theo thứ tự lần đầu. Sau đó mỗi tuần chỉ mở đúng file của giai đoạn đang làm, và đối chiếu mục **"Tiêu chí hoàn thành"** trước khi cho phép mình chuyển giai đoạn.

| File | Nội dung | Khi nào đọc |
|---|---|---|
| [00-tong-quan.md](00-tong-quan.md) | Bức tranh tổng thể, dòng thời gian 53 tuần, 4 con số, 6 nguyên tắc | Đọc đầu tiên, đọc lại mỗi tháng |
| **[00b-giai-doan-0-de-cuong.md](00b-giai-doan-0-de-cuong.md)** | **T1–T5 · Đo đạc lấy số liệu → viết đề cương → cổng G0** | **BẮT ĐẦU TỪ ĐÂY** |
| [01-giai-doan-1-nen-mong.md](01-giai-doan-1-nen-mong.md) | T6–T9 · Hạ tầng, repo, deploy rỗng | Sau cổng G0 |
| [02-giai-doan-2-du-lieu.md](02-giai-doan-2-du-lieu.md) | T8–T17 · Quay video, gán nhãn, xây dataset | Sau G0, song song GĐ1 |
| [03-giai-doan-3-thi-giac-may-tinh.md](03-giai-doan-3-thi-giac-may-tinh.md) | T14–T21 · RF-DETR fine-tune, bám vết, đếm xe | Sau khi có ≥1000 ảnh |
| [04-giai-doan-4-do-thi-spark.md](04-giai-doan-4-do-thi-spark.md) | T18–T25 · OSM, Spark, định tuyến, độ trung tâm | Song song GĐ3 |
| [05-giai-doan-5-mo-phong-sumo.md](05-giai-doan-5-mo-phong-sumo.md) | T24–T29 · Hiệu chỉnh SUMO, kịch bản phân luồng | Sau khi có số đếm tin cậy |
| [06-giai-doan-6-web-app-deploy.md](06-giai-doan-6-web-app-deploy.md) | T26–T33 · Frontend, API, triển khai công khai | Khung deploy làm từ T7 |
| [07-giai-doan-7-bai-bao-1.md](07-giai-doan-7-bai-bao-1.md) | T22–T31 · Bài báo thị giác máy tính | Sau GĐ3 |
| [08-giai-doan-8-bai-bao-2.md](08-giai-doan-8-bai-bao-2.md) | T30–T39 · Bài báo dữ liệu lớn / đồ thị | Sau GĐ4+5 |
| [09-giai-doan-9-luan-van-bao-ve.md](09-giai-doan-9-luan-van-bao-ve.md) | T34–T53 · Viết quyển, phản biện, bảo vệ | Viết dần từ T13 |
| [A-nguon-du-lieu.md](A-nguon-du-lieu.md) | Nguồn dữ liệu đã kiểm chứng, API, checklist pháp lý | **Đọc ngay** |
| [B-kien-truc-ky-thuat.md](B-kien-truc-ky-thuat.md) | Cây thư mục repo, hợp đồng dữ liệu, docker-compose | Tra cứu |
| [C-quan-ly-rui-ro.md](C-quan-ly-rui-ro.md) | Sổ rủi ro + phương án dự phòng từng mục | Rà lại mỗi tháng |
| [D-cong-nghe-va-huong-moi.md](D-cong-nghe-va-huong-moi.md) | Mô hình 2026 (RF-DETR/YOLO26), hướng nghiên cứu nóng, bảng quyết định nâng cấp | **Đọc trước khi chốt mô hình** |

---

## Ba việc làm ngay hôm nay

1. **Chạy job thu dữ liệu TomTom** — 2 giờ. Đây là việc duy nhất thực sự khẩn: dữ liệu tốc độ là dữ liệu quá khứ, mỗi ngày trì hoãn là một ngày mất vĩnh viễn.
2. **Đăng ký opendata.danang.gov.vn** — 30 phút, không cần công văn. Xem checklist ở [00b](00b-giai-doan-0-de-cuong.md) mục 0.2.
3. **Tạo repo** theo [B](B-kien-truc-ky-thuat.md).

Ba việc này không phụ thuộc vào việc đề cương đã viết hay chưa.

---

## Giả định cần xác nhận

Kế hoạch này giả định:

1. **Thời gian:** bắt đầu 09/2026, bảo vệ khoảng 09–10/2027 (~53 tuần, đã gồm 5 tuần viết đề cương). Nếu mốc thật khác, giữ nguyên thứ tự giai đoạn và co giãn tỉ lệ.
2. **Phần cứng:** có máy GPU (hoặc dùng Colab/Kaggle miễn phí) cho khâu huấn luyện; máy cá nhân ≥16GB RAM cho Spark giả lập cụm.
3. **Nhân lực:** một người làm chính. Nếu có người phụ gán nhãn, GĐ2 rút ngắn được ~3 tuần.
4. **Venue:** IAENG *Engineering Letters* / *IJCS* (nhận bài quanh năm) là đích chính; FAIR là đích phụ tùy lịch hội thảo.

Nếu bất kỳ giả định nào sai, sửa [00-tong-quan.md](00-tong-quan.md) trước rồi mới sửa các file giai đoạn.

---

## Nguyên tắc số một

> **Luôn có một bản chạy được từ đầu đến cuối.**

Từ tuần thứ 4, trong repo phải luôn tồn tại một đường ống hoàn chỉnh: video → đếm → đồ thị → bản đồ. Ban đầu nó chạy trên 1 video và 100 cạnh đường với kết quả xấu — không sao. Việc còn lại của cả kỳ chỉ là làm sâu từng mắt xích, chứ không phải nối chúng lần đầu vào tháng cuối.

Học viên trượt tiến độ gần như luôn vì lý do ngược lại: dành 3 tháng tinh chỉnh mAP rồi không kịp nối vào phần đồ thị, và bảo vệ với một mô hình chứ không phải một hệ thống.
