# Hình minh hoạ cho đề cương nghiên cứu

Hình sơ đồ, không chữ (quy tắc mục 63). Sinh bằng `python3 research_notes/proposal/figs.py`. Dùng trong
`research_notes/proposal/SIGDROP-PROPOSAL-vi.md` (mục 290).

| Tệp | Mô tả | Lệnh | Tham số | Ngày | Commit |
|---|---|---|---|---|---|
| `prop-b-deviation-threshold.png` | lưới lục giác; quỹ đạo dự kiến (đứt) qua dải SPINE xanh đậm, vùng sửa từ cell kề xanh nhạt; quỹ đạo thật (liền) lệch e (mũi tên hai đầu); cell cam ngoài vùng, mũi tên đỏ kéo về SPINE | `figs.py` (`deviation`) | sơ đồ, không dữ liệu | 2026-11-08 | xem git log |
| `nd2-takeover-header-report.png` | quỹ đạo dự kiến qua SPINE xanh đậm, quỹ đạo thật qua các cell cam; mũi tên chấm là báo cáo, mũi tên cam là dữ liệu kéo về, mũi tên xanh tới critical cell đỏ | `figs.py` (`takeover`) | sơ đồ | 2026-11-08 | xem git log |
| `nd0-phase0-topology-and-plan-flow.png` | lưới cell có CL (chấm xám) và cặp gateway (đoạn đen); mũi tên chấm từ cell lên trạm gốc (thoi đen), mũi tên đỏ từ trạm gốc xuống cell | `figs.py` (`phase0`) | sơ đồ | 2026-11-08 | xem git log |
| `nd6-phase2-score-ordered-visits.png` | lưới cell nhạt; 7 cell nghi vấn tô đỏ đậm dần và vòng tròn to dần theo điểm; tour từ trạm gốc thăm theo điểm giảm dần | `figs.py` (`phase2`), seed 3 | sơ đồ | 2026-11-08 | xem git log |
