# Cài scikit-learn (river_surrogate cần cho lm_tour plan; thiếu làm hỏng tác vụ R1 r200 k16 lần đầu)

- Bắt đầu: 2026-10-27 18:17:38, chạy 3 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
pip install --break-system-packages -q scikit-learn 2>&1 | grep -v WARNING | tail -3; python3 -c 'import sklearn, scipy; print("ok", sklearn.__version__, scipy.__version__)'
```

**Kết quả**

```text
ok 1.9.1 1.17.1
```
