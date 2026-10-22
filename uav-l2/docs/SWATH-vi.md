# SWATH-K: lớp 2 bằng một đường luống liền

Lời gốc: CLAUDE.md §8 mục 115–118, 135–136. Mã: `tools/swath.py` (chia cụm, đường bay), `tools/swath_mission.py` (nhiệm vụ), `tools/dubins.py` (`path_csc`), `tools/mission_policy.py` (tour `skin`), `tools/l2_metrics.py` (chỉ số giao dữ liệu). Log: `logs/2026-10-22_1806-propose-iter/`, `logs/2026-10-22_1947-swath-validate/`.

## 1. Ý tưởng

Với một UAV cánh bằng, hơn một nửa tour đội 1 của k-medoids là bay nối giữa các cụm và quay vòng (k8-s10: 327 s nối, 143 s về BS trong 899 s). SWATH-K dựng tuyến bay trước, rồi chia cụm dọc theo nó:
- toàn miền được phủ bởi **một đường luống liền**; UAV chỉ quay đầu ở cuối mỗi luồng;
- K cụm là **các đoạn liên tiếp** của đường luống, nên giữa hai cụm kề nhau UAV bay thẳng tiếp, không có quãng nối.

## 2. Các bước

1. **Luồng.** Cắt đất liền thành dải thẳng song song rộng L = 6 cell (1,04 km). Một cụm 80 cell trong luồng này dài khoảng 2 km, đủ cho một bản bộ manh mối (4 041 gói, mục 3 của `SAT-vi.md`). Luồng 7–8 cell kém hơn vì nhiều cụm không chứa đủ bộ manh mối (§4).
2. **Đường luống.** Mỗi luồng bay dọc đường giữa của nó, từ cell đầu tới cell cuối, đổi chiều luân phiên. Hai luồng nối bằng đường Dubins ngắn nhất bán kính 255 m (50 m/s, nghiêng 45°). Hồ và chỗ lõm được bay qua.
3. **Hướng luống.** Thử mọi hướng (bước 5°) và độ lệch (0, 1/3, 2/3 luồng). Mặc định chọn tổng BS → tuyến → BS ngắn nhất. Biến thể `--routeBy latency` chọn tuyến bay qua các cell có khả năng là critical cell sớm nhất trung bình (`likely_critical`: BS biết năng lực node từ trước).
4. **Cắt cụm.** Xếp cell theo thứ tự bay, cắt thành đúng K đoạn N/K cell (K bằng số cụm của k-medoids). Mảnh rời (do hồ) nhập vào cụm kề, rồi cân lại về trần 80 cell (`partition.rebalance`).
5. **CH.** Node mạnh nhất trong các cell nằm dưới đoạn bay của cụm (`uav-coop-deploy --chCells`). Đoạn bay được uốn nhẹ để đi qua CH (lệch 4–110 m trên k8-s10).
6. **Tour.** Nối Dubins giữa các cụm, nhưng bay liền khi đoạn sau nối tiếp đoạn trước (tour `skin`).

## 3. Hai sửa đổi mô hình đi kèm (áp dụng cho mọi cách chia)

- **Critical cell theo lân cận thật** (`--critRing domain`): phép thử "vượt trội so với vùng quanh nó" xét cả cell của cụm bên cạnh. Trước đây cụm mảnh có thêm critical cell (k8-s10: 57 so với 45).
- **Axe gồm cả gói phát sát mép cụm** (`--axeNear`): gói phát khi UAV ở cell kề cụm được gán cho cell gần nhất của cụm; node ở đó cách UAV chỉ khoảng 200–290 m.

## 4. Kết quả

16 bản đồ (4 mỗi cỡ), ghép cặp với k-medoids + đường thẳng dài nhất qua CH, cùng P\* (`PROPOSE-ITER-vi.md` §1). Chênh = SWATH trừ k-medoids.

| | k2 | k4 | k6 | k8 | cả 16 |
|---|---|---|---|---|---|
| SWATH-K, ΔT\* (bản đồ tốt hơn) | +57 s (0/4) | +15 s (2/4) | −28 s (4/4) | −20 s (2/4) | +6 s (8/16) |
| SWATH-L, ΔT\* | +56 s (0/4) | +4 s (2/4) | −33 s (4/4) | −44 s (4/4) | −4 s (10/16) |
| SWATH-K, Δ tour đội 1 | +77 s | +2 s | +4 s | +5 s | +22 s |
| SWATH-K, Δ khung River | +36 k | +40 k | +60 k | +18 k | +38 k |

- Ở bản đồ nhỏ (2 cụm), ba luồng cùng các vòng quay đầu dài hơn hai đường thẳng của k-medoids.
- Ở bản đồ lớn, SWATH-L thắng đều (k6, k8: 8/8), nhưng tốn gần gấp đôi khung River (+94 k mỗi bản đồ) vì Axe dài.
- Luồng 7–8 cell kém hơn luồng 6: trên k8-s10 chỉ 38 % / 33 % critical cell giữ đủ 12 manh mối sau River, so với 77 % (vòng 3, trước khi sửa Axe; số T\* của vòng đó không ghép cặp nên không dùng).

**Kết luận:** SWATH-K không phải lựa chọn tốt nhất cho mọi cỡ. Ưu điểm chính của nó (bỏ quay vòng giữa các cụm) đạt được rẻ hơn bằng CHORD-T (`PROPOSE-ITER-vi.md` §3): giữ cụm k-medoids, chỉ chọn hướng đường bay của các cụm cùng với thứ tự tour.
