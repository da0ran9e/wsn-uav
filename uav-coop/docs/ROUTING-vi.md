# Routing dựng sẵn — PECEE elastic clustering

> Cài lại trong `uav-coop` cơ chế routing trên lớp cell đã dùng ở `uav-sar`
> (`cell-grid` và `inter-cell-routing`). Mã: `models/common/routing.{h,cc}`, chạy ở
> bước 6 của `uav-coop-deploy`. Bố trí seed 1 (109 cell, CH #136).

## Mỗi node lưu gì

**Liên kết G2G:** hai node được coi là nối nhau nếu cách nhau ≤ **50 m** (`--linkRange`).
- Đây là hop ngắn nhất của thí nghiệm G2G-CHAIN, với biên trung vị 11.5 dB.
- Ở 75 m biên chỉ còn 5.3 dB, ở 100 m còn 1 dB, và chuỗi G2G gần như tắc.

| bảng | next hop tới | đường đi được phép |
|---|---|---|
| `toCL` | **CL của cell mình** | chỉ qua node trong cell mình |
| `toCell[B]` | **node gần nhất của cell kề B** (mỗi cell kề trong cụm một bảng, tối đa 6) | chỉ qua node của cell mình và cell B |
| **đường chính** | một trong các next hop trên, cái mở đầu **đường ngắn nhất tới CH** | — |

- **"Ngắn nhất"** là ít hop nhất; nếu bằng nhau thì ít mét hơn.
- **Đường chính** được tính như sau: mỗi node chỉ được chuyển tiếp theo một next hop *đã
  lưu của chính nó*. Đường chính là đường ngắn nhất trong ràng buộc đó (Dijkstra ngược từ
  CH). CH là CL của cell mình, nên trong cell của CH đường chính thường là `toCL`.
- **Không có vòng lặp:** mỗi hop trên đường chính giảm số hop còn lại đúng 1. Điều này
  được kiểm cho mọi node bằng cách đi lần theo từng hop.

Bản đầu tôi viết làm khác: đường chính ở cell A ghép cả đoạn `toCell[B]` rồi đi tiếp từ
node đầu tiên vào B. Phần kiểm tra tự động đã bắt được lỗi của cách đó: node nằm giữa đoạn
có thể chọn hướng khác, nên số hop đã lưu không khớp với đường thực đi. Định nghĩa hiện
tại nhất quán ở mọi node.

## Bảng của một cell

![bảng](figures/route-tables.png)

Ví dụ cell (−3, 3), kề cell của CH:
- Mỗi node có một cây tới CL (ô đầu) và sáu cây tới sáu cell kề.
- **Ô cuối là đường chính của từng node:**
  - 14 node đi thẳng sang cell của CH (−3, 2);
  - một số node phía trên đi về CL trước, vì từ CL sang cell của CH cũng ngắn bằng;
  - 1 node đi qua cell (−2, 2).

## Đường tới CH

![đường chính](figures/route-main.png)

| spacing | node | bậc TB | tới được CH | hop TB (tối đa) | so với tối thiểu bỏ qua cell |
|---|---|---|---|---|---|
| 20 m | 7 080 | 19.0 | **100 %** | 18.1 (39) | +10 % |
| 35 m | 2 312 | 6.2 | **95.9 %** (2 217) | 24.7 (47) | +8 %; 16 % node bằng tối thiểu; tệ nhất +7 hop, ×1.5 |
| 50 m | 1 133 | 3.0 | **2.6 %** (29) | 4.5 (9) | — |

(a) Mỗi đoạn thẳng nối một node với next hop chính của nó. Tất cả tạo thành một cây hướng
về CH, càng xa CH càng đậm màu. (b) Đường thực đi từ 6 node xa nhất: các đường đi gần
thẳng về CH, chỉ lệch so với đường ngắn nhất bỏ qua cell (nét đứt) 2–4 hop.

**Ở spacing 35 m, 95 node (4 %) không có đường chính:**
- **6 node cô lập:** không có node nào trong vòng 50 m.
- **72 node trong các cụm tách rời:** nhóm node nối với nhau nhưng không nối được tới phần
  còn lại của mạng. Nhóm lớn nhất là mũi phía nam cụm, quanh (0, −800). Không cơ chế
  routing nào nối được những node này.
- **17 node bị cơ chế cell chặn:** tới được CH nếu bỏ qua cell, nhưng không qua bảng. Cụm
  node của chúng chỉ nối với phần còn lại qua một cell thứ ba, trong khi `toCell[B]` chỉ
  được đi trong A ∪ B.

Ngoài ra, ở 35 m có **383 node không tới được CL của chính cell mình** khi chỉ đi trong
cell: cell có khoảng 21 node, bậc khoảng 6, nên đồ thị trong cell hay bị đứt. Những node
này vẫn có đường chính qua cell kề, nên đa số vẫn tới được CH.

**Ở spacing 50 m, liên kết ≤ 50 m làm mạng rời rạc** (bậc TB 3): chỉ 29 node quanh CH
tới được CH.

## Kiểm tra tự động (31 triệu CHECK, tất cả qua)

- **Liên kết:** so với duyệt mọi cặp node, đúng tập các cặp cách nhau ≤ 50 m, hai chiều.
- **`toCL`:**
  - số hop bằng BFS độc lập trong cell;
  - đi lần từng hop: mỗi hop là một liên kết, ở trong cell, giảm số hop đúng 1, và kết thúc
    ở CL.
- **`toCell[B]`:**
  - số hop bằng BFS độc lập trong A ∪ B;
  - đi lần: ở trong A cho tới hop cuối, hop cuối vào đúng B, tới đúng node đầu vào đã lưu.
- **Đường chính:**
  - đi lần từ mọi node: tới đúng CH, mỗi hop giảm 1;
  - mỗi hop ở trong cell hoặc sang cell kề;
  - không bao giờ ngắn hơn đường bỏ qua cell;
  - thoả phương trình Bellman: bằng min trên các next hop đã lưu của node đó (1 + số hop từ
    next hop).

## Điểm cần chốt

- **Tầm liên kết 50 m** là giá trị tôi tự chọn. Với 35 m spacing, nó để lại 4 % node không
  có đường.
- **Nới ràng buộc cell.** Hiện `toCL` chỉ được đi trong cell mình và `toCell[B]` chỉ trong
  A ∪ B. Nới ra thì 17 node bị chặn sẽ có đường, nhưng sẽ khác PECEE gốc.
- **Liên kết đang là hình học.** Kênh G2G thật có che khuất tĩnh σ = 7.8 dB, nên tập liên
  kết thực sẽ khác. Có thể dựng liên kết từ kênh đó (bước "hello").

## Chạy lại

```bash
B=/home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-deploy-optimized
$B --spacings=20,35,50 --linkRange=50 --out=deploy     # ghi deploy-routes-sS.csv
python3 tools/route_figures.py docs/data docs/figures --spacing 35 --range 50
```

`deploy-routes-sS.csv`: mỗi dòng là một node, với các cột:
- bậc;
- `toCL` (next hop, số hop);
- next hop chính và bảng được chọn (`CL` hoặc `q:r` của cell kề);
- số hop và số mét tới CH, số hop tối thiểu bỏ qua cell;
- `toCells` = `q:r>next/hops|…`.
