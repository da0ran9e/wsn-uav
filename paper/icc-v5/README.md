# Draft v5: Algorithm 3 and Evaluation (CLAUDE.md §8 item 184)

Bộ khung cho bản `SigDrop_ICC_draft_v5.pdf`. Chưa chạy thực nghiệm mới (người dùng sắp hết quota).

| Tệp | Nội dung |
|---|---|
| `alg3-lmtour.tex` | Algorithm 3 bản v5: dòng 6 và 8 dùng đĩa B(·, ξ); giá trị ξ theo (5) cho từng r |
| `evaluation-v5.tex` | Mục VI viết lại: setup, tên phương án mới, hai bảng, hình, đoạn VI-C, VI-D |
| `table-tstar.tex`, `table-complete.tex` | sinh bởi `estimate.py` |
| `figs/fig6-tstar-vs-k-4ranges.{pdf,png}` | Fig. 6 vẽ lại: T\* theo K, bốn panel theo r |
| `numbers.csv` | mọi số trong bảng và hình, cột `kind` = measured / estimate |

**Số đo** lấy từ `uav-l2/docs/data/results/baselines.csv` (ns-3, 26/10). **Số LM-Tour là ước lượng** (đánh dấu đỏ [EST]), công thức và giả định ở đầu `estimate.py`: T\* chạy gần 1:1 theo thời điểm sẵn sàng trung bình; giả sử LM-Tour cắt nửa thời gian River của các cell không tự giải mã được (G = 0,5), tour không đổi. Kết quả ước lượng: nhanh hơn CHORD 1–7 % ở r ≤ 500 m, 0 % ở 1 km. G = 0,5 là lạc quan: các lần chạy mức mô hình trước (ξ = R/2) không thấy lợi.

**Đổi tên:** B1 → No broadcast (rotary TSP); B4 → Single pass, no cooperation; DN → FC + DTSP-N; FC → FC + gather; P\* → CHORD + River-FC. Bỏ Direct pull khỏi bảng và hình mức nhiệm vụ (mục VI-B về River vs direct pull trên một cụm vẫn giữ). Bảng I thêm hàng River-FC + LM-Tour.

**ξ** (mã: `lm_tour.py plan --xi auto` hoặc `--xi 100|175|250`): ξ = min(ω = 303, ρ = 255, √(r² − h²)) = 255 / 255 / 199 / 99 m cho r = 1000 / 500 / 200 / 150 m.

**Các TODO đỏ trong v5:**

| TODO | Xử lý |
|---|---|
| Tác giả, đơn vị | để người dùng |
| Abstract: "X % incomplete" | số đo: không hợp tác 0–1 % hoàn tất ở r ≤ 200 m (FC lượn nên 100 %, cái giá là thời gian, Bảng I) |
| III-C: nguồn h_v, ν_v | chưa; giả lập dùng mô hình cosine của `paper/L1-MODEL-vi.md`, không dùng V(H) |
| V: quét ξ ∈ {100, 175, 250} | đã có cờ `--xi`; chưa chạy |
| V: chứng minh / trích số hạng Dubins; vẽ tour và River theo R | chưa |
| V: Students (1)–(5) | (1) đã cài trừ GROW; (2) bộ dự đoán xong; (3)–(4) quét R trước đây không thấy lợi; (5) hình của người dùng |
| VI: các chế độ A2G | xong: L_obs = 0 / 9,0 / 19,8 / 25,7 dB |
| VI-C, Bảng I: RUN | điền số đo; hàng LM-Tour [EST] |
| VI-D: chạy lại với V(H), T_hit, event pull, quét r | quét r xong; V(H) và event pull chưa cài |
| Kết luận: kết quả LM-Tour, đo A2G thực địa | chờ chạy |
| Tài liệu [12], [24], [26] | chưa kiểm |

**Lệnh khi có quota** (mỗi kênh, mỗi bản đồ; FIX như `uav-l2/docs/RESULTS-vi.md`):
```text
python3 uav-l2/tools/lm_tour.py plan FIX/ENV/kK-s1 --out LM5/ENV/kK-s1 --R 450 --xi auto --rounds 1 --free
python3 uav-l2/tools/lm_tour.py score LM5/ENV/kK-s1 --mode pred --out LM5/ENV-kK
```
rồi chạy ns-3 trên pass mới (bước D) trước khi thay số [EST].
