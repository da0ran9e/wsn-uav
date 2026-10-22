# Hình trong `uav-l2/docs/figures/` (CLAUDE.md §8 mục 131)

Chỉ ghi các hình từ 2026-10-22 trở đi; hình cũ hơn không đổi. Mọi hình không có chữ. Cột "commit": commit thêm hình
(tra bằng `git log -- uav-l2/docs/figures/<tên>`).

| Tên | Mô tả trực quan | Lệnh | Tham số chính | Ngày |
|---|---|---|---|---|
| `iter1-k8-s10-kmedoids-meanderK.png` | Hai bản đồ cạnh nhau, cùng miền k8-s10. Trái: 8 cluster k-medoids (màu nhạt), mỗi cluster một đường bay thẳng đen qua CH (sao trắng). Phải: 8 cluster MEANDER-K là các dải ngang, đường bay cong uốn móc qua CH. Vòng trắng là critical cell, ô xanh đậm là hồ, nét đỏ đứt là bay nối của tour, ô vuông đen là BS. | `python3 tools/iter_fig.py OUT latency KC-k8-s10 MK-k8-s10` | k8-s10, River cửa sổ theo critical cell, tour nối thẳng | 2026-10-22 |
| `iter2-k8-s10-kmedoids-swathK6.png` | Như trên. Trái: k-medoids với tour nối Dubins. Phải: SWATH-K, một đường luống liền gồm 6 luồng thẳng chéo 45°, quay đầu bằng vòng Dubins ở hai đầu luồng; 8 cluster là các đoạn liên tiếp của đường luống. Cả hai dùng critical cell theo lân cận thật. | `python3 tools/iter_fig.py OUT kin KD-k8-s10:kin SW-k8-s10:skin` | k8-s10, luồng 6 cell, `--critRing domain` | 2026-10-22 |
| `chordT-k6-s9-kmedoids-vs-chordT1.png` | Cùng miền k6-s9, cùng 6 cluster k-medoids (màu nhạt), CH là sao trắng, critical cell vòng trắng. Trái: mỗi cluster bay đường thẳng dài nhất qua CH, các đường chĩa mỗi hướng một kiểu. Phải: CHORD-T1, hướng của mọi đường chọn cùng thứ tự tour, các đường gần song song và nối đuôi nhau. Nét đỏ đứt nối điểm cuối đường này với điểm đầu đường sau (bay thật là cung Dubins). | `python3 tools/iter_fig.py OUT kin VB/kmedoids/k6-s9 VB/chordT1/k6-s9` | k6-s9, `--chordTour 0.6,0.8`, `--critRing domain --axeNear --windowAt crit` | 2026-10-22 |
