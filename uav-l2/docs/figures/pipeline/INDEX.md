# Hình luồng chương trình

| Tệp | Mô tả | Sinh bằng | Tham số | Ngày | Commit |
|---|---|---|---|---|---|
| files-flow.png, files-flow.svg | Sơ đồ các tệp của một nhiệm vụ ns-3 và cách chúng tương tác: chạy chiến dịch, Python điều phối, kế hoạch River, ba binary ns-3, thư mục WORK, chấm điểm; mũi tên liền = gọi chạy, đứt = import/include, chấm = ghi/đọc tệp | `dot -Tsvg files-flow.dot -o files-flow.svg && dot -Tpng -Gdpi=100 files-flow.dot -o files-flow.png` | nguồn `files-flow.dot` (sửa tay khi luồng đổi) | 2026-11-09 | sau a979590 |
