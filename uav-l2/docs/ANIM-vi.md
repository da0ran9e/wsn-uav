# Các animation (không chữ trên bản đồ)

Lời gốc: CLAUDE.md §8 mục 71, 86, 87.

| Animation | Nội dung | File, công cụ | Bản đăng |
|---|---|---|---|
| **P: trọn nhiệm vụ** | Bản đồ 4 cluster, 10 bước: sinh miền, hồ, node, chia cluster, vai trò, quét hướng, tour đội 1, kế hoạch River, rồi cả nhiệm vụ (lượt phát, River trên ns-3, đối sánh, LoRa, đội 2) | `anim/mission-replay.html`, `tools/mission_anim.py` | https://claude.ai/artifact/Sd79Xy3LuP27wuNn38nTg6 |
| **P + lớp 2 (LANE)** | Bản đồ 8 cluster: quét hướng, luồng, mảnh vụn, cắt, đường bay, tour quét luống; sau đó cách chia k-medoids để so sánh. **Chỉ có phần hình học**, chưa có River trên ns-3 cho các cluster LANE (chờ duyệt chạy) | `anim/lane-replay.html`, `tools/restructure_anim.py` | https://claude.ai/artifact/UGFp5srtMjxJFMzwuQFNNY |
| **So sánh phương án** | Cùng bản đồ 4 cluster và cùng lượt bốc nghi vấn với P. Các phương án: P; ablation chính sách (tour ngắn nhất, đội 2 chờ đủ báo cáo, thứ tự TSP); ablation lớp 3 (kéo thẳng, Circle cố định 12); baseline B4-0,9, B1, B2-300/500, B3-300/500, B6, B7. Mọi phương án dùng chung một trục thời gian | `anim/compare-replay.html`, `tools/compare_anim.py` | https://claude.ai/artifact/XHjD6X7ssHFeDn7c2Z4vrf |

**Kết thúc nhiệm vụ trên lượt bốc của trang so sánh** (một lượt, chỉ để minh hoạ, không phải số thống kê):

| P | P·short | P·wait | P·tsp | L3·direct | L3·circle12 | B4·0,9 | B1 | B2·300 | B2·500 | B3·300 | B3·500 | B6 | B7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 952 s | 971 | 1 109 | 952 | 952 | 952 | thất bại (1 004) | 2 276 | 2 548 | 1 883 | 2 011 | 1 691 | 1 931 | 671 |

**Ghi chú:**
- Kéo thẳng và Circle 12 cho cùng thời điểm kết thúc với P trên lượt này. Phần chênh của River (vài giây đến vài chục giây) bị nuốt vào khe LoRa 40 s.
- B4 thất bại vì cell thật chỉ giữ dưới 90 % của D. Ngưỡng này là số tạm (xem `L1-PARAMS-vi.md`, câu S1).
- Thời gian xác minh mỗi lần thăm là khoảng 83 s (tệp 1 MiB), theo `mission_baselines.py`.
