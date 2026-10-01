// Goi cac API cua tang phuc vu (services/api/main.py)

async function lay(duongDan) {
  const res = await fetch(duongDan);
  if (!res.ok) throw new Error(`${duongDan}: HTTP ${res.status}`);
  return res.json();
}

function themThoiDiem(duongDan, thoiDiem) {
  return thoiDiem ? `${duongDan}?thoi_diem=${encodeURIComponent(thoiDiem)}` : duongDan;
}

export const api = {
  thoiDiem: () => lay('/api/thoi-diem'),
  doan: (thoiDiem) => lay(themThoiDiem('/api/doan', thoiDiem)),
  chuoiThoiGian: (id) => lay(`/api/doan/${id}/chuoi-thoi-gian`),
  theoGio: () => lay('/api/theo-gio'),
  phanLuong: () => lay('/api/phan-luong'),
  duongDi: (tu, den, kichBan) => lay(`/api/phan-luong/duong-di?tu=${tu}&den=${den}&kich_ban=${kichBan}`),
};
