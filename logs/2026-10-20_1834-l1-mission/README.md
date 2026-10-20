# 2026-10-20 · Nhiệm vụ trọn vẹn với mô hình lớp 1 mới (CLAUDE.md §8 mục 113–114)

**Mục đích:**
- Cài mô hình lớp 1 tổng quát (`paper/L1-MODEL-vi.md`) vào giả lập nhiệm vụ cùng lớp 2 và lớp 3 đã có.
- Chạy ablation và baseline, kể cả cluster có sẵn (nay là ablation) và baseline subCH.
- Sau mỗi vòng rút số liệu, phát triển ý tưởng; vòng cuối báo cáo từng bước kèm hình.

Báo cáo đầy đủ: `uav-l2/docs/L1-MISSION2-vi.md`. Dữ liệu ns‑3 của vòng 2 do `logs/2026-10-20_1846-campaign2/` tạo.

**Các bước (chạy từ `uav-l2/`, log ghi bằng `tools/runlog.py`):**

| Log | Lúc | Việc |
|---|---|---|
| `r1-rank.md` | 18:34 | Vòng 1: `l1_rank.py`, 39 bản đồ k‑medoids (River đầy đủ D) và 3 bản đồ cho mọi cách chia lớp 2, 100 lượt. |
| `r1b-policy.md` | 18:50 | Vòng 1b: bốn ý tưởng (tour độ trễ, chờ P_U + đón đầu, báo hai lần), 39 bản đồ × 50 lượt. |
| `sens.sh`, `sens.md` | 19:16 | Độ nhạy lớp 1 (D, tỉ lệ mặc giống, M), chính sách lúc đó, KF. |
| `e1kf.sh`, `e1kf.md` | 19:31 | Xem trước E1 trên KF (River đầy đủ D), 40 bản đồ × 50 lượt. |
| `rule.sh`, `rule.md` | 20:00 | Chọn ngưỡng chờ của đội 2 trên 40 bản đồ: β = 1, 1/2, 1/4, 0 và quy tắc theo thời gian; chọn β = 1/4. |
| `e1.sh`, `e1.md` | 21:15 | **E1:** cluster có sẵn, River cửa sổ (KW), 40 bản đồ × 100 lượt, 24 phương án. |
| `anim.md`, `anim-meander.md` | 21:15 | Xuất hình động và hình từng bước k4‑s2 (k‑medoids, MEANDER) cho P\*. |
| `e1-figs.sh`, `e1-figs.md` | 21:31 | Bảng và hình E1 (`l1_compare.py`). |
| `sens2.md` | 21:31 | Độ nhạy chạy lại với P\* cuối trên KW (`sens.sh` đã sửa), `l1_sens.py`. |
| `allclues.sh`, `allclues.md` | 21:34 | Cận trên: mọi critical cell đủ 12 manh mối sau River. |
| `state.md` | 21:40 | `l1_state.py`: đội 2 đang làm gì lúc báo cáo của c\* về BS. |
| `redir.sh`, `redir.md` | 21:45 | Đội 2 đổi hướng giữa đường (`-redir`), 40 bản đồ × 100 lượt. |
| `trace-subch.md` | 21:52 | River có trace trên subCH k4‑s2 (`river_trace.sh`, kết quả trùng lần chạy gốc), hình từng bước subCH. |
| `e2.sh`, `e2-subch.md`, `e2-meander.md` | | **E2:** subCH (SW) và MEANDER (MW), 40 bản đồ × 100 lượt, ghép cặp với E1. |
| `e2-figs.sh`, `e2-figs.md` | | Bảng và hình E2. |

**Đầu vào:** các thư mục nhiệm vụ trong scratchpad (`/tmp/claude-0/.../scratchpad/`): `KF` (k‑medoids, River đầy đủ D), `KW` (River cửa sổ 400 kB), `SW` (subCH), `MW` (MEANDER), `TR` (trace River cho hình động). Mỗi bộ khoảng 80–120 MB, không commit.

**Đầu ra:**
- Dữ liệu: `uav-l2/docs/data/l1rank/{r1,r1b,e1kf,rule,e1,e1-all,e1-abl,e1-base,e1-bd,allclues,state,redir,sens-*,e2-*}*.csv`
- Hình: `uav-l2/docs/figures/l1-{model,sens,e1-abl-tstar,e1-base-tstar,e1-breakdown,e2-tstar,e2-breakdown,steps-k4-s2,steps-mw-k4-s2,steps-sw-k4-s2}.png`
- Hình động: `uav-l2/docs/anim/l1-replay.html` (artifact https://claude.ai/artifact/24qasoy6bpmLpBZo2nxAjR)
- Mã mới: `uav-l2/tools/{l1_model,l1_rank,l1_compare,l1_sens,l1_figs,l1_anim,l1_steps,l1_state,subch,tour_heur}.py`, `river_trace.sh`

**Kết quả chính (E1, cluster có sẵn, T\* k2 / k4 / k6 / k8):**
- P\* 408 / 566 / 675 / 769 s. P cũ chậm hơn 98–112 s, trên 40/40 bản đồ.
- Không hợp tác chậm hơn 26–68 s, trên 39/40 bản đồ. Phân vị 90 chậm hơn 75–234 s.
- Baseline cánh quay tốt nhất (B3‑500) chậm hơn 1,9–2,8 lần, B1 chậm hơn 2,2–4,0 lần. Cận dưới B7: 245–347 s.
- Cận trên "đủ 12 manh mối" chỉ nhanh hơn 0–7 s. Đổi hướng giữa đường nhanh hơn 5–15 s (36/40 bản đồ).

__E2__

**Dang dở:**
- Mọi số là số thăm dò: 10 bản đồ mỗi cỡ, dưới quy tắc N ≥ 120.
- Tham số lớp 1 (trước hết D) chưa neo vào số đo thật.
- Hai hướng cho pha 2 chưa cài: xác minh hai bước, và cell báo thêm độ tự tin.
