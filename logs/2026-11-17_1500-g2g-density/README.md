# 2026-11-17 · Mật độ node và lưới cell G2G (chatlog mục 333)

Mục đích: giãn cách node tối đa để lưới cell R = 100 m còn liên thông và còn gateway giữa mọi cặp cell kề, trên đúng kênh
G2G của mô phỏng. Tính Monte Carlo, không chạy ns-3.

Lệnh: `run.md` (`python3 paper/j1/analysis/g2g_density.py --trials 400 --seed 1`, chạy khoảng 1 phút).

Kết quả: giãn cách tối đa khoảng 50–60 m (280–400 node/km², 7–10 node một cell); từ 70 m có 10 % cặp cell kề mất gateway
dùng được; ETX trong cell khoảng 1,9 mỗi 100 m ở mọi giãn cách còn liên thông. Bảng và nhận xét ở
`paper/j1/CONTEXT-vi.md` mục 10.

Dang dở: chưa tính che khuất tương quan không gian, chưa tính P_k của pha bay theo mật độ, chưa chạy ns-3 ở các mức mật độ.
