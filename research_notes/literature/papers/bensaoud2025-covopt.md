---
status: reference
updated: 2026-11-12
key: bensaoud2025-covopt
doi: 10.1109/JSYST.2025.3532232
title: Coverage Optimization for Reliable UAV-Assisted 5G/6G Communication Systems
authors: B. Ben Saoud, L. Nasraoui
venue: IEEE Systems Journal 19(1):65–74
year: 2025
file: Coverage_Optimization_for_Reliable_UAV-Assisted_5G_6G_Communication_Systems.pdf (Drive); tr. 1 = trang 65
topics: uav-coverage, a2g-channel
relevance: ★
read: abstract
---
# Ben Saoud, Nasraoui 2025 · Tối ưu vùng phủ cho hệ thống 5G/6G có UAV hỗ trợ

## Tóm tắt một dòng
Với mô hình LoS xác suất (nhà phân bố Poisson, chiều cao trong [h_min, h_max]) và fading Rician có hệ số K phụ thuộc góc ngẩng, bán kính phủ đạt ngưỡng SNR hoặc hiệu suất phổ tăng theo độ cao rồi giảm (hai chế độ), có độ cao tối ưu ứng cùng một góc ngẩng cho mọi chỉ số; bay trên bề mặt bê tông cho bán kính lớn tới 5 lần so với đất gồ ghề có cây.

## Vì sao đọc
Chỉ để biết: xác nhận lại kết quả "góc ngẩng tối ưu cố định" của Al-Hourani 2014 với mô hình fading Rician theo góc, thêm ảnh hưởng bề mặt đất [KÊNH].

## Bài toán và mô hình
- **[GĐ]** Liên kết lai không–đất; LoS xác suất; fading đa đường Rician với K theo góc ngẩng (mô hình vật lý hoặc mũ); yêu cầu QoS về SNR ξ hoặc hiệu suất phổ C₀ (tr. 1–4).

## Định nghĩa và ký hiệu
| Ký hiệu | Nghĩa |
|---|---|
| h₁, h₂ | độ cao UAV, độ cao thiết bị mặt đất |
| ξ, C₀ | ngưỡng SNR, ngưỡng hiệu suất phổ |
| P_D, P_C | xác suất đạt ngưỡng SNR, hiệu suất phổ |
| φ | góc ngẩng |
| K | hệ số Rician |

## Kết quả chính
- **[KQ]** Bán kính phủ tăng theo xác suất LoS (tăng theo độ cao) đến một độ cao rồi giảm do suy hao đường truyền; độ cao tối ưu ứng cùng góc ngẩng cho mọi chỉ số (tr. 1, 9).
- **[SỐ]** Đô thị phủ kém ngoại ô 5 lần khi bay trên bê tông (LoS mạnh), tới 30 lần trên đất gồ ghề; bê tông cho bán kính lớn tới 5 lần so với bề mặt có cây (tr. 1, 9).

## Thuật toán
Không có thuật toán; tìm số tập cấu hình (h₁, R_h₁) đạt mục tiêu P_D, P_C = 0,9 (Fig. 8–9).

## Thực nghiệm và số liệu
Không đọc (mức abstract).

## Hình tiêu biểu
Không có (bài ★, không chọn hình).

## Trích nguyên văn
- **[TRÍCH]** "this optimal position occurs at the same elevation angle across all metrics considered." (tr. 9)

## Liên hệ SigDrop
- **[NX] [KÊNH]** Củng cố việc dùng góc ngẩng để định nghĩa bán kính vùng nghe; ảnh hưởng bề mặt đất (bê tông/đất/cây) là tham số mô hình kênh SigDrop chưa xét.

## Hạn chế và câu hỏi mở
- Chỉ đọc abstract, mở đầu, kết luận.
