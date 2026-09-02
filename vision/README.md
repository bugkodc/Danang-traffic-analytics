# Mô-đun thị giác máy tính — đếm phương tiện

## Cơ chế hoạt động

Đây là mắt xích **tạo ra dữ liệu lưu lượng** cho toàn bộ luận văn. TomTom cho
tốc độ; mô-đun này cho **số xe và loại xe** — thứ TomTom không có và cũng là
thứ hàm BPR cần để tính trọng số cạnh đồ thị.

```
   Video (30 fps)
        │
        ▼
   ┌─────────────────┐   Mỗi khung hình: tìm xe, vẽ hộp bao,
   │ 1. PHÁT HIỆN    │   gán nhãn loại (xe máy / ô tô / xe tải…)
   │    YOLOv11      │   → ra danh sách hộp + độ tin cậy
   └────────┬────────┘
            │  hộp bao rời rạc, chưa biết hộp nào là xe nào
            ▼
   ┌─────────────────┐   Nối hộp giữa các khung hình liên tiếp,
   │ 2. BÁM VẾT      │   gán mỗi xe một ID xuyên suốt
   │    ByteTrack    │   → ra quỹ đạo từng xe
   └────────┬────────┘
            │  giờ đã biết "xe ID 47 đi từ đây tới đây"
            ▼
   ┌─────────────────┐   Kẻ một vạch ảo. Xe nào có quỹ đạo cắt vạch
   │ 3. ĐẾM QUA VẠCH │   thì đếm 1, ghi nhận hướng và loại xe
   │                 │   → ra số đếm theo loại, theo hướng
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐   Quy đổi xe máy 0,25 / ô tô 1,0 / xe tải 2,5
   │ 4. QUY ĐỔI PCU  │   → ra lưu lượng V (PCU/giờ)
   └────────┬────────┘
            │
            ▼
      counts.parquet  ──►  Giai đoạn 4: trọng số cạnh qua hàm BPR
                      ──►  Giai đoạn 5: hiệu chỉnh nhu cầu cho SUMO
```

**Vì sao phải bám vết chứ không chỉ phát hiện:** phát hiện đơn thuần cho biết
"khung hình này có 12 xe máy", nhưng khung sau cũng có 12 xe máy — không biết
là 12 xe cũ hay 12 xe mới. Bám vết gán ID cho từng xe nên mới đếm được xe đi
qua, không đếm trùng.

---

## Ba script

| Script | Việc | Cần gì |
|---|---|---|
| `thu_moi_truong.py` | Kiểm tra GPU, CUDA, thư viện | — |
| `chan_doan.py` | **Đo tỷ lệ mô hình gốc sót xe máy** | Một thư mục ảnh |
| `dem_xe.py` | Đường ống đầy đủ: phát hiện → bám vết → đếm | Một video |

### Bước đầu tiên nên làm: `chan_doan.py`

Đây là **thí nghiệm rẻ nhất cho giả thuyết đắt nhất**. Nó chạy YOLOv11 gốc
(chưa huấn luyện lại) lên ảnh giao thông Việt Nam và đo tỷ lệ sót xe máy.

Kết quả quyết định toàn bộ hướng đi:

| Tỷ lệ sót | Nghĩa là | Phải làm gì |
|---|---|---|
| < 15% | Khoảng cách miền nhỏ | Luận điểm yếu — đổi trọng tâm sang đánh giá theo điều kiện mưa/đêm/tắc |
| **15–40%** | Khoảng cách rõ rệt | **Kịch bản lý tưởng** — viết thẳng con số vào đề cương |
| > 40% | Rất lớn | Kiểm tra lại chất lượng ảnh trước khi mừng |

Chạy được **ngay hôm nay**, không cần ra hiện trường, không cần GPU mạnh.

---

## Cài đặt

```bash
pip install -r vision/requirements.txt
python vision/thu_moi_truong.py
```

## Chạy chẩn đoán

Cần một thư mục ảnh giao thông Việt Nam. Ba nguồn lấy ngay:

- **Roboflow Universe** — `car-classification/vietnamese-vehicle` (1.547 ảnh,
  **có sẵn nhãn** nên đo được khách quan, không phải đếm tay)
- **Kaggle** — `duongtran1909/vietnamese-vehicles-dataset`
- Ảnh chụp màn hình từ cổng camera giao thông TP.HCM

```bash
python vision/chan_doan.py --anh duong/dan/toi/thu/muc/anh
```

Sinh ra:
- `results/chan_doan_yolo.csv` — bảng số theo lớp xe
- `results/chan_doan/` — ảnh có hộp bao để xem mắt thường

## Chạy đường ống đếm xe

```bash
python vision/dem_xe.py --video video.mp4 --site S01 --vach 0.5
```

`--vach 0.5` là vị trí vạch đếm theo tỷ lệ chiều cao khung hình (0,5 = giữa).

Sinh ra:
- `data/processed/counts.parquet` — theo đúng hợp đồng dữ liệu ở
  `docs/plan/B-kien-truc-ky-thuat.md`
- `results/dem_xe/<site>_danhdau.mp4` — video có hộp bao, vạch đếm và bộ đếm
  chạy, để **kiểm tra bằng mắt** và để đưa vào slide bảo vệ

---

## Về phần cứng

GTX 1050 4GB đủ để:

| Việc | Được không |
|---|---|
| Suy luận (chẩn đoán, đếm xe) | ✅ Thoải mái |
| Fine-tune `yolo11n` / `yolo11s` ở 640 px | ✅ Batch 8–16 |
| Fine-tune ở 960 px | ⚠️ Batch 2–4, chậm |
| Fine-tune `yolo11m` | ❌ Thiếu VRAM |

Cho lần chạy huấn luyện cuối cùng (ảnh 960 px, mô hình lớn hơn), dùng
**Kaggle** — 30 giờ GPU miễn phí mỗi tuần, phiên 12 giờ.

---

## Lưu ý về đạo đức dữ liệu

Đường ống **chỉ ghi hộp bao, nhãn lớp và mốc thời gian**. Không lưu ảnh có
khuôn mặt hoặc biển số nhận dạng được — theo Nghị định 13/2023/NĐ-CP về bảo
vệ dữ liệu cá nhân. Video đánh dấu chỉ dùng để kiểm tra nội bộ; nếu đưa vào
luận văn hay bài báo thì phải làm mờ biển số và khuôn mặt trước.
