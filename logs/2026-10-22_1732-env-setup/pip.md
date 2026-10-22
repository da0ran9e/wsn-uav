# Cài gói Python

- Bắt đầu: 2026-10-22 17:32:54, chạy 19 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
pip install --break-system-packages -q matplotlib markdown pymupdf 2>&1 | tail -3; python3 -c 'import matplotlib, markdown, pymupdf; print("ok", matplotlib.__version__)'
```

**Kết quả**

```text
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv
ok 3.11.2
```
