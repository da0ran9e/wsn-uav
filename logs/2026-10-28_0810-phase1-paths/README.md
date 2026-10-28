# 2026-10-28 · Hình đường bay pha 1 của các phương án, seed 1 (CLAUDE.md §8 mục 202)

**Mục đích:** vẽ đường bay pha 1 (đội 1) của bốn phương án trong chiến dịch 4 trên seed 1:
- CHORD + River (đề xuất 1);
- LM-Tour + River (đề xuất 2);
- DTSP-N + River;
- FC + DTSP-N.

Hình học không phụ thuộc seed, nên seed 1 đại diện cho mọi seed.

**Lệnh:**
- `paths.md`: `paths_fig.py uav-l2/docs/figures/c4-phase1`.
  - Đường bay của ba phương án River là track của `kin_time.run(folder, "kin")`, đúng đường mà `lm_tour.py score` dùng để chấm.
  - Đường của FC + DTSP-N là `dn-path.csv` mà `l1_rank` ghi vào thư mục CHORD.
  - Đầu vào: `scratchpad/C4/{CP,LMD,DR}/<kênh>/R1/k{8,12,16}-s1` của phiên chính.
- `shrink.md`: `shrink.py` nén PNG về bảng 256 màu, giảm từ 20 MB xuống 5,1 MB, không thấy khác bằng mắt.

**Đầu ra:** `uav-l2/docs/figures/c4-phase1/` gồm 51 ảnh không chữ, mục lục ở `INDEX.md`:
- ba lưới `c4-phase1-k{8,12,16}-s1-grid.png`: hàng là kênh (open, r500, r200, r100), cột là phương án;
- 48 hình lẻ `c4-phase1-k<K>-s1-<kênh>-<phương án>.png`.

**Chiều dài đường bay và thời gian đội 1** (bảng đầy đủ trong `paths.md`). Phương án River: profile kin_time cộng phần bù giao đủ dữ liệu; FC + DTSP-N: `dn-info.json`.

| Bản đồ | CHORD (mọi kênh) | LM-Tour | DTSP-N + River | FC + DTSP-N: open → r100 |
|---|---|---|---|---|
| k8 | 38,6 km · 784 s | 30,8–31,1 km · 697–708 s | 43,6–51,1 km · 1018–1170 s | 30,5 km · 669 s → 113,1 km · 3305 s |
| k12 | 64,0 km · 1292 s | 46,3–46,5 km · 1082–1085 s | 65,4–69,1 km · 1553–1589 s | 40,9 km · 913 s → 172,7 km · 5078 s |
| k16 | 70,7 km · 1437 s | 56,1–60,5 km · 1291–1394 s | 86,2–91,1 km · 2007–2105 s | 49,5 km · 1134 s → 227,5 km · 6808 s |

**Nhận xét:**
- CHORD giống hệt nhau ở mọi kênh: mỗi cụm một dây cung qua CH, thời gian trong cụm cố định khoảng 40 s.
- LM-Tour ngắn hơn CHORD 14–28 % về quãng đường và 3–16 % về thời gian đội 1. Đường đổi nhẹ theo kênh vì ξ tự chọn theo kênh.
- DTSP-N + River dài nhất trong ba phương án River, vì đi zigzag vào đĩa của mọi critical cell.
- FC + DTSP-N ngắn nhất ở kênh open. Khi kênh xấu đi, số vòng lượn quanh nhóm critical cell tăng mạnh, nên đội 1 bay gấp 4–6 lần ở r100.

**Bản một màu (mục 204):**
- `mono.md`: `mono.py` vẽ bốn hình riêng cho k8-s1, kênh r500.
  - Mọi đường bay cùng một màu hồng sẫm `#e6007e`.
  - Màu cụm nhạt hơn: pha thêm 40 % trắng.
  - Bốn hình dùng chung một khung nhìn.
- `shrink-mono.md`: nén bốn hình này.
- Đầu ra: `c4-phase1-k8-s1-r500-{chord,lmtour,dtspn-river,fc-dtspn}-mono.png`.

**Còn dở:** chưa có bản có nhãn cho paper; vẽ bằng `paths_fig.py` nếu cần.
