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

## Phần hai: Sionna RT (chatlog mục 399)

```sh
pip index versions sionna-rt          # 2.2.0
pip download sionna-rt --no-deps -d <scratchpad>/sw   # wheel 8,5 MB, giải nén để đọc, không cài
grep trong sionna/rt/__init__.py, radio_materials/itu.py, radio_map_solvers/radio_map_solver.py, scene.py
```

Đầu ra: `paper/j1/TOOL-SIONNA-vi.md`. Chạy CPU được (biến thể LLVM), vật liệu ITU phủ 2,4 GHz. Dang dở: thử nghiệm nhỏ
(cài, dựng mesh một ô Punggol, đo thời gian) chờ người dùng duyệt.
