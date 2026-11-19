# sg-downtown-poles

- Bắt đầu: 2026-11-19 14:15:13, chạy 20 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/urban_nodes.py paper/j1/maps/sg-downtown sg-downtown paper/j1/figures --poles 35
```

**Kết quả**

```text
| Bản đồ | Biến thể | Node (node/km² đất) | Chạy pin | Cell đất | Cell nước | Cell rỗng | Cell đứt bên trong | Cặp kề không có gateway | Thành phần | Cell trong thành phần lớn nhất | Node pin không với tới node điện | Node điện lạc khỏi nhóm chính của cell |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sg-downtown | như hiện tại | 4094 (816) | 18 % | 192 | 3 | 11 (6 %) | 0 (0 %) | 4 / 491 (1 %) | 1 | 100.0 % | 1 (0 %) | 2 (0.1 %), 0 % trên nhà |
| sg-downtown | có tường | 4094 (816) | 18 % | 192 | 3 | 11 (6 %) | 81 (45 %) | 21 / 491 (4 %) | 1 | 100.0 % | 51 (7 %) | 297 (8.8 %), 62 % trên nhà |
| sg-downtown | có tường, cột đèn ở cell cần | 5570 (1110), +1476 cột đèn | 13 % | 192 | 3 | 11 (6 %) | 52 (29 %) | 9 / 491 (2 %) | 1 | 100.0 % | 28 (4 %) | 161 (3.3 %), 53 % trên nhà |
| sg-downtown | có tường, cột đèn mọi phố | 7582 (1511), +3488 cột đèn | 9 % | 192 | 3 | 11 (6 %) | 52 (29 %) | 9 / 493 (2 %) | 1 | 100.0 % | 26 (4 %) | 180 (2.6 %), 49 % trên nhà |
```
