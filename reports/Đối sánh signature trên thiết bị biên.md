# Ống kính, không phải con chip, làm lệch điểm khớp

Câu trả lời ngắn cho ba câu hỏi như sau. **(1) Có, cùng một bộ signature cho ra điểm khác nhau trên các thiết bị.** Tuy vậy phần chênh do chip, tức lượng tử hóa int8 trên NPU, chỉ cỡ **0,01–0,03 cosine**. Trên thang 70–90 % đã hiệu chỉnh, mức đó tương ứng khoảng **2–5 điểm phần trăm**, đúng cỡ ví dụ "70 % so với 75 %" của người dùng. Phần chênh do camera (quang học, ISP, nén, góc đặt) lớn hơn một bậc. Nó kéo điểm của cặp thật xuống và biến camera kém thành camera "luôn trả NO". Thiết bị chạy *mô hình khác* thì không so được điểm với nhau. **(2) Mất 1 trong 5 file tốn khoảng 0–2 điểm recall** nếu file mất là một view trùng lặp. Nếu file mất là view duy nhất khớp với góc nhìn của camera thì tốn **2–6 điểm** trong miền huấn luyện và **15–25 điểm** ngoài miền. File *nào* mất quan trọng hơn *bao nhiêu* file mất. **(3) "Dữ liệu đầy đủ cho kết quả gần như tuyệt đối" chỉ đúng với ảnh mặt tốt và biển số đọc được.** Body re‑ID cùng quần áo đạt khoảng 95 % Rank‑1, đổi quần áo còn 56–74 %, cá thể động vật 34–99 % tùy loài. Bộ lọc thô kiểu "áo vàng" đúng khoảng 74 % ban ngày và gần như vô dụng ban đêm. Về ngưỡng: "70–90 %" **không thể là cosine thô**. Với ArcFace, ngưỡng vận hành chỉ khoảng 0,30–0,45, nên ngưỡng cosine 0,7–0,9 loại bỏ phần lớn cặp thật. Con số này phải là một thang đã hiệu chỉnh, gắn với một FMR, ví dụ 70/80/90 % ↔ FMR 10⁻³/10⁻⁴/10⁻⁵. Ngay cả ở mức 90 %, một camera có 5 000 phép so sánh vẫn trả YES nhầm khoảng 5 % số lần. Vì vậy kết luận của báo cáo lớp 1 trước vẫn giữ: nút gửi LLR, BS quyết định.

**Quy ước nhãn**

| Nhãn | Nghĩa |
|---|---|
| **[nguồn]** | Số đọc được trực tiếp từ nguồn có link trong phiên nghiên cứu |
| **[nguồn·trích]** | Số lấy từ đoạn trích tìm kiếm, bảng cào lại, bài thứ cấp hoặc diễn đàn. Có link nhưng phải đối chiếu bản gốc trước khi đưa vào paper |
| **[NSX]** | Số do nhà sản xuất tự đo hoặc tự công bố |
| **[mô hình]** | Phép tính, khớp tham số hoặc ngoại suy của nhóm. Không phải số đo |

Báo cáo này nối tiếp *Nhận dạng tại node biên lớp 1* (gọi tắt là "báo cáo lớp 1"). Những gì báo cáo đó đã trình bày (chọn modality, số bit, phân tầng thiết bị T0–T3, phép tính E[FA] cho cluster) chỉ được dẫn lại khi cần. Báo cáo không đánh giá chuyện hợp tác giữa các nút có làm hệ thống nhanh hơn hay rẻ hơn không. Câu hỏi ở đây chỉ là một nút đã có file thì phán đoán đúng đến đâu.

---

## (A) "70–90 %" chỉ có nghĩa khi gắn với một tỉ lệ khớp nhầm

### Cosine thô không phải phần trăm, và các hãng mỗi nơi một thang

Cosine giữa hai embedding không phải xác suất. Ngưỡng cosine dùng được thì nằm thấp hơn nhiều so với 0,7. Với các gói ArcFace của InsightFace, ngưỡng xác minh 1:1 điển hình là **0,30–0,45 tại FMR = 10⁻⁴–10⁻⁵**. Giá trị này phải tính lại cho từng backbone, dữ liệu huấn luyện và quần thể. Cách tính là lấy phân vị (1 − FMR) của phân bố impostor trên tập kiểm định, với ít nhất 10/FMR cặp khác người. Hướng dẫn của InsightFace gọi một ngưỡng không kèm FMR là "vô nghĩa" ([InsightFace](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)) [nguồn]. Trên tập mặt cải trang DFW2019, điểm của cặp thật và cặp giả lẫn vào nhau ở khoảng **0,3–0,4** ([ArcFace DFW, ICCVW 2019](https://openaccess.thecvf.com/content_ICCVW_2019/papers/DFW/Deng_ArcFace_for_Disguised_Face_Recognition_ICCVW_2019_paper.pdf)) [nguồn]. Với re‑ID, ngưỡng tối ưu trên *khoảng cách* chuẩn hóa về [0,1] dao động **0,16–0,49 tùy mô hình**: MobileNetV2 0,27, BagTricks 0,16–0,20, AGW 0,47–0,49 trên Market/Duke, và 0,32–0,43 trên VeRi‑776 ([Wang et al., arXiv 2011.11506](https://ar5iv.labs.arxiv.org/html/2011.11506)) [nguồn]. Với động vật, chưa tìm thấy ngưỡng cosine cố định nào được công bố. WildFusion nói rõ điểm cosine toàn cục "không thể gộp với khớp cục bộ nếu không hiệu chỉnh" ([arXiv 2408.12934](https://arxiv.org/pdf/2408.12934v1)) [nguồn·trích]. Người tham gia AnimalCLEF dùng ngưỡng riêng cho từng loài ([CEUR Vol‑4283](https://ceur-ws.org/Vol-4283/paper368.pdf)) [nguồn·trích].

Các con số "phần trăm" của các hãng là ánh xạ đơn điệu riêng của từng hãng. AWS Rekognition đặt `FaceMatchThreshold` mặc định **80 %** ([AWS API](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_SearchFacesByImage.html)) [NSX]. Cho an ninh công cộng, AWS khuyến nghị **≥ 99 % kèm người duyệt**. Riêng cho tìm người mất tích, AWS khuyên dùng ngưỡng **thấp hơn 99 %** để có tập ứng viên rộng hơn, và đăng ký nhiều ảnh của người đó để giảm báo nhầm ([AWS public safety](https://docs.aws.amazon.com/rekognition/latest/dg/considerations-public-safety-use-cases.html)) [NSX]. Azure Face Verify trả `isIdentical` khi confidence ≥ **0,5** ([Azure](https://learn.microsoft.com/en-us/javascript/api/@azure-rest/ai-vision-face/verificationresultoutput)) [NSX]. Microsoft Entra Face Check dùng ngưỡng mặc định **70 %** ([Campus Technology](https://campustechnology.com/articles/2024/08/16/microsoft-releases-face-check-identity-verification-for-enterprise-use.aspx)) [nguồn·trích]. Cùng một cặp ảnh có thể là "YES" ở Azure và "NO" ở AWS. Không hãng nào công bố cách ánh xạ similarity sang phần trăm. Kịch bản của dự án (tìm trẻ lạc, nhiều ảnh tham chiếu) khớp đúng với tình huống mà AWS khuyên hạ ngưỡng và dùng nhiều ảnh.

### Giả định của người dùng đứng vững ở đâu, và chỗ nào nguồn phản bác

Giả định "điểm khớp trên 70–90 % thì YES" **đứng vững nếu 70–90 % là một thang đã hiệu chỉnh**. Nó **sai nếu hiểu là cosine thô**. Để thấy mức sai, nhóm khớp một mô hình Gauss cho mặt (ArcFace R100) vào các điểm neo có nguồn. Impostor có phân bố N(0; 0,10). Cặp thật trên ảnh rõ có phân bố N(0,58; 0,12), khớp với TAR ≈ 96 % tại FAR 10⁻⁴ trên IJB‑C ([InsightFace](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)) [mô hình neo vào nguồn]. Với mô hình này, ngưỡng cosine **0,7 chỉ giữ 16 % cặp thật** trên ảnh rõ và 3 % trên ảnh giám sát (μ = 0,48). Ngưỡng **0,9 giữ chưa tới 0,4 %** [mô hình]. Như vậy, một bộ quyết định áp nguyên 0,7–0,9 lên cosine sẽ gần như luôn trả NO. Nó hiếm khi báo nhầm, nhưng bỏ sót gần hết.

Thang đề xuất là **phương án B**: neo **70 % ↔ FMR 10⁻³, 80 % ↔ 10⁻⁴, 90 % ↔ 10⁻⁵**. Thang này gần với cách AWS/Azure vận hành, ngưỡng cao hơn thì ít khớp nhầm hơn. Phương án A là xác suất hậu nghiệm đã hiệu chỉnh tại prior cân bằng (80 % ≡ LR = 4). Phương án này kém tự nhiên vì prior thật của một crop là mục tiêu cực nhỏ. Với mô hình mặt ở trên, ba mốc 70/80/90 % rơi vào cosine **0,31 / 0,37 / 0,43**, cho TPR trên ảnh rõ lần lượt là **0,99 / 0,96 / 0,89** và trên ảnh giám sát **0,92 / 0,82 / 0,66** [mô hình]. Hiệu chỉnh từ điểm thô sang thang này là kỹ thuật chuẩn: logistic/Platt hoặc beta calibration. FairCal gọi beta calibration là "phương pháp khuyến nghị cho điểm bị chặn" như cosine ([FairCal, arXiv 2106.03761](https://ar5iv.arxiv.org/html/2106.03761)) [nguồn]. Hiệu chỉnh "phân loại" có thêm chất lượng ảnh làm biến phụ cải thiện cả độ hiệu chỉnh lẫn xác minh trên SCface, một tập camera giám sát ([Mandasari et al., IET Biometrics 2014](https://infoscience.epfl.ch/record/198437?ln=en)) [nguồn].

### YES/NO theo từng lớp mục tiêu: ngưỡng phải riêng cho từng lớp

Một ngưỡng chung cho mọi lớp sẽ cho tỉ lệ khớp nhầm khác nhau giữa các lớp. Ngay trong một lớp, ngưỡng chung đã tạo chênh lệch: ở FPR toàn cục 5 %, tỉ lệ khớp nhầm giữa hai nhóm nhân khẩu học chênh khoảng **15 lần**, và FairCal kéo về khoảng **1,2 lần** ([FairCal](https://ar5iv.arxiv.org/html/2106.03761)) [nguồn]. Bảng dưới gộp hành vi của câu trả lời YES/NO theo lớp. Các cột TPR là khớp tham số của nhóm, neo vào số có nguồn.

| Lớp mục tiêu | Điểm neo có nguồn | Hành vi YES/NO tại "80 %" (FMR 10⁻⁴) | Nhãn |
|---|---|---|---|
| Mặt, ảnh rõ | IJB‑C TAR@10⁻⁴ ≈ 96–97,5 % (R100), 90–93 % (mobile MBF) ([InsightFace](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)) | TPR ≈ 0,96; mobile thấp hơn vài điểm, có thể chênh hai chữ số ở nhóm khó | [nguồn] / TPR [mô hình] |
| Mặt, ảnh giám sát | FNMR 5–8 % tại FMR ≤ 10⁻⁶ trên tập khó (số nội bộ InsightFace) | TPR ≈ 0,82 | [NSX] / [mô hình] |
| Người, toàn thân | mReP đỉnh chỉ 58–81 % ngay tại ngưỡng tốt nhất ([arXiv 2011.11506](https://ar5iv.labs.arxiv.org/html/2011.11506)); đổi quần áo Rank‑1 99,8 → 41,8 % (PCB, PRCC) ([arXiv 2501.05851](https://arxiv.org/pdf/2501.05851)) | d′ ≈ 2,5–3; TPR ≈ 0,7–0,85 ở FMR 10⁻³; đổi quần áo ×0,4–0,65 | [nguồn] / [mô hình] |
| Xe, nhìn ngoại hình | mReP đỉnh 58–69 % trên VeRi‑776 | d′ ≈ 2,5; TPR ≈ 0,7–0,8 cùng góc nhìn; khác góc thấp hơn (chưa có số) | [nguồn] / [mô hình] |
| Động vật (cá thể) | Open‑set ARI ≈ 0,20 (AnimalCLEF 2026 baseline) | d′ ≈ 1,5–2; TPR ≈ 0,4–0,6 ở FMR 10⁻³; ngưỡng theo loài | [nguồn·trích] / [mô hình] |

Rank‑1 không phải TPR tại FAR cố định. Dùng Rank‑1 làm đại diện là một giả định, và ở FAR chặt thì giả định này lạc quan.

### Một camera có nhiều phép so sánh, nên "90 %" vẫn chưa đủ chặt

Ngưỡng 70–90 % được định nghĩa trên *một* phép so sánh. Câu trả lời YES lại được đưa ra cho *cả kho* của camera. Với N crop (hoặc tracklet) và k file signature, xác suất camera trả YES nhầm là P = 1 − (1 − f)^(N·k), với f là FMR một phép so sánh. NIST dùng FPIR cho 1:N vì false positive tăng theo kích thước gallery ([NIST FRTE](https://face.nist.gov/frte/reportcards/1N/psl_002.pdf)) [nguồn]. Bảng dưới giả định các phép so sánh độc lập [mô hình]:

| Thang hiệu chỉnh | f mỗi phép so sánh | 100 tracklet × 1 | 1 000 crop × 1 | 1 000 crop × 5 file |
|---|---|---|---|---|
| 70 % | 10⁻³ | 9,5 % | 63 % | **99,3 %** |
| 80 % | 10⁻⁴ | 1,0 % | 9,5 % | 39 % |
| 90 % | 10⁻⁵ | 0,1 % | 1,0 % | 4,9 % |

Đọc bảng: ở mức 70 %, gần như mọi camera có kho 1 000 crop đều trả YES nhầm khi so với 5 file. Ở mức 90 %, cứ khoảng 20 camera thì có một camera báo nhầm. Khi crop trong cùng một track tương quan nhau, tỉ lệ thật nằm giữa f × (số tracklet) và f × N. Hai hệ quả. Thứ nhất, ngưỡng phải tính từ ngân sách YES nhầm *mỗi camera* bằng hiệu chỉnh kiểu Šidák, f = 1 − (1 − FY_target)^(1/(N·k)), không phải chọn tay một mức trong 70–90 %. Thứ hai, ở mức cluster (10⁷–10¹⁰ phép so sánh), báo cáo lớp 1 đã tính FMR cần đạt là 10⁻⁸–10⁻¹⁰, vượt xa thang 70–90 %. Do đó YES/NO tại nút chỉ nên là **cổng gửi báo cáo**. Kết luận nghi vấn thuộc về BS, làm bằng LLR và kiểm soát FDR như báo cáo lớp 1 đã đề xuất.

---

## (B) Giữa các thiết bị: chip lệch vài điểm, camera lệch hàng chục điểm, khác mô hình thì không so được

Câu hỏi "cùng bộ tham chiếu, thiết bị này 70 %, thiết bị kia 75 %" có ba nguồn gây chênh, lớn dần như sau.

### Cùng mô hình, khác phần cứng và độ chính xác số

Cùng một mô hình fp32 **không cho kết quả giống hệt từng bit** trên các phần cứng khác nhau. Phép cộng dấu phẩy động không có tính kết hợp, và mỗi kiến trúc chọn kernel với thứ tự cộng dồn riêng. Với LLM, chỉ đổi loại GPU, số GPU hoặc batch đã làm độ chính xác lệch tới 9 % ([arXiv 2506.09501](https://alphaxiv.org/abs/2506.09501)) [nguồn]. Con số này không chuyển sang được bài toán của dự án. Ở LLM, sai số mức bit cuối bị khuếch đại qua hàng nghìn bước sinh token. Ở đây chỉ có một lượt CNN rồi một tích vô hướng đã chuẩn hóa. Vì vậy chênh lệch cosine dự kiến **≪ 0,001** với fp32 và khoảng **0,001–0,005** khi so fp16 với fp32 [mô hình, chưa ai đo].

Lượng tử hóa int8 mới là nguồn chênh đáng kể về số học. Các bảng zoo cho thấy độ chính xác benchmark gần như không đổi. Hailo‑8 báo arcface_mobilefacenet LFW 99,4 → 99,4 % và arcface_r50 99,7 → 99,7 % khi chuyển sang int8 ([Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_face_recognition.rst)) [NSX]. ONNX zoo báo ArcFace R100 int8 giảm 0 % trên LFW ([onnxmodelzoo](https://huggingface.co/onnxmodelzoo/arcfaceresnet100-11-int8)) [NSX]. Trên IJB‑C, R50 w8a8 đạt 94,13 % TAR@10⁻⁴ ([Ef‑QuantFace, arXiv 2402.18163](https://arxiv.org/abs/2402.18163)) [nguồn·trích, cột bảng bị lỗi khi trích]. Mốc fp32 tham chiếu là R100 95,6 % ([ArcFace CVPR 2019](https://openaccess.thecvf.com/content_CVPR_2019/papers/Deng_ArcFace_Additive_Angular_Margin_Loss_for_Deep_Face_Recognition_CVPR_2019_paper.pdf)) [nguồn]. Nhưng "giảm 0 điểm" ở đây là độ chính xác *sau khi chọn lại ngưỡng tối ưu* cho từng biến thể, trên LFW vốn đã bão hòa. Nó chỉ chứng tỏ thứ hạng được giữ, không chứng tỏ điểm giữ nguyên. Số đo duy nhất về điểm là của một người thực hành: ArcFace biên dịch qua toolchain Hailo sang int8 lệch **+0,025 cosine** sau khi khớp lại ngưỡng, trong khi riêng việc lấy mẫu lại các cặp đánh giá đã làm ngưỡng fp32 dao động **±0,017** ([Towards Data Science](https://towardsdatascience.com/the-number-your-quantization-gate-doesnt-have/)) [nguồn·trích: trang trả 403, chỉ đọc được đoạn trích]. Tác giả cảnh báo rằng giữ nguyên ngưỡng fp32 trên mô hình int8 có thể làm FAR trông tốt hơn trong khi che giấu false reject tăng. Khi biên dịch hỏng thì sai lệch rất lớn: một chuyển đổi PyTorch → ONNX → RKNN trên RK3588 tụt "như vách đá" 20–30 % ([CSDN/GitCode](https://gitcode.csdn.net/6a277c7110ee7a33f279960f.html)) [nguồn·trích, diễn đàn], và TVM với hiệu chỉnh KL sai làm ResNet‑50 rơi từ 76,25 % xuống khoảng 50–55 % ([TVM forum](https://discuss.tvm.apache.org/t/quantization-accuracy-drop-with-kl-divergence/5642)) [nguồn·trích]. RKNN‑Toolkit2 có sẵn `accuracy_analysis`, cho cosine từng lớp giữa đầu ra float và đầu ra lượng tử, chạy được trên chính NPU ([Rockchip](https://dl.radxa.com/rockpin10/docs/sw/rknn-toolkit/Rockchip_Quick_Start_RKNN_Toolkit_V1.3.0_EN.pdf)) [NSX]. Vì vậy độ lệch này **đo được cho từng loại thiết bị** trước khi triển khai.

**Quy đổi sang ví dụ 70 % so với 75 %** [mô hình]. Trên thang phương án B với mô hình mặt ở mục (A), đoạn 70→80 % ứng với 0,06 cosine, tức độ dốc khoảng 9 logit mỗi đơn vị cosine. Chênh **5 điểm phần trăm (70 → 75 %) tương đương khoảng 0,028 cosine**, gần đúng bằng độ lệch int8 +0,025 ở trên. Câu trả lời cho ví dụ của người dùng vì thế là **có, và cỡ đó là thực tế**. Hai thiết bị cùng mô hình, một chạy fp16 và một chạy int8 biên dịch tốt, có thể cho 70 % và 75 % trên cùng một cặp. Cũng trong mô hình này, lệch ±0,025 làm FMR thực tế tại mốc "80 %" thay đổi khoảng **2,6–2,8 lần** (2,8·10⁻⁴ hoặc 3,9·10⁻⁵ thay vì 10⁻⁴), trong khi TPR trên ảnh rõ chỉ đổi khoảng 2 điểm (0,94 hoặc 0,97 thay vì 0,96). Như vậy độ lệch do chip ảnh hưởng tới phía khớp nhầm nhiều hơn phía bỏ sót. Nó chỉ lật YES/NO với những cặp vốn đã nằm cách ngưỡng khoảng 0,03.

### Camera, ISP, độ phân giải và nén làm cặp thật mất hàng chục điểm

Chênh lệch từ phía ảnh lớn hơn phía chip một bậc. Re‑ID đổi miền là trường hợp rõ nhất: ResNet‑50 đạt 92,6 % Rank‑1 trên Market‑1501 nhưng chỉ còn **37,6 %** khi thử thẳng trên DukeMTMC (khoảng −55 điểm) ([arXiv 2101.01215](https://arxiv.org/pdf/2101.01215)) [nguồn·trích]. Các bài khác báo 27,3–31,8 % cho Market→Duke ([arXiv 1807.11334](https://arxiv.org/pdf/1807.11334), [arXiv 2007.15560](https://arxiv.org/pdf/2007.15560)) [nguồn·trích, chưa đối chiếu từng dòng]. Ngay trong một tập dữ liệu, mỗi camera đã được xử lý như một miền riêng ([arXiv 2208.08624](https://arxiv.org/pdf/2208.08624)) [nguồn]. Về nén, Schlett et al. cho thấy dưới khoảng 5 kB, JPEG XL giữ điểm nhận dạng mặt tốt hơn JPEG, còn ở kích thước lớn hơn thì khác biệt không đáng kể ([arXiv 2302.12593](https://arxiv.org/abs/2302.12593)) [nguồn]. Nén có mất mát hại ArcFace nhiều hơn ở người da sẫm màu, tới 34,55 % ([Unite.AI](https://www.unite.ai/jpeg-compression-increases-facial-recognition-error-rate-for-non-caucasian-faces-study-finds/)) [nguồn·trích, bài tóm tắt báo chí]. Chất lượng ảnh và điểm khớp liên hệ gần tuyến tính: QMagFace khai thác quan hệ này để tạo điểm có xét chất lượng ([QMagFace, WACV 2023](https://openaccess.thecvf.com/content/WACV2023/papers/Terhorst_QMagFace_Simple_and_Accurate_Quality-Aware_Face_Recognition_WACV_2023_paper.pdf)) [nguồn]. MagFace cho thấy FNMR@FMR 10⁻³ giảm khi loại bỏ mẫu chất lượng thấp ([MagFace, CVPR 2021](https://openaccess.thecvf.com/content/CVPR2021/papers/Meng_MagFace_A_Universal_Representation_for_Face_Recognition_and_Quality_Assessment_CVPR_2021_paper.pdf)) [nguồn].

Chưa có nguồn nào cho ra mức tụt cosine của cùng một người giữa crop chính diện, sáng tốt và crop nhỏ, nén, lệch góc. Ước lượng của nhóm là **0,1–0,4 cosine** [mô hình, chưa kiểm chứng]. Điều có cơ sở hơn là *hướng* của độ lệch. Nó **chủ yếu kéo điểm cặp thật xuống và đi kèm chất lượng ảnh**, chứ không phải nhiễu đối xứng. Với ngưỡng cố định, camera chuông cửa kém hay camera đặt cao trở thành "luôn trả NO", tức bỏ sót có hệ thống, chứ không trả lời ngẫu nhiên. Điểm này quan trọng cho lớp 3: chọn critical cell theo "khả năng tính toán" mà bỏ qua chất lượng ống kính có thể chọn trúng nút không bao giờ trả YES được.

### Khác mô hình: không có "chênh lệch", chỉ có không tương thích

Nếu chuông cửa chạy mô hình mặt riêng của hãng còn hub chạy ArcFace, cosine giữa embedding của hai bên **không có nghĩa**, chỉ ở mức impostor [mô hình]. Embedding từ hai mô hình huấn luyện độc lập chỉ so được với nhau nếu được huấn luyện để tương thích, như BCT (backward‑compatible training) ([Shen et al., CVPR 2020](https://openaccess.thecvf.com/content_CVPR_2020/html/Shen_Towards_Backward-Compatible_Representation_Learning_CVPR_2020_paper.html)) [nguồn]. Đây là yêu cầu giao thức, không phải dung sai: signature phải mang **trường model ID**, và BS phải gửi signature riêng cho từng họ mô hình có trong cluster. Nếu không, nút chạy mô hình khác bị loại khỏi tập nút xử lý. Trong ngân sách 4–5 KB, làm vậy có nghĩa là hoặc giảm số view cho mỗi họ, hoặc thống nhất một họ mô hình cho cả cluster.

### Ngân sách chênh lệch giữa các thiết bị

| Nguồn chênh | Ảnh hưởng lên điểm (cosine) | Trên thang 70–90 % | Độ mạnh bằng chứng |
|---|---|---|---|
| Cùng mô hình fp32, khác CPU/GPU | ≪ 0,001 | ≈ 0 | Cơ chế có nguồn; độ lớn [mô hình] |
| fp16 so với fp32 | ≈ 0,001–0,005 | < 1 điểm | [mô hình] |
| int8 PTQ biên dịch tốt (Hailo, TensorRT, RKNN, Edge TPU) | ≈ 0,01–0,03, có thể lệch một chiều | ≈ 2–5 điểm; FMR ×≈2,7 | Một số đo +0,025 [nguồn·trích]; zoo ≤ 0,5–1 điểm độ chính xác [NSX] |
| Biên dịch hỏng, int4, op không hỗ trợ | Tới sụp độ chính xác 20–30 điểm | Mất tác dụng | [nguồn·trích] diễn đàn |
| Camera, ISP, độ phân giải, nén | ≈ 0,1–0,4, chủ yếu kéo cặp thật xuống | Hàng chục điểm | Re‑ID đổi miền −45 đến −55 điểm Rank‑1 [nguồn·trích]; dải cosine [mô hình] |
| Khác phiên bản hoặc backbone | Không so được (≈ mức impostor) trừ khi có BCT | Vô nghĩa | [nguồn] BCT |

Chưa có nghiên cứu nào đo phương sai điểm theo thiết bị trên một đội camera IoT không đồng nhất chạy chung một mô hình. Đây là một khoảng trống, và có thể thành một đóng góp phụ của paper nếu dự án tự đo được.

---

## (C) Mất 1–2 file: file nào mất quan trọng hơn mất bao nhiêu

### Đường cong số tham chiếu bão hòa ở khoảng 3–4

Lợi ích lớn nằm ở bước từ 1 lên vài tham chiếu. Trên Market‑1501, dùng mọi ảnh query của một người thay vì một ảnh đưa ResNet‑50 từ 79,51 lên 85,84 % Rank‑1 và từ 59,87 lên 70,33 % mAP ([Zheng et al., arXiv 1611.05666](https://ar5iv.labs.arxiv.org/html/1611.05666)) [nguồn]. Trên IJB‑A, điểm xác minh ở FAR 10⁻² tăng khoảng 19 % từ 1 lên 64 media mỗi template và "bão hòa ở khoảng 3 media" ([Crosswhite et al., arXiv 1603.03958](https://ar5iv.labs.arxiv.org/html/1603.03958)) [nguồn]. Trong FRVT 2002, gộp điểm từ năm ảnh mỗi người giảm lỗi xác minh khoảng một nửa ([NISTIR 7083](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7083.pdf)) [nguồn, thế hệ thuật toán cũ]. Video re‑ID trên MARS đạt 75,0 % với 2 khung, 79,8 % với 4, 78,6 % với 8 ([Mekhazni et al., WACV 2023 supp.](https://openaccess.thecvf.com/content/WACV2023/supplemental/Mekhazni_Camera_Alignment_and_WACV_2023_supplemental.pdf)) [nguồn·trích]. FRVT 1:N 2021 còn ghi nhận rằng ảnh *mới* có giá trị hơn ảnh *nhiều* ([NIST FRVT 1:N](https://pages.nist.gov/frvt/reports/1N/frvt_1N_report_2021_03_04.pdf)) [nguồn]. Những con số này là **cận trên** của cái giá khi rút từ 5 xuống 1. Bước 5 → 4 và 5 → 3 nằm trên đoạn phẳng của đường cong, khớp với kết luận "3–4 view đa dạng là đủ" của báo cáo lớp 1. Lưu ý: dữ liệu multi‑query và MARS gần như là các view trùng nhau cùng camera. Chúng đo hiệu ứng trung bình hóa nhiễu, không đo độ phủ góc nhìn.

### Mất đúng view mà camera nhìn thấy mới là cú tụt lớn

Camera của nút có góc nhìn cố định: chuông cửa thấy mặt trước, camera phố thấy mặt bên hoặc phía sau. Sun & Zheng loại bỏ các cặp thật trong khoảng ±10–40° quanh góc nhìn của query và thấy mAP tụt **khoảng 3 %** trên Market‑1203 và khoảng 1 % trên PersonX45 so với loại bỏ ngẫu nhiên. Ở độ phân giải thấp, mức tụt **gần gấp đôi**. View nghiêng trái/phải là tham chiếu đơn lẻ có giá trị nhất: Rank‑1 93,8 % ở góc trái so với 91,7 % chính diện ([Sun & Zheng, CVPR 2019](https://ar5iv.labs.arxiv.org/html/1812.02162)) [nguồn]. Với xe, Ben Mabrouk et al. đổi gallery từ cùng góc sang khác góc (trước ↔ sau). Trên các loại xe đã thấy khi huấn luyện, mAP chỉ giảm 2–6 điểm (TransReID 93,1 → 89,7). Trên loại xe chưa thấy, mAP giảm **20–25 điểm** (TransReID 66,5 → 46,6; RotTrans 68,8 → 44,5) ([arXiv 2606.01981](https://arxiv.org/html/2606.01981)) [nguồn, preprint 06/2026]. Lý do: khớp cùng góc dựa vào chi tiết như nhãn dán, vết xước, logo, còn khớp khác góc phải dựa vào màu và những đặc trưng ít phân biệt hơn.

| Trường hợp | 5 → 4 file: recall tại FAR cố định | 5 → 3 file | Cơ sở |
|---|---|---|---|
| File mất là view trùng lặp (camera vẫn còn view khớp) | **−0 đến −2 điểm** | −1 đến −4 điểm | Bão hòa ở ~3–4 (IJB‑A, MARS) |
| Mất view duy nhất khớp camera; người, trong miền, ảnh rõ | −1 đến −3 điểm | Như 5 → 4 nếu file mất thứ hai là trùng lặp | Sun & Zheng [nguồn] |
| Như trên; xe, trong miền | −2 đến −6 điểm | Như trên | Ben Mabrouk 2026 [nguồn] |
| Mất view khớp; ngoài miền hoặc độ phân giải thấp (người ngoài thực địa, xe lạ, động vật) | **−15 đến −25 điểm** (≈ 30–35 % tương đối) | Bằng hoặc tệ hơn | Ben Mabrouk (loại chưa thấy); Sun & Zheng (×2 khi phân giải thấp) |
| Mất cả view khớp lẫn view gần nhất | — | Như dòng trên, thêm −2 đến −5 điểm | [mô hình] |

Toàn bộ bảng là **[mô hình]**, ngoại suy từ các điểm neo có nguồn. Chưa bài nào đo đúng 5 → 4 → 3 file khác góc nhìn. Các điểm neo chủ yếu là mAP hoặc Rank‑1, không phải TAR@FAR. Ở FAR chặt (≤ 10⁻³), TAR thường tụt mạnh hơn mAP, nên các con số trên là phía lạc quan. Với file "điều kiện" (ban đêm/IR, bộ quần áo khác), chưa nguồn nào đo trường hợp mất file. Giả định của nhóm là nó giống trường hợp view: tụt lớn khi đó là file duy nhất khớp điều kiện [mô hình]. Công thức cho giả lập [mô hình]: recall₄ ≈ recall₅ − [(1 − p_view)·δ_red + p_view·δ_view], với δ_red ≈ 1 điểm, δ_view ≈ 4 điểm trong miền hoặc 20 điểm ngoài miền, và p_view là xác suất file mất đúng là file khớp góc nhìn của camera.

### Cách gộp điểm quyết định ngưỡng có còn đúng khi thiếu file

Hai ghi chú nghiên cứu kéo về hai phía. Phía thứ nhất: nếu điểm là **max** qua các file, bỏ một file chỉ có thể làm điểm của cả cặp thật lẫn impostor giảm hoặc giữ nguyên. Do đó FAR tại ngưỡng đã hiệu chỉnh cho 5 file không tăng khi còn 4 hay 3 file, chỉ recall giảm [mô hình, suy diễn]. Nếu dùng **template trung bình**, bỏ một view không khớp có thể *tăng* điểm cặp thật, còn điểm impostor dịch chuyển theo cả hai chiều. Khi đó ngưỡng hiệu chỉnh cho 5 file không còn đảm bảo FAR cho 4 file [mô hình]. Phía thứ hai: báo cáo lớp 1 đã dẫn bảng NAN trên IJB‑A, nơi chọn "cặp tốt nhất" (min L2, tức max điểm) chỉ đạt **TAR@10⁻³ = 0,038**, so với 0,771 khi lấy trung bình ([NAN, arXiv 1603.05474](https://arxiv.org/abs/1603.05474)) [nguồn]. Lấy max qua k file cũng nhân số phép so sánh lên k lần, tức k lần cơ hội khớp nhầm.

Hai bằng chứng này không mâu thuẫn thật. Max có tính **đơn điệu khi mất file**, nhưng phân biệt kém ở FAR thấp. Trung bình phân biệt tốt hơn, nhưng **ngưỡng phải hiệu chỉnh lại theo tập file đang giữ**. Lưu ý thêm: bảng NAN gộp hàng chục media chất lượng lẫn lộn, còn 3–5 file signature đã được chọn lọc, nên khoảng cách giữa max và trung bình ở đây có lẽ nhỏ hơn [mô hình]. Phương án dung hòa đề xuất [mô hình]. Lấy trung bình điểm theo các file của cùng một mục tiêu (luật tổng, vốn ổn định nhất theo Kittler et al. 1998 trong báo cáo lớp 1). BS hiệu chỉnh trước ngưỡng cho từng tổ hợp file có thể thiếu: với 5 file chỉ có 5 tổ hợp thiếu một file và 10 tổ hợp thiếu hai file. Nút gửi về **bitmap 5 bit các file đang giữ** thay cho trường `ref_frac` 4 bit trong báo cáo 6 B của báo cáo lớp 1. Như vậy BS biết chính xác nút thiếu file *nào* chứ không chỉ thiếu *bao nhiêu*, đúng với kết luận "file nào mất quan trọng hơn".

### Hệ quả cho lớp 2 và lớp 3

Việc mất file trong hệ thống này không ngẫu nhiên đều. Một file fp16 1 KB chiếm khoảng 11 khung 99 B, và chỉ dùng được khi nhận đủ cả 11 khung liền nhau. Theo dự đoán giải tích A2G (CLAUDE.md mục 8.2), chuỗi liên tục dài nhất là 208 ± 73 gói ở lệch ngang 300 m và chỉ 40 ± 9 gói ở 600 m. Đặc tả ghi rằng dự đoán này lạc quan khoảng 4 lần [mô hình, dự đoán giải tích, chưa phải số đo ns‑3]. File phát sau hoặc file rơi vào đoạn bay gần mép River sẽ mất nhiều hơn. Do đó: phát **view tổng quát nhất trước** (với người là view nghiêng) ở đoạn giao nhận chắc nhất. Coi "3 file có view của camera" tốt hơn "4 file không có view đó". Khi lớp 3 gom file về critical cell, nên ưu tiên file khớp góc nhìn của các camera trong cell đó, thay vì chỉ đếm đủ số lượng [mô hình].

---

## (D) Signature nhẹ để lọc, dữ liệu đầy đủ để xác nhận: "gần như chắc chắn" chỉ đúng ở hai trường hợp

### Bộ lọc "áo vàng" sai khoảng một phần tư, và mù vào ban đêm

Bộ lọc thô có thể yếu hơn người ta nghĩ. Trên Market‑1501, APR nhận đúng **màu áo 74,0 %** và màu quần 73,8 %, trong khi độ chính xác *trung bình* của mọi thuộc tính là 86,6 %. Trên DukeMTMC, hai con số màu là 74,2 % và 69,9 % ([Lin et al., arXiv 1703.07220](https://ar5iv.arxiv.org/html/1703.07220)) [nguồn]. Lý do là con số trung bình bị kéo lên bởi các thuộc tính nhị phân dễ, như giới tính đạt 88,9 %. PA‑100K, tập thuộc tính lớn phổ biến, **không có nhãn màu** ([UPAR, arXiv 2209.02522](https://arxiv.org/pdf/2209.02522)) [nguồn]. Với xe, nhận dạng màu trên footage giám sát thật đạt 94,6 % micro nhưng chỉ **79,7 % macro**. Lớp "không xác định" chủ yếu là ảnh hồng ngoại ban đêm, nơi màu không khôi phục được ([arXiv 2606.13625](https://arxiv.org/pdf/2606.13625)) [nguồn]. Trên UFPR‑VCR, ảnh đêm chưa tới 10 % tập nhưng chiếm 32,4 % số lỗi, và 44,4 % ảnh đêm vẫn sai ngay cả khi xét top‑2 ([Lima et al., arXiv 2408.11589](https://arxiv.org/pdf/2408.11589)) [nguồn]. Hãng/đời xe đạt 97,6 % (model) và 99,3 % (make) trên ảnh web CompCars ([J. King Saud Univ. 2023](https://www.sciencedirect.com/science/article/pii/S1319157823004391)) [nguồn]. Khi đổi miền, cùng mô hình rơi từ 96,88 % xuống **36,10 %** trên VMMRdb ([Tafazzoli et al., CVPRW 2017](https://openaccess.thecvf.com/content_cvpr_2017_workshops/w9/papers/Tafazzoli_A_Large_and_CVPR_2017_paper.pdf)) [nguồn·trích]. Với loài động vật trên ảnh bẫy ảnh Snapshot Serengeti, CNN đạt trên 93,8 % và tự động hóa được 99,3 % ảnh ở độ chính xác 96,6 % ([Norouzzadeh et al., PNAS 2018](https://www.uber.com/blog/research/automatically-identifying-counting-and-describing-wild-animals-in-camera-trap-images-with-deep-learning)) [nguồn]. Tuy vậy, khả năng tổng quát sang điểm đặt mới "kém, nhất là cho phân loại" ([Beery et al., ECCV 2018](https://arxiv.org/abs/1807.04975)) [nguồn].

Bộ lọc lọc bớt được bao nhiêu thì **chưa có nguồn**. Không tìm thấy bảng nào cho tỉ lệ người mặc áo vàng: Market‑1501‑attribute chỉ có biểu đồ tròn. Ước lượng của nhóm: màu hiếm giữ lại khoảng 5–15 % ứng viên, lớp phổ biến ("sedan trắng", "một con chó") khoảng 20–40 %. Với 9 màu ở độ chính xác 74 %, mỗi người không phải mục tiêu có khoảng 3 % khả năng lọt lưới do nhận sai màu [mô hình].

### Hai tầng ghép nối tiếp: recall nhân với nhau, nên lọc phải mềm

Thiết kế hai tầng có cơ sở. PROVID dùng thuộc tính ngoại hình để lọc thô, rồi mạng Siamese để xác minh biển số, và tăng +9,28 % mAP trên VeRi‑776 ([Liu et al., ECCV 2016](https://mlanthology.org/eccv/2016/liu2016eccv-deep/)) [nguồn]. Học chung thuộc tính và ID đưa Market Rank‑1 từ 73,69 lên 84,29 % ([Lin et al.](https://arxiv.org/pdf/1703.07220)) [nguồn]. Nhưng tầng thô dùng một mình còn xa mới đủ để kết luận. Tìm người chỉ bằng mô tả văn bản trên CUHK‑PEDES đạt cao nhất khoảng **76–78 % Rank‑1** (CONQUER 77,13 %) ([arXiv 2601.18625](https://arxiv.org/html/2601.18625)) [nguồn]. Re‑ID bằng ảnh đạt khoảng 95 % trên Market (TransReID 95,0 / 88,2) ([arXiv 2308.10717](https://arxiv.org/pdf/2308.10717)) [nguồn·trích, có thể là số chạy lại].

Với lọc cứng, recall toàn tuyến là tích hai tầng: **0,74 × 0,95 ≈ 0,70** cho người [mô hình]. Ghép thêm một thuộc tính độc lập nữa làm tích giảm theo cấp số nhân (0,74 × 0,89 ≈ 0,66 cho màu áo + giới tính) [mô hình]. Ban đêm, dùng màu làm bộ lọc cứng gần như chắc chắn loại mục tiêu. Kết luận: **signature nhẹ nên xếp hạng hoặc giữ top‑k, không loại cứng**, và cần tự tắt ở ảnh IR. Kết luận này nhất quán với báo cáo lớp 1: lớp L0 thuộc tính "không bao giờ kết luận". Chưa bài nào báo cáo recall đầu‑cuối của chuỗi "lọc bằng văn bản/thuộc tính → re‑ID bằng ảnh" so với re‑ID bằng ảnh thuần trên cùng một giao thức.

### Trần độ chính xác khi có dữ liệu đầy đủ

Đây là nơi giả định "dữ liệu đầy đủ thì gần như tuyệt đối" của người dùng **chỉ đúng một phần**.

| Lớp mục tiêu, điều kiện | Trần với dữ liệu đầy đủ | "Gần như chắc chắn"? | Nhãn |
|---|---|---|---|
| Mặt, ảnh hợp tác chất lượng tốt (visa, cửa khẩu, mugshot) | FNMR tốt nhất 0,06 % (Visa‑Visa), 0,14–0,20 % (Border, Mugshot); Kiosk‑Border 0,53 %, đa số thuật toán ≈ 3,7 %; điểm vận hành chuẩn FMR 10⁻⁶ ([Biometric Update 08/2026](https://www.biometricupdate.com/202608/nist-frte-11-shows-facial-verification-accuracy-converging); [NIST FRTE 1:1](https://pages.nist.gov/frvt/html/frvt11.html)) | **Có** | [nguồn·trích] (bài tóm tắt; FMR cần đối chiếu bảng NIST) |
| Mặt ngoài thực địa (IJB‑C) | TAR 81,15 % @ FAR 10⁻⁶ (2018) ([arXiv 1804.01159](https://arxiv.org/pdf/1804.01159)); ≈ 95–97 % @ 10⁻⁵ với mô hình mới ([arXiv 2105.00634](https://arxiv.org/pdf/2105.00634)) | Không ở FAR rất thấp | [nguồn] |
| Sinh đôi cùng trứng, người thân | NIST IR 8439: FMR vẫn cao với sinh đôi cùng trứng và đa số cặp sinh đôi khác trứng cùng giới ([NIST IR 8439](https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8439.pdf)) | **Không** | [nguồn] |
| Người toàn thân, cùng quần áo | Market ≈ 95 % Rank‑1 / 88–91 % mAP; MSMT17 77–83 % ([arXiv 2308.10717](https://arxiv.org/pdf/2308.10717)); open‑set mReP đỉnh chỉ 58–81 % ([arXiv 2011.11506](https://ar5iv.labs.arxiv.org/html/2011.11506)) | Không, "rất có thể" | [nguồn·trích] / [nguồn] |
| Người toàn thân, đổi quần áo | PRCC 74,4 % Rank‑1 ([arXiv 2606.11661](https://arxiv.org/html/2606.11661)); LTCC ≈ 56–58 % ([arXiv 2305.06145](https://arxiv.org/pdf/2305.06145)) | **Không** | [nguồn] |
| Xe, chỉ ngoại hình | VeRi‑776 ≈ 96,6 % Rank‑1 / 85,2 mAP ([CVPRW 2019](https://openaccess.thecvf.com/content_CVPRW_2019/html/AI_City/Ayala-Acevedo_Vehicle_Re-Identification_Pushing_the_limits_of_re-identification_CVPRW_2019_paper.html)); xe cùng hãng/đời/màu chỉ phân giải được bằng biển số (PROVID) | Không | [nguồn] |
| Xe, biển số đọc được | Biển số là tầng giải quyết xe trông giống nhau; LPR ≈ 96,8 % end‑to‑end trên 8 tập (báo cáo lớp 1) | **Có, khi đọc được** | [nguồn] / mức 0,99 là [mô hình] |
| Cá thể động vật | MegaDescriptor: Cows2021 99,54 %, BelugaID 66,48 %, HappyWhale 34,30 % ([WACV 2024](https://openaccess.thecvf.com/content/WACV2024/papers/Cermak_WildlifeDatasets_An_Open-Source_Toolkit_for_Animal_Re-Identification_WACV_2024_paper.pdf)); MiewID trung bình 80,6 % top‑1 ([arXiv 2412.05602](https://arxiv.org/html/2412.05602)) | Chỉ với loài có hoa văn rõ | [nguồn] |

Có ba điều kiện làm giả định gãy, và cả ba đều phổ biến trong kịch bản đô thị của dự án. **Đổi quần áo**: nghi phạm thay áo sau vụ việc. **Xe trông giống nhau mà không đọc được biển**. **Độ phân giải thấp hoặc ban đêm**: mặt và biển số xuống cấp, màu mất hẳn. Ngoài ra còn **đổi miền** khi triển khai ở điểm đặt mới (CompCars → VMMRdb: 97 % → 36 %). Có một điểm tinh tế hơn. Ngay cả khi độ chính xác từng cặp đạt mức "gần như chắc chắn" của mặt tốt (FNMR 0,1 % tại FMR 10⁻⁶), phép tính ở mục (A) vẫn áp dụng ở mức nút. Đội UAV 2 xác minh trên một cluster nghi vấn, gallery nhỏ hơn hẳn cả bản đồ, nên mức khớp nhầm còn lại thấp hơn tầng 1 nhiều bậc. Tuy vậy nó không bằng 0. AWS khuyến nghị ≥ 99 % *kèm người duyệt* cho an ninh công cộng chính là vì lý do này ([AWS](https://docs.aws.amazon.com/rekognition/latest/dg/considerations-public-safety-use-cases.html)) [NSX]. Với pha 2 của dự án, "xác minh" nên được mô hình hóa là **xác suất đúng theo lớp mục tiêu** như bảng trên, không phải 1,0 [mô hình].

---

## Tham số đề xuất cho mô hình hệ thống

Mọi tham số dưới đây là giá trị khởi đầu cho giả lập. Những dòng ghi [mô hình] cần thay bằng số đo khi có bộ khớp và footage thật.

| Nhóm | Tham số | Giá trị / khoảng | Nhãn |
|---|---|---|---|
| Signature | Số file mỗi mục tiêu; kích thước | 3–5 file, ~1 KB mỗi file (512‑d fp16 ≈ 11 khung 99 B), tổng 4–5 KB | [mô hình] (phép tính ở báo cáo lớp 1) |
| | Trường bắt buộc trong header | model ID (họ mô hình + phiên bản), chỉ số file/view | [mô hình] từ [nguồn] BCT |
| Thang điểm | Ánh xạ "phần trăm" | 70 / 80 / 90 % ↔ FMR 10⁻³ / 10⁻⁴ / 10⁻⁵ mỗi phép so sánh | [mô hình], neo theo [NSX] AWS/Azure, [nguồn] InsightFace |
| | Hiệu chỉnh | Beta hoặc logistic theo lớp mục tiêu, có biến chất lượng ảnh | [nguồn] FairCal, Mandasari |
| Mô hình điểm, mặt | Impostor; cặp thật rõ; cặp thật giám sát | N(0; 0,10); N(0,58; 0,12); N(0,48; 0,12) → τ₇₀/₈₀/₉₀ = 0,31/0,37/0,43; TPR 0,99/0,96/0,89 (rõ), 0,92/0,82/0,66 (giám sát) | [mô hình] neo vào [nguồn] IJB‑C TAR ≈ 96 % @10⁻⁴ |
| Mô hình điểm, các lớp khác | d′ (tách cặp thật/impostor) | Người toàn thân 2,5–3; xe 2,5; động vật 1,5–2 | [mô hình] neo vào [nguồn] mReP 58–81 %, ARI 0,20 |
| | Hệ số đổi quần áo | TPR × 0,4–0,65 | [mô hình] từ [nguồn] PRCC Rank‑1 |
| Lợi ích theo số file | Tăng điểm cặp thật mỗi lần gấp đôi k | δ ≈ 0,02–0,05 cosine | [mô hình], chưa có nguồn |
| Chênh theo thiết bị | Lệch hệ thống theo loại thiết bị (int8) | b_dev ~ U(−0,03; +0,03) cosine, cố định theo loại thiết bị | [mô hình] neo vào +0,025 [nguồn·trích] |
| | Nhiễu từng cặp; fp16 | σ ≈ 0,005–0,01; fp16 ≈ 0,001–0,005 | [mô hình] |
| | Biên dịch hỏng | Loại khỏi tập nút xử lý (qua kiểm thử nghiệm thu `accuracy_analysis`) | [NSX] RKNN; tỉ lệ hỏng chưa có nguồn |
| Chênh theo camera | Tụt điểm cặp thật theo hạng chất lượng camera | Δμ_G ∈ [−0,4; −0,1] cho camera kém (chuông cửa, đặt cao, nén mạnh) | [mô hình], chưa kiểm chứng |
| | Khác họ mô hình | Không tương thích: nút không có signature cho họ của nó thì không xử lý | [nguồn] BCT |
| Quyết định tại nút | Vùng UNSURE | ≥ τ + δ: YES; ≤ τ − δ: NO; còn lại UNSURE, δ ≈ 0,03 | [mô hình] |
| | Ngưỡng cổng theo kho | f = 1 − (1 − FY_target)^(1/(N·k)), N = số tracklet | [mô hình] (Šidák); [nguồn] NIST FPIR |
| | Báo cáo về BS | 6 B như báo cáo lớp 1, thay `ref_frac` bằng bitmap 5 bit các file đang giữ | [mô hình] |
| Mất file | Recall giảm khi thiếu file | δ_red ≈ 1 điểm mỗi file trùng lặp; δ_view ≈ 4 điểm (trong miền) / 20 điểm (ngoài miền) khi mất view khớp camera | [mô hình] neo vào [nguồn] Sun & Zheng, Ben Mabrouk |
| | Xác suất mất theo vị trí file | Không đều: tăng theo thứ tự phát và theo khoảng cách tới trục bay | [mô hình] từ dự đoán A2G |
| Lọc thô | P(mục tiêu qua bộ lọc màu) | 0,74 ban ngày (người); 0,80–0,95 (màu xe); ban đêm/IR: tắt bộ lọc | [nguồn] Lin et al., arXiv 2606.13625 |
| | Tỉ lệ ứng viên còn lại | 0,05–0,15 (màu hiếm); 0,2–0,4 (lớp phổ biến) | [mô hình], chưa có nguồn |
| | Lọt lưới do sai màu | ≈ 3 % mỗi người không phải mục tiêu (9 màu, độ chính xác 74 %) | [mô hình] |
| Xác minh đầy đủ (pha 2) | P(quyết định đúng) theo lớp | Mặt tốt ≥ 0,998; mặt ngoài thực địa ≈ 0,81 @ FAR 10⁻⁶; người cùng quần áo ≈ 0,95, đổi quần áo 0,56–0,74; xe có biển ≈ 0,99, chỉ ngoại hình 0,85–0,95; động vật 0,35–0,99 theo loài | [nguồn]/[nguồn·trích] cho các điểm neo; giá trị xác suất là [mô hình] |
| | Sinh đôi, người trông giống | Không phân giải được bằng ảnh, cần ngữ cảnh | [nguồn] NIST IR 8439 |

---

## Chưa kiểm chứng / khoảng trống

| Mục | Vấn đề |
|---|---|
| Phương sai điểm theo thiết bị trên đội camera IoT không đồng nhất | Chưa nghiên cứu nào đo. Là khoảng trống, có thể thành đóng góp nếu tự đo |
| Độ lệch cosine int8 so với fp32 | Chỉ có một số đo của người thực hành (+0,025, ±0,017), đọc qua đoạn trích (trang 403). Chưa có bảng mean/p95 \|Δcos\| cho Hailo, Edge TPU, RKNN, QNN, TensorRT |
| Tụt cosine theo độ phân giải, bitrate, ISP | Dải 0,1–0,4 là [mô hình]. Schlett et al. và luận văn Andreas (h‑da 2026) có số nhưng chưa đọc toàn văn |
| Chênh lệch cross‑hardware fp32 | ≪ 0,001 là [mô hình], chưa có số đo cho embedding thị giác |
| Đường TAR@FAR theo 1–5 tham chiếu khác góc nhìn | Chưa có cho người, xe hay động vật. Đây là thí nghiệm offline then chốt (Market‑1203 hoặc VeRi‑776 có nhãn góc nhìn) trước khi đưa bảng mục (C) vào paper |
| Mất file "điều kiện" (đêm/IR, quần áo khác) | Chưa nguồn nào đo; đang giả định giống mất view |
| Max so với trung bình khi bỏ một file | Chưa có số đo; phần hòa giải ở mục (C) là suy diễn |
| Tỉ lệ người/xe theo màu trong footage thật | Chưa có bảng; tỉ lệ ứng viên còn lại của bộ lọc thô là [mô hình] |
| Recall đầu‑cuối của chuỗi lọc thô → xác minh | Chưa có bài nào so trên cùng giao thức |
| Số NIST FRTE 1:1 (FNMR 0,06–0,20 %) | Lấy từ bài tóm tắt của Biometric Update; điểm vận hành FMR 10⁻⁶ cần đối chiếu bảng NIST |
| IJB‑C TAR @ FAR 10⁻⁶ của mô hình sau 2022 | Chưa kiểm từ bài gốc |
| Re‑ID đổi miền (Market → Duke 27–38 %) | Lấy từ đoạn trích; gán số cho từng bài chưa đối chiếu từng dòng |
| Ef‑QuantFace 94,13 % | Tiêu đề bảng bị lỗi khi trích; cột chưa xác nhận |
| Ngưỡng cosine cố định cho động vật, CLIP ảnh‑ảnh | Không tìm thấy nguồn |
| Phân bố điểm cặp thật/impostor của ArcFace trên IJB‑C | Không trích được trung bình/SD; mô hình Gauss của nhóm là khớp tham số, không phải số đo |
| Ánh xạ similarity → phần trăm của AWS | Không được công bố |
| Dự đoán chuỗi liên tục A2G (208/40 gói ở 300/600 m) | Dự đoán giải tích, lạc quan khoảng 4 lần; cần số đo ns‑3 với N đủ lớn |

---

## Kết luận

Câu hỏi "thiết bị A 70 %, thiết bị B 75 %" thực ra có hai đáp án ở hai tầng khác nhau. Ở tầng số học, chênh lệch đó có thật, nhưng nhỏ, đo được trước trên từng loại thiết bị và hấp thụ được bằng vùng UNSURE ±0,03. Ở tầng ảnh, chênh lệch lớn hơn nhiều và có hướng xác định: camera kém kéo điểm cặp thật xuống, nên lỗi chủ yếu là bỏ sót. Đây là chỗ lớp 1 phản hồi ngược về lớp 3. Khi chọn critical cell và điểm xử lý, "năng lực" của nút phải gồm chất lượng ống kính và họ mô hình, không chỉ TOPS. Một Jetson gắn camera đặt cao, nén mạnh có thể đóng góp ít hơn một hub T1 nhìn thẳng vào lối vào.

Kết luận thứ hai có tính thiết kế. Ba câu hỏi đều quy về cùng một nhu cầu: BS phải biết *nút giữ file nào, chạy mô hình nào, nhìn bằng camera loại nào*, thì mới diễn giải đúng một câu YES/NO. Mất 1 file có thể vô hại hoặc tốn 20 điểm recall tùy file đó là view nào. Cùng điểm 75 % có thể nghĩa là FMR 10⁻⁴ hoặc gấp 2,7 lần tùy chip. Dữ liệu đầy đủ chỉ "gần như chắc chắn" với mặt tốt và biển số đọc được. Vì vậy, đóng góp đáng giá nhất của lớp 1 cho paper không phải một ngưỡng 70–90 % đẹp. Đó là một báo cáo vài byte đủ ngữ cảnh: LLR đã hiệu chỉnh, bitmap file, model ID ngầm định qua tập signature, và hạng chất lượng camera. Từ báo cáo đó, BS hiệu chỉnh lại thay cho nút.
