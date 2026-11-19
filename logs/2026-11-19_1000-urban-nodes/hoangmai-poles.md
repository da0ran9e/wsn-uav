# hoangmai-poles

- Bắt đầu: 2026-11-19 14:17:56, chạy 104 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/urban_nodes.py paper/j1/maps/hoangmai hoangmai paper/j1/figures --poles 35
```

**Kết quả**

```text
| Bản đồ | Biến thể | Node (node/km² đất) | Chạy pin | Cell đất | Cell nước | Cell rỗng | Cell đứt bên trong | Cặp kề không có gateway | Thành phần | Cell trong thành phần lớn nhất | Node pin không với tới node điện | Node điện lạc khỏi nhóm chính của cell |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hoangmai | như hiện tại | 26929 (816) | 11 % | 1285 | 267 | 32 (2 %) | 5 (0 %) | 55 / 3572 (2 %) | 1 | 100.0 % | 8 (0 %) | 18 (0.1 %), 11 % trên nhà |
| hoangmai | có tường | 26929 (816) | 11 % | 1285 | 267 | 32 (2 %) | 44 (4 %) | 67 / 3572 (2 %) | 1 | 100.0 % | 32 (1 %) | 65 (0.3 %), 57 % trên nhà |
| hoangmai | có tường, cột đèn ở cell cần | 27991 (848), +1062 cột đèn | 10 % | 1285 | 267 | 31 (2 %) | 18 (1 %) | 24 / 3577 (1 %) | 1 | 100.0 % | 29 (1 %) | 29 (0.1 %), 55 % trên nhà |
| hoangmai | có tường, cột đèn mọi phố | 45568 (1381), +18639 cột đèn | 6 % | 1285 | 267 | 31 (2 %) | 23 (2 %) | 24 / 3587 (1 %) | 1 | 100.0 % | 21 (1 %) | 30 (0.1 %), 70 % trên nhà |
```
