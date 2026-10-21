# Lớp 1: đối sánh truy vấn tại nút xử lý — mô hình hệ thống

Lời gốc: CLAUDE.md §8 mục 110–114 (mô hình) và 118 (cách viết). Mã: `uav-l2/tools/l1_model.py` (mô hình điểm, hiệu chỉnh, xác suất), `uav-l2/tools/l1_rank.py` (thời gian và quy tắc thăm). Bản này thay bản ngày 2026‑10‑20; nội dung mô hình không đổi, cách trình bày và ký hiệu được viết lại cho mục System Model của bài báo. Các nguồn đánh số [n] ở §8.

---

## 1. Bối cảnh và phạm vi

Hệ thống tìm một người (*mục tiêu*) trong một vùng đô thị phủ bởi nhiều camera IoT đã ghi hình sẵn. Dữ liệu thô không được tải về. BS (trạm gốc) gửi tới vùng một *truy vấn*: một tập nhỏ ảnh tham chiếu của mục tiêu. Các camera tự so khớp tại chỗ với những gì chúng đã ghi.

Nhiệm vụ chia làm hai pha:
- **Pha 1 (giao truy vấn).** Một UAV cánh bằng bay qua từng *cluster* (cụm nút mặt đất) và phát truy vấn. Mạng mặt đất chuyển truy vấn tới các *nút xử lý* (lớp 2 và lớp 3). Mỗi nút xử lý đối sánh và gửi một báo cáo ngắn về BS qua kênh tầm xa tốc độ thấp.
- **Pha 2 (xác minh).** Một UAV cánh quay tới từng nút xử lý theo thứ tự BS đề xuất. Nó mang *bộ tham chiếu đầy đủ* để xác minh chắc chắn.

**Lớp 1** là mô hình nối hai pha. Từ việc mỗi nút xử lý *nhận được phần nào của truy vấn, vào lúc nào*, nó cho biết BS *xếp hạng các nút đúng tới đâu*, và do đó pha 2 tìm ra nút đáng xác minh nhất *nhanh tới đâu*.

Bài báo không đóng góp về xử lý ảnh. Lớp 1 dùng một mô hình tổng quát dựa trên độ giống cosine giữa các vector đặc trưng, là cách mà các hệ nhận dạng mặt và tái nhận dạng người (re‑ID) hiện đại đều dùng [1]–[5]. Mô hình chỉ giữ lại những gì ảnh hưởng tới mạng:
- lượng dữ liệu phải giao và cách tổ chức nó;
- độ tin cậy của điểm khi dữ liệu giao về thiếu hoặc muộn;
- thời gian xử lý tại nút và thời gian xác minh.

## 2. Thực thể và khái niệm

- **Mạng mặt đất.** Các nút nằm trên lưới ô lục giác (*cell*) bán kính R = 100 m. Mạng chia thành K *cluster*, mỗi cluster có một *cluster head* (CH). Mỗi cell có một nút đại diện (CL), là nút mạnh nhất trong cell.
- **Nút xử lý và critical cell.** Chỉ một số ít cell có camera đủ mạnh để đối sánh. Đó là cell của CH, cộng các cell có CL vượt trội so với toàn cluster hoặc so với vùng quanh nó. Các cell này gọi là *critical cell*; tập của mọi critical cell là 𝒞, của cluster k là 𝒞_k. Chúng được chọn trước nhiệm vụ.
- **Cửa sổ truy vấn.** Khoảng thời gian mục tiêu có thể đã xuất hiện. Camera của critical cell c đã ghi trong cửa sổ đó M người đi qua, và giữ mỗi người một ảnh cắt (*crop*) tốt nhất.
- **Khía cạnh.** Phần nào của người được dùng để so: *mặt*, *dáng toàn thân* (re‑ID) hay *bộ phận* (quần áo, giày, túi, tóc). Tập khía cạnh là 𝒱 = {mặt, dáng, bộ phận}.
- **Mô hình đặc trưng.** Mỗi khía cạnh có một mô hình biến ảnh thành một vector đơn vị trong không gian đặc trưng. Ví dụ: mô hình nhận dạng mặt cho vùng mặt [1], [2], mô hình re‑ID cho cả người [3], [5], và mô hình thuộc tính cho vùng quần áo [15]. Camera đã tính vector cho mọi crop ngay lúc ghi và lưu thành *chỉ mục*. Khi truy vấn tới, so khớp chỉ là tính tích vô hướng, không phải xử lý lại video.
- **Bộ tham chiếu đầy đủ R.** Mọi ảnh rõ nét của mục tiêu mà BS có, khoảng 1 MB. Chỉ đội 2 mang R tới nút, khi xác minh.
- **Bộ manh mối (truy vấn).** L ảnh do BS trích từ R. Mỗi ảnh cho thấy một khía cạnh của mục tiêu. Đây là thứ pha 1 giao tới mọi critical cell.
- **Người lạ, người mặc giống.** Không mô hình hoá ảnh của chính mục tiêu (mục 112): mọi crop trong kho đều là người lạ. Một phần nhỏ người lạ mặc giống mục tiêu. Câu hỏi của pha 2 không phải "mục tiêu có ở đây không", mà là *nút nào đáng xác minh trước*.

## 3. Ký hiệu

| Ký hiệu | Ý nghĩa | Miền, đơn vị |
|---|---|---|
| K, k | số cluster, chỉ số cluster | |
| 𝒞, 𝒞_k, c | tập critical cell (toàn mạng, của cluster k), một critical cell | |
| M, i | số crop trong kho của một camera, chỉ số crop | |
| 𝒱, v | tập khía cạnh {mặt, dáng, bộ phận}, một khía cạnh | |
| L, j | số manh mối, chỉ số manh mối | |
| v(j) | khía cạnh của manh mối j | 𝒱 |
| F_j, n_j | kích thước manh mối j; số gói của nó | byte; gói |
| B | tải tin hữu ích của một gói | 99 byte |
| Q | tổng số gói của bộ manh mối, Q = Σ_j n_j | gói |
| r_j | độ nhận diện của manh mối j | (0, 1), gần 1 |
| w_j | độ quan trọng của manh mối j, do BS chấm | > 0 |
| W_v | độ quan trọng của khía cạnh v, W_v = Σ_{j: v(j)=v} w_j | |
| d | số chiều hiệu dụng của không gian đặc trưng | |
| μ_v | hướng của mục tiêu ở khía cạnh v trong không gian đặc trưng | vector đơn vị |
| a_{i,v} | độ giống thật của crop i với mục tiêu ở khía cạnh v | [−1, 1] |
| m_{ij} | giá trị khớp (cosine) giữa crop i và manh mối j | [−1, 1] |
| H_c | tập manh mối cell c đang giữ trọn vẹn | ⊆ {1, …, L} |
| â_{i,v} | ước lượng của a_{i,v} từ các manh mối đang giữ | |
| S_i, S_c | điểm của crop i; điểm của cell c, S_c = max_i S_i | |
| U_i, U_c | điểm xác minh của crop i; của cell c | |
| c\* | critical cell có điểm xác minh cao nhất | |
| ā_v, σ_v | trung bình, độ lệch của a_{i,v} ở người lạ | |
| ρ; ā_ℓ, σ_ℓ | tỉ lệ người mặc giống; trung bình, độ lệch của a_{i,bộ phận} ở họ | |
| b⁰_H, b¹_H, σ_H | hệ số hiệu chỉnh và độ lệch dư của BS cho tập manh mối H | |
| f_0, F_0 | mật độ và hàm phân phối tiên nghiệm của U_c | |
| p_c(t) | xác suất cell c là c\*, theo thông tin BS có tại thời điểm t | [0, 1] |
| P_U(t), n_0(t) | xác suất c\* nằm trong các cell chưa báo; số cell chưa báo | |
| τ_m, τ_v | thời gian đối sánh tại nút; thời gian xác minh của đội 2 | s |
| G, φ_k, T_air | chu kỳ khe LoRa; pha khe của CH cluster k; thời gian phát một bản tin | s |
| V_2, β | tốc độ đội 2; ngưỡng chờ của đội 2 | m/s; — |
| T\* | thời điểm xác minh xong c\* (chỉ số chính) | s |

Ở các lớp khác, chữ D là tập gói một cluster nhận được (lớp 2–3). Vì vậy ở đây số chiều hiệu dụng viết là d thường.

## 4. Mô hình

### 4.1 Độ giống trong không gian đặc trưng

Mô hình đặc trưng biến mỗi ảnh x thành vector đơn vị f(x) trên mặt cầu 𝕊^{d−1}. Độ giống giữa hai ảnh là cosine giữa hai vector, cũng là tích vô hướng của chúng [1]–[3]:

$$\operatorname{sim}(x, y) = \langle f(x), f(y) \rangle \in [-1, 1]. \tag{1}$$

Gọi μ_v là hướng "thật" của mục tiêu ở khía cạnh v. Vector của crop i và vector của manh mối j tách được thành phần dọc μ_v và phần vuông góc:

$$f(x_i) = a_{i,v}\,\mu_v + \sqrt{1 - a_{i,v}^2}\;\nu_{i,v}, \qquad \nu_{i,v} \perp \mu_v,\ \lVert \nu_{i,v} \rVert = 1, \tag{2}$$

$$f(y_j) = r_j\,\mu_{v(j)} + \sqrt{1 - r_j^2}\;\zeta_j, \qquad \zeta_j \perp \mu_{v(j)},\ \lVert \zeta_j \rVert = 1. \tag{3}$$

Ở (2), a_{i,v} = ⟨f(x_i), μ_v⟩ là *độ giống thật* của crop với mục tiêu. Ở (3), r_j = ⟨f(y_j), μ_{v(j)}⟩ là *độ nhận diện* của manh mối: ảnh tham chiếu thể hiện khía cạnh của mục tiêu trung thành tới đâu. Ảnh mặt chính diện, rõ nét có r_j gần 1; ảnh mặt nhỏ hay nghiêng có r_j thấp hơn. Vì ảnh nào cũng chỉ là một lần chụp, r_j < 1 (mục 112).

Nhân (2) với (3), và vì ν_{i,v} ⊥ μ_v, ζ_j ⊥ μ_v:

$$m_{ij} = \langle f(x_i), f(y_j) \rangle = r_j\,a_{i,v(j)} + \sqrt{(1 - a_{i,v(j)}^2)(1 - r_j^2)}\;\langle \nu_{i,v(j)}, \zeta_j \rangle. \tag{4}$$

Phần vuông góc của hai ảnh khác nhau không có liên hệ gì với nhau. Coi ζ_j như một hướng ngẫu nhiên đều trên mặt cầu đơn vị của phần bù trực giao của μ_v, có số chiều d − 1. Khi đó ⟨ν, ζ⟩ có trung bình 0 và phương sai 1/(d − 1), và gần phân phối chuẩn khi d lớn [6], [7]. Vậy với d lớn:

$$m_{ij} = r_j\,a_{i,v(j)} + \varepsilon_{ij}, \qquad \varepsilon_{ij} \sim \mathcal{N}\!\left(0,\ \frac{(1 - a_{i,v(j)}^2)(1 - r_j^2)}{d}\right). \tag{5}$$

Các ε_{ij} của cùng một crop với các manh mối khác nhau là không tương quan, vì các ζ_j độc lập với nhau. Số chiều danh nghĩa của vector đặc trưng (512 hoặc 2 048) lớn hơn nhiều số chiều mà dữ liệu thật sự trải ra [8]. Vì vậy d trong (5) là *số chiều hiệu dụng*, một tham số được quét độ nhạy (§6).

Ý nghĩa của (5): giá trị khớp đo được bằng độ giống thật thu nhỏ theo độ nhận diện, cộng một nhiễu. Nhiễu nhỏ đi khi manh mối càng trung thành (r_j → 1), khi crop càng giống hẳn hoặc khác hẳn mục tiêu (|a| → 1), và khi không gian đặc trưng càng nhiều chiều hiệu dụng.

### 4.2 Kho ảnh của một camera

Kho của critical cell c gồm M crop, mỗi crop có một bộ độ giống (a_{i,v})_{v∈𝒱}. Với người lạ, các khía cạnh độc lập với nhau:

$$a_{i,v} \sim \mathcal{N}(\bar a_v, \sigma_v^2),\ \text{cắt về } [-1, 1]. \tag{6}$$

Với xác suất ρ, crop là người *mặc giống* mục tiêu. Khi đó khía cạnh bộ phận được bốc lại theo a_{i,\text{bộ phận}} ∼ 𝒩(ā_ℓ, σ_ℓ²).

Thứ tự các trung bình, ā_mặt < ā_dáng < ā_bộ phận, phản ánh các hiện tượng đã được ghi nhận:
- Vector mặt của hai người khác nhau gần như vuông góc [2].
- Dáng toàn thân của người lạ giống nhau nhiều hơn, vì cùng tư thế, cùng bối cảnh và trang phục phổ biến [3], [5].
- Thuộc tính quần áo (màu, loại) được nhiều người cùng chia sẻ nên phân biệt danh tính kém [15].
- Bài toán là tập mở: người lạ không có trong danh sách theo dõi vẫn có thể cho điểm cao [13], [14].

### 4.3 Bộ manh mối, luồng phát và tập manh mối được giữ

Manh mối j có khía cạnh v(j), kích thước F_j byte, độ nhận diện r_j và độ quan trọng w_j. Độ quan trọng chỉ do BS chấm (mục 114). Nó cho biết một lần khớp ở khía cạnh này nói lên bao nhiêu về danh tính: mặt nặng, màu áo nhẹ (mục 113). Mỗi manh mối đi trong

$$n_j = \left\lceil F_j / B \right\rceil \tag{7}$$

gói, với B = 99 byte là tải tin hữu ích của một khung IEEE 802.15.4: khung 127 byte trừ phần đầu, bảo mật và kiểm tra [16], mục 2. Cả bộ chiếm Q = Σ_j n_j gói. Độ quan trọng của một khía cạnh là

$$W_v = \sum_{j:\, v(j) = v} w_j. \tag{8}$$

**Thứ tự phát.** UAV phát bộ manh mối thành một luồng gói, lặp lại theo chu kỳ dọc đường bay. Các manh mối của mỗi khía cạnh được *rải đều dọc luồng*: manh mối thứ κ trong N_v manh mối của khía cạnh v đứng ở vị trí tương đối (κ − ½)/N_v của luồng (mục 113). Nhờ vậy một đoạn luồng bất kỳ đều có đủ loại khía cạnh. Đây là cùng ý với kỹ thuật xen kẽ (interleaving) trong truyền tin, vốn dùng để rải lỗi cụm [17]. Ở đây "lỗi cụm" là một nút chỉ nghe được một đoạn liền của luồng.

**Tập manh mối được giữ.** Không dùng mã sửa xoá (erasure code). Một manh mối chỉ dùng được khi có *đủ mọi gói của ít nhất một bản sao* (mục 34). Gọi H_c ⊆ {1, …, L} là tập manh mối critical cell c giữ trọn vẹn ở thời điểm báo cáo. H_c do các lớp dưới quyết định:
- **Tự nghe:** những bản sao mà chính các nút của cell nghe đủ trong lượt bay. Tập này là H_c^{dir}, có được sau khi gom trong cell.
- **Sau River:** River (lớp 3) chuyển cho mọi critical cell một bản sao đặt trên các gói Axe quanh CH, nên tập lớn hơn: H_c^{riv} ⊇ H_c^{dir}.

### 4.4 Điểm của crop, của cell và báo cáo

Cell c chấm mỗi crop theo hai bước. **Bước 1** ước lượng độ giống ở từng khía cạnh v mà cell giữ được ít nhất một manh mối, gọi tập các khía cạnh đó là 𝒱(H_c):

$$\hat a_{i,v} = \frac{\sum_{j \in H_c,\ v(j) = v} w_j\, m_{ij}}{\sum_{j \in H_c,\ v(j) = v} w_j\, r_j}. \tag{9}$$

Từ (5), E[m_{ij} | a] = r_j a_{i,v(j)}, nên E[â_{i,v} | a] = a_{i,v}: ước lượng không chệch. Mẫu số chia cho r_j để bù phần ảnh tham chiếu chưa thể hiện trọn mục tiêu, nên một crop giống tuyệt đối cho â = 1.

**Bước 2** gộp các khía cạnh có mặt theo độ quan trọng của khía cạnh:

$$S_i = \frac{\sum_{v \in \mathcal{V}(H_c)} W_v\, \hat a_{i,v}}{\sum_{v \in \mathcal{V}(H_c)} W_v}. \tag{10}$$

Gộp theo W_v (của cả bộ) chứ không theo tổng w_j của các manh mối đang giữ, nên tỉ trọng giữa các khía cạnh không đổi khi thiếu manh mối:
- Thiếu một ảnh dáng thì các ảnh dáng còn lại gánh phần của dáng.
- Thiếu hẳn một khía cạnh thì khía cạnh đó bỏ ra, các khía cạnh còn lại chia lại phần trọng số.

Gộp một bước (một tổng duy nhất trên các manh mối đang giữ) làm lệch tỉ trọng. Ví dụ giữ 2 ảnh mặt và 2 ảnh dáng thì mặt chiếm 2/3 thay vì 1/2, và tương quan với điểm xác minh giảm từ 0,51 xuống 0,42.

**Điểm của cell** là điểm của crop giống nhất:

$$S_c = \max_{1 \le i \le M} S_i. \tag{11}$$

**Báo cáo** của cell c là cặp (S_c, H_c): 1 byte cho S_c đã lượng tử, cộng ⌈L/8⌉ byte cho bitmap của H_c. Báo cáo đi critical cell → CH → kênh LoRa của CH → BS (§4.7).

### 4.5 Điểm xác minh và mục tiêu của pha 2

Với bộ tham chiếu đầy đủ R, nút đo được mọi khía cạnh một cách chính xác. Điểm xác minh của crop và của cell là

$$U_i = \frac{\sum_{v \in \mathcal{V}} W_v\, a_{i,v}}{\sum_{v \in \mathcal{V}} W_v}, \qquad U_c = \max_{1 \le i \le M} U_i, \qquad c^* = \arg\max_{c \in \mathcal{C}} U_c. \tag{12}$$

Đội 2 thăm mọi critical cell đã báo về (mục 112). **Pha 2 hoàn thành khi c\* đã được xác minh** (mục 114), nên chỉ số chính là

$$T^* = \text{thời điểm đội 2 xác minh xong } c^*. \tag{13}$$

Theo (9)–(11), điểm pha 1 S_c là một ước lượng có nhiễu của U_c. Ước lượng tốt khi H_c đầy đủ; kém khi thiếu manh mối, nhất là thiếu khía cạnh nặng (mặt). Đây là chỗ lớp 2–3 tác động lên lớp 1.

### 4.6 Suy diễn tại BS

**Hiệu chỉnh.** BS biết mô hình (5)–(11) và mọi tham số của bộ manh mối do chính nó soạn. Trước nhiệm vụ, với mỗi tập manh mối H có thể nhận, BS mô phỏng N_cal camera theo (6). Trên các camera này nó tính cặp (S_c, U_c) theo (11)–(12), rồi khớp hồi quy tuyến tính bình phương tối thiểu:

$$U_c \mid (S_c, H_c = H) \;\sim\; \mathcal{N}\!\left(b^0_H + b^1_H\, S_c,\ \sigma_H^2\right), \tag{14}$$

trong đó σ_H là độ lệch chuẩn của phần dư. H càng thiếu thì σ_H càng lớn, nên bitmap của H_c cho BS biết điểm đáng tin tới đâu. Với H = ∅, (14) lấy trung bình và độ lệch của U_c.

**Tiên nghiệm cho cell chưa báo.** f_0 là ước lượng mật độ nhân Gauss của các U_c mô phỏng, với độ rộng nhân theo quy tắc Silverman [12]:

$$f_0(u) = \frac{1}{N_{\rm cal}\, h}\sum_{n=1}^{N_{\rm cal}} \phi\!\left(\frac{u - U^{(n)}}{h}\right), \qquad h = 1{,}06\, \hat\sigma_U\, N_{\rm cal}^{-1/5}; \tag{15}$$

F_0 là hàm phân phối của f_0, φ là mật độ chuẩn tắc.

**Xác suất là c\*.** Tại thời điểm t, BS chia các critical cell thành ba nhóm:
- 𝒦(t): đã báo, chưa thăm, mỗi cell có mật độ f_c và hàm phân phối F_c theo (14), tính từ báo cáo mới nhất;
- n_0(t) cell chưa báo, mỗi cell theo f_0;
- 𝒲(t): đã xác minh, với U_c đã biết.

Coi các cell độc lập. Xác suất cell c ∈ 𝒦(t) giữ điểm xác minh cao nhất là xác suất biến của nó lớn hơn mọi biến khác [9], [10]:

$$p_c(t) = \int f_c(u) \prod_{c' \in \mathcal{K}(t) \setminus \{c\}} F_{c'}(u)\; F_0(u)^{\,n_0(t)} \prod_{c'' \in \mathcal{W}(t)} \mathbb{1}\!\left[u \ge U_{c''}\right] du. \tag{16}$$

Xác suất c\* nằm trong số các cell chưa báo là

$$P_U(t) = n_0(t) \int f_0(u)\, F_0(u)^{\,n_0(t) - 1} \prod_{c' \in \mathcal{K}(t)} F_{c'}(u) \prod_{c'' \in \mathcal{W}(t)} \mathbb{1}\!\left[u \ge U_{c''}\right] du. \tag{17}$$

Các tích phân lấy trên lưới 551 điểm của đoạn [0,25; 0,80], đoạn chứa gần như mọi U_c.

### 4.7 Thời gian

**Đối sánh tại nút.** Crop đã có vector từ lúc ghi. Khi truy vấn tới, nút giải mã và tính vector cho L ảnh manh mối, rồi tìm trong chỉ mục M vector:

$$\tau_m(L, M) = L\,\tau_{\rm dec} + \frac{L}{\Theta} + \max\!\left(\frac{M\, d_0\, b}{\mathrm{BW}},\ \frac{M\, L\, d_0}{\mathrm{MAC}}\right), \tag{18}$$

trong đó:
- τ_dec: thời gian giải mã một ảnh;
- Θ: tốc độ tính vector của bộ tăng tốc [18];
- d_0 = 2 048: số chiều vector danh nghĩa;
- b = 2 byte (fp16);
- BW: băng thông đọc bộ nhớ;
- MAC: tốc độ nhân‑cộng của CPU.

Với L = 12, M = 223 trên Raspberry Pi 5 + Hailo‑8L, τ_m ≈ 0,11 s.

**Báo cáo về BS.** Cluster k được UAV rời lúc t_k^{leave}. Cell c ∈ 𝒞_k có H_c sau thời gian δ_c, do ns‑3 đo: δ_c^{dir} là thời gian gom trong cell, δ_c^{riv} là thời gian River. Kết quả tới CH sau τ_h cho mỗi cell trên đường đi, với d_hex là khoảng cách theo số cell:

$$t_c^{\rm CH} = t_k^{\rm leave} + \delta_c + \tau_m + \tau_h\, d_{\rm hex}(c, \mathrm{CH}_k). \tag{19}$$

CH phát LoRa theo chu kỳ G = T_air/η, với η là giới hạn chu kỳ hoạt động [19] và T_air là thời gian phát một bản tin [20]. Mỗi bản tin gom mọi kết quả đã tới CH. Bản tin tới BS lúc

$$t_c^{\rm BS} = \varphi_k + G \left\lceil \frac{t_c^{\rm CH} - \varphi_k}{G} \right\rceil + T_{\rm air}, \qquad \varphi_k \sim \mathcal{U}[0, G). \tag{20}$$

Mỗi critical cell báo hai lần: theo H_c^{dir} (δ_c = δ_c^{dir}) và theo H_c^{riv} (δ_c = δ_c^{riv}). BS dùng báo cáo mới nhất.

**Xác minh.** Đội 2 hover trên cell, gửi R bằng unicast IEEE 802.15.4 tới CL của cell, rồi nút đối sánh R:

$$\tau_v = \tau_{\rm settle} + \left\lceil \frac{F_R}{B} \right\rceil \tau_{\rm uc} + \tau_m(L_R, M). \tag{21}$$

τ_uc là thời gian của một khung unicast có ACK, khi chỉ có một bên phát:

$$\tau_{\rm uc} = \underbrace{3{,}5 \times 0{,}32}_{\text{lùi ngẫu nhiên, BE = 3}} + \underbrace{0{,}32}_{\text{CCA + quay}} + \underbrace{133 \times 0{,}032}_{\text{khung}} + \underbrace{0{,}544}_{\text{quay + ACK}} + \underbrace{0{,}64}_{\text{LIFS}} = 6{,}88 \text{ ms}. \tag{22}$$

Các đại lượng trong (22) đều theo IEEE 802.15.4 ở 250 kb/s [16]:
- chu kỳ lùi đơn vị 20 symbol = 320 µs, macMinBE = 3;
- CCA 8 symbol cộng thời gian quay 12 symbol;
- khung đầy đủ 133 byte, 32 µs mỗi byte;
- ACK 11 byte sau 12 symbol quay;
- LIFS 40 symbol.

### 4.8 Từ xác suất tới thứ tự thăm

Đội 2 cất cánh cùng đội 1 và ra quyết định ở ba thời điểm: khi một báo cáo mới tới BS, khi xác minh xong một cell, và lúc cất cánh. Đặt x là vị trí hiện tại của đội 2, x_c là vị trí của cell c. Ứng viên tiếp theo là cell đã biết có xác suất trên thời gian lớn nhất:

$$c^{\rm next} = \arg\max_{c \in \mathcal{K}(t)} \frac{p_c(t)}{\lVert x - x_c \rVert / V_2 + \tau_v}. \tag{23}$$

Đội 2 đi xác minh c^next nếu

$$p_{c^{\rm next}}(t) \;\ge\; \beta\, P_U(t), \tag{24}$$

và nếu không thì bay đón đầu về tâm có trọng số của các cell chưa thăm. Trọng số của cell đã báo là p_c, của mỗi cell chưa báo là P_U/n_0. β cân bằng hai rủi ro:
- đi quá sớm tới một cell sai;
- chờ quá lâu trong khi c\* đã báo về.

β = 1/4 được chọn trên 40 bản đồ (báo cáo nhiệm vụ, mục 5.1).

## 5. Tham số

| Tham số | Giá trị | Nguồn hoặc tình trạng |
|---|---|---|
| M | 223 | Suy từ điểm vận hành công bố đầu tiên của [13] (tỉ lệ nhận nhầm 0,1 % mỗi crop) và tỉ lệ báo nhầm 20 % mỗi camera: M = ln(1 − 0,2)/ln(1 − 0,001) ≈ 223 (mục 101, `L1-STATEMENT-vi.md` §10) |
| L; F_j | 12 manh mối: 2 mặt × 24,9 kB, 4 dáng × 49,9 kB, 6 bộ phận × 24,9 kB | Thiết kế: mỗi ảnh 15–50 kB, 3–6 góc cộng các crop bộ phận (mục 94, 99); tổng vừa cửa sổ River 400 kB |
| Q | 4 036 gói | Theo (7), B = 99 byte |
| B | 99 byte | IEEE 802.15.4 [16]; đặc tả mục 2 |
| r_j | mặt 0,825 / 0,875; dáng 0,889–0,941; bộ phận 0,953–0,987 | Giả định kịch bản: ảnh mặt khó chụp trung thành nhất, màu áo dễ nhất |
| w_j (W_v) | mặt 4 (8); dáng 2 (8); bộ phận 2/3 (4) | BS chấm (mục 113–114); giả định: mặt và dáng mỗi khía cạnh 40 %, bộ phận 20 % |
| d | 128; quét 64 và 256 | Giả định kịch bản. Số chiều nội tại của biểu diễn sâu nhỏ hơn nhiều số chiều danh nghĩa [8] |
| ā_v, σ_v | mặt 0,10 / 0,10; dáng 0,35 / 0,12; bộ phận 0,45 / 0,15 | Giả định kịch bản; thứ tự theo [2], [3], [5], [15] |
| ρ; ā_ℓ, σ_ℓ | 2 % (quét 0 và 5 %); 0,85 / 0,05 | Giả định kịch bản; tập mở [13], [14] |
| N_cal | 2 000 camera | Thiết kế (dung lượng mô phỏng của BS) |
| τ_dec; Θ | 5 ms; 257,56 ảnh/s | τ_dec ước lượng; Θ: ResNet‑50, Pi 5 + Hailo‑8L, batch 8 [18] |
| d_0, b, BW, MAC | 2 048; 2 byte; 8 GB/s; 20 GMAC/s | d_0: vector ResNet‑50; còn lại là ước lượng cho Pi 5 |
| τ_h | 0,1 s mỗi cell | Giả định: một khung điều khiển mỗi chặng |
| T_air; η; G | 0,4 s; 1 %; 40 s | η: ETSI EN 300 220 [19]; T_air: bản tin vài byte ở hệ số trải phổ cao, tính theo [20] |
| τ_settle | 5 s | Giả định: ổn định hover |
| F_R; L_R | 1 MiB; 20 ảnh | Số tạm (mục 73) |
| τ_uc | 6,88 ms | (22), IEEE 802.15.4 [16] |
| τ_v | 78,1 s | (21) |
| V_2; β | 15 m/s; 1/4 | V_2 theo mục 73; β chọn trên 40 bản đồ |

Các dòng "giả định kịch bản" là tham số của kịch bản, không phải số đo. Chúng được chọn để mô hình có các hiện tượng đã được ghi nhận: mặt phân biệt tốt nhất, quần áo dễ khớp nhầm, người lạ có thể vượt ngưỡng. Kết quả luôn đi kèm phép quét độ nhạy theo d, ρ và M (`uav-l2/docs/L1-MISSION2-vi.md` §6). Trong đó d quyết định mức T\* nhiều nhất, nên là tham số cần neo vào số đo thật trước tiên.

## 6. Đặc trưng của mô hình

Đo trên 3 200 camera mô phỏng (`l1_model.py`). "Nửa luồng" là các manh mối nằm trọn trong nửa đầu hoặc nửa sau của luồng phát, tính theo số gói. Đó là điều xảy ra với một cell chỉ tự nghe được một đoạn luồng.

| Cell giữ | Manh mối (m = mặt, d = dáng, b = bộ phận) | Tương quan S_c với U_c | Cell đứng đầu theo S là c\* | Hạng TB của c\* theo S |
|---|---|---|---|---|
| đủ 12 manh mối | m m d d d d b b b b b b | 0,88 | 54 % | 1,9 |
| nửa đầu luồng xen kẽ | m d d b b b | 0,75 | 41 % | 2,9 |
| nửa sau luồng xen kẽ | m d d b b b | 0,82 | 59 % | 2,3 |
| nửa đầu luồng xếp nhóm | m m d d | 0,51 | 29 % | 6,1 |
| nửa sau luồng xếp nhóm | d b b b b b b | 0,43 | 16 % | 9,0 |
| thiếu cả hai manh mối mặt | d d d d b b b b b b | 0,44 | 20 % | 8,2 |
| chỉ có manh mối bộ phận | b b b b b b | 0,04 | 4 % | 17,0 |
| đủ 12, trọng số đều (bỏ w) | như dòng đầu | 0,43 | 28 % | 8,9 |

- Ngay cả khi đủ dữ liệu, pha 1 chỉ chọn đúng c\* khoảng một nửa số lần, nên thứ tự thăm và quy tắc (23)–(24) vẫn quan trọng.
- Thiếu manh mối làm xếp hạng kém đi nhanh, nhất là thiếu mặt.
- Phát xen kẽ cho hai nửa luồng gần như bằng nhau và gần với đủ bộ. Xếp nhóm thì nửa nào cũng thiếu hẳn một khía cạnh.
- Hình `uav-l2/docs/figures/l1-model.png` (không chữ):
  - Hàng trên: luồng phát một bản sao, xếp nhóm (trên) và xen kẽ (dưới). Mỗi khối là một manh mối, rộng theo số gói, cao theo độ quan trọng. Đỏ là mặt, xanh là dáng, vàng là bộ phận; màu càng đậm thì r_j càng gần 1. Dải xám là nửa đầu luồng.
  - Ô trái dưới: S_c (ngang) so với U_c (dọc). Xanh đậm là đủ bộ, vàng là nửa sau luồng xếp nhóm; đường đứt là đường chéo.
  - Ô giữa dưới: tỉ lệ cell đứng đầu là c\*, theo thứ tự: đủ bộ; hai nửa xen kẽ (xanh nhạt); hai nửa xếp nhóm (vàng); thiếu mặt (đỏ); trọng số đều (xám).
  - Ô phải dưới: phân bố hạng của c\* theo S, từ 1 tới 10 (cột cuối là từ 10 trở đi). Xanh đậm là đủ bộ, vàng là nửa sau luồng xếp nhóm.

## 7. Giả định và giới hạn

1. Mỗi khía cạnh được so bằng một mô hình đặc trưng riêng. Mọi camera dùng chung các mô hình đó và chung thang điểm đã hiệu chỉnh. Khác biệt giữa thiết bị (mục 88) chưa đưa vào. Nếu cần, mỗi nút chuẩn hoá điểm theo phân phối điểm của chính kho mình trước khi gửi (`L1-VECTOR-vi.md` §3).
2. Ở người lạ, các khía cạnh độc lập với nhau, trừ nhóm mặc giống. Chưa mô hình góc chụp của crop; ví dụ crop chụp từ phía sau thì không có mặt.
3. (5) là xấp xỉ khi d lớn. Nó coi phần vuông góc của manh mối như một hướng ngẫu nhiên, nên bỏ qua tương quan giữa các ảnh tham chiếu cùng trích từ một video.
4. BS biết đúng mô hình khi hiệu chỉnh (14). Thực tế BS phải hiệu chỉnh trên một tập thẩm định.
5. Xác minh với R coi như đo đúng tuyệt đối U_c.
6. Kho chỉ có người lạ: mô hình trả lời "xác minh cell nào trước", không phải "mục tiêu có ở đây không" (mục 112).

## 8. Tài liệu tham khảo

1. F. Schroff, D. Kalenichenko, J. Philbin, "FaceNet: A unified embedding for face recognition and clustering," in *Proc. IEEE CVPR*, 2015, pp. 815–823.
2. J. Deng, J. Guo, N. Xue, S. Zafeiriou, "ArcFace: Additive angular margin loss for deep face recognition," in *Proc. IEEE CVPR*, 2019, pp. 4690–4699.
3. H. Luo, Y. Gu, X. Liao, S. Lai, W. Jiang, "Bag of tricks and a strong baseline for deep person re‑identification," in *Proc. IEEE CVPR Workshops*, 2019.
4. L. Zheng, L. Shen, L. Tian, S. Wang, J. Wang, Q. Tian, "Scalable person re‑identification: A benchmark," in *Proc. IEEE ICCV*, 2015, pp. 1116–1124.
5. M. Ye, J. Shen, G. Lin, T. Xiang, L. Shao, S. C. H. Hoi, "Deep learning for person re‑identification: A survey and outlook," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 44, no. 6, pp. 2872–2893, 2022.
6. R. Vershynin, *High‑Dimensional Probability: An Introduction with Applications in Data Science*. Cambridge University Press, 2018, §3.3 (vector ngẫu nhiên đều trên mặt cầu; giới hạn trung tâm theo phép chiếu).
7. P. Diaconis, D. Freedman, "A dozen de Finetti‑style results in search of a theory," *Ann. Inst. Henri Poincaré Probab. Stat.*, vol. 23, no. S2, pp. 397–423, 1987.
8. A. Ansuini, A. Laio, J. H. Macke, D. Zoccolan, "Intrinsic dimension of data representations in deep neural networks," in *Proc. NeurIPS*, 2019.
9. C. E. Clark, "The greatest of a finite set of random variables," *Operations Research*, vol. 9, no. 2, pp. 145–162, 1961.
10. H. A. David, H. N. Nagaraja, *Order Statistics*, 3rd ed. Wiley, 2003.
11. (dự phòng)
12. B. W. Silverman, *Density Estimation for Statistics and Data Analysis*. Chapman & Hall, 1986, §3.4.2.
13. X. Li, A. Wu, W.‑S. Zheng, "Adversarial open‑world person re‑identification," in *Proc. ECCV*, 2018; arXiv:1807.10482.
14. W.‑S. Zheng, S. Gong, T. Xiang, "Towards open‑world person re‑identification by one‑shot group‑based verification," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 38, no. 3, pp. 591–606, 2016.
15. Y. Lin, L. Zheng, Z. Zheng, Y. Wu, Z. Hu, C. Yan, Y. Yang, "Improving person re‑identification by attribute and identity learning," *Pattern Recognition*, vol. 95, pp. 151–161, 2019.
16. *IEEE Standard for Low‑Rate Wireless Networks*, IEEE Std 802.15.4‑2020.
17. J. L. Ramsey, "Realization of optimum interleavers," *IEEE Trans. Inf. Theory*, vol. 16, no. 3, pp. 338–345, 1970.
18. Hailo Community, "Raspberry Pi 5 with Hailo‑8L benchmark," 06/2024, https://community.hailo.ai/t/raspberry-pi-5-with-hailo-8l-benchmark/746 (benchmark cộng đồng, chưa bình duyệt; xem `L1-STATEMENT-vi.md` [10]).
19. ETSI EN 300 220‑2 V3.2.1, *Short Range Devices (SRD) operating in the frequency range 25 MHz to 1 000 MHz; Part 2*, 2018 (giới hạn chu kỳ hoạt động 1 % ở băng 868,0–868,6 MHz).
20. Semtech, "LoRa modem designer's guide," Application Note AN1200.13, 2013 (công thức thời gian phát).

Ghi chú về nguồn:
- [1]–[5], [13]–[15] đỡ cho *dạng* của mô hình: so khớp bằng cosine, và thứ tự phân biệt giữa các khía cạnh. Chúng không cho các *giá trị* của §5. Các giá trị đó là giả định kịch bản và được quét độ nhạy.
- Hàm Φ trong mã dùng xấp xỉ erf 7.1.26 của Abramowitz–Stegun (sai số < 1,5·10⁻⁷). Đây là chi tiết cài đặt, không cần đưa vào bài.

## 9. Bản ngắn tiếng Anh cho paper

> **Layer 1: query matching at the edge.** Each critical cell c ∈ 𝒞 hosts a camera that recorded M person crops in the query window and indexed them as unit‑norm embeddings at recording time; matching is a cosine similarity, as in face recognition and person re‑identification [1]–[5]. We model each aspect v ∈ 𝒱 = {face, body, part} of the unknown target by a direction μ_v. Crop i has true similarity a_{i,v} = ⟨f(x_i), μ_v⟩, and clue j, an image of aspect v(j) distilled by the BS from the full reference set R, has recognizability r_j = ⟨f(y_j), μ_{v(j)}⟩ < 1. Decomposing both embeddings into their components along and orthogonal to μ_v gives the measured match m_{ij} = r_j a_{i,v(j)} + ε_{ij}, ε_{ij} ∼ 𝒩(0, (1 − a²)(1 − r_j²)/d), for d effective dimensions [6]–[8]. The BS assigns each clue an importance w_j, with W_v = Σ_{v(j)=v} w_j. The clues are broadcast as Q = Σ_j ⌈F_j/B⌉ packets with aspects interleaved, and a clue is usable only once all packets of one copy are held. A cell holding the clue subset H_c estimates each aspect without bias, â_{i,v} = Σ_{j∈H_c, v(j)=v} w_j m_{ij} / Σ_{j∈H_c, v(j)=v} w_j r_j, combines the aspects present with weights W_v into S_i, and reports S_c = max_i S_i together with the bitmap of H_c through its CH's duty‑cycled LoRa uplink. Verification by team 2 with R measures U_c = max_i Σ_v W_v a_{i,v} / Σ_v W_v. Phase 2 ends once c* = argmax_c U_c is verified, at time T*. The BS calibrates U_c | (S_c, H_c) as a normal variable by simulation, computes the probability p_c that each cell is c* [9], [10], and sends team 2 to the known cell with the largest p_c per unit of flight plus verification time, once that probability reaches a fraction β of the probability that c* has not reported yet.
