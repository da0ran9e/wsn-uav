# Cỡ cụm của các bản đồ C4 k8, k12, k16 (chatlog mục 416)

Mục đích: giải thích vì sao bản đồ "k16" chỉ có 15 cụm và có cụm nào quá 80 cell không.

Lệnh: `01-cluster-sizes.md` gọi `restructure.domain(K, seed=1)` (cùng hàm `mission.py stage_map` dùng) rồi `partition.partition(land, 80)`
trong `uav-l2/tools`.

Kết quả: bộ sinh bản đồ đặt 80·K cell rồi đục K hồ, mỗi hồ khoảng 10 cell; số cụm là ⌈số cell đất / 80⌉. k8 có 617 cell đất, ra 8 cụm
(70–80 cell); k12 có 899, ra 12 cụm (53–80); k16 có 1 126, ra 15 cụm (57–80). Không cụm nào quá 80 cell. Chữ "k16" là tham số sinh bản
đồ, không phải số cụm.

Kèm phép tính tay (không có tệp log riêng): thời gian LoRa cho truy vấn dạng vector, quy tỉ lệ từ bảng 400 KB ở
`paper/j1/archive/urban-v1/CONTEXT-vi.md` mục 12. 12 vector 512 chiều: float32 24 576 B, float16 12 288 B, int8 6 144 B. SF7 (gói 222 B):
39 / 19 / 10 s phát thuần, 6,4 / 3,2 / 1,6 phút ở chu kỳ 10 %, 64 / 32 / 16 phút ở chu kỳ 1 %. SF12 (51 B): 198 / 99 / 49,5 phút ở
chu kỳ 10 %.
