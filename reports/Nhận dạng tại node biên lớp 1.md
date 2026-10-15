# Lớp 1: tính đúng số false alarm trước khi tính bit

Với hệ thống này, **nút camera nên trả lời câu hỏi truy hồi mở (open-set retrieval có lựa chọn từ chối)**: "trong kho của tôi có tracklet nào giống mục tiêu không, và mạnh đến mức nào". Modality chính nên là **ngoại hình toàn thân (person re-ID)**, có thêm cổng lọc người/trẻ em và thuộc tính. Khuôn mặt chỉ là kênh phụ ở chuông cửa và cửa ra vào. Lý do: re-ID đạt R1 82–95 % trên benchmark sạch, còn mặt trong ảnh giám sát thật chỉ đạt R1 29,9 % và TPIR ≈ 13 % ở chế độ mở. Giới hạn thực sự không nằm ở đường xuống. Một chữ ký 64 B (PQ‑64 hoặc mã nhị phân 512 bit) vừa đúng **1 khung 99 B**. Một template float32 512‑d cần 21 khung, chưa tới 1 % ngân sách 10³–10⁴ khung của một cluster. Giới hạn nằm ở **phép tính false alarm**. Một cluster thực hiện 10⁷–10¹⁰ phép so sánh cho mỗi truy vấn, nên muốn E[FA] ≤ 1 thì FMR mỗi phép so sánh phải vào khoảng 10⁻⁸–10⁻¹⁰. Mức này thấp hơn mọi FMR thường được công bố cho nhận dạng ngoài thực địa. Vì vậy ba thứ là bắt buộc, không phải tùy chọn: gộp theo tracklet, gộp mọi view của một mục tiêu thành một template, và quyết định tập trung tại BS có kiểm soát FDR. Ba thứ này quan trọng hơn việc chọn 256 hay 512 bit. Tập tham chiếu nên chia lớp thô→mịn: thuộc tính và tiền tố Matryoshka nằm gọn trong một khung, template đầy đủ khoảng 11 khung. Như vậy nút nào nhận được phần nào cũng dùng được phần đó, khớp với quy tắc "file chỉ dùng được khi đủ mọi khung". Theo dữ liệu đã có, độ phủ tham chiếu bão hòa sớm, ở khoảng **3–4 view đa dạng**. Ngưỡng không nên cố định theo điểm thô ở từng nút. Nút gửi một LLR đã hiệu chỉnh, kèm số phép so sánh và tỉ lệ tham chiếu đã nhận. Ngưỡng cổng tại nút tăng theo k·G, không theo việc nút nhận ít hay nhiều. Báo cáo này không bàn hợp tác nhanh hơn hay rẻ hơn. Lớp 1 chỉ đòi các nút xử lý có đủ file và trả về đúng vài byte.

**Quy ước nhãn** (giữ nguyên phân biệt của ghi chú gốc):

| Nhãn | Nghĩa |
|---|---|
| **[nguồn]** | Số đọc được từ nguồn có link trong phiên nghiên cứu |
| **[nguồn·trích]** | Số lấy từ đoạn trích kết quả tìm kiếm, từ bảng cào lại, hoặc do nhà sản xuất tự công bố. Có link, nhưng phải đối chiếu bản gốc trước khi đưa vào paper |
| **[chưa kiểm]** | Số người nghiên cứu nhớ từ bài báo đã nêu tên, chưa mở lại để kiểm trong phiên này |
| **[mô hình]** | Phép tính hoặc ngoại suy của nhóm, không phải số đo |

---

## (1) Nút trả lời câu hỏi "truy hồi mở", và body re‑ID thắng face ở camera đô thị

### Câu hỏi nào: metric quyết định thứ tự ưu tiên

Mỗi nút xếp hạng các crop/tracklet đã lưu theo độ giống với truy vấn, rồi đặt ngưỡng trên điểm cao nhất. Bản chất đây là **truy hồi (retrieval) trong bối cảnh open‑set**: phần lớn người trong kho không phải mục tiêu. QMUL‑SurvFace tách rõ hai giao thức. Giao thức 1:1 đo bằng TAR@FAR. Giao thức 1:N mở dùng gallery 3 000 ID và 10 254 ID probe, nhiều probe là người ngoài danh sách, và đo bằng TPIR theo FPIR. Bài báo lập luận rằng chế độ mở "bắt buộc cho giám sát" vì có rất nhiều người không phải mục tiêu ([Cheng et al., arXiv 1804.09691](https://arxiv.org/abs/1804.09691)) [nguồn]. NIST FRTE 1:N báo cáo **FNIR tại ngưỡng cố định FPIR = 0,003** ([NIST FRTE 1:N](https://pages.nist.gov/frvt/html/frvt1N.html)) [nguồn]. Ngược lại, re‑ID và person search bằng văn bản báo cáo Rank‑k/mAP trong chế độ đóng, giả định mọi truy vấn đều có mặt trong gallery ([CLIP‑SCGI, arXiv 2410.09382](https://arxiv.org/pdf/2410.09382)) [nguồn]. Hệ quả là con số R1 trên benchmark **đánh giá cao hơn thực tế** khi đem ra hiện trường. Paper nên báo cáo tỉ lệ false alarm theo nút và tỉ lệ bỏ sót theo cluster, vì mỗi false alarm làm đội UAV 2 bay tới sai chỗ [mô hình].

| Loại câu hỏi | Nút trả lời gì | Metric chuẩn | Hợp với hệ thống |
|---|---|---|---|
| Detection | "Có người hoặc trẻ em không?" | AP@IoU | Chỉ dùng để lọc trước, không mang danh tính |
| Attribute search | "Cỡ trẻ em, áo đỏ?" | mA, F1, Rank‑k | Bộ lọc thô tốt, quá yếu nếu dùng một mình |
| 1:1 verification | "Crop này có phải mục tiêu?" | TAR@FAR | Là viên gạch cơ sở, nhưng bỏ qua hiệu ứng có nhiều probe |
| 1:N open‑set | "Mục tiêu nào, hay không ai?" | FNIR@FPIR, TPIR@FPIR | **Đúng ngữ nghĩa triển khai** |
| Retrieval / re‑ID | "Xếp hạng crop của tôi" | Rank‑1/5, mAP | **Đúng đầu ra của nút** |

### Modality nào: độ chính xác trên benchmark sạch và trên ảnh giám sát

Trên benchmark sạch, mặt, re‑ID toàn thân và re‑ID xe đều đạt 85–97 % ở metric chính. Thứ phân biệt chúng là **mức suy giảm trong điều kiện giám sát thật**. Mặt suy giảm mạnh nhất khi độ phân giải thấp. Trên IJB‑C, AdaFace đạt **TAR@FAR=1e‑4 ≈ 97,39 %** ([AdaFace, arXiv 2204.00964](https://arxiv.org/pdf/2204.00964)) [nguồn]. Trên TinyFace, R1 chỉ còn 68,2–72,0 % (cùng nguồn [nguồn]) và tối đa 75,99 % với adapter ([arXiv 2407.14972](https://arxiv.org/html/2407.14972v1)) [nguồn]. Trên QMUL‑SurvFace, mô hình tốt nhất (CentreFace) đạt **R1 đóng 29,9 %**, trong khi cùng mô hình đạt 65,2 % trên MegaFace. Ở chế độ mở, nó chỉ đạt **TPIR ≈ 13,2–13,8 % tại FPIR = 10 %**; hai con số khác nhau đến từ hai phiên bản bài báo ([arXiv 1804.09691](https://arxiv.org/abs/1804.09691)) [nguồn]. Siêu phân giải không cứu được: AUC open‑set giảm từ 13,8 % xuống 9,9 % ([arXiv 1912.02851](https://arxiv.org/pdf/1912.02851)) [nguồn].

Re‑ID toàn thân chịu ảnh hưởng chủ yếu từ việc **đổi quần áo** và đổi miền camera. CLIP‑ReID đạt Market‑1501 **94,7 % R1 / 88,1 % mAP** và MSMT17 82,1 / 60,7 ([PMC11769178](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769178/)) [nguồn]. Khi đổi quần áo, LTCC chỉ còn R1 40–46 % và mAP ≈ 20 %, PRCC còn 55–71 % ([arXiv 2501.05851](https://arxiv.org/pdf/2501.05851), [arXiv 2305.06145](https://arxiv.org/pdf/2305.06145)) [nguồn]. Dáng đi (gait) sụp mạnh khi đổi miền: huấn luyện trên GREW rồi thử trên Gait3D chỉ đạt **16,5 % R1** ([arXiv 2511.06245](https://arxiv.org/pdf/2511.06245)) [nguồn].

| Modality | Benchmark sạch | Điều kiện giám sát / khó | Kích thước truy vấn | Sinh trắc học (GDPR)? |
|---|---|---|---|---|
| Face | IJB‑C TAR@1e‑4 ≈ 97,4 % [nguồn]; LFW ≈ 99,8 % [chưa kiểm] | TinyFace R1 68–76 % [nguồn]; SurvFace R1 29,9 %, TPIR ≈ 13 % @FPIR 10 % [nguồn] | 512‑d ≈ 0,5–2 kB | Có |
| Body re‑ID | Market R1 ≈ 95 % / mAP 88 %; MSMT17 R1 82 % [nguồn] (CLIP‑SCGI tự báo 88,2 %, không khớp aggregator [nguồn·trích]) | Đổi quần áo LTCC R1 40–46 %, mAP ≈ 20 % [nguồn]; đổi miền giảm mạnh [chưa kiểm] | 0,5–8 kB/ảnh | Còn tranh cãi |
| Gait | GREW R1 77,7–81,2 %, Gait3D 74,4–78,3 % [nguồn] | Chéo miền R1 16,5–43,9 % [nguồn] | Nhỏ, nhưng cần chuỗi ảnh | Có |
| Vehicle re‑ID | VeRi‑776 mAP ≈ 84,5–85,2 %, R1 96,6–97,6 % ([CVPRW 2019](https://openaccess.thecvf.com/content_CVPRW_2019/html/AI_City/Ayala-Acevedo_Vehicle_Re-Identification_Pushing_the_limits_of_re-identification_CVPRW_2019_paper.html), [arXiv 2409.17908](https://arxiv.org/pdf/2409.17908)) [nguồn] | Chưa có số | ~kB | Không |
| Biển số (LPR) | ≈ 96,8 % end‑to‑end trên 8 tập ([arXiv 1909.01754](https://arxiv.org/abs/1909.01754v3)) [nguồn] | UFPR‑ALPR: hệ 2018 78,33 %, hệ thương mại < 70 % ([arXiv 1802.09567](https://arxiv.org/abs/1802.09567v2)) [nguồn] | Vài byte | Không (vẫn là dữ liệu cá nhân) |
| Text / thuộc tính | CUHK‑PEDES R1 76,93 % (ROGLE) ([arXiv 2606.01825](https://arxiv.org/pdf/2606.01825)) [nguồn] | RSTPReid R1 61,8–65,2 % [nguồn]; chỉ thuộc tính: Market R1 49,0 %, mAP 29,8 % ([SAL, arXiv 2007.09609](https://arxiv.org/html/2007.09609v2)) [nguồn] | < 1 kB | Thường không |

Mật độ điểm ảnh giải thích vì sao mặt chỉ dùng được ở số ít nút. Theo IEC 62676‑4:2025, mức "Characterize" cần 250 px/m (40 px/mặt) và mức "Validate" cần 500 px/m ([Axis 2025](https://whitepapers.axis.com/en/pixel-density-based-on-iec-62676-4-2025)) [nguồn]. Câu "500 px/m đủ cho hầu hết phần mềm nhận dạng mặt" chỉ là tuyên bố của ngành, không phải chuẩn ([asmag](https://www.asmag.com/showpost/35334.aspx)) [nguồn·trích]. Lấy ví dụ camera 1080p với FOV khoảng 90°: mật độ khoảng 960/d px/m, nên chỉ đạt 250 px/m trong phạm vi khoảng 4 m. Ở cùng cự ly 10 m, người lớn cao 1,7 m chiếm khoảng 160 px, đủ cho crop re‑ID 128 px [mô hình]. Với trẻ em còn thêm một bất lợi: NISTIR 8280 ghi nhận false positive tăng ở hai đầu độ tuổi ([tóm tắt thứ cấp, defensedaily](https://defensedaily.com/nist-study-finds-demographics-make-difference-face-recognition-algorithms/homeland-security)) [nguồn·trích, câu chữ chưa đối chiếu với thân báo cáo].

**Kết luận cho câu (1).** Phương án được chọn là **body re‑ID trong khung truy hồi open‑set, có cổng thuộc tính/cỡ trẻ em**. Với trẻ lạc, ảnh tham chiếu thường là ảnh chụp cùng ngày nên quần áo khớp; nhận định này lấy từ ghi chú [chưa kiểm]. Mặt là kênh thứ hai ở chuông cửa và lối vào, có ích cho trường hợp nghi phạm đã đổi quần áo. Xe/biển số là một loại truy vấn riêng. Gait không phù hợp cho nghiên cứu này. Khuyến nghị này vẫn đứng vững trước phản biện ở mục (15), nhưng chỉ khi body re‑ID không bao giờ là bộ quyết định duy nhất ở mức crop.

---

## (4) Đơn vị truyền: 64 byte là một khung, và đường xuống không phải giới hạn

Mọi kích thước dưới đây là phép nhân số chiều × số byte mỗi phần tử, chia cho 99 B mỗi khung [mô hình], trừ các dòng có nguồn riêng.

| Biểu diễn | Cấu hình | Byte/chữ ký | Khung 99 B | Bit/chữ ký |
|---|---|---|---|---|
| Crop mặt JPEG | 112×112×3 | ~3–6 kB (ước lượng không nguồn) | ~30–60 | ~24–48 k |
| Crop người JPEG | 256×128×3 | ~5–15 kB (ước lượng không nguồn) | ~50–150 | ~40–120 k |
| MPEG CDVS | 6 điểm tốc độ | 512 B – 16 KB ([arXiv 1704.08141](https://arxiv.org/pdf/1704.08141)) [nguồn] | 6–166 | 4 k – 131 k |
| float32 2048‑d (ResNet50 re‑ID) | | 8 192 | 83 | 65 536 |
| float32 512‑d (ArcFace/CLIP) | | 2 048 | 21 | 16 384 |
| float16 512‑d | | 1 024 | 11 | 8 192 |
| int8 512‑d | | 512 | 6 | 4 096 |
| 4‑bit 512‑d | | 256 | 3 | 2 048 |
| PQ/OPQ 64×8 bit | | 64 | 1 (1/khung) | 512 |
| PQ 16×8 / mã nhị phân 128 bit | | 16 | 1 (6/khung) | 128 |
| Mã nhị phân 512 / 256 / 64 bit | | 64 / 32 / 8 | 1 (1 / 3 / 12 mỗi khung) | 512 / 256 / 64 |
| Tiền tố Matryoshka int8 64‑d | | 64 | 1 | 512 |

Các bằng chứng về độ chính xác theo số bit cùng chỉ một hướng, nhưng hiếm có số tuyệt đối cho mô hình mặt hiện đại. Chuyển embedding mặt 512‑d sang **int8** giảm tới khoảng 80 % dung lượng mà "không mất nhiều". Tuy vậy mức mất phụ thuộc mô hình: FaceNet ổn định, TransFace giảm đáng kể ([nghiên cứu UFMS](https://repositorio.ufms.br/retrieve/cf33dad8-c741-4948-b7aa-d4885c44a9f2/29545.pdf)) [nguồn]. Nhị phân hóa template mặt sâu được mô tả là chỉ giảm "không đáng kể" ([Drozdowski et al., ICIP 2018](https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/2577914)) [nguồn, chỉ phần tóm tắt; bảng EER chưa đọc được]. Ngược lại, IronMask coi nhị phân hóa là "nguyên nhân chính gây mất hiệu năng" ([DeepAI](https://deepai.org/publication/ironmask-modular-architecture-for-protecting-deep-face-template)) [nguồn]. Hai nguồn này không mâu thuẫn thật sự. Mất mát nhỏ ở EER trung bình vẫn có thể thành lớn ở FMR rất thấp, và đó chính là vùng hệ thống này phải hoạt động [mô hình].

Với re‑ID, bảng hashing năm 2017 cho thấy mAP tăng đến khoảng 512 bit rồi bão hòa. Bảng này cũng cho thấy 500 K người gây nhiễu làm mAP **giảm gần một nửa**:

| Độ dài mã | Market R1 % | Market mAP % | +500K R1 % | +500K mAP % |
|---|---|---|---|---|
| 128 bit | 19,06 | 9,58 | 12,20 | 4,48 |
| 512 bit | 25,36 | 12,37 | 17,61 | 6,44 |
| 2048 bit | 27,14 | 12,76 | 18,68 | 6,56 |
| PDH 2048 bit | 47,89 | 26,06 | — | — |

Nguồn: ([Zhang et al., arXiv 1705.02145](https://ar5iv.labs.arxiv.org/html/1705.02145)) [nguồn]. Đặc trưng ở đây là thế hệ 2017. Re‑ID float hiện đại đạt khoảng 85–90 % mAP trên Market [chưa kiểm], nên mức tuyệt đối của mã nhị phân hiện đại sẽ khác. So khoảng cách Hamming nhị phân mất 1,81 ms, so float 4096‑d mất 101,4 ms (cùng nguồn) [nguồn].

Có một chi tiết thiết kế quan trọng. Gallery của nút không bao giờ rời khỏi nút, nên nút có thể giữ gallery ở dạng **float đầy đủ** và so sánh *bất đối xứng* với truy vấn đã nén. Đây là nguyên lý ADC của PQ: chỉ một phía bị lượng tử hóa ([Jégou et al., TPAMI 2011](https://paper-notes.zhjwpku.com/assets/pdfs/Product_Quantization_for_Nearest_Neighbor_Search.pdf)) [nguồn]. Áp nguyên lý này cho mặt/re‑ID là suy luận [mô hình], nên mức mất thực tế phải nhỏ hơn số liệu hashing đối xứng ở bảng trên. Ràng buộc riêng của dự án là "file chỉ dùng được khi đủ mọi khung". Ràng buộc này làm đảo lập luận "float32 rẻ, cứ gửi": một chữ ký 21 khung cần 21 khung liền nhau còn nguyên, còn chữ ký 1 khung sống sót như một đơn vị độc lập [mô hình]. Đặc tả A2G trong CLAUDE.md (mục 8.2) cho dự đoán giải tích về chuỗi liên tục dài nhất với α = 3,0: **≈ 11 ± 2** ở lệch ngang 900 m, **40 ± 9** ở 600 m, **208 ± 73** ở 300 m, **823 ± 202** ngay dưới đường bay [mô hình, dự đoán giải tích của người dùng, chưa phải số đo ns‑3]. Đặc tả cũng ghi rằng giả thiết fading không đổi trong một gói làm kết quả *lạc quan* khoảng hệ số 4. Từ đó suy ra: chữ ký 1 khung sống ở mọi nơi có thu; template fp16 11 khung chỉ chắc chắn trong khoảng ~600 m; crop JPEG 50–150 khung chỉ an toàn trong khoảng ~300 m quanh trục bay [mô hình].

**Kết luận cho câu (4).** Đơn vị nên dùng là **mã 64 B, mỗi khung một mã có header tự định danh** (PQ‑64, nhị phân 512 bit, hoặc tiền tố MRL 64‑d int8), phát lặp nhiều lần. Có thể thêm một bản int8 hoặc fp16 đầy đủ (6–11 khung) cho những nút nhận trọn. Ảnh thô chỉ đáng gửi nếu cần độc lập mô hình giữa các hãng: nút tự tính embedding bằng mô hình của nó. Đổi lại, ảnh thô chỉ đến được các nút gần trục [mô hình].

---

## (5) Ba đến bốn view đa dạng là đủ, và gộp chúng thành một template

Dữ liệu cho thấy lợi ích bão hòa sớm. Trong báo cáo du lịch của NIST (gallery 420 người), NEC‑3 tăng từ **98,7 % lên 99,0 %** khi chuyển từ 1 ảnh sang trung bình khoảng 6 ảnh đăng ký. Visionlabs‑10 tăng từ 99,9 % lên 100 %, tức ít lỗi hơn khoảng 10 lần. Số chuyến bay không có false negative tăng từ ≤ 428/567 lên 545/567 ([NIST IR 8381 travel report](https://pages.nist.gov/frvt/reports/travel/frvt_travel_report.pdf)) [nguồn]. NIST nhấn mạnh rằng **ảnh hưởng của thuật toán lớn hơn** ảnh hưởng của số ảnh đăng ký. Tăng gallery 100 lần (420 → 42 000) chỉ làm lỗi tăng khoảng 3 lần ([NIST IR 8381](https://nvlpubs.nist.gov/nistpubs/ir/2021/NIST.IR.8381.pdf)) [nguồn]. Trên IJB‑A, điểm xác minh ở FAR 1e‑2 tăng khoảng 19 % khi đi từ 1 lên 64 media mỗi template, và **chững lại ở khoảng 3 media** ([Crosswhite et al., arXiv 1603.03958](https://ar5iv.labs.arxiv.org/html/1603.03958)) [nguồn]. Video re‑ID trên MARS đạt R1 75,0 % với 2 khung, 79,8 % với 4, 78,6 % với 8, và "ổn định từ 4 khung" ([Mekhazni et al., WACV 2023 supp.](https://openaccess.thecvf.com/content/WACV2023/supplemental/Mekhazni_Camera_Alignment_and_WACV_2023_supplemental.pdf)) [nguồn·trích]. Market‑1501 multi‑query đưa HA‑CNN từ 91,2 / 75,7 lên 93,8 / 82,8 (R1/mAP) ([arXiv 1804.01438](https://arxiv.org/pdf/1804.01438)) [nguồn·trích].

Cách gộp quan trọng hơn số lượng view. Bảng NAN trên IJB‑A cho thấy lấy max hoặc "cặp tốt nhất" có thể **tệ thảm hại** ở FAR thấp:

| Cách gộp template (IJB‑A) | TAR@FAR=1e‑3 | TPIR@FPIR=1e‑2 | Rank‑1 |
|---|---|---|---|
| MaxPool | 0,202 | 0,079 | 0,757 |
| Min L2 (cặp tốt nhất) | 0,038 | 0,026 | 0,853 |
| AvePool (trung bình 1 vector) | 0,771 | 0,634 | 0,931 |
| AvePool† (trung bình trong media, rồi giữa các media) | 0,856 | 0,793 | 0,951 |
| NAN† (trọng số chú ý) | 0,881 | 0,817 | 0,958 |

Nguồn: ([NAN, arXiv 1603.05474](https://arxiv.org/abs/1603.05474)) [nguồn]. Hai điểm đáng chú ý. Vector đã gộp **có cùng số chiều với một đặc trưng đơn**, nên gửi một template đã gộp tốn đúng bằng một view. Trên YTF, nơi các khung gần như giống nhau, lợi ích của tập gần bằng 0 (AvePool 95,20 % so với NAN 95,72 %). Nghĩa là **độ đa dạng của view mới tạo ra giá trị**, không phải số lượng (cùng nguồn) [nguồn].

Liên hệ với số file tối thiểu mỗi cluster. Gọi một "file" là một đơn vị tự giải mã được. Đề xuất là mỗi mục tiêu cần **1 file template đã gộp**, cộng 2–3 file prototype theo điều kiện: góc nghiêng, ban đêm/IR, bộ quần áo khác. Tổng cộng **3–4 file mỗi mục tiêu**. Ngoài ra có 1 file thô (L0+L1) nằm trong một khung [mô hình, ngoại suy từ NIST/IJB‑A/MARS]. Nếu gửi ảnh thô thay vì embedding, cần 3–6 ảnh đa dạng, tức khoảng 90–900 khung liền nhau gom theo từng ảnh [mô hình]. Với 1–3 mục tiêu, số file tối thiểu một cluster phải gom về các nút xử lý là khoảng 3–12, tổng ~30–150 khung nếu dùng fp16, và chỉ vài chục khung nếu dùng mã 64 B [mô hình]. Hiệu ứng chéo phổ ngày/đêm chưa có nguồn. Chỉ gait có số cho điều kiện đổi quần áo: 62,7–68,3 % so với khoảng 94 % khi đi bình thường ([PMC7959613](https://pmc.ncbi.nlm.nih.gov/articles/PMC7959613/table/table-1)) [nguồn·trích].

---

## (9) Thô→mịn làm được, nhưng embedding phải được huấn luyện để cắt được

Matryoshka Representation Learning (MRL) chứng minh rằng tiền tố của *một* embedding gần chính xác bằng cả vector. Điều kiện là mô hình được huấn luyện cho việc đó. Cắt embedding thường sẽ sụp đổ:

| Số chiều | MRL 1‑NN % | Huấn luyện riêng ở chiều đó (FF) % | Cắt FF‑2048 ngẫu nhiên % |
|---|---|---|---|
| 8 | 62,19 | 58,93 | 2,36 |
| 16 | 67,91 | 66,77 | 12,06 |
| 64 | 70,17 | 69,41 | 49,91 |
| 512 | 70,82 | 70,18 | 68,77 |
| 2048 | 70,97 | 71,19 | 71,19 |

Nguồn: ([Kusupati et al., arXiv 2205.13147](https://arxiv.org/abs/2205.13147)) [nguồn]. SVD‑16 chỉ đạt 46,02 % (cùng nguồn) [nguồn]. Một số giá trị ở bảng phụ lục trích ra không rõ ràng; ghi chú partial_set đề nghị kiểm lại ([NeurIPS supp.](https://papers.neurips.cc/paper_files/paper/2022/file/c32319f4868da7613d78af9993100e42-Supplemental-Conference.pdf)). Lọc phễu 16 → … → 2048 "chính xác bằng tìm kiếm một lần 2048‑d nhưng hiệu quả hơn khoảng 128 lần về lý thuyết", và nhanh hơn khoảng 14 lần về thời gian thực (cùng nguồn) [nguồn]. Điểm yếu: toàn bộ bằng chứng MRL đến từ ImageNet, **chưa có kết quả MRL trên mặt hay re‑ID**.

Lớp thô nhất là thuộc tính, và một mình nó không đủ phân biệt. SAL truy vấn bằng vector thuộc tính chỉ đạt **R1 49,0 % / mAP 29,8 %** trên Market, so với mAP 84,0 % khi truy vấn bằng ảnh. Trung bình khoảng 26 ảnh huấn luyện có chung một mô tả thuộc tính ([SAL](https://arxiv.org/html/2007.09609v2)) [nguồn]. PAR trên PA‑100K đạt mA khoảng 83,5–88,0 % ([arXiv 2604.26873](https://arxiv.org/pdf/2604.26873), [arXiv 2509.22331](https://arxiv.org/pdf/2509.22331)) [nguồn·trích], tức mỗi thuộc tính sai khoảng 12–16 %. Nếu lọc cứng bằng phép hội trên nhiều thuộc tính thì sẽ thường xuyên loại nhầm chính mục tiêu. Nên lọc mềm, hoặc chỉ dùng 2–3 thuộc tính có độ tin cao như trẻ/người lớn và màu áo [mô hình].

| Lớp | Nội dung | Kích thước | Khung | Dùng khi chỉ nhận được đến lớp này |
|---|---|---|---|---|
| L0 | ID, cửa sổ thời gian, 26–65 bit thuộc tính | ≤ 16 B | chung 1 khung với header | Lọc trước gallery, không bao giờ kết luận |
| L1 | Tiền tố MRL 64‑d int8 hoặc PQ 16 B | 16–64 B | 1 | Xếp hạng shortlist |
| L2 | Template đã gộp, 512‑d fp16 | ~1 KB | ~11 | Khớp cuối cùng |
| L3 | Prototype theo điều kiện | ~1 KB mỗi cái | ~11 mỗi cái | Bền vững với góc nhìn, ánh sáng, quần áo |

Bảng phân lớp là thiết kế của nhóm [mô hình]. Kích thước lấy từ phép tính ở mục (4). Cách chia này khớp với quy tắc "file đủ mới dùng": L0/L1 là file một khung, gần như chắc chắn sống sót; L2/L3 là file nhiều khung. Không có nguồn nào so sánh fountain code với phân lớp với file độc lập cho dữ liệu truy vấn. Lập luận của ghi chú là: fountain code phù hợp cho L2/L3 vì xóa bỏ yêu cầu "chuỗi liền nhau", nhưng không cho gì dưới ngưỡng K(1+ε). L0/L1 quá nhỏ nên không cần fountain code [mô hình]. Overhead ε của LT/Raptor với K nhỏ trên 802.15.4 chưa được đo.

---

## (10) Nhận 20 % tập tham chiếu giữ được khoảng 95 % recall, nhưng chỉ khi đó là view đa dạng

Chưa có nghiên cứu nào thay đổi trực tiếp "tỉ lệ tập truy vấn nhận được". Các tương tự gần nhất là các đường template‑size và frames‑per‑tracklet ở mục (5). Ghi chú partial_set dựng một luật xấp xỉ: recall(f) ≈ recall(100 %)·(1 − c·e^(−fK/k₀)), với k₀ ≈ 2–3 view và c ≈ 0,15–0,2 [mô hình]. Với K = 15, f = 20 % (3 view) cho khoảng **95 % recall của trường hợp đầy đủ**. Từ f ≥ 50 % trở lên gần như bão hòa. Recall chỉ tụt mạnh khi còn **đúng 1 view** (f ≲ 7 %) [mô hình]. Độ bất định cũng lớn nhất khi template chỉ có 1 media, và độ phân tán điểm không giảm khi thêm media gần giống nhau ([Crosswhite et al.](https://ar5iv.labs.arxiv.org/html/1603.03958)) [nguồn]. Hệ quả cho lớp 2: thứ tự phát phải đưa **các view khác nhau nhất lên trước** [mô hình].

Mỗi biểu diễn có một nghĩa khác cho "tỉ lệ nhận được":

| Biểu diễn | "Phần nhận được" nghĩa là | Precision/recall khi nhận một phần | Nhãn |
|---|---|---|---|
| Ảnh thô (mỗi ảnh = 1 file) | Số ảnh nguyên vẹn | Theo đường template‑size: +19 % từ 1→64, bão hòa ~3 ([Crosswhite](https://ar5iv.labs.arxiv.org/html/1603.03958)) | [nguồn] / luật f: [mô hình] |
| Embedding float/int8 theo view | Số view nguyên vẹn | MARS: 75,0 % (2 khung) → 79,8 % (4), phẳng sau đó | [nguồn·trích] |
| Template đã gộp + prototype | Có/không L2; số L3 | NAN: AvePool 0,771 → NAN† 0,881 TAR@1e‑3 | [nguồn] |
| Tiền tố MRL | Tỉ lệ số chiều | 8/2048 chiều giữ 62,19/70,97 = 88 % độ chính xác 1‑NN; 64 chiều giữ ~99 % | [nguồn] (ImageNet) |
| Embedding thường bị cắt | Tỉ lệ số chiều | 16 chiều còn 12 %, SVD‑16 còn 46 % | [nguồn] |
| Mã băm nhị phân | Số bit | HashNet NUS‑WIDE 0,588/0,677/0,722/0,725 ở 16/32/48/64 bit ([arXiv 2510.18218](https://arxiv.org/pdf/2510.18218)); ImageNet‑100 0,506 → 0,683 ([arXiv 1808.01990](https://arxiv.org/pdf/1808.01990)) | [nguồn] |
| Chỉ thuộc tính | Chỉ có L0 | Market R1 49,0 %, mAP 29,8 % | [nguồn] |

Kích thước gallery tác động mạnh hơn tỉ lệ tham chiếu. NIST đưa ra **FPIR(τ) = 1 − (1 − FMR(τ))^N ≈ N·FMR(τ)** ([NIST implications for 1:N](https://pages.nist.gov/frvt/reports/demographics/implications_for_1N.pdf)) [nguồn]. Trên MegaFace, các thuật toán đạt trên 95 % ở quy mô LFW chỉ còn **35–75 % R1 khi có 1 triệu người gây nhiễu** ([Kemelmacher‑Shlizerman et al., CVPR 2016](https://ar5iv.labs.arxiv.org/html/1512.00596)) [nguồn]. Gallery G mỗi nút thay đổi hàng bậc độ lớn (chuông cửa so với cửa hàng ghi 24/7), trong khi k chỉ thay đổi tối đa khoảng 5 lần. Vì vậy **k·G là biến chính quyết định false alarm**, và nút phải báo cáo đại lượng này [mô hình].

---

## (15) Số bit tối thiểu do ngân sách phản hồi quyết định, và ngưỡng đặt khắt khe hơn mọi số đo hiện có

### Ngân sách phản hồi

LoRa ở duty 1 %, với một khe 0,4 s mỗi 40 s cho mỗi cluster, cho **90 khe uplink/giờ**. Vệ tinh vài trăm byte/giờ tương ứng khoảng **50–100 báo cáo vài byte** [mô hình, số học trên tham số đề bài]. Nếu mỗi cluster có 10 false alarm thì đã chiếm 10–20 % ngân sách vệ tinh một giờ. Quan trọng hơn, mỗi false alarm có thể kéo theo một chuyến UAV xác minh. Vì vậy mục tiêu hợp lý là **E[FA] ≤ 1 mỗi cluster**, và ≲ 0,1 khi có nhiều cluster [mô hình]. Phép tính này khớp với 2–3 điểm nghi vấn giả đã giả định trong giả lập trọn nhiệm vụ ở mục 68 của CLAUDE.md.

### Phép tính false alarm

Số phép so sánh là C = Q × G × n, với Q là số chữ ký truy vấn, G là số mục lưu mỗi nút, n là số nút. Điều kiện E[FA] ≈ C·FMR ≤ 1 cho ra bảng sau [mô hình]:

| Kịch bản | Q | G | n | C | FMR cần | log₂C (sàn lý thuyết thông tin) |
|---|---|---|---|---|---|---|
| Nhỏ | 1 | 10⁴ crop | 100 | 10⁶ | ≤ 1e‑6 | 19,9 bit |
| Cơ sở, theo tracklet | 5 | 10⁴ tracklet | 500 | 2,5·10⁷ | ≤ 4e‑8 | 24,6 bit |
| Cơ sở, theo crop | 5 | 10⁵ crop | 500 | 2,5·10⁸ | ≤ 4e‑9 | 27,9 bit |
| Lớn | 10 | 10⁶ crop | 1000 | 10¹⁰ | ≤ 1e‑10 | 33,2 bit |

Sàn log₂C chỉ đúng khi mọi cặp thật khớp tuyệt đối, nên không bao giờ đạt được trong thực tế. Muốn có số bit thực tế, mô hình hóa khoảng cách Hamming giữa hai người khác nhau bằng Binomial(N_eff, 0,5). Giả thiết này dựa trên Daugman: IrisCode 2 048 bit chỉ có **khoảng 249 bậc tự do**, và 9 060 003 cặp so sánh khớp Binomial(249, 0,5) với SD 0,0317 ([Daugman](https://www.cl.cam.ac.uk/~jgd1000/binomdata.html)) [nguồn]. Một thuật toán khác cho N = 352 ([arXiv 2306.12572](https://arxiv.org/pdf/2306.12572)) [nguồn]. Số bit hiệu dụng tối thiểu theo ngưỡng Hamming chuẩn hóa t như sau. Phép tính nhị thức chính xác đã được chạy lại khi viết báo cáo này và khớp với ghi chú [mô hình]:

| FMR mục tiêu | t = 0,25 | t = 0,30 | t = 0,35 |
|---|---|---|---|
| 1e‑6 (nhỏ) | 87 | 136 | 245 |
| 4e‑8 (cơ sở, tracklet) | 111 | 173 | 311 |
| 4e‑9 (cơ sở, crop) | 127 | 202 | 360 |

Nếu tỉ lệ bit hiệu dụng/bit danh nghĩa xấp xỉ 1 (ITQ đã khử tương quan), **mã 256 bit (32 B, 3 mã/khung) đủ cho kịch bản cơ sở theo tracklet khi t ≤ 0,30**, và **mã 512 bit (64 B, 1 mã/khung) đủ cho mức crop khi t ≈ 0,35**. Nếu độ dư giống mống mắt (khoảng 8:1) thì cần 2 048 bit danh nghĩa [mô hình]. Tỉ lệ này **chưa ai đo** cho ArcFace hay re‑ID nhị phân. t phụ thuộc độ phân tán của các cặp thật, tức phụ thuộc chất lượng crop, nên phải đo trên mô hình và dữ liệu của dự án. NIST xác nhận định tính rằng muốn giữ FPIR cố định khi gallery tăng (0,6 M → 12 M) thì ngưỡng phải tăng ([NIST report card](https://face.nist.gov/frte/reportcards/1N/hik_3.pdf)) [nguồn]. Giá trị cụ thể chưa trích được.

### Mâu thuẫn giữa các ghi chú: body re‑ID có đủ mạnh không?

Hai ghi chú đưa ra hai kết luận khác nhau. Ghi chú *task_and_modality* chọn body re‑ID làm kênh **chính**, dựa trên độ phủ camera và R1 82–95 %. Ghi chú *representation_bits* lập luận rằng re‑ID kém phân biệt hơn mặt rất nhiều, nên N_eff thấp hơn hẳn. Bằng chứng là mAP hashing thấp và mAP giảm một nửa khi thêm 500 K người gây nhiễu ([arXiv 1705.02145](https://ar5iv.labs.arxiv.org/html/1705.02145)) [nguồn]. Theo ghi chú này, re‑ID dùng một mình trên gallery 10⁵ trở lên "nhiều khả năng sinh nhiều false alarm mỗi cluster" và chỉ nên là bộ lọc trước [mô hình]. Ghi chú partial_set bổ sung một ví dụ: G = 10⁴, k = 20, tức M = 2·10⁵ phép so sánh. Ở FMR = 1e‑5, khoảng **86 %** số nút báo động giả. Muốn giữ 2 % thì cần FMR ≈ 1e‑7 [mô hình, đã kiểm lại số học].

**Cách hòa giải:** hai kết luận trả lời hai câu hỏi khác nhau, và cả hai đều đúng. Re‑ID là kênh *recall* tốt nhất, vì nó là modality duy nhất nhìn thấy mục tiêu ở đa số camera. Nhưng không modality nào, kể cả mặt, đạt FMR 10⁻⁸ ở mức crop trong điều kiện giám sát. Mặt ngoài thực địa thường chỉ được công bố ở khoảng 1e‑4 đến 1e‑6 [mô hình, theo ghi chú representation_bits]. Vậy re‑ID là kênh chính *để tìm*, không phải *để quyết định một mình ở mức crop*. Có bốn cơ chế đưa C·FMR về ≤ 1 mà không cần thêm bit, và ba cơ chế đầu bắt buộc:

1. Khớp theo **tracklet** thay vì crop. Việc này giảm G đi 10–100 lần, và trung bình hóa embedding làm phân bố cặp thật chặt hơn, cho phép t thấp hơn. FMR giảm theo hàm mũ khi t giảm [mô hình].
2. **Gộp mọi view của một mục tiêu thành một template trước khi khớp.** Khi đó Q là số mục tiêu, không phải số view, tránh nhân false alarm tuyến tính theo Q [mô hình]. Kết quả MaxPool so với AvePool của NAN cũng ủng hộ việc không lấy max theo view [nguồn].
3. **Cổng thuộc tính** (cỡ trẻ em, màu áo) và **cửa sổ thời gian**. Hai cổng này giảm G hiệu dụng [mô hình].
4. Yêu cầu k tracklet độc lập cùng khớp. FA giảm theo khoảng FMR^k, nhưng đây là ước lượng lạc quan vì người giống nhau có tương quan giữa các view [mô hình].

Kênh mặt ở chuông cửa đóng vai trò bằng chứng xác nhận, không phải kênh tìm kiếm. Phần còn lại do BS lọc bằng BH ở mục (16). Kết luận này vẫn là lập luận. Chừng nào chưa đo phân bố điểm impostor của re‑ID trên footage thật, không thể khẳng định re‑ID cộng ba cơ chế trên đạt E[FA] ≤ 1.

### Báo cáo vài byte

Payload đề xuất khoảng 6 B gồm: `llr_q` 1 B, `top_s` 1 B, `n_hit` 1 B, `log2_M` 1 B, `ref_frac` 4 bit, `q` 4 bit, `target_id` 1 B. Đây là đề xuất thiết kế, không phải chuẩn đã công bố [mô hình]. Với 90 khe/giờ, payload này dư chỗ trong một khe LoRa.

---

## (16) Ngưỡng tăng theo k·G, không theo việc nút nhận ít hay nhiều

Không nên để mỗi nút áp một ngưỡng cố định trên điểm thô. Nếu làm vậy, FPIR giữa các nút sẽ chênh nhau hàng bậc độ lớn, và chênh lệch đó do G quyết định [mô hình]. Câu hỏi "nhận ít tham chiếu thì nâng hay hạ ngưỡng" có hai lực ngược chiều. Ít tham chiếu nghĩa là ít phép so sánh, nên có thể hạ ngưỡng mà vẫn giữ FPIR (theo mục 10). Nhưng ít tham chiếu cũng làm điểm max nhiễu hơn, vì độ phân tán lớn nhất khi template có kích thước 1 ([Crosswhite et al.](https://ar5iv.labs.arxiv.org/html/1603.03958)) [nguồn]. Lời giải có nguyên tắc là đặt **FMR(τ) = α_node/(k·G)** theo Bonferroni/Šidák. Nút không tự đổi ngưỡng vì f, mà gửi `ref_frac` để BS chiết khấu bằng chứng [mô hình].

Văn liệu hỗ trợ ba thành phần của chính sách này. Thứ nhất là **chuẩn hóa điểm**: adaptive S‑norm trong xác minh người nói giảm EER tương đối 21 % và MinDCF 19,9 % ([arXiv 2007.07689](https://arxiv.org/pdf/2007.07689)) [nguồn]; AS‑norm có thể huấn luyện được giảm thêm 4,11 % ([arXiv 2504.04512](https://arxiv.org/html/2504.04512v1)) [nguồn]. Áp vào đây, nút dùng chính các crop của nó làm cohort impostor để hấp thụ lệch miền theo camera [mô hình]. Thứ hai là **LLR đã hiệu chỉnh**, dạng báo cáo được ENFSI khuyến nghị ([ENFSI Guideline](https://roebuckforensics.com.au/wp-content/uploads/2024/07/ENFSI-Guideline.pdf)) [nguồn]. Thứ ba là **kiểm soát FDR** Benjamini–Hochberg tại BS ([DOI 10.1111/j.2517‑6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)) [chưa kiểm]. Về luật gộp, Kittler et al. 1998 cho thấy **luật tổng (sum/mean)** ổn định nhất, còn luật tích dễ vỡ ([Kittler et al.](https://people.cs.pitt.edu/~chang/231/y14/combineclassifier.pdf)) [nguồn]. Áp vào đây: lấy trung bình theo tham chiếu của một mục tiêu; lấy max theo crop, có hiệu chỉnh Šidák p = 1 − (1 − p_single)^G; báo cáo riêng theo từng mục tiêu [mô hình]. Độ lớn embedding của MagFace là thước đo chất lượng tăng đơn điệu theo khả năng nhận dạng ([arXiv 2103.06627](https://arxiv.org/abs/2103.06627)) [nguồn]. Tuy vậy chưa tìm thấy luật đặt ngưỡng theo độ lớn này.

| | Ngưỡng cố định tại nút | Ngưỡng thích nghi tại nút + quyết định tại BS (đề xuất) |
|---|---|---|
| Biến điều khiển | Điểm thô cosine | FMR(τ) = α/(k·G) cho cổng; LLR + BH tại BS |
| FPIR giữa các nút | Chênh hàng bậc độ lớn theo G | Đồng đều ở α_node |
| Nút nhận ít tham chiếu | Không xét | Cổng hơi thấp hơn (M nhỏ hơn), LLR bị BS chiết khấu theo `ref_frac` |
| Thứ cần đo trước | Không | Phân bố điểm impostor và cặp thật của bộ khớp thực tế |
| Nhãn | — | [mô hình] trên nền [nguồn] S‑norm/ENFSI/Kittler |

---

## Phân tầng thiết bị biên: chỉ T1 trở lên quét kịp footage trước khi bị ghi đè

Số đo chia thành bốn dải tự nhiên. Ghi chú khuyên **giảm số của nhà sản xuất đi 2–3 lần**. Ví dụ Hailo‑8L: zoo công bố 182 FPS cho YOLOv8n, đo thực tế ở mức ứng dụng chỉ 61,9 FPS ([Hailo community](https://community.hailo.ai/t/yolov8n-real-performance-didnt-expected-from-hailo-model-zoo-documentation/18904)) [nguồn].

| Tầng | Ví dụ | Số đo then chốt | Nhãn |
|---|---|---|---|
| **T0 MCU** | ESP32‑S3, STM32N6, IMX500 | ESP32‑S3 embedding mặt 255 ms (MFN_S8_V1) ([Espressif](https://developer.espressif.com/workshops/edge-ai-with-esp32-s3/assignment-2/)), 287 ms int8 ([ESP‑DL](https://docs.espressif.com/projects/esp-dl/en/release-v1.1/esp32s3/performance.html)); STM32N6 YOLOv8n‑256 24,94 ms ([ST](https://huggingface.co/STMicroelectronics/yolov11n/blob/main/README.md)), 9,4 mJ/lần ([Ultralytics](https://www.ultralytics.com/customers/embedded-vision-ai-with-ultralytics-yolo-and-stmicroelectronics-mcu)); IMX500 tổng 8 388 480 B cho firmware, trọng số và bộ nhớ làm việc ([Hackster](https://hackster.io/news/raspberry-pi-s-ai-eye-hands-on-with-the-raspberry-pi-ai-camera-module-383fb34afcf7)) | [nguồn·trích] (NSX) |
| **T1 SoC camera 1–2 TOPS** | RV1126(B), Hi3516DV300, Ambarella CV28 | RV1126 2,0 TOPS ([CNX](https://cnx-software.com/2021/01/22/rockchip-rv1126-ai-camera-soc-features-2-0-tops-npu-promises-250ms-fast-boot)); RV1126B YOLOv8n‑640 24,0 FPS, RetinaFace‑mobile 144,8 FPS, CLIP không hỗ trợ ([RKNN zoo](https://github.com/airockchip/rknn_model_zoo)) | [nguồn·trích] (bảng cào lại) |
| **T2 SBC + bộ tăng tốc** | Pi 5 + Hailo‑8L, RK3588, Coral, hub/NVR | Hailo‑8L ArcFace‑MFN 1666 FPS, R50 93,2/300 FPS ở mức chip ([Hailo zoo](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_face_recognition.rst)); RK3588 CLIP ảnh 6,3 FPS; Coral SSD 6,5–14 ms ([Coral](https://www.coral.ai/docs/edgetpu/benchmarks)) | [nguồn·trích] / đo độc lập [nguồn] |
| **T3 Jetson Orin Nano Super** | Hộp biên Orin | 67/33 TOPS (sparse/dense), CLIP ViT‑B/32 314 FPS, B/16 161 FPS, 7–25 W ([NVIDIA](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules)) | [nguồn·trích] (NSX) |

Lượng footage cần quét được tính từ thời gian lưu trữ. Ở 2 Mbps, thẻ 128 GB giữ khoảng **5,5 ngày** ([Foscam](https://www.foscam.com/faqs/view.html?id=285)) [nguồn]. Eufy công bố 128 GB giữ khoảng 16 ngày ở 1080p ([Eufy](https://service.eufy.com/article-description/Learn-about-Continuous-Recording1)) [nguồn·trích]. Giả định lấy mẫu 1 khung/s và khoảng 2 crop mỗi khung. Bảng dưới gộp câu trả lời cho mọi câu hỏi theo từng tầng; mọi thông lượng trong bảng đều là [mô hình]:

| Tầng | Giờ video / giờ tính | Quét 132 h tồn kho | Câu hỏi (1) khả thi | Đơn vị (4) dùng được | Lớp (9) xử lý được | Ngưỡng (16) | Vai trò |
|---|---|---|---|---|---|---|---|
| T0 | ~1–2× | ~66–130 h, **không kịp** trước khi bị ghi đè; ESP32‑S3 có thể không có bộ giải mã H.264 (chưa kiểm) | Detection; khớp mặt chậm, chỉ trên luồng trực tiếp | int8 / 64 B; truy vấn ≤ ~100 KB | L0, L1 | Chỉ cổng, gửi cờ "đã thấy người" | Chuyển tiếp, không phải điểm xử lý |
| T1 | ~6–12× | ~11–22 h (có thể chỉ còn một nửa nếu bộ giải mã dùng chung với việc ghi hình) | Detection, face, **re‑ID** | Embedding mặt/re‑ID | L0–L2 | Cổng Bonferroni + LLR | Critical cell nếu quanh đó không có nút mạnh hơn |
| T2 | ~30–60× | ~2–4 h | Mọi loại trừ CLIP nhanh | Thêm ArcFace‑R50, RepVGG re‑ID | L0–L3 | S‑norm + LLR | CL / điểm xử lý chính |
| T3 | ~50–150× | ~1–3 h | Mọi loại, kể cả truy vấn văn bản/thuộc tính CLIP | Mọi định dạng | L0–L3 + CLIP | Đầy đủ | Ứng viên CH |

Ghi chú edge_devices đề xuất điểm năng lực theo thang log (T0 ≈ 1, T1 ≈ 10, T2 ≈ 50, T3 ≈ 100 giờ video/giờ tính) để gán cho thuộc tính "khả năng tính toán" của nút [mô hình]. Đặt cạnh nhau, các con số trên cho thấy giới hạn của lớp 1 là **thời gian quét**, không phải bit. Một chuông cửa T0 không quét kịp kho ghi liên tục trước khi bị ghi đè. Vì vậy chỉ các nút T1 trở lên mới là điểm xử lý thực sự cần nhận đủ file truy vấn [mô hình]. Hub như Eufy HomeBase 3 (Cortex‑A55, 16 GB eMMC) là nơi footage và chức năng nhận dạng mặt cục bộ cùng tồn tại ([eufy](https://www.eufy.com/eu-it/products/t80303d1)) [nguồn·trích]. Tỉ lệ thiết bị mỗi tầng trong một khu đô thị thực tế chưa được nghiên cứu.

---

## Đề xuất cho thực nghiệm

Thực nghiệm nên mô hình hóa lớp 1 như một **bài toán truy hồi open‑set bằng body re‑ID theo tracklet**. Mỗi mục tiêu được mô tả bằng 3–4 file đa dạng: 1 file L0+L1 trong 1 khung (thuộc tính + mã 64 B), 1 template L2 fp16 khoảng 11 khung, và 1–2 prototype L3. Thứ tự phát đặt view khác nhau nhất lên trước. Recall theo tỉ lệ nhận được dùng luật bão hòa ở mục (10), ghi rõ là [mô hình], cho tới khi có số đo. Nút xử lý chỉ gồm các nút T1 trở lên. Tiêu chí "đủ dữ liệu" của lớp 3 nên là "đủ L2 cho mỗi mục tiêu", còn "đủ cả L3" là mức tốt. Mỗi nút gửi về báo cáo 6 B (LLR đã hiệu chỉnh, log₂M, ref_frac). BS quyết định bằng BH và nhắm mục tiêu E[FA] ≤ 1 mỗi cluster. Có thể giữ 2–3 nghi vấn giả trong giả lập hiện có như một hệ quả của chính phép tính này, thay vì một giả định tự do. Thông số đầu tiên cần đo thật là **phân bố điểm impostor và cặp thật của bộ khớp re‑ID trên footage tracklet**: N_eff, t, và FMR ở 1e‑7–1e‑9. Thông số này quyết định đồng thời số bit ở mục (15), ngưỡng ở mục (16), và việc body re‑ID có đủ mạnh mà không cần kênh mặt hay không.

## Chưa kiểm chứng / cần đọc lại

| Mục | Vấn đề |
|---|---|
| NIST FRTE 1:N | Chưa trích được bảng FNIR theo cột (mugshot/webcam/profile) và độ dốc FNIR theo N (0,6 M → 12 M) trong NISTIR 8271 |
| LFW ≈ 99,8 %, AGW Market 95,1/87,8, IRRA/RDE, CASIA‑B > 90 % | [chưa kiểm], số nhớ, chưa mở lại |
| CLIP‑SCGI MSMT17 88,2/92,9 | Không khớp với aggregator, cần đọc bài gốc |
| MARS frames‑per‑tracklet, Market multi‑query, GaitSet 7 khung, PAR mA | Lấy từ đoạn trích, cần đối chiếu bảng gốc |
| Bảng phụ lục MRL (SVD‑8 = 19,14 %) | Trích ra không rõ ràng; MRL trên mặt/re‑ID chưa có |
| Drozdowski 2018, Jégou 2011 | Không đọc được toàn văn; chưa có TAR@1e‑4/1e‑6 cho ArcFace nhị phân hoặc 4‑bit trên IJB‑C |
| N_eff của mã mặt/re‑ID | Mô hình Binomial chỉ là giả định; tỉ lệ hiệu dụng/danh nghĩa "1–2×" chưa được đo |
| Kích thước JPEG crop mặt/người | Ước lượng không nguồn |
| NISTIR 8280 (trẻ em) | Câu chữ chưa đối chiếu với thân báo cáo; FNMR 0–5 tuổi do nhà cung cấp trích lại |
| AI Act Art. 5(1)(h), Art. 26(10); body re‑ID có phải dữ liệu sinh trắc học | Chưa đối chiếu với Official Journal; pháp luật Việt Nam chưa xét |
| Bảng RKNN zoo | Ghép cột từ bảng cào lại; RV1106, Hailo‑8, Ambarella TOPS, OSNet/SCRFD trên thiết bị chưa có số |
| Thông lượng quét theo tầng; khả năng giải mã H.264 của ESP32‑S3 | Toàn bộ là [mô hình], chưa có số đo end‑to-end |
| Chuỗi liên tục dài nhất 11/40/208/823 | Dự đoán giải tích trong CLAUDE.md, lạc quan khoảng 4 lần; cần số đo ns‑3 với N đủ lớn |
| Overhead ε của fountain code với K nhỏ trên 802.15.4 | Chưa có nguồn |
| BH 1995, Auckenthaler 2000 | Kiến thức sẵn có, chưa mở lại |
