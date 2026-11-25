# Đọc phần phát biểu bài toán của các bài tiêu biểu (chatlog mục 400)

Mục đích: chọn các bài có cách phát biểu bài toán quen thuộc để học cách viết (P0), (P1), (P2) của J1.

Lệnh (chạy tay, trong scratchpad, không commit PDF):
- `curl -L -o <id>.pdf https://arxiv.org/pdf/<id>` với id 1705.02723, 1708.00221, 1703.05401, 1911.08959, 1801.02799, 1304.5330, 2512.08576
- `pdftotext` (có và không `-layout`) để đọc phần system model và problem formulation

Trong repo: ghi chú `research_notes/literature/papers/zeng2018-multicast.md`.

Đầu ra: `paper/j1/FORMULATION-EXAMPLES-vi.md`. Mozaffari 2017 (1703.05401) đã đọc nhưng không chọn làm mẫu chính.
Còn dở: chưa ghi chú các bài arXiv vào repo (chờ người dùng quyết, theo quy tắc mục 328).
