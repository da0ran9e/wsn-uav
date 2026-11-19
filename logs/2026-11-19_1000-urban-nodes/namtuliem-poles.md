# namtuliem-poles

- Bắt đầu: 2026-11-19 14:15:32, chạy 144 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/urban_nodes.py paper/j1/maps/namtuliem namtuliem paper/j1/figures --poles 35
```

**Kết quả**

```text
| Bản đồ | Biến thể | Node (node/km² đất) | Chạy pin | Cell đất | Cell nước | Cell rỗng | Cell đứt bên trong | Cặp kề không có gateway | Thành phần | Cell trong thành phần lớn nhất | Node pin không với tới node điện | Node điện lạc khỏi nhóm chính của cell |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| namtuliem | như hiện tại | 25081 (816) | 17 % | 1199 | 39 | 59 (5 %) | 13 (1 %) | 69 / 3198 (2 %) | 2 | 99.9 % | 3 (0 %) | 20 (0.1 %), 5 % trên nhà |
| namtuliem | có tường | 25081 (816) | 17 % | 1199 | 39 | 59 (5 %) | 122 (11 %) | 86 / 3198 (3 %) | 2 | 99.9 % | 111 (3 %) | 407 (2.0 %), 77 % trên nhà |
| namtuliem | có tường, cột đèn ở cell cần | 27400 (891), +2319 cột đèn | 16 % | 1199 | 39 | 56 (5 %) | 75 (7 %) | 42 / 3212 (1 %) | 2 | 99.9 % | 87 (2 %) | 254 (1.1 %), 80 % trên nhà |
| namtuliem | có tường, cột đèn mọi phố | 40429 (1315), +15348 cột đèn | 11 % | 1199 | 39 | 56 (5 %) | 71 (6 %) | 38 / 3222 (1 %) | 1 | 100.0 % | 75 (2 %) | 245 (0.7 %), 80 % trên nhà |
```
