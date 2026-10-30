# 2026-10-30 · Ground transport on fixed CHORD passes: River vs direct pull vs Deluge (CLAUDE.md §8 mục 227–229)

**Mục đích:** bảng reviewer yêu cầu: trên cùng pass CHORD, so sánh River (rf), kéo trực tiếp (d2) và Deluge/Trickle
(t, tp) theo T\*, frame và năng lượng radio (tổng và node nóng nhất). Bản đồ k8-s1 (8 cụm, 45 critical cell), kênh
r100, seed ns-3 1 và 2 (ghép cặp: cùng pass, cùng kênh G2G). Phiên chính điều phối; các phiên phụ chạy theo `CHILD.md`.

**Binary:** `river-bin8.xz` (CAMP-BIN6 = CAMP-BIN5 của chiến dịch 4 + river-bin này; hash trong `setup.sh`).
- Bộ đếm trạng thái PHY từng node (`-energy.csv`: thời gian TX/RX/nghe/tắt, frame phát/nhận, lúc phát frame cuối).
- River không đổi: cụm 6, 7, 8 seed 1 trùng chiến dịch 4 tới từng hop; T\* seed 1 = 891,9 s (chiến dịch 4: 892).

**Các phương án**
- `rf`: River, `--prep=full --repair=20` như chiến dịch 4.
- `d2`: kéo trực tiếp với hai cơ chế sửa lỗi của River (Axe cell bù Seg từ cell kề; critical cell đứng yên 20 s
  thì hỏi lại). Bản `d` không sửa lỗi kẹt ở cụm 6 seed 1 (4 cell thiếu 1 gói tới 900 s) nên không công bằng.
- `t`: Deluge/Trickle trên các cell của kế hoạch River. `tp`: chỉ trên Axe, critical cell và cell của đường kéo
  trực tiếp (phạm vi reviewer đề nghị).
- Trickle (RFC 6206): Imin 1 s, Imax 64 s, k = 1. Page 64 gói, ngắt thêm tại đầu mỗi ảnh (`page_breaks.py`) và đầu
  Seg của Axe cell; Axe cell bù Seg như River. Không có hai điều này, Deluge kẹt ở 3/8 cụm vì có page không cell
  nào giữ trọn (luật quảng bá của Deluge cần page đủ).
- Năng lượng (`uav-l2/tools/energy.py`, `uav-l2/docs/ENERGY-vi.md`): CC2420 và EFR32MG21; "scheduled sleep" cho
  rf/d2 (node ngủ sau frame cuối của mình), Trickle phải nghe nên không ngủ. Tổng năng lượng chỉ tính các node của
  cell tham gia mỗi phương án (tp mô phỏng 8 696 node, các phương án khác khoảng 11 260).

**Kết quả** (`table.md`, `table.csv`; `python3 table.py 1 2`), 2 seed × 8 cụm, T\* 200 lượt ghép cặp:

| | River | Kéo trực tiếp | Deluge (cell River) | Deluge (cell đường) |
|---|---|---|---|---|
| critical cell xong | 90/90 | 90/90 | 90/90 | 90/90 |
| cell cuối sẵn sàng, s | 119 | 121 | 154 | 150 |
| frame phát, nghìn | 955 | 848 | 2 351 | 1 795 |
| năng lượng CC2420, ngủ theo lịch, J | 1 687 | 1 289 | 14 772 | 11 060 |
| node nóng nhất CC2420, ngủ theo lịch, J | 19,0 | 18,9 | 27,5 | 26,8 |
| T\*, s | 870 | 873 | 904 | 901 |

- River so với Deluge: cùng giao đủ, T\* nhanh hơn 31–34 s (≈ 3,5 %; River thắng 146–148/200 lượt), cell sẵn sàng
  sớm hơn khoảng 31–35 s, ít frame hơn 1,9–2,5 lần, năng lượng radio ít hơn 6,6–8,8 lần khi ngủ theo lịch, node
  nóng nhất nhẹ hơn khoảng 30 %.
- River so với kéo trực tiếp (có sửa lỗi): T\* và thời điểm sẵn sàng ngang nhau (Δ trong khoảng tin cậy); kéo trực
  tiếp tốn ít hơn 11 % frame và 24 % năng lượng. Ở r100 trên bản đồ này River không rẻ hơn kéo trực tiếp.

**Dở dang:** mới 2 seed (reviewer khuyên 3–5); c1, c2 của Zeng–Zhang chưa đối chiếu PDF gốc (arXiv bị chặn).
