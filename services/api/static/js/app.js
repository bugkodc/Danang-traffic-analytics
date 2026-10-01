// Dieu phoi giao dien: tab, thanh thoi gian, danh sach diem do, chi tiet.
import { api } from './api.js';
import { MAU_MUC, TEN_MUC, hienGio } from './mau.js';
import { taoBanDo, hienLop, veDiemDo, danhDauDiemChon, bayToi, veTuyen, hienPhanLuong } from './ban-do.js';
import { veLichSu, veNhiet } from './bieu-do.js';

const $ = (id) => document.getElementById(id);

// so theo kieu Viet Nam: 12,5 / 1.200
const so = (v, chuSoThapPhan = 2) => Number(v).toLocaleString('vi-VN', { maximumFractionDigits: chuSoThapPhan });

const trangThai = {
  thoiDiem: [],        // cac lan do, tu cu den moi
  viTri: 0,            // chi so lan do dang xem
  doan: [],            // trang thai cac diem do tai lan do dang xem
  dangChon: null,      // segment_id dang mo chi tiet
  tab: 'hien-trang',
  daVeNhiet: false,
  phanLuong: null,     // ket qua gan luong (tai mot lan)
  kichBan: 'hien-trang',
};

// ---------- tab ----------

function chuyenTab(tab) {
  trangThai.tab = tab;
  document.querySelectorAll('.tab button').forEach((b) => b.classList.toggle('dang-chon', b.dataset.tab === tab));
  document.querySelectorAll('.noi-dung-tab').forEach((s) => s.classList.toggle('an', s.id !== `tab-${tab}`));

  if (tab === 'theo-gio' && !trangThai.daVeNhiet) taiNhiet();
  if (tab === 'phan-luong') {
    moPhanLuong();
  } else {
    veTuyen(null, null);
    hienPhanLuong(null);
  }
}

// ---------- tab Hien trang ----------

function capNhatChiSo(ds) {
  const coToc = ds.filter((d) => d.current_speed != null);
  const tb = (mang) => mang.reduce((a, b) => a + b, 0) / mang.length;

  $('cs-so-diem').textContent = ds.length;
  $('cs-toc-do').textContent = coToc.length ? tb(coToc.map((d) => d.current_speed)).toFixed(1) : '--';
  $('cs-dong').textContent = ds.filter((d) => d.muc_tac >= 3).length;
  const coTyLe = ds.filter((d) => d.speed_ratio != null);
  $('cs-ty-le').textContent = coTyLe.length ? tb(coTyLe.map((d) => d.speed_ratio)).toFixed(2) : '--';
}

function veDanhSach(ds) {
  const ul = $('ds-diem');
  ul.replaceChildren();
  // diem tac nhat len dau de nguoi quan ly thay ngay
  const sapXep = [...ds].sort((a, b) => (a.speed_ratio ?? 2) - (b.speed_ratio ?? 2));
  for (const d of sapXep) {
    const li = document.createElement('li');
    li.dataset.id = d.segment_id;
    li.classList.toggle('dang-chon', d.segment_id === trangThai.dangChon);
    li.innerHTML = `
      <span class="cham" style="--mau:${MAU_MUC[d.muc_tac]}"></span>
      <span><span class="ten"></span> <span class="ma">${d.segment_id}</span></span>
      <span class="toc-do so">${d.current_speed ?? '--'} km/h<small>${TEN_MUC[d.muc_tac]}</small></span>`;
    li.querySelector('.ten').textContent = d.ten;
    li.addEventListener('click', () => chonDiem(d.segment_id));
    ul.append(li);
  }
}

async function chonDiem(id) {
  if (trangThai.tab !== 'hien-trang') chuyenTab('hien-trang');
  trangThai.dangChon = id;
  danhDauDiemChon(id);
  document.querySelectorAll('#ds-diem li').forEach((li) => li.classList.toggle('dang-chon', li.dataset.id === id));

  const d = trangThai.doan.find((x) => x.segment_id === id);
  if (d) bayToi(d.lon, d.lat);

  $('chi-tiet').classList.remove('an');
  $('ct-ten').textContent = d ? d.ten : id;
  $('ct-mo-ta').textContent = d && d.current_speed != null
    ? `${d.current_speed} km/h ở lần đo đang xem, so với ${d.freeflow_speed} km/h khi đường thông thoáng.`
    : '';
  $('ct-canh-bao').textContent = d?.canh_bao ? `Cần kiểm tra: ${d.canh_bao}` : '';
  $('ct-canh-bao').classList.toggle('an', !d?.canh_bao);
  $('ct-bieu-do').textContent = 'Đang tải…';
  try {
    const ls = await api.chuoiThoiGian(id);
    if (trangThai.dangChon === id) veLichSu($('ct-bieu-do'), ls.diem);
  } catch (e) {
    $('ct-bieu-do').textContent = 'Không tải được lịch sử đo.';
    console.error(e);
  }
}

function boChon() {
  trangThai.dangChon = null;
  danhDauDiemChon(null);
  $('chi-tiet').classList.add('an');
  document.querySelectorAll('#ds-diem li').forEach((li) => li.classList.remove('dang-chon'));
}

// ---------- tab Theo gio ----------

async function taiNhiet() {
  $('nhiet').textContent = 'Đang tải…';
  try {
    veNhiet($('nhiet'), await api.theoGio(), chonDiem);
    trangThai.daVeNhiet = true;
  } catch (e) {
    $('nhiet').textContent = 'Không tải được dữ liệu theo giờ.';
    console.error(e);
  }
}

// ---------- tab Phan luong ----------

async function moPhanLuong() {
  if (!trangThai.phanLuong) {
    try {
      trangThai.phanLuong = await api.phanLuong();
    } catch (e) {
      $('pl-gia-dinh').textContent = 'Chưa có kết quả phân luồng. Chạy: python graph/chay_phan_luong.py';
      console.error(e);
      return;
    }
    dungPhanLuong(trangThai.phanLuong);
  }
  chonKichBan(trangThai.kichBan);
}

function dungPhanLuong(pl) {
  $('pl-gia-dinh').textContent = `Nhu cầu đi lại đang là giả định (${pl.nhu_cau.tong_xe_gio.toLocaleString('vi-VN')} xe/giờ `
    + 'giữa 12 vùng) vì chưa có số đếm phương tiện. Kết quả minh hoạ thuật toán, chưa phản ánh thực tế.';

  for (const id of ['pl-tu', 'pl-den']) {
    $(id).innerHTML = pl.vung.map((v) => `<option value="${v.ma}">${v.ten}</option>`).join('');
    $(id).addEventListener('change', timDuong);
  }
  [$('pl-tu').value, $('pl-den').value] = pl.cap_goi_y || ['S11', 'S08'];

  const ds = [{ ma: 'hien-trang', ten: 'Hiện trạng', mo_ta: 'Lưu lượng sau khi gán luồng cân bằng, tô màu theo lưu lượng / năng lực.' },
    ...pl.kich_ban];
  $('pl-kich-ban').replaceChildren(...ds.map((k) => {
    const nut = document.createElement('button');
    nut.dataset.ma = k.ma;
    const doi = k.thay_doi_phan_tram;
    const nhan = doi == null
      ? `<span class="so">${pl.hien_trang.tong_thoi_gian.toLocaleString('vi-VN')} xe·giờ</span>`
      : `<span class="so ${doi > 0 ? 'tang' : 'giam'}">${doi > 0 ? '+' : ''}${so(doi)}%</span>`;
    nut.innerHTML = `<span class="dong-dau"><span></span>${nhan}</span><span class="mo-ta"></span>`;
    nut.querySelector('.dong-dau span').textContent = k.ten;
    nut.querySelector('.mo-ta').textContent = k.mo_ta;
    nut.addEventListener('click', () => chonKichBan(k.ma));
    return nut;
  }));

  $('pl-trong-yeu').innerHTML = pl.hien_trang.diem_trong_yeu
    .map((d) => `<li>${d.ten.replace(/</g, '')}<span class="so">V/C ${d.v_c.toFixed(2)}</span></li>`).join('');
  $('pl-thong-tin').textContent = `Frank–Wolfe hội tụ sau ${pl.hien_trang.so_vong} vòng `
    + `(khoảng cách tương đối ${pl.hien_trang.khoang_cach_cuoi.toExponential(1)}) trên mạng lưới `
    + `${pl.mang_luoi.so_nut.toLocaleString('vi-VN')} nút, ${pl.mang_luoi.so_canh.toLocaleString('vi-VN')} cạnh.`;
}

function chonKichBan(ma) {
  trangThai.kichBan = ma;
  document.querySelectorAll('#pl-kich-ban button').forEach((b) => b.classList.toggle('dang-chon', b.dataset.ma === ma));
  const kb = trangThai.phanLuong.kich_ban.find((k) => k.ma === ma);
  hienPhanLuong(ma, kb ? kb.canh_tac_dong : []);
  $('pl-chu-giai').innerHTML = ma === 'hien-trang'
    ? `<span style="--mau:${MAU_MUC[1]}">V/C thấp</span><span style="--mau:${MAU_MUC[2]}">0,7</span>`
      + `<span style="--mau:${MAU_MUC[3]}">0,9</span><span style="--mau:${MAU_MUC[4]}">quá tải</span>`
    : '<span style="--mau:#ff6b6b">Lưu lượng tăng</span><span style="--mau:#4dabf7">Lưu lượng giảm</span>'
      + '<span style="--mau:#f8f9fa">Đoạn bị đóng / hạn chế</span>';
  if (trangThai.tab === 'phan-luong') timDuong();
}

async function timDuong() {
  const tu = $('pl-tu').value, den = $('pl-den').value;
  const khung = $('pl-duong');
  if (tu === den) {
    khung.textContent = 'Chọn hai điểm khác nhau.';
    veTuyen(null, null);
    return;
  }
  try {
    const d = await api.duongDi(tu, den, trangThai.kichBan);
    const the = (tieuDe, x, mau, dut) => `
      <div class="tuyen">
        <div class="dong-dau"><span><i class="ky-hieu${dut ? ' dut' : ''}" style="--mau:${mau}"></i>${tieuDe}</span>
          <span class="so">${x.thoi_gian_phut == null ? 'không đi được' : `${so(x.thoi_gian_phut)} phút`}</span></div>
        <div class="phu so">${so(x.dai_km)} km${x.qua_doan_dong ? ' · đi qua đoạn đang bị đóng' : ''}</div>
      </div>`;

    let ketLuan;
    if (d.ban_do.qua_doan_dong) {
      ketLuan = `Đường theo bản đồ đi qua đoạn đang đóng. Hệ thống phân luồng sang tuyến khác dài `
        + `${so(d.phan_luong.dai_km)} km, mất ${so(d.phan_luong.thoi_gian_phut)} phút.`;
    } else if (d.trung_nhau) {
      ketLuan = 'Đường theo bản đồ cũng là đường tốt nhất trong kịch bản này.';
    } else {
      ketLuan = `Tuyến phân luồng nhanh hơn ${so(d.ban_do.thoi_gian_phut - d.phan_luong.thoi_gian_phut, 1)} phút.`;
    }
    khung.innerHTML = the('Theo bản đồ', d.ban_do, '#c9ced6', true)
      + the('Theo phân luồng', d.phan_luong, MAU_MUC[1], false)
      + `<p class="ghi-chu">${ketLuan}</p>`;
    veTuyen(d.ban_do.toa_do, d.phan_luong.toa_do);
  } catch (e) {
    khung.textContent = 'Không tải được đường đi.';
    console.error(e);
  }
}

// ---------- thoi gian ----------

async function xemLanDo(viTri) {
  trangThai.viTri = viTri;
  const td = trangThai.thoiDiem[viTri];
  $('thanh-tg').value = viTri;
  $('nhan-tg').textContent = hienGio(td);

  const kq = await api.doan(td);
  trangThai.doan = kq.doan;
  veDiemDo(kq.doan, chonDiem);
  capNhatChiSo(kq.doan);
  veDanhSach(kq.doan);
  if (trangThai.dangChon) danhDauDiemChon(trangThai.dangChon);
}

let henGio = null;
function phatLai() {
  const nut = $('nut-phat');
  if (henGio) {
    clearInterval(henGio);
    henGio = null;
    nut.textContent = '▶';
    return;
  }
  nut.textContent = '❚❚';
  henGio = setInterval(() => {
    const tiep = (trangThai.viTri + 1) % trangThai.thoiDiem.length;
    xemLanDo(tiep);
  }, 700);
}

function baoDuLieuCu(moiNhat) {
  const soGio = (Date.now() - Date.parse(moiNhat)) / 3.6e6;
  if (soGio > 24) {
    $('nhan-cu').textContent = `Dữ liệu chưa cập nhật ${Math.floor(soGio / 24)} ngày`;
    $('nhan-cu').classList.remove('an');
  }
}

// ---------- khoi dong ----------

async function khoiDong() {
  document.querySelectorAll('.tab button').forEach((b) => b.addEventListener('click', () => chuyenTab(b.dataset.tab)));
  $('ct-dong').addEventListener('click', boChon);
  $('nut-phat').addEventListener('click', phatLai);
  $('nut-moi-nhat').addEventListener('click', () => xemLanDo(trangThai.thoiDiem.length - 1));

  let cho = null;   // cho nguoi dung keo xong moi goi API
  $('thanh-tg').addEventListener('input', (e) => {
    $('nhan-tg').textContent = hienGio(trangThai.thoiDiem[e.target.value]);
    clearTimeout(cho);
    cho = setTimeout(() => xemLanDo(Number(e.target.value)), 150);
  });

  $('lop-toa-nha').addEventListener('change', (e) => hienLop('toa-nha', e.target.checked));
  $('lop-duong').addEventListener('change', (e) => hienLop('duong', e.target.checked));
  $('lop-ve-tinh').addEventListener('change', (e) => {
    hienLop('nen-ve-tinh', e.target.checked);
    hienLop('nen-toi', !e.target.checked);
  });

  await taoBanDo('map');

  try {
    trangThai.thoiDiem = await api.thoiDiem();
    if (!trangThai.thoiDiem.length) throw new Error('chưa có lần đo nào');
    const cuoi = trangThai.thoiDiem.length - 1;
    $('thanh-tg').max = cuoi;
    $('lan-do').textContent = hienGio(trangThai.thoiDiem[cuoi]);
    baoDuLieuCu(trangThai.thoiDiem[cuoi]);
    await xemLanDo(cuoi);
    $('trang-thai').classList.add('an');
  } catch (e) {
    $('trang-thai').textContent = `Không tải được dữ liệu đo (${e.message}).`;
    console.error(e);
  }
}

khoiDong();
