---
status: reference
updated: 2026-11-12
key: liang2008-typhoon
doi: 10.1007/978-3-540-77690-1_17
title: "Typhoon: A Reliable Data Dissemination Protocol for Wireless Sensor Networks"
authors: C.-J. M. Liang, R. Musăloiu-E., A. Terzis
venue: EWSN 2008, LNCS 4913, tr. 268–285
year: 2008
file: 978-3-540-77690-1_17.pdf (Drive); chỉ có 2 trang đầu (tr. 1 = trang 268, tr. 2 = trang 269)
topics: dissemination
relevance: ★
read: abstract
---
# Liang, Musăloiu-E., Terzis 2008 · Typhoon: phổ biến dữ liệu tin cậy trong WSN

## Tóm tắt một dòng
Typhoon phát dữ liệu bằng unicast có ACK (khôi phục mất gói nhanh) nhưng các nút khác nghe lén (snooping) để nhận cùng lúc, đặt bộ hẹn giờ theo không gian để nút xa nguồn ưu tiên chuyển tiếp, và đổi kênh để giảm khoảng cách tái dùng không gian từ ba xuống hai chặng; nhanh và tiết kiệm năng lượng hơn Deluge tới 3 lần, rõ nhất ở mạng thưa, mất gói nhiều.

## Vì sao đọc
Chỉ để biết: một biến thể Deluge giảm nghe rỗi; nêu ý "đổi kênh giảm khoảng tái dùng xuống 2 chặng" so với giới hạn 3 chặng của Deluge.

## Bài toán và mô hình
- **[GĐ]** Phổ biến đối tượng lớn (~50–100 KB) tới mọi nút, tin cậy 100 % (tr. 1).
- **[GĐ]** Nghe rỗi là nguồn tiêu hao năng lượng chính, nên mọi quyết định giao thức nhằm giảm thời gian nút không gửi/nhận dữ liệu (tr. 1).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| network completion time | thời điểm mọi nút nhận đủ đối tượng (tr. 2) |
| page | phần của đối tượng, pipeline theo trang như Deluge |

## Kết quả chính
- **[KQ]** Unicast + ACK dương + nghe lén: khôi phục nhanh và vẫn giao cho cả vùng quảng bá bằng một lần phát (tr. 1).
- **[KQ]** Khoảng cách tối thiểu tránh nhiễu giữa các phát đồng thời là ba chặng; đổi kênh (802.15.4 có 16 kênh không chồng) giảm còn hai chặng trong nhiều trường hợp (tr. 2).
- **[SỐ]** Nhanh hơn và tiết kiệm năng lượng hơn Deluge tới 3× (mô phỏng và testbed trong nhà) (tr. 1).

## Thuật toán
- **[TT]** Bộ hẹn giờ theo không gian, unicast + snooping, đổi kênh khi truyền dữ liệu; chi tiết ở mục 3 (không có trong bản 2 trang).

## Thực nghiệm và số liệu
Không có trong bản PDF (chỉ 2 trang đầu).

## Hình tiêu biểu
Không có.

## Trích nguyên văn
- **[TRÍCH]** "Typhoon is able to reduce dissemination time and energy consumption by up to three times compared to Deluge." (tr. 1)

## Liên hệ SigDrop
- **[NX] [D]** Ý "đổi kênh giảm khoảng tái dùng xuống 2 chặng" ảnh hưởng tới cận dưới thời gian phổ biến mặt đất: giới hạn 1/3 của Deluge không phải là cố định nếu đa kênh.

## Hạn chế và câu hỏi mở
- PDF chỉ có 2 trang; mọi khẳng định chỉ lấy từ abstract và mở đầu.
