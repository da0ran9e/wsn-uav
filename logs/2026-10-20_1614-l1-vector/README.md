# 2026-10-20 · Lớp 1 bằng điểm cosine của từng ảnh, bản thử (CLAUDE.md §8 mục 110)

**Mục đích:** thử ý tưởng thay xác suất khớp đã công bố bằng điểm cosine của từng ảnh, để node xếp hạng còn BS xếp hạng các cell. Câu hỏi: hạng của cell thật thay đổi thế nào theo độ tách d′, người mặc giống, thiết bị lệch nhau, k, và cách node báo điểm.

**Lệnh:** `run.md`: `uav-l2/tools/l1_vector.py --draws 2000`, 48 cấu hình × 3 cách xếp hạng, khoảng 1 phút.

**Đầu ra:**
- `uav-l2/docs/data/l1/vector.csv`
- Thiết kế và kết quả: `paper/L1-VECTOR-vi.md`

**Kết quả chính** (d′ = 4, k = 3, thiết bị lệch, tỉ lệ cell thật đứng đầu):

| | Điểm thô | Chuẩn hoá theo camera | TB 3 điểm đầu, chuẩn hoá |
|---|---|---|---|
| Không có người mặc giống | 65 % | 84 % | 87 % |
| 2 % người mặc giống | 24 % | 29 % | 42 % |

**Dang dở:**
- Hàm kết hợp ở BS chưa chốt.
- Chưa nối bảng xếp hạng vào giả lập nhiệm vụ.
- Chưa có mức vector.
- μ_L, ρ, τ và khoảng a_c là tham số tôi chọn để thử, không phải số đo.
