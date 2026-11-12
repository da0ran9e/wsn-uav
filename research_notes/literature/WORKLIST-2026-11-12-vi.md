---
status: current
updated: 2026-11-12
---
# Danh sách ghi chú 50 PDF trong Drive (phạm vi C, chạy tuần tự)

Theo chat log mục 312–313: ghi chú mọi bài trong thư mục Drive theo `METHOD-vi.md`, làm tuần tự trong một phiên. Thứ tự:
★★★ (đọc toàn văn) → ★★ (đọc một phần) → ★ (`read: abstract`: abstract, mở đầu, kết luận, 1–2 hình). Khoá dưới đây là
đề xuất. Sau khi đọc trang đầu, sửa khoá theo họ tác giả đầu thật (quy tắc khoá ở METHOD §2) và ghi lại ở cột "Khoá dùng".

- **Nguồn PDF:** thư mục Drive `https://drive.google.com/drive/folders/1t7LkA-jF7JAL6tFUrS5RakqcmkwQOEi2`.
  - Tải: `python3 tools/papers/drive_fetch.py "<link>" <scratchpad>/pdf`.
  - Trích: `python3 -I tools/papers/pdf_extract.py <pdf> <key> <scratchpad>/papers`.
  - Cần `python3 -m pip install pymupdf`; dùng `python3 -m pip` vì `pip` có thể trỏ tới bản Python khác.
- **DOI:** metadata Crossref tự lấy bị sai ở `shkel2001` (ra một bài về cây việt quất) và `gudmundson1991`. Luôn đối chiếu DOI với trang đầu bài.
- **Đã có, bỏ qua:**
  - `leny2012-dtsp`, `zeng2018-multicast`, `isaacs2011-dtspn`;
  - `1708.06478v1` là bản arXiv của Zeng 2018: chỉ thêm một dòng vào mục Hạn chế của `zeng2018-multicast.md`, không cần file riêng;
  - `leny2012 (1).pdf` trùng từng byte với `leny2012.pdf`.

| # | File PDF | Khoá đề xuất | Mức | Đọc | Chủ đề gợi ý | Khoá dùng | Xong |
|---|---|---|---|---|---|---|---|
| 1 | hui2004.pdf | hui2004-deluge | ★★★ | full | dissemination, control-overhead | `hui2004-deluge` | ✓ |
| 2 | gallager1976.pdf | gallager1976-protocol | ★★★ | full | control-overhead | `gallager1976-protocol` | ✓ |
| 3 | minsky2003.pdf | minsky2003-setrecon | ★★★ | full | control-overhead | `minsky2003-setrecon` | ✓ |
| 4 | du2017.pdf | du2017-pando | ★★★ | full | dissemination, coding | `du2017-pando` | ✓ |
| 5 | IEEE_WTran08_Stojanovic_Wu_Sharif_Starobinski_rev4.pdf | stojanovic2009-nccoop | ★★★ | full | coding, ground-coop | `stojanovic2009-nccoop` | ✓ |
| 6 | savla2008.pdf | savla2008-dtsp | ★★★ | full | dtsp, approx-bound | `savla2008-dtsp` | ✓ |
| 7 | babel2017.pdf | babel2017-obstacles | ★★★ | full | dtsp, dtspn, np-hard | `babel2017-obstacles` | ✓ |
| 8 | al-hourani2014.pdf | alhourani2014-lap | ★★★ | full | a2g-channel, uav-coverage | | |
| 9 | matolak2017.pdf | matolak2017-a2g | ★★★ | full | a2g-channel | | |
| 10 | nekrasov2019.pdf | nekrasov2019-aerial154 | ★★★ | full | uav-collection, a2g-channel, testbed | | |
| 11 | techy2009.pdf | techy2009-wind | ★★★ | full | trajectory-error, dtsp | | |
| 12 | 02_kulkarnis_mnp.pdf | kulkarni2005-mnp | ★★ | partial | dissemination | | |
| 13 | FZMT2012.pdf | ferrari2012-lwb | ★★ | partial | dissemination, testbed | | |
| 14 | infocom-reliability.pdf | (theo tác giả) 2008-ncrel | ★★ | partial | coding | | |
| 15 | nsdi13-final22.pdf | (theo tác giả) 2011-chandiv | ★★ | partial | a2g-channel, testbed | | |
| 16 | main.pdf | (theo tác giả) 2021-lqe | ★★ | partial | uav-collection, a2g-channel | | |
| 17 | gudmundson1991.pdf | gudmundson1991-shadow | ★★ | partial | a2g-channel | | |
| 18 | nelson2007.pdf | nelson2007-vfield | ★★ | partial | trajectory-error | | |
| 19 | park2007.pdf | park2007-guidance | ★★ | partial | trajectory-error | | |
| 20 | dubins1957.pdf | dubins1957-curves | ★★ | partial | dtsp | | |
| 21 | leny2007.pdf | leny2007-highdensity | ★★ | partial | dtsp, np-hard | | |
| 22 | rathinam2007.pdf | rathinam2007-multivehicle | ★★ | partial | dtsp, multi-uav, approx-bound | | |
| 23 | s10732-020-09440-2.pdf | (theo tác giả) 2020-dtspheur | ★★ | partial | dtsp, tsp-solver | | |
| 24 | noon1993.pdf | noon1993-gtsp | ★★ | partial | tsp-solver | | |
| 25 | helsgaun2000.pdf | helsgaun2000-lkh | ★★ | partial | tsp-solver | | |
| 26 | obermeyer2009.pdf | obermeyer2009-recon | ★★ | partial | dtspn | | |
| 27 | penicka2017.pdf | penicka2017-dopn | ★★ | partial | orienteering, dtspn | | |
| 28 | 10.1007@s10514-019-09844-5.pdf | (theo tác giả) 2019-datacoll | ★★ | partial | orienteering, uav-collection | | |
| 29 | Joint_Rate_and_Coverage_Design_for_UAV-Enabled_Wireless_Networks_with_Underlaid_D2D_Communications.pdf | (theo tác giả) 2020-d2d | ★★ | partial | uav-coverage, ground-coop | | |
| 30 | Fixed-Wing-UAV-Coverage-Path-Planning-Based-on-Turning-Span-Selection.pdf | (theo tác giả) 2025-turnspan | ★ | abstract | uav-coverage | | |
| 31 | 978-3-540-77690-1_17.pdf | liang2008-typhoon | ★ | abstract (chỉ có 2 trang) | dissemination | | |
| 32 | shkel2001.pdf | shkel2001-dubinsset | ★ | abstract | dtsp | | |
| 33 | ma2006.pdf | ma2006-receding | ★ | abstract | dtsp | | |
| 34 | faigl2017.pdf | faigl2017-ceop | ★ | abstract | orienteering | | |
| 35 | vana2017.pdf | vana2017-budget | ★ | abstract | orienteering, uav-collection | | |
| 36 | sensors-23-06432.pdf | (theo tác giả) 2023-minmax | ★ | abstract | dtsp, multi-uav | | |
| 37 | sensors-23-02560-v2.pdf | (theo tác giả) 2023-coverage | ★ | abstract | uav-coverage, multi-uav | | |
| 38 | 1-s2.0-S2214914725000170-main.pdf | (theo tác giả) 2025-fwcoverage | ★ | abstract | uav-coverage, multi-uav | | |
| 39 | Deep_Reinforcement_Learning_for_AoI_Minimization_in_UAV-Aided_Data_Collection_for_WSN_and_IoT_Applications_A_Survey.pdf | (theo tác giả) 2024-aoi | ★ | abstract | uav-collection | | |
| 40 | An_Optimized_LTE-Based_Technique_for_Drone_Base_Station_Dynamic_3D_Placement_and_Resource_Allocation_in_Delay-Sensitive_M2M_Networks.pdf | (theo tác giả) 2023-lte | ★ | abstract | uav-coverage | | |
| 41 | Coverage_Maximization_for_Heterogeneous_Aerial_Networks.pdf | (theo tác giả) 2022-hetcov | ★ | abstract | uav-coverage | | |
| 42 | Coverage_Optimization_for_Reliable_UAV-Assisted_5G_6G_Communication_Systems.pdf | (theo tác giả) 2025-covopt | ★ | abstract | uav-coverage | | |
| 43 | Energy_and_Service-Priority_aware_Trajectory_Design_for_UAV-BSs_using_Double_Q-Learning.pdf | (theo tác giả) 2021-dql | ★ | abstract | uav-coverage | | |
| 44 | Multi-UAV_Assisted_Network_Coverage_Optimization_for_Rescue_Operations_using_Reinforcement_Learning.pdf | (theo tác giả) 2023-rescue | ★ | abstract | uav-coverage, multi-uav, sar | | |
| 45 | UAV-Assisted_Cellular_Communication_Joint_Trajectory_and_Coverage_Optimization.pdf | (theo tác giả) 2021-cellular | ★ | abstract | uav-coverage | | |
| 46 | tan2003.pdf | tan2003-pegasis | ★ | abstract | wsn-gathering | | |

Mức sao là đề xuất. Nếu đọc xong thấy khác thì sửa `relevance` trong ghi chú, giữ thứ tự làm như bảng.

## Quy tắc chạy

1. **Mỗi bài:**
   - viết `papers/<key>.md` theo khuôn METHOD §4;
   - chép hình đã chọn vào `papers/figures/`;
   - điền "Khoá dùng" và "Xong" ở bảng này;
   - commit và push ngay (nhánh `claude/document-review-xslwgg`). Nhờ vậy việc bị ngắt giữa chừng vẫn giữ được phần đã xong.
2. **Mỗi 5 bài, và ở cuối:** chạy `python3 tools/papers/paper_index.py && python3 tools/build_index.py && python3 tools/check.py`.
3. **Chủ đề mới ngoài bảng METHOD §6** (ví dụ cho path-following): thêm vào bảng §6 trước khi dùng.
4. **Cuối việc:**
   - cập nhật `NOTES-DRIVE-PDF-vi.md` §1, các ý mới quan trọng nhất cho J1;
   - viết `logs/<ngày-giờ>-paper-notes/README.md` và thêm dòng vào `logs/INDEX.md`;
   - báo số bài xong và bài nào còn thiếu hoặc hỏng.
5. **Ngân sách:** khoảng 0,7–0,8 triệu token. Bài ★ chỉ đọc mức abstract, bài ★★ bỏ phụ lục và chứng minh dài.
