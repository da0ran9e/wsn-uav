# 2026-11-20 · Cỡ truy vấn và chặn dưới không hợp tác (chatlog mục 370)

Mục đích: xem chặn dưới của mọi phương án không hợp tác (Mệnh đề 1 của bản thảo, có tính quãng bay) đổi thế nào khi truy vấn
nhỏ đi (vector đặc trưng thay ảnh).

Lệnh: `bound-nc-Q400.md`, `bound-nc-Q1000.md`: chạy `paper/j1/draft-v1/analysis/bound_nc.py` qua một lớp bọc đặt
`common.Q` = 400 và 1 000 (bản gốc Q = 4 041). Đầu vào như lần chạy gốc (bản đồ C4, `campaign4.csv`, điểm L1).

Đầu ra: `paper/j1/figs-q/bound-nc-Q400.md`, `bound-nc-Q1000.md`. Kết quả chính và nhận xét ở `paper/j1/CONTEXT-vi.md` mục 27.
Chặn phủ (Định lý 2) tỉ lệ thẳng với Q nên tính tay.
