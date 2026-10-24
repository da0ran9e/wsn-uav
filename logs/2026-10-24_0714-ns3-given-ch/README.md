# 2026-10-24 · CHORD-T uốn nhẹ, pass ns-3 bay theo hồ sơ vận tốc, so với MEANDER theo CH có sẵn (CLAUDE.md §8 mục 156–157)

**Mục đích:**

- Mục 156: uốn nhẹ đường CHORD-T để bám các critical cell gần đó, rồi chạy ns-3 cả hai thiết kế trên vài bản đồ.
- Mục 157: trước khi chạy, sửa pass ns-3. Pass cũ bay đều 50 m/s nên không có giảm tốc hay lượn bù cho cụm thiếu giao.

Bản đồ k8 seed 1–3, mỗi bản đồ cùng 5 CH có sẵn: node mạnh nhất của mỗi cụm k-medoids, ở vị trí bất kỳ (mục 154–155).

**Mã:**

- `mission.py --bendCrit 5` (`stage_bend`): critical cell cách dây cung từ nửa bề rộng River (303 m) đến 5 cell kéo đường bay về phía nó, mỗi chỗ tối đa 1 cell; CH vẫn được ghim (`meander_lane.bend_lane`). Đường thẳng giữ lại ở `c{k}-path-chord.csv`. CHORD-T uốn dùng Bank theo pháp tuyến cục bộ (`--banks local`).
- `uav-coop/examples/coop-pass.cc`: đọc thêm cột tuỳ chọn `t` (giây tại mỗi đỉnh đường bay); gói thứ s phát ở thời điểm s·10 ms tại vị trí UAV khi đó. Không có `t` thì chạy như cũ.
  - Binary mới là `BIN/pass-bin`; binary cũ giữ ở `BIN/pass-bin-v1`.
  - Kiểm tra ở `check-pass.md`: đường không có `t` cho bitmap giống hệt bản cũ.
- `pass_speed.py` (`--kinPass`) tính hồ sơ vận tốc của mỗi cụm ở bank 45°, gia tốc ±2 m/s²:
  - cụm thiếu giao giảm tốc trên cell của nó (cap trong khoảng 25–50 m/s, chia đôi) cho tới khi đủ 4041 gói phát trên cell;
  - 25 m/s vẫn chưa đủ thì lượn n vòng bán kính 63,7 m tiếp tuyến tại CH.
- `river_plan.packets`: đặt gói theo đúng cách pass đặt, dùng cho `load` và `mission_report.load_map`. Độ cong của Bank cục bộ tính theo chiều dài cung thật.
- `kin_time`: áp cùng các cap trên tour, nên thời điểm rời cụm (`-kt`) khớp với pass.
- `ns3_cmp.py`: lập bảng so sánh. Đã kiểm tra tái tạo đúng `ns3-diag.md` của `logs/2026-10-24_0403-meander-straight`.

**Lệnh:**

- `geo-*.md`: hình học CHORD-T uốn; `geo-chord-straight-vs-bent.md`: so CHORD-T thẳng và uốn.
- `ns3-{chordB,ml8,ml10}-k8-s*.md`: 9 lượt ns-3, thư mục làm việc `scratchpad/NS157/`, scheme `rf`.
- `l1rank-*.md` → `l1rank/`: T\*, 100 lần bốc mỗi bản đồ, phương pháp `-kt`.
- `ns3-cmp.md` → `ns3-cmp-table.md`: bảng so sánh.
- `fig-s*.md`: hình `chordbend-k8-s*`.
- `check-refactor-ml.md`: kiểm tra `write_path` sinh lại đường bay giống hệt.

Lượt ns-3 chạy trước khi sửa pass đã bị dừng; log của nó bị bỏ.

**Kết quả ns-3** (`ns3-cmp-table.md`; T\* là trung bình 100 lần bốc):

| bản đồ | phương án | tour 45° (s) | cụm giảm tốc / số vòng lượn | rời cụm TB (s) | River xong TB / p90 (s) | sẵn sàng TB (s) | đủ 12 manh mối | T\* (s) |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | CHORD-T uốn | 604 | 3 / 0 | 261 | 10 / 26 | 272 | 100 % | **662** |
| k8-s1 | MEANDER luồng 8 | 534 | 0 / 1 | 270 | 45 / 72 | 315 | 95 % | 763 |
| k8-s1 | MEANDER luồng 10 | 532 | 3 / 0 | 370 | 38 / 77 | 408 | 100 % | 833 |
| k8-s2 | CHORD-T uốn | 531 | 4 / 0 | 251 | 16 / 41 | 267 | 100 % | **632** |
| k8-s2 | MEANDER luồng 8 | 576 | 2 / 0 | 319 | 47 / 100 | 365 | 100 % | 721 |
| k8-s2 | MEANDER luồng 10 | 590 | 4 / 3 | 302 | 52 / 112 | 355 | 92 % | 723 |
| k8-s3 | CHORD-T uốn | 576 | 2 / 0 | 267 | 27 / 54 | 294 | 100 % | **692** |
| k8-s3 | MEANDER luồng 8 | 632 | 1 / 0 | 322 | 48 / 148 | 370 | 100 % | 749 |
| k8-s3 | MEANDER luồng 10 | 531 | 3 / 0 | 327 | 41 / 91 | 368 | 100 % | 812 |

**Vì sao CHORD-T thắng T\* ở cả 3 bản đồ** (nhanh hơn 57–171 s), kể cả khi tour MEANDER ngắn hơn (s1; s3 với luồng 10):

1. **Rời cụm muộn hơn.** Thời điểm rời các cụm có critical cell của MEANDER trung bình muộn hơn 9–109 s. CHORD-T chọn hướng và thứ tự cụm để giảm độ trễ (`chord_tour`); MEANDER bay theo thứ tự cố định của luồng, nên tour ngắn hơn chưa chắc giao sớm hơn.
2. **River chậm gấp 2–4 lần.** MEANDER "giao vừa đủ" nên mỗi Axe chỉ mang đúng một bản tập manh mối. Cửa sổ dữ liệu của mỗi critical cell vì thế trải gần hết Axe, River phải chở xa. Dây cung CHORD-T dài hơn mức cần (quy tắc CLUE 80 %), có nhiều bản sao dọc Axe, nên mỗi critical cell lấy được bản gần nó.

**So với CHORD-T thẳng** (chỉ so hình học, không chạy ns-3 bản thẳng): tour đổi −30 đến +20 s, khoảng cách trung bình tới critical cell giảm 47–96 m.

**Dang dở:**

- Cho MEANDER dư dữ liệu trên Axe (ví dụ 1,5–2 bản) để River ngắn lại, đổi lấy tour dài hơn.
- Sắp thứ tự luồng ưu tiên cụm có nhiều critical cell.
- Mới có 3 bản đồ với 100 lần bốc, chưa đủ cho số liệu công bố (STATUS: N ≥ 120).
