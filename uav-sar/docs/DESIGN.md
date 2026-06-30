# UAV-SAR over PECEE — Tài liệu mô tả ý tưởng (reference)

> Project mới, làm lại từ đầu. **Không phụ thuộc CC2420** — chỉ dùng module ns-3
> chuẩn (lr-wpan, spectrum, mobility, energy, propagation, network, core).
> PECEE chỉ là **substrate tham khảo** (chia cell + CL/CGW), không phải đối tượng
> nghiên cứu. Tài liệu này chốt ý tưởng TRƯỚC khi code.

Cập nhật: 2026-06-30. Trạng thái: thiết kế đã thống nhất, **chưa hiện thực logic**.

---

## 1. Câu chuyện & mục tiêu

Tìm **1 người mất tích** trong vùng không hạ tầng (rừng/vườn quốc gia), không
sóng cellular. Mặt đất có sẵn mạng camera-node chạy edge-AI nhẹ, **mỗi node có
footage riêng**. Dữ liệu tìm kiếm = ảnh/mô tả người mất tích, nằm ở BS (ở rìa
vùng, xa). Không có đường ground→BS ngoài UAV.

**Mục tiêu nghiên cứu (1 câu):** dùng các **manh mối nhỏ để KHOANH VÙNG trước**,
rồi mới **điều dữ liệu lớn tới đúng vùng** — để đưa được **dữ liệu hoàn chỉnh đến
đúng node và được xác nhận, rồi báo về BS, nhanh hơn** so với cách không hợp tác.

**Không mô phỏng CV/AI.** Phát hiện chỉ là trigger; fragment là byte mờ. Trọng
tâm là **networking + điều phối UAV/độ tin cậy/airtime**.

---

## 2. Substrate PECEE (thuần, chỉ tham khảo — KHÔNG phải đóng góp)

PECEE thuần ở đây chỉ gồm:
- Node được chia theo **cell** (lưới hexagon).
- Mỗi cell bầu **Cell Leader (CL)** và **Cell Gateway (CGW)** để **routing
  trong cell và liên cell**.
- Coi như **đã thiết lập xong trước nhiệm vụ** (Phase 0). Mạng node **ổn định**
  trong thí nghiệm (không chết, không duty-cycle ở round này).

> Ghi chú quan trọng: code cũ tìm thấy trong lịch sử (`topology-helper` với
> `SelectCandidates`/`SelectDetectionNode`) là **cơ chế khoanh vùng thử nghiệm
> CŨ, làm khi chưa có đội UAV FAST** → **KHÔNG dùng lại**. Chỉ tham khảo phần
> chia cell + bầu CL (và bổ sung CGW) của PECEE thuần.

---

## 3. Vai trò UAV (2 đội)

| Đội | Mang | Bay | Nhiệm vụ |
|---|---|---|---|
| **FAST** | fragment **nhỏ, giàu nhận diện** (màu áo, vóc dáng…) | nhanh | (1) rải nhanh mảnh nhận diện khắp vùng; (2) **vừa bay vừa nghe** lời gọi của node; (3) **relay lời gọi về đội DATA** |
| **DATA** | fragment **lớn** (dữ liệu đầy đủ) | chậm, chắc | **KHÔNG nghe trực tiếp**. Chỉ hành động khi FAST relay lời gọi → bay tới vùng → **giao toàn bộ dữ liệu** để xác nhận |

- DATA bay chậm nên **không cần vừa bay vừa nghe ngóng** — việc nghe là của FAST.
- Cần **1 DATA UAV đáp ứng/lời gọi** (token claim chung) để khỏi nhiều UAV cùng lao tới.
- "Đổi role động" (story có nhắc) — để **ngỏ cho sau**, round này role cố định.

---

## 4. Cơ chế thống nhất chống "loạn gọi" — Cell Leader đại diện

Một nạn nhân có thể bị **nhiều node trong cùng vùng** cùng thấy → nếu node nào
cũng tự gọi UAV sẽ loạn. Cơ chế:

1. Node phát hiện manh mối → **báo lên Cell Leader của cell** (không tự gọi UAV).
2. CL **gộp/đối chiếu** manh mối từ các node trong cell (và xác nhận chéo với
   hàng xóm nếu cần).
3. **Chỉ CL được phát lời gọi UAV** — **1 lời gọi / cell** (đại diện vùng).

→ Đây chính là "cơ chế trao đổi/thống nhất" đã chốt. CL là đại diện duy nhất.

---

## 5. Luồng nhiệm vụ (đã thống nhất)

```
Phase 0  PECEE đã chia cell + bầu CL/CGW (cho trước).
Phase 1  BS chia ảnh thành fragment (nhỏ-nhận-diện + lớn-dữ-liệu),
         giao cho đội FAST (nhỏ) và đội DATA (lớn). UAV cất cánh.
Phase 2  FAST quét + broadcast mảnh nhận diện xuống các node.
Phase 3  Node đối chiếu footage (giả lập) → có manh mối → BÁO CL.
Phase 4  CL gộp manh mối của cell → phát 1 lời gọi (beacon) triệu hồi DATA.
Phase 5  FAST nghe được lời gọi → RELAY về đội DATA.
Phase 6  1 DATA UAV (claim) bay tới vùng → giao TOÀN BỘ dữ liệu cho node/CL
         → node XÁC NHẬN.
Phase 7  UAV truyền 1 GÓI NHỎ REPORT về BS  →  KẾT THÚC.
```

**Điểm dừng metric chính = lúc gói report nhỏ tới được BS** (cả vòng tròn).

---

## 6. Metrics

| Metric | Ý nghĩa |
|---|---|
| `timeToReportAtBS_s` | **CHÍNH** — từ start đến khi report nhỏ tới BS (cả vòng) |
| `timeToLocalize_s` | đến khi CL phát lời gọi (khoanh vùng xong) |
| `timeToCompleteData_s` | đến khi node nhận đủ data + xác nhận |
| `pdr`, `pktSent`, `pktRecv` | độ tin cậy + airtime (proxy năng lượng) |
| `beaconCount`, `custodyHandoffs` | overhead điều phối |
| `routeDeviation_m`, `uavEnergy` | chi phí bay |

`-1` = không đạt trong thời lượng mô phỏng.

---

## 7. Baselines (so sánh — chốt sau)

- **proposed**: FAST khoanh vùng → CL gọi → FAST relay → DATA giao đúng vùng → report.
- **nocoop**: multi-UAV quét + giao khắp nơi, không CL/không lời gọi (không khoanh vùng).
- **pure-uav**: UAV tự bay tìm, không có hỗ trợ WSN.

---

## 8. Tham số dự kiến (round-2)

| Tham số | Mặc định | Ghi chú |
|---|---|---|
| gridSize / spacing | 8–12 / 20 m | mật độ node |
| hex cell radius | 80 m | PECEE |
| numUav (FAST/DATA) | 4 (2/2) | sẽ quét nhiều cấu hình |
| numFrag / maxFragBytes | 8 / (100B–20KB) | nhỏ=nhận diện, lớn=dữ liệu |
| UAV broadcast radius | ~50 m | từ link budget LogDistance |
| A2G channel | LogDistance (round-2: tiến tới LoS/NLoS thực tế) | |
| seeds | ≥100 | thống kê |

---

## 9. Khác biệt so với round-1 (sửa theo phản hồi)

- **Bỏ** logic khoanh-vùng candidate/detection-node cũ.
- **CL đại diện gọi** (không phải mọi node beacon).
- **DATA không nghe trực tiếp**; chỉ qua relay của FAST.
- **Thêm chặng report nhỏ về BS** làm điểm kết thúc + metric chính.
- **Bỏ hẳn CC2420**; chỉ ns-3 chuẩn + lr-wpan.
- PECEE = substrate tham khảo (cell + CL + CGW), không phải đối tượng nghiên cứu.

---

## 10. Phạm vi round này (chưa làm)

Tài liệu này **chỉ chốt ý tưởng + dựng skeleton project**. Chưa hiện thực logic
mô phỏng. Bước kế: hiện thực PECEE-substrate (cell/CL/CGW tham khảo) → FAST/DATA
apps → CL coordination → report-to-BS → metrics → batch + visualizer.
