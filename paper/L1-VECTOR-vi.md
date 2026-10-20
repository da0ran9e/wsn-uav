# Lớp 1 bằng điểm cosine của từng ảnh (CLAUDE.md §8 mục 110)

Thay cho: điểm vận hành công bố ở `L1-STATEMENT-vi.md` §10–11. Các số công bố ([7], f = 0,1 %, TTR = 82,26 %) giờ chỉ là **một điểm tham chiếu** để đối chiếu giả lập, không còn là đầu vào của mô hình hệ thống.

Mã thử: `uav-l2/tools/l1_vector.py`. Số liệu: `uav-l2/docs/data/l1/vector.csv`. Log: `logs/2026-10-20_1614-l1-vector/`.

## 1. Vì sao đổi

- f và TTR của [7] gắn với kịch bản của [7]: bộ Market‑1501, cùng 6 camera, mục tiêu có trong tập huấn luyện.
- Kịch bản của ta khác: nhiều thiết bị khác nhau, camera khác miền, số người mặc giống mục tiêu thay đổi theo nơi.
- Một mô hình bắt đầu từ **điểm của từng ảnh** mô tả được các khác biệt đó bằng tham số. Tỉ lệ bỏ sót và báo nhầm khi đó là **kết quả** của mô hình, không phải đầu vào.

## 2. Mô hình

**Vector và điểm.**
- Mỗi ảnh x được node biến thành vector đơn vị f(x).
- BS gửi L ảnh signature r_1..r_L. Điểm của một crop là độ giống nhất với signature: s(x) = max_j cos(f(x), f(r_j)).
- Ảnh tham chiếu so với chính nó có s = 1, là đầu trên của thang điểm.

**Ba loại crop trong kho của một camera** (M crop trong khung thời gian truy vấn):

| Loại | Điểm (đơn vị chuẩn hoá, người lạ: trung bình 0, độ lệch 1) | Tham số kịch bản |
|---|---|---|
| Người lạ | z ~ N(0, 1) | |
| Người mặc giống mục tiêu | z ~ N(μ_L, 1), mỗi crop với xác suất ρ | ρ, μ_L |
| Mục tiêu (chỉ ở camera thật, k lượt) | z ~ N(d′, 1) | d′ (độ tách), k |

**Thiết bị và cảnh** biến đổi điểm của cả camera: s = a_c·z + b_c, với a_c (co giãn) và b_c (dịch) riêng từng camera.
- Đây chính là chuyện "cùng một ảnh, thiết bị này cho 70 %, thiết bị kia 75 %" ở mục 88.
- Có thể thêm nhiễu lượng tử hoá của NPU vào từng điểm.

**Kịch bản được mô tả bằng (d′, ρ, μ_L, a_c, b_c, k, M), không bằng số của một bài báo.**
- [7] tương ứng khoảng d′ ≈ 4,4 (độ lệch của mục tiêu ≈ 1,3) trong cách khớp hai phân phối chuẩn ở §8 của `L1-STATEMENT-vi.md`.
- Đó chỉ là một điểm trên trục d′, dùng để đối chiếu.

**Hai mức giả lập:**
- **Mức điểm (đang dùng):** bốc thẳng s cho từng crop như bảng trên. Nhanh, dễ giải thích.
- **Mức vector (sau):** mỗi người một vector gốc; người mặc giống là vector gần vector mục tiêu; mỗi crop = vector gốc + lệch theo góc nhìn + nhiễu camera; node tính cosine thật.
  - Mức này tự sinh ra tương quan giữa các crop của cùng một người.
  - Nó cũng tự sinh ra ảnh hưởng của góc nhìn: thiếu signature đúng góc thì điểm thấp hơn. Vì vậy nó mô tả được việc nhận thiếu ảnh signature khi lớp 3 giao không đủ.

## 3. Cơ chế tại node: xếp hạng, không đặt ngưỡng

```
Node(c):                                   // khi L ảnh signature đã đủ
  for each crop i in index (M crops):  s_i ← max_j cos(f_i, f(r_j))
  sort s descending                        // danh sách ưu tiên
  z_i ← (s_i − median(s)) / (1.4826 · MAD(s))   // so với đám đông của chính camera
  report (c, z_(1), z_(2), z_(3))          // 3 điểm đầu, mỗi điểm 1 byte: vài byte qua CH và LoRa
```

- **Không đặt ngưỡng ở node**, nên không còn câu hỏi "lấy ngưỡng nào từ bài báo nào".
- **Chuẩn hoá theo đám đông của chính camera** (median, MAD) triệt tiêu a_c và b_c: thứ tự trong một camera không đổi qua biến đổi tuyến tính, và z không phụ thuộc thang điểm của thiết bị.
- **Gửi 3 điểm đầu thay vì 1:** cell thật có k crop cao; cell chỉ có một người mặc giống thường có 1 crop cao.

## 4. Cơ chế tại BS: xếp hạng các cell

```
BS:
  for each reporting cell c:  q_c ← g(z_(1), z_(2), z_(3))   // ví dụ max z, hoặc trung bình 3 điểm
  rank cells by q_c → danh sách nghi vấn
  team 2 thăm theo thứ tự (điểm / thời gian bay), dừng khi gặp cell thật
```

- Giả định "1 nghi vấn thật + 2–3 nghi vấn giả" của giả lập nhiệm vụ được thay bằng **toàn bộ bảng xếp hạng**. Số cell giả phải thăm là kết quả của mô hình.
- **Đại lượng chính: hạng R\* của cell thật.**
  - Số cell giả bị thăm là R\* − 1, thay cho "báo nhầm".
  - Bỏ sót là khi R\* lớn hơn số lần thăm đội 2 làm được (ngân sách B).
  - Kỳ vọng E[R\*] cho số lần thăm trung bình, và từ đó cho thời gian nhiệm vụ.

## 5. Bản thử (`l1_vector.py`, 2 000 lần bốc mỗi cấu hình)

**Thiết lập:**
- 32 critical cell trên một bản đồ, M = 223 crop mỗi camera.
- Người mặc giống: μ_L = 2,5, ρ ∈ {0; 2 %}.
- Thiết bị: a_c ~ U(0,8; 1,2) và b_c ~ N(0; τ), với τ ∈ {0; 0,5}.
- d′ ∈ {3; 4; 5}, k ∈ {1; 3}.
- Ba cách xếp hạng ở BS: điểm thô s_(1); z_(1) đã chuẩn hoá; trung bình 3 điểm đầu đã chuẩn hoá.

Các giá trị μ_L, ρ, τ và khoảng của a_c là **tham số kịch bản tôi chọn để thử**, không phải số đo.

Tỉ lệ cell thật đứng **đầu** bảng (trong 3 đầu), d′ = 4:

| Thiết bị | Người mặc giống | k | Điểm thô | z_(1) | TB 3 điểm đầu |
|---|---|---|---|---|---|
| giống nhau (τ = 0) | không | 3 | **91 %** (98 %) | 83 % (94 %) | 88 % (97 %) |
| lệch (τ = 0,5) | không | 3 | 65 % (82 %) | 84 % (95 %) | **87 % (96 %)** |
| lệch | 2 % | 3 | 24 % (45 %) | 29 % (55 %) | **42 % (69 %)** |
| lệch | 2 % | 1 | 12 % (27 %) | **15 % (31 %)** | 12 % (28 %) |
| lệch | không | 1 | 40 % (58 %) | **53 % (70 %)** | 36 % (56 %) |

Hạng trung bình của cell thật ở dòng thứ ba (thiết bị lệch, 2 % mặc giống, k = 3): 6,5 / 4,9 / 3,7.

**Đọc kết quả:**
- **Thiết bị lệch nhau làm điểm thô xếp hạng sai:** từ 91 % tụt còn 65 % đứng đầu. Điểm đã chuẩn hoá không bị ảnh hưởng (83–88 % dù thiết bị giống hay lệch), đổi lại thấp hơn điểm thô vài điểm khi mọi thiết bị giống hệt nhau. Thực tế thiết bị không giống nhau, nên node nên gửi z thay vì cosine thô.
- **Người mặc giống là khó khăn lớn nhất.** 2 % người mặc giống, tức khoảng 4–5 người trong 223 crop, đủ kéo tỉ lệ đứng đầu từ 84–88 % xuống còn 29–42 %.
- **Gửi nhiều điểm giúp khi mục tiêu đi qua nhiều lần (k = 3)**, nhưng làm loãng khi k = 1. Vì không biết trước k, node nên gửi cả 3 điểm và BS dùng một hàm kết hợp, ví dụ tỉ số hợp lý theo mô hình. Phần này chưa cài.
- **Kết quả phụ thuộc mạnh vào độ tách d′.** Với k = 3 và trung bình 3 điểm đầu, d′ = 5 cho ≥ 83 % đứng đầu ở mọi tổ hợp thiết bị và người mặc giống; d′ = 3 cho tối đa 55 %. Vì vậy paper nên trình bày theo trục d′ thay vì một con số.

## 6. Chỗ cần chốt trước khi đưa vào giả lập nhiệm vụ

1. **Hàm kết hợp g ở BS:** max z, trung bình 3 điểm đầu, hoặc tỉ số hợp lý theo mô hình.
2. **Số điểm gửi về (n = 3?) và số bit mỗi điểm** (8 bit là đủ cho thứ hạng).
3. **Lưới kịch bản:** d′, ρ, μ_L, τ và khoảng a_c, M, k. Đề xuất trình bày kết quả theo d′ ∈ {3; 4; 5}, ρ ∈ {0; 1; 2 %}.
4. **Nối vào giả lập nhiệm vụ:** thay bước bốc nghi vấn trong `mission_policy.py` bằng bảng xếp hạng này. Mỗi lần bốc sinh điểm cho mọi critical cell, đội 2 thăm theo hạng và dừng ở cell thật. Từ đó có trực tiếp thời gian nhiệm vụ, số lần thăm giả và tỉ lệ bỏ sót theo ngân sách B.
5. **Mức vector** (góc nhìn, tương quan crop, signature thiếu): để sau khi mức điểm đã chốt.
