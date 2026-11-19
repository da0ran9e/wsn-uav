# 2026-11-19 · Đặt node IoT trên bản đồ thật, kiểm lưới cell (chatlog mục 356)

Mục đích: đặt node vào chỗ hợp lý trên bốn bản đồ thật (Punggol, Downtown Core, Nam Từ Liêm, Hoàng Mai) và xem lưới cell
R = 100 m liên thông, hổng ra sao trên kênh G2G của mô phỏng.

Lệnh: mỗi bản đồ một file `<bản đồ>.md` (`python3 paper/j1/analysis/urban_nodes.py paper/j1/maps/<bản đồ> ...`, mỗi bản đồ
10–60 s). Đầu vào: `paper/j1/maps/<bản đồ>/` (đã chạy lại `osm_district.py` để xuất thêm `roads.csv.gz`,
`water_all.geojson`).

Đặt node: theo viền nhà mỗi 40 m (chuông cửa, camera tường; 45 % chạy pin, không chuyển tiếp) và dọc phố mỗi 30 m (camera
cột, máy bán hàng; cắm điện), không đặt trên nước, lấy mẫu về 816 node/km² đất. Hai biến thể kênh: như mô phỏng hiện tại, và
trừ 15 dB cho mỗi toà nhà mà đoạn nối cắt qua (tối đa 3).

Kết quả: bảng ở `paper/j1/CONTEXT-vi.md` mục 20; hình `paper/j1/figures/cells-*.png`.

Dang dở: OSM ở Hà Nội thiếu nhiều nhà thấp tầng nên biến thể có tường đánh giá thấp mức đứt ở Hà Nội; một seed; mô hình
xuyên tường là bước đầu của K1c, chưa hiệu chỉnh.

**Bổ sung (mục 357):** thêm node chuyển tiếp trên cột đèn mỗi 35 m (`--poles 35`), hai cách đặt: chỉ ở cell cần và trên mọi
phố; log `<bản đồ>-poles.md`. Che khuất giờ cố định theo từng cặp node (băm mã hai node), nên số của biến thể không cột đèn
lệch nhẹ so với lần chạy đầu (cùng mô hình, khác lần bốc). Bảng ở `paper/j1/CONTEXT-vi.md` mục 21.
