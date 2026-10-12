# River trên ns-3 — từng bước của một lượt bay

Lời gốc: CLAUDE.md §8 mục 50–53. Thuật toán: [`L3-vi.md`](L3-vi.md) (Thuật toán 1–7).

Trang này cho thấy từng bước của **một** lượt bay (lượt 1) trên ns-3, so ba biến thể. Đây chưa
phải kết quả thống kê: chiến dịch 120 lượt còn chờ chốt.

| Biến thể | Viết tắt | Khác nhau ở |
|---|---|---|
| River, Circle chuẩn bị sẵn | `river --prep=full` | thành viên Circle lấy cả phần được giao từ Bank ngay khi gom xong |
| River, Circle chỉ lấy khi được hỏi | `river --prep=ondemand` | thành viên Circle chỉ đi lấy những gói critical cell hỏi, sau khi nó hỏi |
| Kéo thẳng (so sánh) | `direct` | critical cell hỏi thẳng từng cell Axe phần nó thiếu |

**Cách dựng lớp truyền.**
- MAC 802.15.4 đầy đủ của ns-3 (lr-wpan): CSMA/CA, ACK, gửi lại.
- Kênh theo lưới cell PECEE:
  - mỗi cell một kênh, 11 + (q + 3r) mod 7, nên cùng kênh chỉ lặp lại ở cell cách 3 ô;
  - mỗi cặp gateway có radio và kênh riêng, 18–26.
- Lịch: mỗi cell và mỗi cặp gateway chỉ có **một máy phát tại một thời điểm**, xoay vòng giữa các radio có gói chờ.
- Kênh G2G: n = 3,5, che khuất 7,8 dB cố định theo từng cặp node, Rayleigh theo khối 100 ms.
  Một mô hình suy hao dùng chung cho mọi kênh, nên che khuất và fading thuộc về cặp node chứ
  không phụ thuộc kênh: đổi kế hoạch kênh không làm đổi liên kết nào yếu.
- Đường trong cell: ETX nhỏ nhất trên kênh của lượt đó. Liên cell vẫn đi đúng cặp gateway duy nhất.

Chạy lại:
```
uav-coop2-river --nodes=… --routes=… --gateways=… --plan=docs/data/river-plan.txt \
    --bits=BITS/p1-bits --runs=1 --scheme=river --prep=full --out=T/rf --trace=T/rf
python3 tools/river_ns3_figures.py --deploy ../uav-coop/docs/data --path docs/data/path-a180.csv \
    --plan docs/data/river-plan.txt --bits BITS/p1-bits-r1.bin --trace "T/{s}" --figs docs/figures
```

## Bước 0 — mạng mô phỏng

![setup](figures/ns3-setup.png)

- 91 cell, 1 945 node được mô phỏng: những cell có mặt trong kế hoạch.
- 235 cặp gateway. 150 cặp phải dùng chung kênh với một cặp khác trong vòng 300 m, vì chỉ có 9 kênh.
- 20 cặp yếu, q < 0,5 (đoạn đỏ), do che khuất cố định của chính cặp đó. Đường liên cell bắt buộc đi qua chúng.
- Trong cell, ETX nhỏ nhất làm cây đường về CL có dạng ngôi sao: 57 % node gửi thẳng tới CL.

## Bước 1 — ngay sau lượt bay

![pass](figures/ns3-pass.png)

- Bitmap thu thật của pass ns-3 trên đường bay thẳng, lượt 1: |D| = 4 607 gói.
- CL một mình chỉ có khoảng 40–80 % D.
- Gộp cả cell thì gần đủ ở giữa River, thưa dần ra biên.

## Bước 2 — gom trong cell về CL

![gather](figures/ns3-gather.png)

- Chỉ những cell có vai trò mới gom: Axe, Bank, thành viên Circle, critical cell.
- Mỗi cell gom đúng phần nó cần.
- Khung gom cuối cùng tới CL lúc 17,0 s. Lâu nhất là các critical cell, vì chúng gom toàn bộ D.

## Bước 3 — sau khi gom: Bank → Circle → critical cell

![flows](figures/ns3-flows.png)

- **Axe → Bank: 0 khung.** Với River rộng 3,5 cell, Bank đã có đủ phần của Axe ngay sau khi gom.
- **River:** dữ liệu chảy dọc River từ Bank tới các thành viên Circle (vàng), rồi chặng cuối ngắn vào critical cell (đỏ).
- **Kéo thẳng:** mọi gói đi suốt từ Axe tới critical cell. Các đường đỏ dài chồng lên nhau ở giữa cụm.

![snapshots](figures/ns3-snapshots.png)

Phần D mà CL của mỗi cell có tại t = 0, 5, 10, 20 s và lúc kết thúc. Critical cell sẫm dần tới đủ.
Các cell khác chỉ thay đổi khi chúng gom hoặc có gói đi qua để giữ lại.

## Bước 4 — critical cell đủ dữ liệu

![timeline](figures/ns3-timeline.png)

Thời điểm critical cell nhận đủ D, tính bằng giây sau khi UAV rời cụm (lượt 1):

| Critical cell | River (chuẩn bị sẵn) | River (khi được hỏi) | Kéo thẳng |
|---|---|---|---|
| CH (−3,2) | 5,8 | 5,6 | 6,1 |
| (−5,0) | 11,3 | 11,3 | 13,8 |
| (−5,1) | 11,2 | 11,2 | 11,4 |
| (−4,−1) | 13,2 | 12,9 | 14,4 |
| (1,−2) | 21,1 | 14,8 | 23,4 |
| (−1,5) | 23,5 | 34,2 | 43,7 |
| (−7,8) | 34,2 | 34,5 | 41,1 |

![phases](figures/ns3-phases.png)

**Khung truyền thành công:**
- River chuẩn bị sẵn: 65 k, trong đó Bank → Circle 36 k.
- River khi được hỏi: 57 k.
- Kéo thẳng: 92 k.

MAC bỏ cuộc 3–7 k lần tuỳ biến thể. Khung bị bỏ cuộc được giữ lại và gửi lại ở lượt sau của radio, nên cuối cùng không gói nào bị mất.

**Đọc sơ bộ (một lượt, chưa phải kết luận):**
- Trên lượt này, River (chuẩn bị sẵn) xong trước kéo thẳng ở cả 7/7 critical cell, và dùng ít hơn khoảng 29 % khung.
- Lấy khi được hỏi tiết kiệm khoảng 13 % khung so với chuẩn bị sẵn. Thời gian lẫn lộn: 4 cell gần như bằng nhau, (1,−2) nhanh hơn 6 s, (−1,5) chậm hơn 11 s. Critical cell thiếu gần hết, nên Circle vẫn phải lấy gần như toàn bộ.
- Ô xa nhất (−7,8) xong muộn nhất ở cả ba biến thể (34–41 s).

Bản trước của trang này dùng một mô hình suy hao riêng cho mỗi kênh, nên che khuất bị bốc lại theo
kênh. Mọi số và hình ở đây đã chạy lại với mô hình dùng chung.

## Biến thể: lưới 3 màu và River hẹp hơn (CLAUDE.md §8 mục 53)

![variants](figures/ns3-variants.png)

**Hai thay đổi được thử:**
- **Lưới 3 màu** (`--colours=3`):
  - cell (q, r) dùng kênh 11 + (q − r) mod 3, nên hai cell cùng kênh chỉ cách nhau 1 cell;
  - đổi lại, cặp gateway có 13 kênh (14–26) thay vì 9;
  - số cặp phải dùng chung kênh với một cặp trong vòng 300 m giảm từ 150 xuống khoảng 60.
- **River hẹp hơn** (`river_export.py --width 2.5`, file `docs/data/river-plan-w2.5.txt`):
  - trên lưới lục giác, độ rộng chỉ đổi theo bậc: 3,0 cho đúng kế hoạch của 3,5, và 2,0 cho đúng kế hoạch của 2,5;
  - vì vậy "hẹp hơn một chút" là W = 2,5: Bank cách Axe 1 cell thay vì 2, River còn 42 cell thay vì 58.

**Kết quả lượt 1** (số liệu: `docs/data/pilot53/`):

| Cấu hình | Critical cell cuối xong | Khung | Bank → Circle | MAC bỏ cuộc | Thời gian chạy thật |
|---|---|---|---|---|---|
| 7 màu, River 3,5, chuẩn bị sẵn | 34,2 s | 65,4 k | 36,2 k | 6,8 k | 96 s |
| 7 màu, River 2,5, chuẩn bị sẵn | 34,5 s | 69,3 k | 40,9 k | 7,7 k | 93 s |
| 3 màu, River 3,5, chuẩn bị sẵn | 34,5 s | 65,4 k | 36,2 k | 8,8 k | 233 s |
| 3 màu, River 2,5, chuẩn bị sẵn | 35,2 s | 69,3 k | 40,9 k | 7,5 k | 236 s |
| 7 màu, River 3,5, khi được hỏi | 34,5 s | 56,7 k | 33,9 k | 3,2 k | 71 s |
| 7 màu, River 2,5, khi được hỏi | 38,0 s | 61,1 k | 38,6 k | 3,6 k | 73 s |
| 3 màu, River 3,5, khi được hỏi | 35,9 s | 57,8 k | 33,9 k | 4,1 k | 191 s |
| 3 màu, River 2,5, khi được hỏi | 44,6 s | 60,8 k | 38,6 k | 4,4 k | 182 s |
| Kéo thẳng, 7 màu | 43,7 s | 91,6 k | — | 6,6 k | 118 s |
| Kéo thẳng, 3 màu | 46,2 s | 91,6 k | — | 8,0 k | 312 s |

**Đọc sơ bộ (một lượt, chưa phải kết luận):**
- **3 màu không nhanh hơn.** Ở mọi cấu hình, critical cell cuối xong bằng hoặc chậm hơn 7 màu (0,3–6,6 s), và MAC bỏ cuộc nhiều hơn ở 4/5 cặp so sánh. Cách giải thích hợp lý (chưa đo trực tiếp): node của hai cell cùng kênh chỉ cách nhau khoảng 100–350 m, vẫn trong tầm nghe. Khi đó lịch "một máy phát mỗi cell" không còn ngăn được va chạm giữa hai cell. Thời gian chạy thật tăng khoảng 2,5 lần cũng cho thấy mỗi khung tới được nhiều máy thu hơn. Thêm 4 kênh cho cặp gateway không bù được phần này.
- **River hẹp hơn tốn thêm khoảng 6–8 % khung, do Bank → Circle tăng khoảng 13 %.** Khi Bank sát Axe, Bank xa các critical cell hơn nên đường Bank → Circle dài hơn. Axe → Bank vẫn là 0 khung, vì Bank đã có đủ ngay sau khi gom, cả khi cách 1 cell lẫn 2 cell.
- Thời gian của từng critical cell lúc nhanh lúc chậm theo độ rộng. Ví dụ với 7 màu: (1,−2) mất 12,9 s ở W = 2,5 so với 21,1 s ở W = 3,5, nhưng ô cuối xong như nhau. Một lượt chưa đủ để tách tác động của độ rộng khỏi nhiễu.

