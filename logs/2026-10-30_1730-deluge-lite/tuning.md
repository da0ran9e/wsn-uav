# Tinh chỉnh Trickle (k12-s1, LM-Tour, open, seed 1)

| Cấu hình | Imin / Imax | Sẵn sàng | Readiness trung bình | Cell cuối | Frame data / quảng bá / request / tổng | Wall |
|---|---|---|---|---|---|---|
| River (đối chứng) | – | 66/66 | 473,0 s | 984,4 s | – / – / – / 930 900 | 175 s |
| dla | 0,5 s / 8 s | 66/66 | 482,8 s | 999,7 s | 2 483 960 / 449 958 / 115 505 / 6 779 134 | 5 240 s |
| dlb | 2 s / 60 s | 66/66 | **482,3 s** | 997,4 s | 2 514 035 / 126 494 / 106 838 / 6 027 140 | 1 941 s |

Chọn **dlb** theo quy tắc của đặc tả (readiness trung bình tốt hơn), cố định cho mọi lần chạy chính (`dl-config.txt`).
