# Mô hình năng lượng cho bảng "Ground transport on fixed CHORD passes" (CLAUDE.md §8 mục 227, phần 3)

Công cụ: `uav-l2/tools/energy.py` (`radio` cho mạng mặt đất, `uav` cho đội 1). Không cần EnergySource của ns-3:
ns-3.46 không có mô hình năng lượng chính thức cho lr-wpan, nên ta làm việc tương đương bằng giải tích trên các
bộ đếm trạng thái PHY mà `coop2-river` ghi vào `OUT-energy.csv`.

## 1. Radio mặt đất

Mỗi node (cộng gộp các radio nếu là gateway hai radio):

$$E_{\rm radio}=V\left(I_{\rm tx}\,T_{\rm tx}+I_{\rm rx}\,T_{\rm rx}+I_{\rm listen}\,T_{\rm listen}+I_{\rm off}\,T_{\rm off}+I_{\rm sleep}\,T_{\rm sleep}\right)$$

tương đương $N_{tx}E_{tx}+N_{rx}E_{rx}+T_{\rm listen}P_{\rm listen}+T_{\rm sleep}P_{\rm sleep}$. $T_{\rm tx}$, $T_{\rm rx}$,
$T_{\rm listen}$, $T_{\rm off}$ là thời gian ở BUSY_TX, BUSY_RX, RX_ON/TX_ON nhàn rỗi và TRX_OFF, tính từ lúc nhiệm vụ mặt
đất bắt đầu tới khi mô phỏng dừng. **Nghe nhàn rỗi là máy thu đang bật, nên $I_{\rm listen}=I_{\rm rx}$** (chế độ
"idle" 426 µA của CC2420 là radio tắt, chỉ dao động thạch anh chạy, nên dùng cho TRX_OFF).

| Hằng số | CC2420 | EFR32MG21 (+10 dBm) | Nguồn |
|---|---|---|---|
| $V$ | 3,0 V (dải 2,1–3,6 V) | 3,0 V | datasheet |
| $I_{\rm tx}$ | 17,4 mA ở 0 dBm (mức tối đa của chip) | 33,8 mA ở +10 dBm | [1] Electrical Specifications; [2] bảng dòng tiêu thụ radio |
| $I_{\rm rx}=I_{\rm listen}$ | 18,8 mA | 9,4 mA (O-QPSK 250 kbps) | [1]; [2] |
| $I_{\rm off}$ | 426 µA (idle: thạch anh bật) | 5,0 µA (EM2) | [1]; [2] |
| $I_{\rm sleep}$ | 20 µA (power down) | 5,0 µA (EM2, giữ 96 kB RAM, RTC từ LFXO) | [1]; [2] |

Mô phỏng phát +10 dBm, vượt mức tối đa 0 dBm của CC2420; cột CC2420 giữ theo đề nghị của reviewer, cột EFR32MG21
khớp công suất phát mô phỏng. Đáng chú ý: ở CC2420 dòng RX cao hơn TX, ở EFR32MG21 ngược lại; với cả hai, thời gian
nghe áp đảo nên thứ hạng giữa các phương án không đổi.

**Hai chế độ**
- `on`: như mô phỏng, mọi radio bật nghe khi rảnh (SetRxOnWhenIdle).
- `sched`: chỉ cho phương án có kế hoạch (River `rf`, kéo trực tiếp `d`). Lịch biết trước nên sau frame cuối của
  mình (`lastTxS`) node tắt máy ($I_{\rm sleep}$). Thời gian đó được trừ vào nghe trước, rồi vào RX (frame nghe lỏm).
  Node đích cũng phát ACK cho frame cuối nó nhận, nên sau `lastTxS` nó không còn nhận gì có ích. Trickle/Deluge
  (`t`, `tp`) không có lịch, phải nghe advertisement, nên `sched` của nó bằng `on`. Đây là cận trên cho phần tiết
  kiệm của River: node thức đến frame cuối, không ngủ xen giữa các trao đổi.

**Đầu ra** mỗi (cụm, phương án, chip, chế độ): tổng năng lượng, max theo node (tuổi thọ mạng do node nóng nhất quyết
định), max theo vai trò cell lấy từ `plan<k>.txt` (critical, Axe, Bank, thành viên Circle, relay trên đường của kế
hoạch, khác), tổng frame phát (gồm ACK, phát lại) và nhận. Một cell có nhiều vai trò thì lấy vai trò đầu theo thứ tự đó.

## 2. UAV đội 1 (cánh bằng)

Zeng & Zhang [3], mô hình có số hạng gia tốc:

$$P(\mathbf v,\mathbf a)=c_1\|\mathbf v\|^3+\frac{c_2}{\|\mathbf v\|}\left(1+\frac{\|\mathbf a\|^2-(\mathbf a^\top\mathbf v)^2/\|\mathbf v\|^2}{g^2}\right),\qquad
E=\int_0^T P\,dt+\tfrac12 m\left(\|\mathbf v(T)\|^2-\|\mathbf v(0)\|^2\right)$$

Số hạng trong ngoặc chỉ giữ gia tốc pháp tuyến $a_\perp=v^2\kappa$ (gia tốc dọc chỉ vào qua $\Delta K$).
$c_1=9{,}26\times10^{-4}$ kg/m, $c_2=2250$ kg·m³/s⁴, $m=10$ kg, theo phần kết quả số của [3] (Mục VI); $c_1$, $c_2$ là
hàm của mật độ không khí, hệ số cản, diện tích cánh và trọng lượng (phụ lục của [3]). Với các hằng số này
$P(30)\approx100$ W, tốc độ bền tối đa khoảng 30 m/s; $P(50)=161$ W, $P(25)=104$ W, $P(25,\ \text{vòng }1g)=194$ W.

Quỹ đạo: profile tốc độ của `kin_time.run(w, "kin")` (bank 45°, ≤ 50 m/s, gia tốc dọc ±2 m/s², trần tốc độ trên cell
của từng cụm theo `c{k}-speed.json`), độ cong từ ba điểm cách 10 m. Phần bù giao dữ liệu (nếu có) bay ở 25 m/s; lượn
vòng ở bank 45° thì bán kính 63,7 m, gia tốc hướng tâm $25^2/63{,}7=9{,}81$ m/s² = 1 g (đã kiểm).

**k8-s1, r100, tour CHORD:** 38,6 km, 783 s, **130 kJ**; chỉ dùng công suất bay đều thì 123 kJ, số hạng gia tốc thêm
6,9 kJ (+5,6 %), không cần bù giao dữ liệu, $\Delta K=0$ (xuất phát và về BS cùng tốc độ).

## 3. Chú thích cho bài

Năng lượng UAV (cỡ trăm kJ) lớn hơn năng lượng radio mặt đất nhiều bậc độ lớn, nên báo riêng: hai đại lượng phục vụ
hai ràng buộc khác nhau, **sức bền của UAV** và **tuổi thọ pin của mạng**.

## Tài liệu

[1] Texas Instruments, *CC2420: 2.4 GHz IEEE 802.15.4 / ZigBee-ready RF Transceiver*, datasheet SWRS041c, mục
Electrical Specifications (dòng tiêu thụ). RX 18,8 mA và TX 17,4 mA đã đối chiếu với trang sản phẩm TI
(ti.com/product/CC2420); 426 µA và 20 µA chưa đối chiếu lại được PDF trong phiên này (mạng chặn), cần kiểm.
[2] Silicon Labs, *EFR32MG21 Mighty Gecko Wireless SoC Family Data Sheet*, bảng dòng tiêu thụ radio 2,4 GHz và EM2.
Trang tóm tắt sản phẩm ghi TX +10 dBm 34,9 mA (datasheet: 33,8 mA); dùng số datasheet.
[3] Y. Zeng, R. Zhang, "Energy-efficient UAV communication with trajectory optimization", *IEEE Trans. Wireless
Commun.*, vol. 16, no. 6, pp. 3747–3760, 2017 (arXiv:1608.01828). $c_1$, $c_2$, $m$ lấy theo Mục VI; chưa mở lại được
PDF trong phiên này (mạng chặn arxiv.org), cần đối chiếu số phương trình và trang trước khi trích.
