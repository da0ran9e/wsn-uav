---
status: reference
updated: 2026-11-12
---
# 06 — Triển khai thực tế: phần cứng camera IoT, testbed, UAV+WSN, pha 0

Phiên tra cứu 2026-11-12, khoảng 25 lượt tìm. **Cách đọc trạng thái:** "đã xác minh" nghĩa là tôi đã thấy URL/DOI và
đoạn trích trong kết quả tìm kiếm khớp với tên, tác giả và ý chính. "chỉ thấy tiêu đề" nghĩa là chỉ thấy tên hoặc
danh mục. **Tôi chưa đọc toàn văn bài nào:** các host `www.ncbi.nlm.nih.gov` và `www.iot-lab.info` bị chặn trong
session này (cần mở trong cài đặt mạng nếu muốn đọc toàn văn). Mọi con số dưới đây lấy từ đoạn trích, cần kiểm lại
với bản gốc trước khi đưa vào J2.

## 1. Tóm tắt

1. **Năng lượng cho một lần suy luận "person detection" trên MCU** là khoảng 0,2–1,6 mJ: MAX78000 0,7 mJ (số của hãng),
   196 µJ (TinyissimoYOLO). Một pipeline nhận dạng đa phương thức trên ESP32 tốn 0,15 J mỗi chu kỳ. **Tôi không tìm
   thấy bài nào chạy person re-ID (đối sánh với ảnh truy vấn) trên MCU.** Đây là lỗ hổng mà J2/SigDrop có thể lấp,
   đồng thời là rủi ro khi trích dẫn.
2. **Bo camera AI rẻ:** Grove Vision AI V2 (HX6538: Cortex-M55 + Ethos-U55) giá khoảng 16 USD, khoảng 0,35 W, 33 ms
   mỗi suy luận. Himax WE-I Plus khoảng 2,5 mW (số của hãng). OpenMV H7 Plus tốn 140–240 mA ở 3,3 V. ESP32-CAM khi ngủ
   sâu vẫn tốn 0,5–18 mA nếu không cắt nguồn camera.
3. **Testbed 802.15.4 công cộng:** FIT IoT-LAB có khoảng 2 700 node và hơn 117 robot di động (robot chạy quỹ đạo
   ghi sẵn, ở mặt đất, trong nhà). FlockLab 2 (ETH), D-Cube (TU Graz) và Indriya2 (NUS) đều tĩnh. **Không testbed nào
   có drone bay trên lưới 802.15.4.** AERPAW có drone, nhưng tập trung vào SDR/LTE/O-RAN/LoRa.
4. **Đo đạc UAV + 802.15.4:** tầm truyền thực tế khi UAV di chuyển chỉ còn khoảng 1/3 tầm danh định (Bacco 2018).
   Độ cao bay tốt nhất khoảng 45 m, ăng-ten thu đặt song song mặt đất (Nekrasov, Sensors 2019). Radio điều khiển của
   drone gây nhiễu 802.15.4 (Wen & Dargie 2020). Ba điểm này ảnh hưởng trực tiếp đến giả định cửa sổ truyền 400 KB
   của SigDrop.
5. **LoRa gắn trên drone đã có tiền lệ:** gateway RPi 4B + SX1302/1303 trên DJI Mavic 3 bay ở 50/100/150 m; mote
   LoRa trên Phantom 4 Pro bay ở 25/50 m.
6. **Pha 0:** GAF (lưới ảo, tiết kiệm 40–60 % năng lượng) là tiền lệ gần nhất cho cấu trúc ô. Đã có nhiều giao thức
   phân cụm lục giác, nhưng đều chỉ là mô phỏng và so với LEACH. Có thuật toán tô màu 2-hop phân tán (Jemili; cận dưới
   STACS 2009). Việc hình thành mạng 6TiSCH chậm do va chạm ở ô dùng chung (Quick6TiSCH giảm 62,6 % thời gian).
   Gateway đa radio 802.15.4: Opal tăng thông lượng 3,7×.
7. **Đề xuất phần cứng cho J2:** mỗi node gồm nRF52840 (radio) + Grove Vision AI V2 (đối sánh). Cluster head thêm
   LoRa. Có 2–4 gateway đôi (hai nRF52840 trên một RPi). Drone đa cánh mang node thu 802.15.4 bay khoảng 45 m.

## 2. Bảng tài liệu và nền tảng

### 2a. Phần cứng camera và chi phí suy luận

| Tên | Năm | Link | Nội dung chính | Trạng thái |
|---|---|---|---|---|
| Cyclops: In Situ Image Sensing and Interpretation in WSN (Rahimi et al., SenSys) | 2005 | https://escholarship.org/uc/item/6kd570mj | Bo camera cho mote: MCU, CPLD làm frame grabber, CMOS imager | đã xác minh |
| Bảng so sánh camera node (UMass, NOSSDAV) | 2005 | https://lass.cs.umass.edu/papers/pdf/NOSSDAV05-network.pdf | Cyclops 46 mW, 352×288, 10 fps; CMUcam 200 mW; camera PTZ 1 W | đã xác minh |
| TinyissimoYOLO (arXiv 2306.00001) | 2023 | https://arxiv.org/pdf/2306.00001 | 196 µJ mỗi suy luận trên MAX78000; Apollo4b 6,1 mJ; 3 lớp (person/chair/car) | đã xác minh |
| Maxim + Aizip, person detection 0,7 mJ (thông cáo) | 2021 | https://www.eenewseurope.com/en/maxim-aizip-team-on-lowest-power-iot-person-detection | Visual Wake Words trên MAX78000, 0,7 mJ mỗi suy luận (số của hãng) | đã xác minh |
| Himax WE-I Plus EVB | ~2020 | https://www.electronicsforu.com/tech-zone/tech-sensors/ai-development-board-that-can-enable-ai-at-low-power-anywhere | HX6537-A (ARC EM9D 400 MHz) + HM0360; khoảng 2,5 mW, dưới 35 ms (số của hãng); giá 65–70 USD | đã xác minh |
| Grove Vision AI V2 | 2024 | https://www.cnx-software.com/2024/01/19/16-grove-vision-ai-v2-module-features-wiseeye2-hx6538-arm-cortex-m55-ethos-u55-ai-microcontroller/ | HX6538, M55 + Ethos-U55, 15,99 USD (không kèm camera) | đã xác minh |
| So sánh bo vision MCU 2024 (Hackster) | 2024 | https://www.hackster.io/limengdu0117/2024-mcu-ai-vision-boards-performance-comparison-998505 | Grove V2: 0,35 W, 33 ms; V1: 0,40 W, khoảng 389 ms | đã xác minh |
| OpenMV Cam H7 Plus | — | https://docs.openmv.io/openmvcam/quickref/openmv-cam-h7-plus.html ; https://www.mouser.in/new/dfrobot/dfrobot-dfr0833-openmv-cam-h7-plus/ | Nghỉ 140 mA, hoạt động 230–240 mA ở 3,3 V (theo listing DFRobot) | đã xác minh (dòng tiêu thụ lấy từ listing) |
| Đo tiêu thụ node IoT chụp ảnh (Cornei et al., Bul. Inst. Politehnic Iași) | 2023 | https://reference-global.com/download/article/10.2478/bipie-2023-0004.pdf | Dòng tiêu thụ theo từng pha khi chụp và gửi ảnh, so sánh HTTP với MQTT | đã xác minh |
| ESP32-CAM ngủ sâu (Hackaday) | — | https://hackaday.io/project/186782 | 2,8 mA, giảm còn 0,8 mA sau khi sửa bo | đã xác minh (nguồn hobby) |
| Nhận dạng đa phương thức trên ESP32 (Sensors 26) | 2026 | https://iris.unisalento.it/retrieve/77e0d310-b97f-4d17-af3c-19664360bec4/sensors-26-03756-v3.pdf | Person detection đánh thức, sau đó nhận dạng mặt và giọng; 0,15 J mỗi chu kỳ | đã xác minh |
| Realtime Person Identification via Gait Analysis | 2024 | https://aminer.org/pub/6629b96001d2a3fbfc7d9341/realtime-person-identification-via-gait-analysis | Arduino Nano 33 BLE: 5 KB RAM, 70 ms, 125 mW | chỉ thấy tiêu đề và trích đoạn |
| Smart camera trap qua Iridium (Gabon) | ~2022 | https://ora.ox.ac.uk/objects/uuid:d3b63897-f23e-42ea-8038-1712b52f730f/files/std96k4767 | Bushnell + bo LoRa + thẻ SD WiFi, bridge gửi cảnh báo qua vệ tinh | đã xác minh |
| IoT camera trap với DL ở biên + LoRaWAN (Computers 11(1):13) | 2022 | https://doi.org/10.3390/computers11010013 | Phân loại loài ở biên, gửi kết quả qua LoRaWAN | đã xác minh |

### 2b. Testbed

| Tên | Năm | Link | Nội dung chính | Trạng thái |
|---|---|---|---|---|
| FIT IoT-LAB: A large scale open experimental IoT testbed (WF-IoT) | 2015 | https://ieeexplore.ieee.org/document/7389098 | 2 728 node, 117 robot di động, 6 site; 802.15.4 ở 2,4 GHz và 868 MHz; robot chạy quỹ đạo ghi sẵn | đã xác minh |
| Importance of Repeatable Setups… (Papadopoulos et al.) | 2016 | https://hal-supelec.archives-ouvertes.fr/INRIA/hal-01609092v1 | Cập nhật: 2 769 thiết bị, 127 robot | đã xác minh |
| FlockLab 2: Multi-Modal Testing and Validation for Wireless IoT (Trüb et al.) | 2020 | https://www.research-collection.ethz.ch/handle/20.500.11850/442038 | Debug/trace và đo công suất dải động cao; mã nguồn mở | đã xác minh |
| Non-Intrusive Distributed Tracing… FlockLab 2 | 2021 | https://doi.org/10.1145/3480248 | Dịch vụ tracing chạy trên FlockLab 2 | chỉ thấy tiêu đề |
| D-Cube / EWSN Dependability Competition (Schuß, Boano, Weber, Römer) | 2017 | https://www.ewsn.org/file-repository/ewsn2017/054_065_schuss.pdf ; https://github.com/TuGraz-ITI/D-Cube | Benchmark độ tin cậy; mở cho người ngoài từ 2019 | đã xác minh |
| X-Lab (mở rộng D-Cube, EWSN) | 2023 | https://www.ewsn.org/file-repository/ewsn2023/EWSN2023-final6878.pdf | Thí nghiệm liên site, testbed trải 4 000 km | đã xác minh |
| Indriya2 (Appavoo et al., TRIDENTCOM) | 2019 | https://doi.org/10.1007/978-3-030-12971-2_1 | TelosB, SensorTag CC2650/CC1350; Contiki/TinyOS; BLE và 802.15.4g | đã xác minh |
| AERPAW (Marojevic, Guvenc, Dutta, Sichitiu) | ~2020 | https://par.nsf.gov/servlets/purl/10174705 | Testbed drone cỡ thành phố (NC State), SDR, có digital twin | đã xác minh |
| AERPAW O-RAN UAV (arXiv 2411.04027) | 2024 | https://arxiv.org/pdf/2411.04027 | O-RAN, FlexRIC, bay thật kết hợp digital twin | đã xác minh |
| AERPAW LoRa: helikite và drone (arXiv 2604.06444) | 2026 | https://arxiv.org/html/2604.06444 | So sánh xe mặt đất, drone 50 m, helikite 150/300 m; mô hình log-distance | đã xác minh |
| Survey testbed IIoT (arXiv 2404.17485) | 2024 | https://arxiv.org/pdf/2404.17485 | Ghi FlockLab 2 có 60 observer trên 3 tầng (số này cần kiểm lại) | đã xác minh |

TWIST và w-iLab.t: chưa tra trong phiên này, không có link.

### 2c. Thí nghiệm UAV + WSN/LoRa ngoài thực địa

| Tên | Năm | Link | Nội dung chính | Trạng thái |
|---|---|---|---|---|
| Optimizing 802.15.4 Outdoor IoT Sensor Networks for Aerial Data Collection (Nekrasov et al., Sensors) | 2019 | https://doi.org/10.3390/s19163479 | Quadcopter, 4 node phát mỗi 500 ms, khoảng 9 giờ bay; tối ưu ở độ cao khoảng 45 m với ăng-ten song song mặt đất; PRR nhạy với độ cao và hướng ăng-ten hơn RSSI | đã xác minh |
| Bộ dữ liệu Aerial Measurements 2.4 GHz 802.15.4 (Dryad) | 2019 | https://doi.org/10.25349/D9KS3W | Log drone và tín hiệu | đã xác minh |
| DroNet'19, bản hội thảo của nhóm UCSB | 2019 | https://ebelding.cs.ucsb.edu/sites/default/files/publications/dronet_2019.pdf | 13 mức độ cao | đã xác minh |
| Bacco et al., testbed UAV–802.15.4 (ISTI-CNR) | 2018 | https://openportal.isti.cnr.it/data/2018/389223/2018_389223.postprint.pdf | Tầm thực tế khoảng 1/3 tầm danh định khi UAV di chuyển; node mặt đất làm PAN coordinator | đã xác minh |
| Wen & Dargie, IEEE Sensors J. (TU Dresden) | 2020 | https://www.rn.inf.tu-dresden.de/uploads/Publikationen/impact.pdf | Link kém khi UAV ở gần mặt đất; radio điều khiển gây nhiễu 802.15.4 | đã xác minh |
| Palmer et al., data muling (ICRA) | 2015 | https://cse.unl.edu/~carrick/papers/PalmerYODB-ICRA15.pdf | Số node tối đa một UAV phục vụ được | đã xác minh |
| KTH Remote Sensing Using UAVs | — | https://people.kth.se/~gonga/remoteuav.html | TmoteSky trên UAV làm relay, Contiki | đã xác minh |
| Improving LoRa Signal Coverage… with UAVs (arXiv 1902.11243) | 2019 | https://arxiv.org/pdf/1902.11243 | Mote LoRa trên Phantom 4 Pro bay 25/50 m; độ cao và hướng ăng-ten quyết định | đã xác minh |
| Measurement of LoRa signal propagation… aerial gateway and ground gateway | 2025 | https://pure.nwpu.edu.cn/en/publications/measurement-of-lora-signal-propagation-in-urban-areas-utilizing-a/ | Mavic 3 mang RPi 4B + SX1302/1303, bay 50/100/150 m; dữ liệu công khai | đã xác minh (venue Scientific Data lấy theo trích đoạn) |
| UAV LoRa 860 MHz dataset (EPFL, arXiv 2512.15268) | 2025 | https://arxiv.org/pdf/2512.15268 | 4 gateway SDR trên mái nhà; mô hình kênh | đã xác minh |

## 3. Đề xuất testbed và phần cứng cho J2 (20–50 node)

Giá và công suất ghi "chưa xác minh" là ước lượng của tôi, không lấy từ nguồn đã thấy.

| Phần cứng | Radio | Giá ước lượng | Công suất | Lý do |
|---|---|---|---|---|
| nRF52840 USB Dongle (Nordic) | 802.15.4 + BLE 2,4 GHz | khoảng 10–16 USD (DigiKey, tổng hợp nhiều nhà phân phối) | TX 6,4 mA ở 0 dBm, 16,4 mA ở +8 dBm; RX 6,26 mA (3 V, DC/DC; số này đo ở BLE 1 Mbps, chưa thấy số riêng cho 802.15.4) | Radio chính cho node và gateway; rẻ; IoT-LAB cũng có nền tảng tương tự (chưa xác minh) |
| Grove Vision AI V2 + camera CSI | không có (giao tiếp I²C/UART) | 15,99 USD cho bo, camera mua riêng | khoảng 0,35 W khi chạy, 33 ms mỗi suy luận | Đối sánh signature trên NPU; đo được năng lượng mỗi lần match |
| Himax WE-I Plus EVB | không có | 65–70 USD | khoảng 2,5 mW (số của hãng) | Phương án công suất cực thấp, dùng cho vài node đo năng lượng |
| MAX78000 (vd. bo FTHR) | không có | chưa xác minh | 0,2–0,7 mJ mỗi suy luận | Có số năng lượng đã công bố để đối chiếu |
| OpenMV Cam H7 Plus | không có | chưa xác minh | 140–240 mA ở 3,3 V | Dễ lập trình (MicroPython) nhưng tốn điện; chỉ dùng làm baseline |
| ESP32-CAM | WiFi (không có 802.15.4) | rẻ (chưa xác minh) | ngủ sâu 0,5–18 mA tuỳ bo | Không khuyến nghị cho node, chỉ dùng thử nhanh |
| Gateway đôi: RPi + 2 × nRF52840 | 2 kênh 802.15.4 | khoảng 60–80 USD (chưa xác minh) | nguồn lưới hoặc pin lớn | Kiểm giả thuyết single- vs multi-radio; tiền lệ: Opal |
| Cluster head: thêm module SX126x/SX1302 | LoRa | chưa xác minh | — | Uplink LoRa như thiết kế; tiền lệ: RPi 4B + SX1302/1303 trên drone |
| Drone đa cánh (cỡ Mavic/Phantom) mang nRF52840 + RPi Zero | 802.15.4 | chưa xác minh | — | Thay cho fixed-wing; bay ở khoảng 45 m, ăng-ten song song mặt đất; tránh RC 2,4 GHz |

**Chiến lược hai tầng:**

- **(a) Chạy trên FIT IoT-LAB** cho phần mạng: quy mô hàng trăm node, thử chi phí pha 0, tô màu kênh, TSCH. Robot di
  động giả lập một lượt "pass" chậm ở mặt đất. Chưa kiểm được trang docs hiện hành vì host bị chặn.
- **(b) Tự dựng 20–50 node ngoài trời** cùng drone cho phần A2G và năng lượng: khoảng 30 × (nRF52840 + Grove V2) ≈
  1–1,5 nghìn USD cho bo mạch, chưa tính pin và vỏ (ước lượng).

D-Cube hoặc FlockLab 2 dùng để đo năng lượng và độ tin cậy, nhưng chỉ khi nền tảng của họ hỗ trợ nRF52840. Điều
này cần kiểm lại.

## 4. Tài liệu cho pha 0 (tổ chức mạng)

| Chủ đề | Tài liệu | Link | Ghi chú | Trạng thái |
|---|---|---|---|---|
| Lưới ô ảo | Xu, Heidemann, Estrin, "Geography-informed Energy Conservation for Ad Hoc Routing", MobiCom 2001, tr. 70–84 | https://doi.org/10.1145/381677.381685 | GAF: node tương đương trong một ô ngủ luân phiên; tiết kiệm 40–60 % năng lượng; tuổi thọ mạng tăng theo mật độ | đã xác minh |
| Phân cụm lục giác | Mammu et al., CCBE, Sensors 2015 | https://pmc.ncbi.nlm.nih.gov/articles/PMC4431196 | Cụm lục giác; chọn CH theo năng lượng còn lại; MAC cấp slot | đã xác minh (qua trích đoạn) |
| Phân cụm lục giác | Virtual hexagon clustering (Guan et al.) | https://pureportal.coventry.ac.uk/en/publications/a-novel-energy-efficient-clustering-technique-based-on-virtual-he/ | Hàm trọng số để chọn CH, tránh bầu lại thường xuyên | chỉ thấy tiêu đề và trích đoạn |
| Phân cụm lục giác | Hex-MASCLE (Uni Rostock) | https://www.itmz.uni-rostock.de/storages/uni-rostock/Alle_IEF/IMD/veroeff/Hex_MASCLE.pdf | — | chỉ thấy tiêu đề |
| Tô màu kênh/slot | Jemili et al., Collision Aware Coloring Algorithm for WSN | https://hal.archives-ouvertes.fr/hal-00808332 | Tô màu 2-hop phân tán, thời gian chạy xác định, không cần pha khám phá láng giềng | đã xác minh |
| Lý thuyết tô màu | Distributed multicoloring, STACS 2009 | https://doi.org/10.4230/LIPIcs.STACS.2009.1852 | Cận dưới số màu cho tính toán cục bộ | đã xác minh |
| TSCH | RFC 9033, 6TiSCH MSF | https://datatracker.ietf.org/doc/rfc9033/ | 6 bước join; dựa trên RFC 8180, 6P, CoJP | đã xác minh |
| TSCH | Quick6TiSCH (MASS 2024) | https://nsl.cau.ac.kr/papers/top/mass24-quick6tisch.pdf | Va chạm ở ô dùng chung là nút thắt; thời gian hình thành mạng giảm 62,6 % trên testbed | đã xác minh |
| TSCH | Join cho node ngoài DODAG (arXiv 2403.12949) | https://arxiv.org/html/2403.12949v1 | Thiếu slot cho DAO và yêu cầu cấp ô | đã xác minh |
| Đa radio | Opal, IEEE Embedded Systems Letters 2011 | https://dissem.in/p/25289957/opal-a-multiradio-platform-for-high-throughput-wireless-sensor-networks | Hai radio 802.15.4, thông lượng tăng 3,7× | đã xác minh |
| Đa radio | Dual-radio 802.15.4 trên OMNeT++ (Elektronika ir Elektrotechnika) | https://eejournal.ktu.lt/index.php/elt/article/view/15321 | Thông lượng tăng tới 36 %, năng lượng tăng tới 20 % (mô phỏng) | đã xác minh |
| Đa radio | Chọn gateway dual-radio (LCN 2012) | https://www.cs.cityu.edu.hk/~weliang/conf_papers/XLJT12.pdf | Tối đa tuổi thọ có ràng buộc thông lượng | đã xác minh |

**Chưa có link (cần tra tiếp):**

- Bài gốc TMCP (Wu et al. 2007) và DCA/CMAC (Chowdhury). Tôi chỉ thấy chúng được nhắc gián tiếp.
- SF-Fastboot (Minet, Teraoka, Tanaka, Watteyne, DCOSS 2021). Chưa thấy URL chắc chắn.
- Tái dùng 7 màu trên lưới lục giác (N = i² + ij + j²). Đây là kiến thức giáo trình cellular, cần một trích dẫn chuẩn.
- LEACH và HEED gốc.

## 5. Rủi ro

1. **Không có tiền lệ re-ID trên MCU.** Các số mJ hiện có là person detection hoặc wake word, không phải đối sánh
   với truy vấn 400 KB. Phải tự đo chi phí "nạp truy vấn + match" trên Grove V2 hoặc MAX78000. Số của hãng
   (0,7 mJ; 2,5 mW) là trường hợp tốt nhất.
2. **Testbed công cộng không có drone bay trên lưới 802.15.4.** Robot của IoT-LAB chậm, ở mặt đất, chạy quỹ đạo
   ghi sẵn. Kết quả A2G trong J2 vì vậy phải dựa vào thí nghiệm tự dựng, cần xin phép bay và chịu rủi ro thời tiết.
3. **Tầm A2G thực tế ngắn hơn mô hình:** khoảng 1/3 tầm danh định khi UAV di chuyển, PRR nhạy với hướng ăng-ten.
   Điều này có thể làm cửa sổ truyền 400 KB trong mô phỏng ns-3 tỏ ra lạc quan.
4. **Nhiễu từ radio điều khiển 2,4 GHz của drone.** Cần dùng RC hoặc telemetry ở 900 MHz/5,8 GHz, hoặc ghi rõ
   kênh 802.15.4 đã chọn.
5. **Công suất ngủ thực của bo phát triển** (ESP32-CAM ở mức mA, OpenMV hơn 100 mA khi nghỉ) cao hơn nhiều so với
   chip trần. Lịch ngủ "thật" trong J2 phải đo trên đúng bo đã chọn, bằng Joulescope hoặc PPK.
6. **Node hai bo (radio + NPU)** làm tăng công suất nghỉ và độ phức tạp. Hướng thay thế (SoC có cả 802.15.4 và
   NPU) chưa tra trong phiên này.
7. **Độ tin cậy dữ liệu:** toàn bộ số liệu lấy từ đoạn trích tìm kiếm. Hai host bị chặn nên chưa đọc được toàn văn
   bài UCSB và docs IoT-LAB. Một số con số còn mâu thuẫn, ví dụ số observer của FlockLab 2 hay giá các bo.
