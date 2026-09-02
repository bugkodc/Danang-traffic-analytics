# Thí nghiệm chẩn đoán — khoảng cách miền của mô hình gốc

*Chạy ngày 02/09/2026 · `vision/chan_doan.py`*

## Thiết lập

| Mục | Giá trị |
|---|---|
| Bộ dữ liệu | `visaitech/vehicle-mixed-traffic-detection` (HuggingFace, CC-BY-4.0) |
| Nội dung | Ảnh dashcam giao thông hỗn hợp Nam Á, có nhãn |
| Số ảnh | 120 (tập train) |
| Mô hình | YOLOv11n và YOLOv11s, **trọng số COCO gốc, chưa fine-tune** |
| Ngưỡng tin cậy | 0,20 |
| Kích thước ảnh | 960 px |
| Ngưỡng khớp hộp | IoU > 0,4 |

## Kết quả

| Loại đối tượng | Nhãn thật | YOLOv11n sót | YOLOv11s sót |
|---|---|---|---|
| **2 bánh** (xe máy / xe đạp) | 444 | **82,9%** | **75,7%** |
| 3 bánh (xe ba gác, lam) | 126 | 73,0% | 66,7% |
| **4 bánh** (ô tô, xe tải) | 122 | **39,3%** | **13,1%** |
| Người đi bộ | 20 | 100%* | 100%* |

*\* Không tính: script lọc YOLO chỉ lấy các lớp phương tiện nên người đi bộ tất
nhiên bị bỏ qua hết. Đây là tạo tác của thiết lập, không phải phát hiện.*

## Phát hiện chính — không phải con số tuyệt đối

Con số 76–83% tự nó dễ gây nghi ngờ: có thể do ảnh mờ, vật thể quá xa, hoặc mô
hình yếu. **Nhưng phép so sánh trong cùng một tập ảnh, cùng một mô hình đã loại
bỏ mọi yếu tố gây nhiễu đó:**

```
YOLOv11s trên CÙNG 120 ảnh:
    4 bánh  sót  13,1%   ← mô hình nhận diện ô tô rất tốt
    2 bánh  sót  75,7%   ← nhưng hỏng hẳn với xe 2 bánh

    Chênh lệch: 5,8 lần
```

Nâng mô hình từ `n` lên `s` cải thiện **4 bánh rất nhiều** (39,3% → 13,1%, giảm
gần 3 lần) nhưng **2 bánh gần như không đổi** (82,9% → 75,7%).

Điều đó cho thấy vấn đề **không phải do mô hình yếu hay ảnh xấu** — nếu vậy thì
mọi lớp đều cải thiện như nhau. Vấn đề nằm ở chỗ **COCO không dạy mô hình nhận
xe 2 bánh trong dòng giao thông hỗn hợp dày đặc**: xe máy che nhau, đi sát nhau,
không theo làn — những tình huống gần như không có trong dữ liệu phương Tây.

## Ý nghĩa cho luận văn

Đây là **bằng chứng thực nghiệm đầu tiên** cho giả thuyết trung tâm. Nó nên vào
phần Lý do chọn đề tài và phần Mở đầu của bài báo.

Cách phát biểu nên dùng — nhấn vào **chênh lệch giữa các lớp**, không phải con
số tuyệt đối, vì chênh lệch mới là thứ đã kiểm soát được nhiễu:

> Trên cùng một tập ảnh giao thông hỗn hợp, YOLOv11s đạt tỷ lệ sót 13,1% với
> phương tiện 4 bánh nhưng 75,7% với phương tiện 2 bánh — chênh lệch 5,8 lần.
> Việc tăng dung lượng mô hình cải thiện rõ rệt nhóm 4 bánh (giảm 3 lần tỷ lệ
> sót) nhưng gần như không tác động tới nhóm 2 bánh, cho thấy hạn chế nằm ở
> phân bố dữ liệu huấn luyện chứ không ở năng lực mô hình.

## Hạn chế cần ghi rõ

- Bộ dữ liệu là ảnh **dashcam Nam Á**, không phải camera treo cao ở Việt Nam.
  Con số sẽ khác khi đo trên dữ liệu Đà Nẵng tự quay.
- Bộ này gộp xe máy và xe đạp thành một lớp "2-wheeler", trong khi COCO tách
  riêng. Đã ánh xạ khi so khớp, nhưng vẫn là một nguồn sai lệch nhỏ.
- Mới thử `yolo11n` và `yolo11s`. Cần bổ sung `yolo11m` và **RF-DETR** để hoàn
  thiện bảng so sánh — xem `docs/plan/D-cong-nghe-va-huong-moi.md` mục 1.
- Chạy trên CPU nên chưa thử được kích thước ảnh lớn hơn 960 px.

## Bước tiếp theo

1. Bổ sung `yolo11m` và RF-DETR vào bảng so sánh
2. Đo lại trên **ảnh camera treo cao** (54 ảnh TP.HCM đã thu) sau khi gán nhãn
3. Đo lại lần cuối trên **video Đà Nẵng tự quay** — đây mới là con số vào luận văn
