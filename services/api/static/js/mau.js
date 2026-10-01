// Bang mau 4 muc tac nghen - dung chung cho ban do, danh sach va bieu do nhiet.
// Nguong giong ham muc_tac_nghen() trong main.py.

export const MAU_MUC = ['#5c6672', '#2f9e44', '#f2c94c', '#f08c00', '#e03131'];
export const TEN_MUC = ['Không có dữ liệu', 'Thông thoáng', 'Hơi đông', 'Đông', 'Tắc'];

export function mucTheoTyLe(tyLe) {
  if (tyLe == null) return 0;
  if (tyLe >= 0.85) return 1;
  if (tyLe >= 0.65) return 2;
  if (tyLe >= 0.45) return 3;
  return 4;
}

// Thang mau lien tuc cho ban do nhiet: do (tac) -> cam -> vang -> xanh (thong thoang)
const MOC = [
  [0.35, [224, 49, 49]],
  [0.55, [240, 140, 0]],
  [0.75, [242, 201, 76]],
  [0.95, [47, 158, 68]],
];

export function mauLienTuc(tyLe) {
  if (tyLe <= MOC[0][0]) return `rgb(${MOC[0][1]})`;
  for (let i = 1; i < MOC.length; i++) {
    const [x1, c1] = MOC[i];
    if (tyLe <= x1) {
      const [x0, c0] = MOC[i - 1];
      const t = (tyLe - x0) / (x1 - x0);
      return `rgb(${c0.map((v, k) => Math.round(v + (c1[k] - v) * t))})`;
    }
  }
  return `rgb(${MOC[MOC.length - 1][1]})`;
}

const dinhDangGio = new Intl.DateTimeFormat('vi-VN', {
  timeZone: 'Asia/Ho_Chi_Minh',
  hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric',
});

export function hienGio(iso) {
  return iso ? dinhDangGio.format(new Date(iso)) : '--';
}
