# 2026-10-22 · Dựng lại môi trường trên container mới

**Mục đích:** container mới không có cây ns-3 `/home/user/ns3-dev` và thiếu gói Python.

**Lệnh:** `setup.sh` (tải ns-3.46 từ gitlab, symlink `uav-sar`, `uav-coop`, `uav-coop2` vào `src/`, configure optimized với ba module đó, build 4 luồng); `pip install matplotlib markdown pymupdf`. Log: `ns3-build.md`, `pip.md`.

**Kết quả:** build xong trong 193 s, mã thoát 0. Binary đóng băng chép vào scratchpad `BIN/` (deploy-bin, pass-bin, river-bin, lib/, pass-lib → lib). Python 3.13 (không có 3.10; ns-3.46 chạy được với 3.13).

**Dang dở:** chưa cài TeX (chỉ cần khi dựng PDF báo cáo lớp 2).
