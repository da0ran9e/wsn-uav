# Tìm hiểu VaN3Twin (2026-11-20, chatlog mục 361)

Mục đích: xem VaN3Twin (github.com/DriveX-devs/VaN3Twin) có dùng được cho kênh A2G/G2G đô thị của J1 không. Chỉ đọc, không
build, không chạy mô phỏng.

Lệnh đã chạy:

```sh
git clone --depth 1 --filter=blob:limit=2m https://github.com/DriveX-devs/VaN3Twin.git repo   # trong scratchpad, 297 MB, không commit
grep/sed trên README.md, sandbox_builder.sh, src/sionna/ (connection handler, server script, propagation-loss-model.cc)
nvidia-smi; nproc; free -g   # container: không GPU, 4 nhân, 15 GB
```

Bài arXiv 2505.14184 đọc qua web (bản HTML v3; mục IV–VI chỉ qua bản tóm tắt, số ở bảng V chưa đối chiếu bảng gốc).

Đầu ra: `paper/j1/TOOL-VAN3TWIN-vi.md`. Kết quả chính: VaN3Twin nền ns-3.35, không có 802.15.4, dò tia mọi cặp nên không
chạy được ở 13 000 node; đề xuất không dùng, giữ LoS hình học, có thể dùng Sionna RT ngoại tuyến trên một ô nhỏ để hiệu
chỉnh K1c. Còn dang dở: chưa thử cài Sionna, chưa đo thời gian dò tia trên CPU.
