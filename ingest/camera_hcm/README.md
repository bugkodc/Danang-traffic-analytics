# Thu ảnh camera giao thông TP.HCM

Ảnh này dùng để **huấn luyện bộ phát hiện** (dạy mô hình "xe máy trông như
thế nào"), **không** dùng cho phần case study Đà Nẵng. Cách chia này còn tạo
ra thí nghiệm khoảng cách miền liên thành phố — xem
[docs/plan/D-cong-nghe-va-huong-moi.md](../../docs/plan/D-cong-nghe-va-huong-moi.md) mục 2.1.

## Nguồn và cách lấy danh sách camera

Cổng thông tin giao thông TP.HCM (Sở Xây dựng TP.HCM) không công bố danh sách
camera, nhưng bản đồ của cổng gọi một API nội bộ. Bắt được lời gọi đó:

```
POST /ajaxpro/VDMS.Web.Library.AJAX.FolderAjax,VDMS.Web.Library.ashx
Header: X-AjaxPro-Method: SearchQuery
Body:   {"path":"/root/vdms/tangthu/data/layerdata/camera",
         "layer":["CAMERA"], "detail":true, "page":0, "limit":-1,
         "filterQuery":["Publish:true"],
         "returnFields":["CamId","Code","Location","SnapshotUrl","CamType",
                         "Disctrict","Publish","ManagementUnit","CamStatus",
                         "PTZ","Angle"]}
```

⚠️ API này **chỉ chấp nhận lời gọi từ trong trang** (cùng nguồn gốc). Gọi từ
ngoài trả về *"Specified method is not supported"*.

Kết quả: **796 camera**, trong đó **615 đang hoạt động** (`CamStatus = UP`).
Đã lọc còn **54 camera thuộc quận nội thành** — nơi mật độ xe máy cao nhất.

## Endpoint ảnh

```
https://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx?id=<cam_id>
```

⚠️ **Máy chủ chặn request không có `User-Agent`** — trả về ReadTimeout chứ
không báo lỗi rõ ràng. Đây là lỗi rất khó đoán: `curl` chạy được vì tự gửi
header này, còn `requests` của Python thì không. Script đã tự đặt header.

## Cách dùng

**Bước 1 — Lấy mẫu để chọn camera:**

```bash
python ingest/camera_hcm/thu_anh.py --mau
```

Mỗi camera 1 ảnh, lưu vào `data/raw/anh_hcm_mau/`. Mất khoảng 70 giây.

**Bước 2 — Xem ảnh và chọn:**

| Giữ | Bỏ |
|---|---|
| Góc chếch từ trên xuống 30–45° | Góc gần ngang (xe che nhau hoàn toàn) |
| Thấy rõ mặt đường | Ảnh mờ, nhoè |
| Có dòng xe qua lại | Hướng vào lề đường, bãi đỗ |

Đánh dấu `x` vào cột `dung` trong `cameras.csv` cho camera giữ lại.

**Bước 3 — Thu định kỳ:**

```bash
python ingest/camera_hcm/thu_anh.py --lap 20 --nghi 180
```

20 vòng, cách nhau 3 phút → 1 giờ thu thập.

## Lưu ý pháp lý

Ảnh từ cổng của cơ quan nhà nước. Dùng để **huấn luyện** thì được, nhưng
**phát tán lại trong bộ dữ liệu công bố có thể không được phép**. Bộ dữ liệu
công bố lên Zenodo chỉ nên gồm phần Đà Nẵng tự quay — phần TP.HCM giữ nội bộ,
trong bài báo mô tả cách lấy để người khác tự thu lại được.
