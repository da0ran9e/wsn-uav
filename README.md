# wsn-uav · SigDrop

Nghiên cứu giao truy vấn tìm kiếm (ảnh tham chiếu, vài trăm kB) tới mạng camera biên bằng một lượt bay UAV
cánh bằng phát quảng bá IEEE 802.15.4, cộng hợp tác mặt đất đã lập kế hoạch (River) và đường bay LM-Tour.
Bản nộp IEEE ICC: *SigDrop: Pre-Planned Ground Cooperation for UAV Query Delivery to Edge-Camera Networks* (v5.3).

| Bắt đầu từ | Để làm gì |
|---|---|
| `CLAUDE.md` | quy tắc làm việc và bản đồ repo |
| `docs/progress/HANDOFF.md` | trạng thái hiện tại, việc dở, lệnh |
| `docs/EXPERIMENTS-INDEX.md` | các thí nghiệm có số trong paper, kèm log, dữ liệu, tài liệu |
| `docs/DOCS-INDEX.md` | mọi tài liệu theo trạng thái (hiện hành / tham khảo / bị thay thế / lịch sử) |
| `logs/INDEX.md` | mọi thư mục log chạy chương trình |
| `docs/chatlog/INDEX.md` | lời gốc của người dùng theo mục |
| `params.yaml` | tham số giả lập (bảng `paper/PARAMS-vi.md` sinh từ đây) |

Kiểm tra repo: `python3 tools/check.py`; dựng lại chỉ mục tài liệu: `python3 tools/build_index.py`.
Mã wsn-uav cũ (scenario 1–4) nằm ở `archive/wsn-uav-legacy/`.
