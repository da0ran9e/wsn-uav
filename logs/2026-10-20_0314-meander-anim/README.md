# 2026-10-20 · Animation từng bước của nhiệm vụ MEANDER (CLAUDE.md §8 mục 105)

**Mục đích:** mô tả chi tiết và visualize từng bước của thử nghiệm MEANDER ns-3 (mục 104): animation và hình tĩnh, không chữ trên bản đồ.

**Lệnh:**
- `trace.cmd` / `trace.log`: chạy lại River (chuẩn bị đầy đủ) có `--trace` cho 6 cluster MEANDER của bản đồ k4.
  - Cùng binary và cùng plan với `logs/2026-10-20_0222-meander-ns3/`.
  - Kết quả critical cell trùng khớp 6/6.
- `export.cmd` / `export.log`: `uav-l2/tools/meander_anim.py` xuất dữ liệu cho player.
  - Gồm các bước MEANDER, đường cong gốc và đường đã uốn qua CH, lượt phát, luồng River theo pha, LoRa, đội 2.
  - Lượt bốc là lượt đầu tiên cần 2 lần thăm.
- Ghép trang: `meander-head.html` + `meander-body.html`, chèn `meander.json`.
- Soát bằng Chromium headless: 0 lỗi JavaScript, khoảng 30 khung. Ảnh soát nằm trong scratchpad `shots/`, không commit.

**Đầu vào:** scratchpad `MM/k4` (bản đồ k4-s2 chia bằng MEANDER, Bank cục bộ), `MM/k4/tr/t*-{hops,held}.csv` (khoảng 36 MB, không commit).

**Đầu ra:**
- `uav-l2/docs/anim/meander.json` (1,35 MB), `meander-head.html`, `meander-body.html`, `meander-replay.html`
- Artifact: https://claude.ai/artifact/43DQcbhZfmQ46iKFbiwDsZ
- `uav-l2/docs/figures/meander-anim-steps.png`: 18 khung, mỗi bước một khung.
- Mô tả từng bước: `uav-l2/docs/ANIM-vi.md`, mục "MEANDER: từng bước".

**Kết quả chính:**
- Player có 13 bước dựng và bước nhiệm vụ. Đội 1 bay theo đường cong thật của từng cluster, theo đúng chiều bay của tour l3first.
- Lượt minh hoạ:
  - Đội 2 cất cánh ở 429 s.
  - Thăm nghi vấn giả ở C5 trước, rồi nghi vấn thật ở C3.
  - Kết thúc ở 1 050 s. Số trung bình 100 lượt là 867 s.

**Dang dở:** chưa có animation cho LANE trên ns-3 và cho bản đồ 6, 8 cluster; công cụ dùng được cho các bản đồ đó nếu cần.
