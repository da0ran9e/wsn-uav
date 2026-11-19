# probe

- Bắt đầu: 2026-11-19 07:23:17, chạy 9 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/osm_probe.py --half 0.003
```

**Kết quả**

```text
| Khu | Toà nhà | Có chiều cao hoặc số tầng | Cao nhất (m, số tầng × 3 m nếu chỉ có số tầng) | Đường |
|---|---|---|---|---|
| hanoi-caugiay | 193 | 24 (12 %) | 87 | 360 |
| hanoi-oceanpark | 47 | 33 (70 %) | 90 | 248 |
| hanoi-royalcity | 86 | 9 (10 %) | 135 | 236 |
| hcmc-district1 | 164 | 26 (16 %) | 193 | 346 |
| singapore-cbd | 287 | 265 (92 %) | 245 | 507 |
| nyc-midtown | 232 | 183 (79 %) | 366 | 598 |
```
