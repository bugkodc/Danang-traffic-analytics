"""
Cau hinh chung cho mo-dun thi giac may tinh.

Tach rieng de moi script dung cung mot dinh nghia lop xe va he so quy doi -
neu moi noi dinh nghia mot kieu thi so lieu khong so sanh duoc voi nhau.
"""

# ---------------------------------------------------------------------------
# LOP PHUONG TIEN
# ---------------------------------------------------------------------------
# YOLO huan luyen tren COCO, ten lop la tieng Anh va chi co 4 loai xe lien quan.
# COCO KHONG co lop rieng cho xe tai nhe, xe ba gac, xe khach - day chinh la
# mot phan cua khoang cach mien voi giao thong Viet Nam.
COCO_XE = {
    3: "motorcycle",
    2: "car",
    5: "bus",
    7: "truck",
    1: "bicycle",
}

# Ten tieng Viet de hien thi
TEN_VIET = {
    "motorcycle": "Xe máy",
    "car":        "Ô tô con",
    "bus":        "Xe buýt",
    "truck":      "Xe tải",
    "bicycle":    "Xe đạp",
}

# ---------------------------------------------------------------------------
# HE SO QUY DOI PCU (Passenger Car Unit)
# ---------------------------------------------------------------------------
# Doi moi loai xe ve "don vi xe con tuong duong" de tinh luu luong V.
# Ham BPR can V tinh bang PCU/gio, khong phai so xe tho.
#
# LUU Y QUAN TRONG cho luan van: he so cho xe may o dieu kien giao thong hon
# hop Viet Nam KHAC voi sach giao khoa phuong Tay. Gia tri duoi day la muc
# thuong duoc dung (0,25-0,3), nhung PHAI trich dan nguon cu the trong luan
# van - tra TCVN hoac cac nghien cuu ve giao thong xe may o VN/Dai Loan/
# Indonesia. Neu hieu chinh duoc tu du lieu TomTom cua chinh minh thi do la
# mot dong gop dang ke.
PCU = {
    "motorcycle": 0.25,
    "bicycle":    0.20,
    "car":        1.00,
    "bus":        2.50,
    "truck":      2.50,
}

# ---------------------------------------------------------------------------
# NGUONG PHAT HIEN VA BAM VET
# ---------------------------------------------------------------------------
# Nguong tin cay thap hon mac dinh (0,25) vi xe may trong dong hon hop
# thuong bi che khuat -> diem tin cay thap. Ha nguong de bot sot, doi lai
# nhieu duong tinh gia hon - buoc bam vet se loc bot.
NGUONG_TIN_CAY = 0.20
NGUONG_IOU = 0.45

# Kich thuoc anh dau vao. 960 thay vi mac dinh 640 vi xe may la VAT THE NHO:
# o goc camera cao, mot chiec xe may chi chiem vai chuc pixel. Tang kich thuoc
# giup mo hinh nhin ro hon, doi lai cham hon khoang 2 lan.
KICH_THUOC_ANH = 960

# ---------------------------------------------------------------------------
# LOGIC DEM QUA VACH
# ---------------------------------------------------------------------------
# Mot vet phai di duoc it nhat bao nhieu pixel moi tinh la da "qua vach".
# Chan xe dung dam len vach roi dao qua dao lai -> dem nhieu lan.
QUANG_DUONG_TOI_THIEU = 25

# Mot vet phai xuat hien it nhat bao nhieu khung hinh moi duoc dem.
# Loc bo cac vet chop nhoang do phat hien nham.
SO_KHUNG_TOI_THIEU = 5

# Gop so dem theo khoang thoi gian bao nhieu phut
KHOANG_GOP_PHUT = 15
