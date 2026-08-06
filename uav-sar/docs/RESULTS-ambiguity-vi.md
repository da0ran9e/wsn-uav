# Kết quả: nhập nhằng khử được, và điều đó thay đổi mọi thứ

16×16, `senseSigma=0.10`, `gpsSigma=5`, `victimOnNode=0`, scheme `proposed`,
**N = 120 hạt giống mỗi nhánh**, một binary duy nhất (đã kiểm bằng
`assert_one_build` + `assert_one_clutter`). Nhập nhằng: **M = 2** vật gây nhầm,
độ tương đồng **s = 0.9**.

| nhánh | phục vụ nạn nhân | **đúng người** | sai số median | sai số p90 | thời gian | năng lượng | gói tin |
|---|---:|---:|---:|---:|---:|---:|---:|
| **A** `clutterResolve=1`, 4 UAV | 90.0 % | **100.0 %** | 14.9 m | 34.3 m | 104.5 s | 68.6 kJ | 4 090 |
| **B** `clutterResolve=0` (ablation) | 44.2 % | **46.7 %** | 143.9 m | 254.6 m | 103.6 s | 63.9 kJ | 5 768 |
| **C** A + 1 UAV DATA (5 UAV) | **93.3 %** | 100.0 % | **13.3 m** | **26.0 m** | 104.5 s | 82.3 kJ | 4 342 |
| **D** không có vật gây nhầm | 95.8 % | 100.0 % | 14.6 m | 28.7 m | 104.0 s | 68.0 kJ | 4 038 |

---

## 1. Cơ chế khử nhập nhằng hoạt động — hoàn toàn

**0/120 run đóng vòng vào nhầm người** (nhánh A). So với nhánh B, nơi nhập nhằng
sống sót qua việc giao dữ liệu: 46.7 %.

Đây là hệ quả trực tiếp của việc sửa tiền đề mô hình. Trước đó tôi coi nhập nhằng
là **cố định**, và kết luận rằng trần khả phân biệt $1/(M{+}1)$ chặn toàn bộ
nhiệm vụ. Kết luận đó **sai**, và nó sai vì mô hình sai: nút chấm điểm bằng mảnh
cue thì không phân biệt được, nút giữ **toàn bộ** tập tham chiếu thì phân biệt
được. Trần $1/(M{+}1)$ chỉ áp cho **lần nhắm đầu tiên**, không áp cho nhiệm vụ —
vì hệ thống có thể **trả tiền để biết thêm**: bay tới, giao dữ liệu, nghe REJECT,
nhắm lại.

Cần nói rõ điều này vào bài báo, vì nó là điểm mạnh thật sự của kiến trúc vòng
kín: **một hệ mở vòng không có cách nào làm được như vậy.** Nó rải dữ liệu rồi
bay đi, không bao giờ biết mình đã phục vụ ai.

## 2. Nhập nhằng gần như MIỄN PHÍ khi nó khử được

So A với D (không có vật gây nhầm nào):

| | phục vụ | sai số median | sai số p90 | năng lượng |
|---|---:|---:|---:|---:|
| D — không nhập nhằng | 95.8 % | 14.6 m | 28.7 m | 68.0 kJ |
| A — 2 vật gây nhầm, s = 0.9 | 90.0 % | 14.9 m | 34.3 m | 68.6 kJ |

Hai vật thể gần-như-giống-hệt trong vùng tìm kiếm tốn **5.8 điểm phần trăm độ tin
cậy** và **gần như không tốn độ chính xác**. Sự sụp đổ thảm khốc đo được trước đây
(34–56 % phục vụ, sai số median 162 m) **hoàn toàn là hệ quả của giả thiết rằng
nhập nhằng không khử được** — chứ không phải của nhập nhằng.

## 3. Khử nhập nhằng còn TIẾT KIỆM gói tin

Nhánh B tốn **5 768** gói so với **4 090** của A — nhiều hơn 41 %. Nhập nhằng
không được giải quyết thì hệ thống cứ nhắm lại, phát lại beacon, giao lại. Đây là
kết quả phản trực giác đáng đưa vào bài: **khả năng nhận ra mình đã sai là một cơ
chế tiết kiệm chi phí, không phải một tính năng phụ trội.**

(Nhánh B tốn ít năng lượng hơn một chút, 63.9 vs 68.6 kJ, vì nhiều run của nó kết
thúc sớm bằng thất bại chứ không phải bằng thành công. Đó là bẫy survivorship —
đọc cột "phục vụ nạn nhân" trước, đừng đọc cột năng lượng một mình.)

## 4. Thêm một UAV DATA: mua độ tin cậy và đuôi phân phối bằng năng lượng

Nhánh C so với A (2 FAST + 3 DATA thay vì 2 + 2):

| | A (4 UAV) | C (5 UAV) | thay đổi |
|---|---:|---:|---|
| phục vụ nạn nhân | 90.0 % | 93.3 % | **+3.3 pp** |
| sai số p90 | 34.3 m | 26.0 m | **−24 %** |
| lần nhắm lại / run | 0.31 | 0.23 | −26 % |
| năng lượng | 68.6 kJ | 82.3 kJ | **+20 %** |
| gói tin | 4 090 | 4 342 | +6 % |

Đổi 20 % năng lượng lấy 3.3 pp độ tin cậy và 24 % đuôi sai số. Đây là một điểm
trên đường cong đánh đổi (P6), **không** phải một cải tiến miễn phí — và nó nên
được trình bày như một điểm trên đường cong đó chứ không phải như "cấu hình tốt
hơn".

Đáng chú ý: C vượt cả D (93.3 % với 2 vật gây nhầm, so với 95.8 % khi không có
vật nào) — tức là **thêm một khung bay bù lại được phần lớn cái giá của nhập
nhằng**.

## 5. Rải cue trên đường bay: tốn radio, không tốn giờ bay — đúng như thiết kế

D (95.8 % phục vụ, 68.0 kJ, 4 038 gói) so với số đã công bố trước đây cùng điều
kiện M = 0 (92.5 %, 68.3 kJ, 3 471 gói):

- **năng lượng không đổi** (68.0 vs 68.3 kJ) — đúng tính chất đã thiết kế: cue
  được rải trên các chặng **đang bay sẵn**, nên không có giá giờ bay.
- gói tin **+16 %** — đó là giá phải trả, bằng radio.
- phục vụ nạn nhân **+3.3 pp**.

**Cảnh báo quy kết:** hai thay đổi bị gộp trong nhánh D (rải cue trên đường bay,
và tiêu chí đóng vòng chặt hơn), nên **không được quy 3.3 pp cho riêng cái nào**
nếu chưa chạy ablation tách. Điều duy nhất kết luận được là hướng của nó khớp với
dự đoán của bản sửa đóng vòng: người ngoài cuộc dưới điểm thả không còn kết thúc
nhiệm vụ thay cho nạn nhân được nữa.

## 6. Hai vấn đề mở đã đóng

- **Vấn đề mở số 2** (tiêu chí CONFIRM sai về nguyên tắc): đã sửa. Giữ dữ liệu
  không còn đủ để xác nhận — nút phải giữ **và vẫn khớp**. Hướng số đo khớp với
  dự đoán (§5).
- **Vấn đề mở số 5** (hàng rào build yếu hơn quảng cáo): đã sửa, `config.txt` ghi
  `binary=<mtime>,<size>` của `/proc/self/exe`. Việc đổi mặc định `dataPatrol`
  chính là ca thử: nó đổi hành vi mà không đụng `sar-metrics.cc`, nên dấu cũ vẫn
  y nguyên và hàng rào cũ đã cho qua.

## 7. Thí nghiệm tiếp theo — và đây là thí nghiệm quyết định bài báo

Chưa chạy `closed-loop` dưới nhập nhằng ở N = 120. Đó **chính là** giả thuyết H ở
`PROBLEM-MULTI-CANDIDATE-vi.md` §11, và giờ nó sắc hơn nhiều so với lúc phát biểu:

> `closed-loop` cũng nhận được REJECT (nút của nó cũng khử được nhập nhằng khi đủ
> dữ liệu), nên nó **không** thua ở chỗ nhận ra sai. Nó thua ở chỗ **xếp hạng ứng
> viên nào đáng đi trước** — vì không có tầng gộp bằng chứng, nó không phân biệt
> được "5 nút quanh $c_1$ cùng báo 0.8" với "1 nút lẻ ở $c_2$ báo 0.78".

Dự đoán kiểm chứng được: dưới nhập nhằng, `proposed` sẽ **giao nhầm ít lần hơn**
`closed-loop`, và vì mỗi lần giao nhầm tốn $2d/V + s$ giây, khoảng cách chi phí
0/120 hiện tại có thể đảo chiều. Nếu không đảo, ta biết chắc hợp tác chỉ mua được
độ chính xác — cũng là một kết luận sạch.
