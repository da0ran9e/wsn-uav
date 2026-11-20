# sg-punggol-absent

- Bắt đầu: 2026-11-20 02:34:00, chạy 37 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/urban_nodes.py paper/j1/maps/sg-punggol sg-punggol $S/CELLFIG --poles 35 --absent 0.1,0.2,0.3
```

**Kết quả**

```text
| Bản đồ | Biến thể | Node (node/km² đất) | Chạy pin | Cell đất | Cell nước | Cell rỗng | Cell đứt bên trong | Cặp kề không có gateway | Thành phần | Cell trong thành phần lớn nhất | Node pin không với tới node điện | Node điện lạc khỏi nhóm chính của cell |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sg-punggol | như hiện tại | 7058 (816) | 22 % | 328 | 32 | 10 (3 %) | 6 (2 %) | 22 / 902 (2 %) | 1 | 100.0 % | 0 (0 %) | 14 (0.3 %), 7 % trên nhà |
| sg-punggol | có tường | 7058 (816) | 22 % | 328 | 32 | 10 (3 %) | 98 (31 %) | 45 / 902 (5 %) | 1 | 100.0 % | 80 (5 %) | 312 (5.7 %), 73 % trên nhà |
| sg-punggol | có tường, cột đèn ở cell cần | 8934 (1033), +1876 cột đèn | 17 % | 328 | 32 | 9 (3 %) | 47 (15 %) | 11 / 908 (1 %) | 1 | 100.0 % | 58 (4 %) | 167 (2.3 %), 68 % trên nhà |
| sg-punggol | có tường, cột đèn ở cell cần, 10 % thiết bị vắng | 8274 (957), +1876 cột đèn | 17 % | 328 | 32 | 9 (3 %) | 64 (20 %) | 15 / 907 (2 %) | 1 | 100.0 % | 67 (5 %) | 189 (2.8 %), 65 % trên nhà |
| sg-punggol | có tường, cột đèn ở cell cần, 20 % thiết bị vắng | 7627 (882), +1876 cột đèn | 16 % | 328 | 32 | 9 (3 %) | 84 (26 %) | 28 / 904 (3 %) | 1 | 100.0 % | 77 (6 %) | 219 (3.4 %), 64 % trên nhà |
| sg-punggol | có tường, cột đèn ở cell cần, 30 % thiết bị vắng | 6902 (798), +1876 cột đèn | 16 % | 328 | 32 | 9 (3 %) | 101 (32 %) | 36 / 904 (4 %) | 1 | 100.0 % | 80 (7 %) | 276 (4.8 %), 60 % trên nhà |
| sg-punggol | có tường, cột đèn mọi phố | 12053 (1393), +4995 cột đèn | 13 % | 328 | 32 | 9 (3 %) | 59 (18 %) | 10 / 908 (1 %) | 1 | 100.0 % | 44 (3 %) | 185 (1.8 %), 68 % trên nhà |
```
