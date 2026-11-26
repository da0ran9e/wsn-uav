---
status: current
updated: 2026-11-26
---
# J1 · Bối cảnh bài toán, phiên bản rừng và khu bảo tồn (v2)

Bắt đầu lại từ bước bối cảnh theo yêu cầu ở chatlog mục 408: kịch bản chuyển từ đô thị sang vùng thiếu kết nối như rừng quốc gia, khu
bảo tồn. Phiên bản đô thị được đóng gói ở [archive/urban-v1](archive/urban-v1/README.md). File này chốt dần qua thảo luận như lần
trước; mỗi ý ghi trạng thái **chốt**, **đề xuất** hoặc **mở**. Nhãn nguồn: [repo] lấy từ tài liệu trong repo, [web] tra trên internet,
[chung] kiến thức chung chưa đối chiếu nguồn.

## 1. Vì sao đổi kịch bản

Lập luận của bản đô thị có mấy chỗ phản biện dễ hỏi (urban-v1 mục 12, 15):
- Đô thị có sẵn mạng di động và Internet, nên phải giải thích dài vì sao node không gửi qua 4G.
- Ảnh camera trong khu dân cư vướng quyền riêng tư; phải dựng mạng dùng chung kiểu Sidewalk mới có chủ vận hành.
- Nhà cao tầng làm kênh A2G khó mô hình; vùng cấm bay và giấy phép bay trên khu đông người là rào cản lớn.

Ở rừng quốc gia và khu bảo tồn, mấy chỗ này nhẹ đi:
- Lõi rừng thường không có sóng di động, nên LoRa và UAV là đường liên lạc thực tế duy nhất [chung].
- Thiết bị do ban quản lý rừng sở hữu và vận hành; ảnh chủ yếu là động vật, người đi rừng và người xâm nhập [chung].
- Không có nhà cao tầng, ít nhiễu 2,4 GHz, bay ngoài tầm nhìn trên vùng ít người dễ được cấp phép hơn [chung].
- Đã có triển khai thật để dẫn chứng [repo, urban-v1 CONTEXT mục 7–8]:
  - Dryad Silvanet: cảm biến cháy rừng nối mesh, khoảng 1 node mỗi ha;
  - 65 camera bẫy ảnh 4G chạy pin mặt trời trên 34 km² (Kissling 2024);
  - camera bẫy ảnh thông minh gửi qua LoRa rồi Iridium (Gabon);
  - GreenOrbs, mạng TelosB tới 330 node trong rừng (Liu 2013).
- Bản ICC và bản đồ tổng hợp C4 vốn được mô tả là "rừng, camera và cảm biến" [repo, urban-v1 CONTEXT mục 8], nên các kết quả kỹ thuật
  đã có (T\*, River, cân tải, takeover, K9) dùng lại được.

## 2. Mang sang từ phiên bản trước (đề xuất giữ)

- Cơ chế: UAV cánh bằng phát truy vấn một lượt; mạng mặt đất chuyển phần còn thiếu theo kế hoạch tính trước (River, cân tải, cây
  dùng chung); takeover khi UAV lệch đường.
- Cấu trúc ba pha và ba bài toán (P0) chọn AI cell, (P1) pha 1, (P2) pha 2 xác minh (urban-v1 PROBLEMS); mục tiêu phân vị 0,9 của T\*.
- Lý thuyết: Định lý 1 (NP-khó), Định lý 2 (chặn phủ cho cách không hợp tác), chặn một radio cho lớp mặt đất.
- Một UAV ở pha 1; nhiều UAV để sau, khi có cơ chế phối hợp thật.

## 3. Lỗ hổng mới của kịch bản rừng (mở)

1. **Mật độ.** Triển khai thật trong rừng chỉ khoảng 0,01–100 node/km² (camera bẫy ảnh 0,01–1, ô nghiên cứu ForestGEO khoảng 50,
   Dryad 100–120), trong khi bài đang dùng khoảng 820 node/km² [repo, urban-v1 CONTEXT mục 8]. Đây là chỗ phản biện sẽ hỏi đầu tiên.
2. **Kênh qua tán rừng.** Sóng 2,4 GHz suy hao mạnh qua lá và thân cây, cả A2G lẫn G2G [chung, cần nguồn]. Đã có trong repo: tầm A2G
   802.15.4 thực tế khi UAV di chuyển chỉ còn khoảng 1/3 tầm danh định (Bacco 2018), độ cao tốt nhất khoảng 45 m (Nekrasov 2019)
   [repo, `research_notes/literature/2026-11-12/06-deployment.md`].
3. **Năng lượng.** Không có điện lưới; mọi node chạy pin hoặc pin mặt trời. Node phải ngủ phần lớn thời gian, nên đánh thức, ngân
   sách năng lượng cho luồng nền và cho River thành ràng buộc chính. Bản đô thị coi phần lớn node cắm điện.
4. **Loại nhiệm vụ và nội dung truy vấn.** Tìm người đi lạc, phát hiện người săn trộm, nhận dạng một cá thể động vật, hay việc khác.
   Mỗi loại cho truy vấn, dữ liệu nền và tiên nghiệm vị trí khác nhau.
5. **Địa hình.** Đồi núi làm khuất tầm nhìn, UAV phải bay theo độ cao địa hình, cell ở sườn khuất nhận kém.
6. **Quy mô vùng.** Vườn quốc gia thường rộng vài trăm km² [chung], trong khi một chuyến bay ước làm được khoảng 50 cụm, khoảng
   100 km² nếu cụm giống bản đồ k8 [repo, urban-v1 CONTEXT mục 7].
7. **Trạm gốc.** Trạm kiểm lâm ở bìa rừng; quãng bay tới vùng nhiệm vụ dài hơn bản đô thị.

## 4. Câu hỏi cần quyết trước

| Mã | Câu hỏi | Trạng thái |
|---|---|---|
| a | Nhiệm vụ điển hình: tìm người mất tích (chatlog mục 409) | chốt |
| b | Thiết bị và mật độ: camera bẫy ảnh thưa cộng cảm biến dày hơn dọc tuyến (đường mòn, suối, ranh giới), hay rải đều; mức mật độ mục tiêu. Hướng đã chốt (mục 409): mật độ hiện nay chưa đạt nhưng hợp lý trong tương lai, bài vẫn khảo sát và báo số thật (mục 5) | mở một phần |
| c | Băng tần mặt đất: giữ 802.15.4 2,4 GHz (cell nhỏ, cần mạng dày) hay chuyển sub-GHz (cell lớn, mạng thưa được) | mở |
| d | Vùng mẫu: khu thật nào để cắt bản đồ (ranh giới vườn quốc gia, đường mòn, suối, địa hình) | mở |
| e | Giữ cơ chế và cấu trúc ba pha như mục 2 | đề xuất |

## 5. Mật độ thiết bị hiện có ở rừng và khu bảo tồn (2026-11-26, mục 409)

Mật độ do tôi chia số thiết bị cho diện tích nêu trong nguồn. Số [web] lấy từ đoạn trích tìm kiếm, chưa đọc toàn văn.

| Triển khai | Loại thiết bị, kết nối | Số thiết bị, diện tích | Mật độ (thiết bị/km²) | Nguồn |
|---|---|---|---|---|
| Dryad Silvanet, thí điểm Lebanon | cảm biến khí cháy, mesh LoRa, 2 gateway | 91 trên 78 ha | khoảng 117 | [repo] urban-v1 CONTEXT mục 7; [web] eenewseurope |
| Dryad Silvanet, Marsden Moor (Anh, 2024) | như trên | 50 trên khoảng 2 500 ha | khoảng 2 | [web] dryad.net, rcrwireless |
| Dryad, tổng | như trên | hơn 30 000 cảm biến ở khoảng 100 điểm (trung bình khoảng 300 mỗi điểm); điểm thí điểm tối thiểu 1 000 ha | — | [web] ITU EW4All, dryad.net |
| Camera 4G, Natura 2000 Hà Lan (Kissling 2024) | camera bẫy ảnh, 4G, pin mặt trời | 65 trên 34 km² | khoảng 1,9 | [repo] `kissling2024-wildcam` |
| VQG Pù Mát | camera bẫy ảnh, không nối mạng | 152 camera ở 5 điểm, vườn hơn 900 km² | khoảng 0,17 trên cả vườn | [web] Saola Working Group 2019 |
| KBT Pù Hoạt | camera bẫy ảnh | 45 trạm trên khoảng 350 km² | khoảng 0,13 | [web] đoạn trích tìm kiếm, chưa xác định bài gốc |
| VQG Bạch Mã, KBT Sao La, Xe Sap | camera bẫy ảnh | 138 trạm lưới thô ở 5 khu (53 ở Bạch Mã) | chưa tính (thiếu diện tích khảo sát) | [web] |
| TrailGuard AI (Grumeti, Tanzania) | camera AI chống săn trộm, 3G rồi LoRa và vệ tinh | bắt đầu với 6 thiết bị | rất thấp | [web] Smithsonian, Mongabay |
| Rainforest Connection Guardian | cảm biến âm thanh, phát hiện tiếng súng, cưa, xe | tầm nghe 50–1 500 m; không có số mật độ | — | [web] rfcx.org |
| ALERTCalifornia | camera PTZ phát hiện cháy trên tháp | khoảng 1 300 camera trên cả bang (khoảng 424 000 km²) | khoảng 1 trên 330 km² (dày hơn ở vùng nguy cơ cao) | [web] PetaPixel 2026, UCSD |
| GreenOrbs | TelosB 802.15.4, mesh nhiều chặng | tới 330 node, không ghi diện tích | — | [repo] `liu2013-greenorbs` |

Nhận xét:
- Trên toàn vườn, các mạng đang chạy thật chỉ có khoảng 0,003–2 thiết bị mỗi km². Mức trên 100 chỉ gặp ở ô thí điểm nhỏ (Dryad
  Lebanon, 78 ha). Bài đang dùng khoảng 820, cao hơn mức toàn vườn hàng trăm tới hàng trăm nghìn lần.
- Các mạng thưa này đều không dùng mesh 2,4 GHz. Chúng nối thẳng bằng 4G, LoRa hay vệ tinh, hoặc không nối mạng (camera bẫy ảnh thu thẻ
  nhớ theo đợt). Riêng Dryad dùng mesh sub-GHz. GreenOrbs là mesh 802.15.4 duy nhất trong rừng mà repo có số liệu.
- Ở bản đô thị, lưới cell R = 100 m dùng 802.15.4 chỉ còn liền khi các node cách nhau không quá khoảng 50–60 m, tức khoảng 300 node/km²
  trở lên (urban-v1 CONTEXT mục 10). Trong rừng, suy hao qua tán lá làm con số này còn cao hơn. Ở mật độ hiện nay, hợp tác mặt đất qua
  802.15.4 vì vậy không chạy được. Bài cần chọn một trong hai: lấy mật độ hướng tới tương lai làm giả định chính và nói rõ đó là giả
  định, hoặc chuyển lớp mặt đất sang sub-GHz.
- Lý lẽ cho mật độ tương lai: Dryad đã giao hơn 30 000 cảm biến và đặt quy mô thí điểm tối thiểu 1 000 ha; giá node giảm; nhiều mạng
  khác nhau (cảm biến cháy, camera, âm thanh) có thể dùng chung một lớp mesh. Đây là suy luận, chưa có nguồn nói thẳng xu hướng mật độ.

Tần suất tìm kiếm cứu nạn [web]: các khu do Cục Vườn quốc gia Hoa Kỳ (NPS) quản lý có 2 890 vụ tìm kiếm cứu nạn năm 2017 (159 người
chết). Trung bình giai đoạn 1992–2007 là 11,2 vụ mỗi ngày (bài "Dead men walking: search and rescue in US National Parks", Wilderness & Environmental Medicine 2009, theo đoạn trích). Grand Canyon
có 785 vụ trong ba năm 2018–2020, Yosemite 732 (phân tích của Outforia, không phải số chính thức). Chưa có số cho Việt Nam.

