# Bước 1 — sinh mạng: lưới lục giác → vùng liền kề ngẫu nhiên → node ngẫu nhiên

> Project mới `uav-coop`, dựa trên bộ tham số của các thí nghiệm đô thị trong `uav-sar`
> (A2G-RUN, A2G-SWEEP, G2G-CHAIN), gom vào `models/common/coop-params.h`. Bước này chỉ
> dùng phần hình học; các khối tham số vô tuyến được mang sang sẵn cho các bước sau.

![các bước](figures/deploy-steps.png)

## Các bước

**① Lưới lục giác đều từ gốc toạ độ.** Lục giác đỉnh nhọn hướng lên, toạ độ trục
(q, r); cell (0, 0) có tâm ở gốc.

| | |
|---|---|
| chiều rộng (mặt–mặt) = khoảng cách tâm hai cell kề | **100 m** (tham số `--width`) |
| bán kính đỉnh R = rộng / √3 | 57.7 m |
| diện tích một cell = (√3/2)·rộng² | 8 660 m² |

**② Chọn ngẫu nhiên một mảng cell liền kề** — mọc kiểu Eden từ cell gốc: mỗi bước
chọn **đều** một cell trong "biên chờ" (các cell chưa chọn nhưng kề vùng) và thêm vào.
Vùng luôn liền kề theo cách dựng. Mặc định 60 cell (`--cells`), tức 0.52 km², trải
khoảng 1.1–1.4 km — cỡ "cụm đủ rộng" của các thí nghiệm trước.

![mọc vùng từng bước](figures/deploy-growth.png)

**③ Rải node ngẫu nhiên trong vùng.** Số node = diện tích ÷ spacing² (một node trên
mỗi spacing² mét vuông). Mỗi node: chọn đều một cell (các cell có diện tích bằng
nhau), rồi chọn đều một điểm trong lục giác đó (loại bỏ điểm rơi ngoài từ khung bao;
tỉ lệ chấp nhận đúng bằng 3/4).

![ba mật độ](figures/deploy-spacing.png)

| spacing | số node | node / cell | khoảng cách láng giềng gần nhất: TB · nhỏ nhất |
|---|---|---|---|
| 20 m | 1299 | 21.7 | 10.7 m (0.53·s) · **0.7 m** |
| 35 m | 424 | 7.1 | 18.9 m (0.54·s) · 1.5 m |
| 50 m | 208 | 3.5 | 27.6 m (0.55·s) · 1.6 m |

Lý thuyết cho trường ngẫu nhiên đều cùng mật độ là 0.50·s; phần dôi ra là hiệu ứng mép
(node ở mép có ít láng giềng hơn).

**Ngẫu nhiên:** dùng `mt19937_64` lấy thẳng 53 bit cao (không qua `std::uniform_*`, vốn
phụ thuộc thư viện), nên cùng seed cho cùng mạng trên mọi trình biên dịch. Vùng và node
dùng **hai luồng riêng**, nên đổi spacing thì hình dạng vùng giữ nguyên. Đã kiểm: chạy
lại với cùng seed ra file giống hệt.

## Kiểm tra tự động (1.2 triệu CHECK, tất cả qua)

- **Lưới:** mọi đỉnh cách tâm đúng R; tâm cell kề cách đúng 100 m; 200 000 điểm ngẫu
  nhiên đều được gán cho cell có **tâm gần nhất** (tính chất Voronoi của lưới lục giác);
  tỉ lệ diện tích lục giác ÷ khung bao = 0.750 ± 0.005.
- **Vùng:** đủ số cell, không trùng; mỗi cell mới kề một cell có trước; liên thông.
- **Node:** đủ số lượng; mỗi node nằm trong vùng **và** trong đúng lục giác của nó; số
  node mỗi cell qua kiểm định χ² cho phân bố đều (vd. 61.9 với 59 bậc tự do ở 35 m).

## Hai điểm cần anh quyết

1. **Lỗ thủng.** Mọc kiểu Eden đôi khi bỏ sót một cell lọt giữa vùng: seed 1 không có,
   nhưng seed 2–5 có 1–4 lỗ (hình dưới). Vùng vẫn liền kề, nhưng giữa cụm sẽ có một ô
   100 m không có node. **Giữ** (cụm thật có khoảng trống) hay **lấp** lỗ?

   ![các seed](figures/deploy-seeds.png)

2. **Rải đều cho phép node sát nhau** — khoảng cách nhỏ nhất 0.7 m ở spacing 20 m. Nếu
   muốn mỗi node cách nhau tối thiểu một khoảng (vd. spacing/2), cần đổi sang rải có
   khoảng cách tối thiểu (Poisson-disk); mật độ vẫn giữ như cũ.

## Chạy lại

```bash
B=/home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-deploy-optimized
$B --cells=60 --spacings=20,35,50 --seed=1 --out=deploy
for s in 1 2 3 4 5 6; do $B --seed=$s --spacings=35 --out=seed$s; done
python3 tools/deploy_figures.py . docs/figures deploy "seed*-lattice.csv"
```

Dữ liệu dùng cho các hình: `docs/data/`.
