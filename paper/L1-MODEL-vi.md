# Lớp 1: mô hình tổng quát cho mục System Model

Lời gốc: CLAUDE.md §8 mục 110–114. Thay cho điểm vận hành công bố ở `L1-STATEMENT-vi.md` §10–11 và cho bản thử ở `L1-VECTOR-vi.md` §2–6. Các số công bố cũ (f = 0,1 %, TTR = 82,26 %) chỉ còn là tham khảo.

Mã: `uav-l2/tools/l1_model.py` (mô hình điểm), `uav-l2/tools/l1_rank.py` (cả nhiệm vụ).

## 1. Ý tưởng trong một đoạn

UAV mang tới mỗi cụm một **bộ manh mối**: vài ảnh tham chiếu của người cần tìm, gồm mặt, toàn thân ở vài góc, quần áo và đồ mang theo. Mỗi camera xử lý (camera của một critical cell) so những người nó đã ghi được với bộ manh mối, rồi chỉ gửi về **một con số**: người giống nhất của nó giống tới đâu. BS xếp các cell theo con số đó. Đội 2 bay tới từng cell theo thứ tự, mang **bộ tham chiếu đầy đủ** để xác minh chắc chắn. Pha 2 hoàn thành khi cell có điểm xác minh cao nhất đã được xác minh.

Lớp 1 không cố cải tiến xử lý ảnh. Nó chỉ cần một mô hình đủ đơn giản để trả lời hai câu hỏi của mạng:
- Mạng phải mang **bao nhiêu dữ liệu, tới đâu, trong bao lâu**?
- Khi dữ liệu tới **không đủ** hoặc **muộn**, thứ tự thăm của đội 2 kém đi bao nhiêu?

## 2. Các thành phần

### 2.1 Kho của camera
- Camera của critical cell c đã ghi trong khung thời gian truy vấn **M người đi qua**, mỗi người giữ một ảnh crop tốt nhất.
- Lúc ghi hình, camera đã biến mỗi crop thành một vector đặc trưng bằng mô hình của chính nó và lưu thành chỉ mục. So khớp về sau chỉ là tính cosine giữa các vector, không phải xử lý lại video.
- Không mô hình hoá ảnh của mục tiêu (mục 112): mọi crop là người lạ. Câu hỏi không phải "có mục tiêu không", mà là "cell nào đáng xác minh trước".

### 2.2 Bộ manh mối
BS soạn từ bộ tham chiếu đầy đủ R của mục tiêu một bộ L manh mối. Mỗi manh mối j là một ảnh, mang bốn thuộc tính:

| Thuộc tính | Ý nghĩa | Ví dụ |
|---|---|---|
| khía cạnh t(j) | phần nào của người: mặt, dáng toàn thân, bộ phận (quần áo, giày, túi, tóc) | mặt chính diện |
| kích thước F_j | số byte của file ảnh | 25 kB |
| độ nhận diện r_j | ảnh tham chiếu thể hiện đúng khía cạnh đó của mục tiêu tới đâu; **gần 1 nhưng không bằng 1** (mục 112) | ảnh mặt nhỏ hoặc nghiêng: thấp hơn; màu áo rõ: rất gần 1 |
| độ quan trọng w_j | **do BS chấm** (mục 114): khớp ở khía cạnh này nói lên bao nhiêu về danh tính | mặt cao; màu áo thấp, vì nhiều người mặc giống nhau |

Tổng kích thước bộ manh mối là Q = Σ F_j byte. UAV phát nó **một lần** cho mỗi cụm, không cần phát lặp, vì River giao trọn cho mọi critical cell.

### 2.3 Giá trị khớp giữa một crop và một manh mối
Gọi a_i,t ∈ [−1, 1] là độ giống thật của crop i với mục tiêu ở khía cạnh t (cosine tới "hướng thật" của khía cạnh đó trong không gian đặc trưng). Camera không biết a_i,t; nó chỉ đo được cosine với ảnh manh mối:

  m_ij = cos(crop i, manh mối j) ≈ r_j · a_i,t(j) + ε_ij,  ε_ij ~ N(0, (1 − a²)(1 − r_j²) / D)

Giải thích không cần công thức: ảnh manh mối là một bức ảnh gần đúng của mục tiêu. Vector của nó chỉ gần, chứ không trùng, hướng thật (r_j < 1). Vì vậy giá trị khớp là độ giống thật nhân với r_j, cộng một phần ngẫu nhiên nhỏ do chỗ chưa khớp. Phần ngẫu nhiên nhỏ đi khi r_j tiến về 1, và khi không gian đặc trưng có nhiều chiều hiệu dụng (D).

Lý do của công thức: tách mỗi vector đơn vị thành phần dọc hướng thật và phần vuông góc. Trong không gian nhiều chiều, phần vuông góc của hai ảnh khác nhau gần như vuông góc với nhau; tích vô hướng của chúng có trung bình 0 và phương sai khoảng 1/D.

### 2.4 Điểm của crop, điểm của cell và báo cáo
- Cell c đang giữ tập manh mối H_c (một file chỉ dùng được khi nhận đủ mọi gói của nó, mục 34).
- **Điểm của crop**, tính hai bước:
  1. **Ước lượng từng khía cạnh** t từ các manh mối của khía cạnh đó mà cell đang giữ:

     â_i,t = Σ_{j ∈ H_c, t(j) = t} w_j m_ij / Σ_{j ∈ H_c, t(j) = t} w_j r_j

     Chia cho r_j để bù phần ảnh tham chiếu chưa khớp hoàn toàn: crop giống tuyệt đối có â = 1.
  2. **Gộp các khía cạnh** có mặt trong H_c theo độ quan trọng của khía cạnh, W_t = tổng w_j của mọi manh mối thuộc t trong cả bộ:

     S_i = Σ_t W_t â_i,t / Σ_t W_t

  Như vậy độ quan trọng được giữ ở mức khía cạnh. Thiếu một góc dáng thì các góc dáng còn lại gánh phần của dáng. Thiếu hẳn một khía cạnh thì khía cạnh đó bị bỏ ra, phần còn lại được chia lại.
  Cách gộp một bước (chia chung cho tổng trọng số các manh mối đang giữ) làm lệch tỉ trọng khi chỉ giữ một phần: giữ 2 mặt + 2 dáng thì mặt chiếm 65 % thay vì 50 %. Tương quan với điểm xác minh khi đó chỉ 0,42 so với 0,51 của cách hai bước.
- **Điểm của cell:** S_c = max_i S_i, tức người giống nhất trong kho.
- **Báo cáo:** S_c (1 byte) và bitmap của H_c (2 byte với L ≤ 16). Báo cáo đi critical cell → CH → LoRa → BS. Bitmap cho BS biết điểm này đáng tin tới đâu.

Độ quan trọng làm đúng việc mục 113 nói: một người lạ mặc cùng màu áo khớp rất cao ở manh mối quần áo, nhưng manh mối đó nặng ít, nên người đó không vượt lên được nhờ quần áo.

### 2.5 Điểm xác minh và mục tiêu của pha 2
- Đội 2 mang tới **bộ tham chiếu đầy đủ** R (tệp lớn, khoảng 1 MB). Với R, camera đo được mọi khía cạnh một cách chính xác.
- **Điểm xác minh** của crop: U_i = Σ_t W_t a_i,t / Σ_t W_t, với W_t là tổng độ quan trọng của các manh mối thuộc khía cạnh t. Điểm xác minh của cell là U_c = max_i U_i.
- **Pha 2 hoàn thành khi cell c\* có điểm xác minh cao nhất đã được xác minh** (mục 114). Đội 2 vẫn thăm mọi cell đã báo về (mục 112–113).
- Như vậy, điểm pha 1 là một **ước lượng** của điểm xác minh. Ước lượng tốt khi cell giữ đủ manh mối, kém khi thiếu, nhất là khi thiếu khía cạnh nặng (mặt).

### 2.6 Từ báo cáo tới thứ tự thăm
- BS biết mô hình của mục 2.3–2.4: trọng số và độ nhận diện của các manh mối do chính nó soạn. Vì vậy với mỗi báo cáo (S_c, H_c), nó suy ra được phân phối của U_c: một phân phối chuẩn có trung bình và độ lệch hiệu chỉnh trước theo H_c. Thiếu manh mối thì độ lệch lớn hơn.
- Từ đó BS tính **p_c, xác suất cell c là c\***, dựa trên mọi thứ đã biết:
  - báo cáo của các cell đã gửi;
  - phân phối tiên nghiệm cho các cell chưa gửi;
  - điểm xác minh của các cell đội 2 đã thăm.
- **Quy tắc thăm (giữ như hiện tại, mục 112):** đội 2 xuất phát khi báo cáo đầu tiên về. Ở BS và sau mỗi lần xác minh, nó chọn cell đã biết, chưa thăm, có p_c / (thời gian bay + thời gian xác minh) lớn nhất. Điểm số trong quy tắc cũ nay được thay bằng xác suất p_c.

## 3. Lớp 1 cần gì từ mạng (giao diện với lớp 2 và 3)

| Lớp 1 cần | Do lớp nào quyết định | Trong giả lập |
|---|---|---|
| tập manh mối H_c ở mỗi critical cell | lớp 2 (đường bay qua cụm, độ dài Axe) và lớp 3 (River) | River giao bản sao manh mối đặt trên cửa sổ Q quanh CH; không hợp tác thì chỉ có phần cell tự nghe được |
| thời điểm cell có đủ H_c | lớp 3 | rời cụm + thời gian River của cell đó |
| thời điểm báo cáo tới BS | kênh phản hồi | khe LoRa của CH, 40 s một bản tin |
| thứ tự manh mối trong luồng phát | BS | xen kẽ khía cạnh (mục 113), xem dưới |

**Xếp xen kẽ (mục 113).**
- Mỗi khía cạnh được rải đều dọc luồng phát: mặt, dáng và bộ phận đan xen nhau.
- Một cell chỉ nghe được một đoạn luồng vẫn có đủ loại khía cạnh. Nếu xếp theo nhóm (hết mặt rồi tới dáng, rồi tới bộ phận), một đoạn luồng có thể chỉ toàn manh mối quần áo, loại mà người lạ cũng khớp cao.
- Với River, critical cell nhận trọn bộ nên thứ tự không đổi kết quả. Thứ tự chỉ có tác dụng khi giao không đủ: cụm có Axe ngắn hơn Q, hoặc khi không hợp tác.

**Ngân sách dữ liệu.** Q = 400 kB cần khoảng 4 040 gói 99 B, tức khoảng 2 km bay trên các cell Axe (một gói mỗi 0,5 m). Cụm có đường bay qua ngắn hơn chỉ nhận được phần đầu của luồng. BS biết trước điều này từ kế hoạch bay.

## 4. Tham số giả lập

| Tham số | Giá trị | Tình trạng |
|---|---|---|
| M (crop mỗi kho) | 223 | giữ từ `L1-STATEMENT-vi.md` §11 làm cỡ kho |
| Bộ manh mối | L = 12: 2 mặt × 24,9 kB, 4 dáng × 49,9 kB, 6 bộ phận × 24,9 kB; tổng 4 036 gói (vừa cửa sổ 400 kB = 4 041 gói) | thiết kế, nằm trong khoảng mục 93, 94, 99 (15–50 kB mỗi ảnh, 3–6 góc cộng các crop bộ phận) |
| Độ nhận diện r_j | mặt 0,80–0,90; dáng 0,88–0,95; bộ phận 0,95–0,99 | giả định kịch bản |
| Độ quan trọng w_j | mặt 4; dáng 2; bộ phận 2/3 (40 / 40 / 20 % tổng trọng số) | BS chấm, giả định |
| Độ giống của người lạ a | mặt N(0,10; 0,10); dáng N(0,35; 0,12); bộ phận N(0,45; 0,15) | giả định kịch bản |
| Người mặc giống | 2 % crop, a(bộ phận) ~ N(0,85; 0,05) | giả định kịch bản |
| Số chiều hiệu dụng D | 128 | giả định kịch bản |
| Đối sánh tại cell | 0,11 s (L = 12, M = 223, Pi 5 + Hailo‑8L) | `L1-STATEMENT-vi.md` §13 |
| Xác minh | ổn định 5 s + 1 MB unicast 72,9 s + đối sánh bộ R (20 ảnh) 0,18 s = 78,1 s | như baseline cũ; 1 MB vẫn là số tạm (mục 73) |

Các giá trị đánh dấu "giả định" là tham số kịch bản, không phải số đo. Chúng được chọn để hiện tượng có thật: khía cạnh mặt phân biệt tốt nhất, quần áo dễ khớp nhầm. Kết quả nên trình bày cùng phép quét độ nhạy (D, tỉ lệ người mặc giống, M).

**Hệ quả của bộ tham số, đo trên 3 200 camera mô phỏng** (32 cell mỗi bản đồ, `l1_model.py`):

"Nửa luồng" là các manh mối nằm trọn trong nửa đầu hoặc nửa sau của luồng phát, tính theo số gói: điều xảy ra với một cell chỉ tự nghe được một đoạn.

| Cell giữ | Manh mối (m = mặt, d = dáng, b = bộ phận) | Tương quan S_c với U_c | Cell đứng đầu pha 1 đúng là c\* | Hạng TB của c\* theo S |
|---|---|---|---|---|
| đủ 12 manh mối | m m d d d d b b b b b b | 0,88 | 54 % | 1,9 |
| nửa đầu luồng xen kẽ | m d d b b b | 0,75 | 41 % | 2,9 |
| nửa sau luồng xen kẽ | m d d b b b | 0,82 | 59 % | 2,3 |
| nửa đầu luồng xếp nhóm | m m d d | 0,51 | 29 % | 6,1 |
| nửa sau luồng xếp nhóm | d b b b b b b | 0,43 | 16 % | 9,0 |
| thiếu cả hai manh mối mặt | d d d d b b b b b b | 0,44 | 20 % | 8,2 |
| chỉ có manh mối bộ phận | b b b b b b | 0,04 | 4 % | 17,0 |
| đủ 12 manh mối nhưng trọng số đều (bỏ độ quan trọng) | như dòng đầu | 0,43 | 28 % | 8,9 |

Đọc bảng:
- Ngay cả khi đủ dữ liệu, pha 1 chỉ chọn đúng c\* khoảng một nửa số lần. Thứ tự thăm của đội 2 vì vậy vẫn quan trọng.
- Thiếu manh mối làm thứ tự hỏng nhanh, nhất là thiếu mặt.
- Xen kẽ cho nửa nào của luồng cũng gần bằng nhau và gần với đủ bộ. Xếp nhóm thì nửa nào cũng kém, vì mỗi nửa thiếu hẳn một khía cạnh.
- Hình `uav-l2/docs/figures/l1-model.png` (không chữ):
  - Hàng trên: luồng phát một bản sao, xếp nhóm (trên) và xen kẽ (dưới). Mỗi khối là một manh mối: rộng theo số gói, cao theo độ quan trọng; đỏ là mặt, xanh là dáng, vàng là bộ phận; màu càng đậm thì độ nhận diện càng gần 1. Dải xám là nửa đầu luồng.
  - Ô trái dưới: điểm pha 1 (ngang) so với điểm xác minh (dọc) của 3 200 cell mô phỏng; xanh đậm là đủ bộ, vàng là nửa sau luồng xếp nhóm; đường đứt là đường chéo.
  - Ô giữa dưới: tỉ lệ cell đứng đầu pha 1 đúng là c\*, theo thứ tự đủ bộ; hai nửa xen kẽ (xanh nhạt); hai nửa xếp nhóm (vàng); thiếu mặt (đỏ); trọng số đều (xám).
  - Ô phải dưới: phân bố hạng của c\* theo điểm pha 1 (1 tới 10, cột cuối là từ 10 trở đi); xanh đậm là đủ bộ, vàng là nửa sau luồng xếp nhóm.

## 5. Đại lượng đánh giá

- **T\*:** thời điểm xác minh xong c\*. Đây là đại lượng chính (mục 114).
- **Hạng của c\*:** số cell đội 2 đã xác minh tính tới c\*, kể cả c\*.
- **T_all:** thời điểm đội 2 thăm hết mọi cell và về BS.
- **Tỉ lệ trọng số manh mối cell giữ được** lúc báo cáo, với và không có River.

## 6. Giả định và giới hạn

- Mọi camera dùng chung một thang điểm đã hiệu chỉnh. Khác biệt giữa thiết bị (mục 88) chưa đưa vào; nếu cần, node chuẩn hoá điểm theo đám đông của chính nó trước khi gửi (`L1-VECTOR-vi.md` §3).
- Các khía cạnh của một người lạ độc lập với nhau, trừ nhóm mặc giống. Chưa mô hình góc nhìn của crop, ví dụ crop chụp từ sau thì không có mặt.
- BS biết đúng mô hình điểm khi hiệu chỉnh. Thực tế BS phải hiệu chỉnh trên dữ liệu thẩm định.
- Điểm xác minh coi như đo đúng tuyệt đối (bộ R đầy đủ).

## 7. Bản ngắn tiếng Anh cho paper (System Model, Layer 1)

> **Query matching at the edge.** The camera of each critical cell c holds an index of M person crops recorded in the query window, embedded at recording time. The BS distils the target's full reference set R into a clue set of L images; clue j shows one aspect t(j) of the target (face, body, part), has size F_j, a recognizability r_j ≲ 1 (how faithfully it renders that aspect) and an importance w_j assigned by the BS (how much a match on that aspect says about identity). Writing a_{i,t} for the unknown similarity of crop i to the target on aspect t, the cosine between crop i and clue j is m_{ij} ≈ r_j a_{i,t(j)} + ε_{ij}, with ε_{ij} ~ N(0, (1−a²)(1−r_j²)/D) for D effective embedding dimensions. A cell holding the clue subset H_c first estimates each aspect from its held clues, â_{i,t} = Σ_{j∈H_c, t(j)=t} w_j m_{ij} / Σ_{j∈H_c, t(j)=t} w_j r_j, then combines the aspects present by their importance, S_i = Σ_t W_t â_{i,t} / Σ_t W_t with W_t the total importance of aspect t in the clue set, and reports S_c = max_i S_i with the bitmap of H_c (three bytes) through its CH's LoRa uplink. Verification by team 2 brings R and measures U_c = max_i Σ_t W_t a_{i,t} / Σ_t W_t exactly. Phase 2 is complete once the cell c* with the highest U_c has been verified. The BS turns each report into a calibrated normal posterior of U_c, whose spread grows as clues are missing, computes the probability p_c that c is c*, and team 2 visits next the known cell with the largest p_c over flight plus verification time. The network decides H_c and the time it is reached: layers 2–3 must place the clue set, Q = Σ F_j bytes, at every critical cell, and the clues are broadcast with their aspects interleaved so that any stretch of the stream carries every aspect.
