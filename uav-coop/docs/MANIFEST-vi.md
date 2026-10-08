# Bước 5 — Manifest giữa các cell (pha cơ sở)

## 0. Bản tham chiếu gốc (nguyên văn, không chỉnh sửa)

Các đoạn dưới đây là mô tả của tác giả, chép nguyên văn để làm chuẩn đối chiếu. Mọi
phần đặc tả và cài đặt phía sau phải khớp với chúng. Chỗ nào chưa khớp thì ghi rõ ở
mục 4.

**(a) Ý tưởng ban đầu** (trích phần nói về manifest; câu cuối của tin nhắn này nói về việc cài chia sẻ nội cell trước)

> ý tưởng là trong một cell các gói được tính là tài sản chung và tự trao đổi nhanh để nắm bắt tình hình của nhau, nếu cell đó thiếu mảnh nào thì manifest mảnh đó.
> gói tin manifest sẽ được gửi về hướng CH nhưng không cần phải tới được Ch. Trên đường gói tin đó đi, các cell nghe manifest nếu có thể đáp ứng thì đáp ứng luôn và sửa lại manifest theo điều kiện cell đó hiện tại, dần dần manifest sẽ được đáp ứng ngay cả khi nó chưa tới được CH

**(b) Cơ chế**

> theo tôi như này:
> khu vực vốn đã lên kế hoạch ký nên các cell vốn đã biết được vị trí của nhau rồi. cell nằm ở biên ngay sau khi tóm tắt nội cell xong( không còn nhận được gói mới từ uav nữa) nó chủ động manifest tới cell tiếp theo. các cell không phải biên thì chỉ chờ mà không chủ động. nếu sau khoảng thời gian đó các cell khác thấy cell biên đáng lẽ phải manifest cho mình thì tự manifest ngược đến nó ( vì đây nằm trong hai trường hợp hoặc là cell biên đã nhận đủ hoặc là cell biên chưa nhận được gói nào nên manifest chưa được trigger) cell nhận được môt manifest ngược sẽ tự hiểu ra tình hình.
> nội dung gói manifest như bạn đề xuất
> trong lúc đang manifest các cell cũng không nằm yên mà tiếp tục tiến hành trao đổi dữ liệu nội cell như đã tóm tắt từ trước để tiết kiệm thời gian, dữ liệu mới đến thì nó cũng được truyền theo đường này đến các node quan trọng
> khi manifest đến nếu cell đó có một trong số các gói được manifest thì nó gửi luôn và cắt bới manifest đồng thời dữ liệu đi qua cell đó mà nó thấy thiếu thì nó cũng tự lưu một bản sao cho bản thân
> về lý thuyết, chỉ các cell ở biên manifest nhưng các cell còn lại đều hưởng lợi
> nếu manifest đến CH mà CH vẫn không thể đáp ứng, nó có thể đoán được hướng đang có và hướng đang thiếu để manifest tiếp (hướng nào không có manifest đến thì coi như là có đủ) nhưng pha manifest cơ sở coi như dừng lại tại đây khi mà manifest tới CH, cluster vấn tiếp tục chạy manifest tiếp nhưng sẽ gọi la bước manifest thứ cấp, chạy song song với nhiệm vụ nhận diện (tạm thơi chưa bàn)
> với khe thời gian, với mỗi cell các cặp gateway có kênh riêng để giao tiếp intercell,
> mảnh nhận lưu luôn tại CL và các node mạnh

**(c) Trả lời các đề xuất**

> trả lời các đề xuất của bạn:
> 1. không cần gửi gói thông báo đủ, nếu cell biên đủ thì cell bên trong cũng có khả năng đã đủ tất nhiên cũng không cần manifest ngược nữa. cho nên cell trong cũng dựa trên trạng thái của bản thân đánh giá tình hình, nếu nó đủ cũng có nghĩa là cell biên ít nhiều cũng có được thông tin, nếu nó thiếu thì mới manifest ngược (cell trong ở đây chỉ các cell cận biên nằm ngay cạch cell biên, không phải cell nào cũng chờ
> 2 đề xuất 2 tôi đồng ý
> 3 đề xuất này tôi sẽ đính chính thêm về thiết kế manifest như sau: các manifest mang thông tin về những cell đi qua có gì ví dụ: có tổng 3 file ABC với các gói lần lượt là 1,2,3,4,5,6,7,8,9 cell biên gửi manifest A4689 tức là nó đang có đủ file A thiếu gói 5 của file B và gói 7 của file C.  cell bên trong nhận được đối chiếu bộ dữ liệu thấy mình có gói 5 thì ngay lập tức gửi cho cell biên và sửa lại nội dung manifest là AB89 cho cell tiếp theo, cell tiếp theo gửi gói 7 trở lại thì nó lưu một bản sao và chuyển tiếp cho cell biên
> tôi đồng ý với đề xuất 4 cần có lập lịch tốt cho gateway
> đề xuất 5 6 7 cũng như ví dụ tôi nêu trên
> trong khi viết đặc tả, lưu lại nguyên văn đoạn mô tả của thôi không chỉnh sửa để làm bản tham chiếu gốc và bắt đầu cài đặt thử

Các đề xuất 1–7 mà (c) trả lời:
1. cell biên đủ thì gửi gói "ĐỦ" thay vì im lặng;
2. lấy thời điểm "UAV đã đi khỏi" theo kế hoạch bay;
3. cell bên trong thiếu thì gửi kèm phần thiếu vào manifest đang đi qua;
4. gateway chỉ có một radio nên cần lịch;
5. cắt manifest nhưng có xác nhận và phát lại;
6. CL báo danh sách thiếu cho các gateway của cell;
7. gộp manifest khi gặp nhau.

**(d) Đính chính sau bản thử đầu**

> 1. manifest mô tả những gì mình có, không phải những gì mình thiếu, những mảnh nó chưa có thì đều là mảnh thiếu
> 2. chỉ những cell biết phía trước mình có một cell biên khác mới chờ, nếu nó cũng vừa là biên nhưng lại vừa là bước tiếp theo của cell biên khác vậy thì nó cũng chờ, chỉ những cell biên không có biên khác của mình sẽ chủ động gửi manifest
> 3. ta sẽ thử bằng thử nghiệm sau
> 4. dữ liệu về CL đi qua các node mạnh thì nó tự lưu lại một bản sao cho mình chứ không chủ động yêu cầu dữ liệu

(d) trả lời bốn phát hiện của bản thử đầu:
1. cell cận biên tự thiếu mà vẫn nghe được manifest của cell biên;
2. 13 cell biên có cell kế tiếp cũng là cell biên;
3. cell biên trắng cạnh cell cận biên đủ;
4. chi phí lưu ở các node quan trọng.

## 1. Thuật ngữ

| | |
|---|---|
| **cell biên** | cell có ít nhất một cạnh lục giác giáp ngoài cụm (seed 1: 40 / 109 cell) |
| **cell kế tiếp** của cell X | cell đầu tiên trên đường chính từ CL của X về CH, đi qua gateway (ROUTING-vi.md) |
| **X chờ b** | X là cell kế tiếp của cell biên b. X có thể là cell biên hay không (d-2) |
| **cell chờ** | cell chờ ít nhất một cell biên. Seed 1: 13 cell biên + 22 cell khác |
| **cell biên chủ động** | cell biên không chờ cell biên nào. Seed 1: 27 cell |
| **trạng thái của cell** | hợp các mảnh mà mọi node trong cell có; CL biết chính xác sau bước tóm tắt (SUMMARY-vi.md) |
| **node mạnh** | node có điểm năng lực > trung bình của cell |

## 2. Gói manifest: những gì cell CÓ

Manifest mô tả **những gì cell có**. Mảnh nào chưa có đều là mảnh thiếu (d-1). Theo ví dụ
(c):
- Có 3 file: A = gói 1–3, B = 4–6, C = 7–9.
- Manifest `A4689` = có đủ A; với B có 4, 6; với C có 8, 9. Vậy thiếu 5 và 7.

```
loại (MANIFEST / MANIFEST NGƯỢC) | cell gốc (q, r) | seq | TTL
cho mỗi file:  fileId | ĐỦ                      -- "A"
                      | đoạn manifest (manifest.h) của các gói có (bộ mã tự chọn: liệt kê có,
                        liệt kê thiếu, hay bitmap, tuỳ cách nào ngắn hơn -- nội dung vẫn là "có")
```

**Sửa manifest ở cell đi qua.** Cell X nhận manifest M:
1. X gửi trả ngay những gì X có mà M thiếu, và coi chúng là đã có: `A4689` → `AB89`
   (X có gói 5).
2. Manifest X chuyển đi tiếp mô tả **X như hiện tại**, theo nguyên tắc (a) "sửa lại
   manifest theo điều kiện cell đó hiện tại": một mảnh là "có" nếu nó có trong M (sau
   bước 1) **và** X cũng có. Mảnh nào X thiếu thì thành mảnh thiếu, kể cả khi cell gốc đã
   có.
3. Cell phía trước gửi trả mảnh đó. X **giữ lại cho mình**, và chỉ chuyển tiếp về phía
   cell gốc nếu cell sau nó cũng thiếu (theo manifest cell đó đã gửi cho X).

Ví dụ: X thiếu gói 8 mà cell gốc có. Manifest X gửi đi là `AB9`. Cell kế tiếp gửi gói 8
về, X giữ, và không chuyển cho cell gốc.

Nhờ cách sửa này, phần thiếu của **mọi cell manifest đi qua tự gộp vào manifest**: "chỉ
các cell ở biên manifest nhưng các cell còn lại đều hưởng lợi" (b).

## 3. Hành vi (pha cơ sở)

1. **Kích hoạt.** Cell biên chủ động gửi manifest (những gì nó có) tới cell kế tiếp khi
   đủ ba điều kiện:
   - đã xong tóm tắt nội cell;
   - UAV đã ra khỏi tầm theo kế hoạch bay (đề xuất 2, (c) đồng ý);
   - cell đó thiếu.

   Cell biên chủ động mà đủ, hoặc chưa nhận được gói nào (không có gì kích hoạt), thì im
   lặng.
2. **Cell chờ** chờ T_chờ rồi xét **trạng thái của chính mình** (c-1):
   - đủ → không làm gì;
   - thiếu → gửi **manifest ngược** (những gì nó có) tới từng cell biên lẽ ra phải gửi cho
     nó mà chưa gửi.
3. **Nhận manifest:** đối chiếu, gửi trả, sửa manifest, chuyển tiếp như mục 2. Manifest
   không còn mảnh thiếu thì dừng.
4. **Dữ liệu đi ngược về:** cell nào dữ liệu tới cũng giữ phần mình thiếu, và chỉ chuyển
   tiếp phần mà cell sau nó thiếu.
5. **Lưu:** mảnh giữ lại được đưa **về CL**. Node mạnh nào nằm trên đường đó tự lưu một bản
   sao, không chủ động xin dữ liệu (d-4).
6. **Nhận manifest ngược, tại cell biên:**
   - gửi trả những gì cell chờ thiếu mà mình có;
   - nếu chính nó cũng thiếu, kể cả chưa nhận được gì ("tự hiểu ra tình hình"), thì từ
     giờ coi như đã được kích hoạt: gửi manifest của mình như bước 1.
7. **Tới CH:** pha cơ sở dừng. Phần còn lại thuộc pha thứ cấp (chưa bàn).
8. **Song song:** trao đổi nội cell vẫn chạy (b). Mỗi cặp gateway có kênh riêng; cần lịch
   cho gateway (đề xuất 4).

## 4. Bản cài thử: phạm vi và giả định

`uav-coop-manifest` là bản thử **mức logic**, chưa có radio. Nó đếm gói và số hop, và mô
phỏng theo sự kiện: dữ liệu chỉ được tính là đã có khi thực sự tới nơi.

| | bản thử |
|---|---|
| trạng thái ban đầu | hợp các mảnh từ các lượt bay thật (bitmap uav-coop-pass, gấp về K mảnh) |
| lúc sẵn sàng | lúc CL của cell xong tóm tắt (summary-cells.csv cùng lượt bay) |
| file | K mảnh chia đều thành F file (mặc định K = 2 000, F = 4) |
| đường đi | đường chính về CH qua gateway, từ routing dựng sẵn |
| chi phí | frame × hop: manifest (tới CL rồi ra gateway), dữ liệu (node giữ mảnh → gateway, gateway → gateway, hoặc qua CL nếu cell giữ lại), lưu (về CL) |
| thời gian | mỗi frame-hop một khe 10 ms, không mất gói, không tranh chấp; dữ liệu đi nối đuôi nhau (mảnh m tới sau mảnh đầu m − 1 khe): **cận dưới lạc quan** |
| chưa có | radio, mất gói, ACK/phát lại (đề xuất 5), lịch gateway (đề xuất 4), trao đổi nội cell song song |

## 5. Kết quả (120 lượt bay, K = 2 000 mảnh chia thành 4 file, T_chờ = 2 s)

| | |
|---|---|
| cell thiếu lúc đầu | 504 lần trên 13 080 lần cell: 414 cell biên chủ động, 85 cell biên chờ, 5 cell khác chờ |
| **sau pha cơ sở** | **0** — mọi cell đủ, kể cả trường hợp bản thử đầu bỏ sót (6.1 cũ) |
| thời gian từ lúc sẵn sàng tới khi đủ | **trung vị 155 ms**, p90 1.0 s, tối đa 2.1 s |
|   cell biên chủ động | trung vị 140 ms, tối đa 1.1 s |
|   cell chờ | trung vị 0.54 s, tối đa 2.1 s (gồm cả T_chờ khi phải gửi manifest ngược) |
| manifest | 415 manifest + 27 manifest ngược; trung bình mỗi manifest đi 1.15 cell; **không manifest nào tới CH** |
| cell đi qua được hưởng lợi | 64 lần, giữ lại 93 mảnh |
| frame × hop mỗi lượt bay (trung vị) | manifest 28, dữ liệu 200, lưu về CL 339 |
| lần nhận trùng | trung vị 0, tối đa 1 lần mỗi lượt bay |

So với bản thử đầu, chi phí lưu giảm từ 805 xuống 339 frame-hop, vì giờ mảnh chỉ đi về CL
và node mạnh tự giữ bản sao dọc đường (d-4).

**Kịch bản kiểm tra `--blank`** (cho một cell coi như không nhận được gói nào; lượt bay 1):

| cell trắng | kết quả |
|---|---|
| (3,−5) biên chủ động + (2,−4) cell chờ nó | (2,−4) chờ 2 s, thiếu, nên gửi manifest ngược → (3,−5) tự hiểu, gửi manifest → (2,−4) giữ bản sao 2 000 mảnh dọc đường. Cả hai đủ lúc **22.3 s** |
| (−5,9) biên chủ động + (−5,8) **biên chờ** | giống trên, đủ lúc **23.3 s**: nhờ (d-2) mà lỗ hổng 6.2 cũ đã được bịt |
| chỉ (−5,9) trắng | (−5,8) thiếu đúng 1 mảnh nên vẫn gửi manifest ngược → (−5,9) được đánh thức, đủ lúc 23.3 s |
| chỉ (3,−5) trắng | (2,−4) đủ nên không làm gì (c-1) → (3,−5) **không được đánh thức** — để thử nghiệm sau (d-3) |

Hai trường hợp 2 000 mảnh mất khoảng 22 s vì cả file phải đi qua một liên kết G2G, mỗi
mảnh một khe 10 ms.

## 6. Còn để ngỏ

1. **Cell biên trắng cạnh một cell chờ đủ** (d-3): để thử nghiệm sau.
2. **Pha thứ cấp:** chưa bàn. Với dữ liệu hiện tại, chưa lần nào manifest tới CH.
3. **Lên mức radio:** kênh G2G, lịch gateway, ACK và phát lại; thử cụm rộng hơn hoặc file
   lớn hơn để manifest phải đi nhiều cell.

## 7. Chạy lại

```bash
M=/home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-manifest-optimized
$M --nodes=deploy-nodes-s35.csv --routes=deploy-routes-s35.csv --bits=bits-r{r}.bin \
   --summary=summary-cells.csv --K=2000 --files=4 --wait=2 --runs=120 --out=manifest
$M ... --runs=1 --blank=3:-5,2:-4 --out=blank    # cell trắng: kiểm tra manifest ngược
```

`docs/data/manifest-cells.csv` có một dòng cho mỗi lượt bay × cell, với các cột:
- vai trò (0 biên chủ động, 1 biên chờ, 2 cell khác chờ, 3 không);
- lúc sẵn sàng; số mảnh thiếu trước và sau; lúc đủ;
- số manifest đã gửi / chuyển tiếp / manifest ngược;
- số mảnh đã gửi đi / giữ bản sao / nhận.

`manifest-missions.csv`: tổng theo lượt bay.

120 lượt bay chạy trong khoảng 20 s, với 5.6 × 10⁸ CHECK, tất cả qua:
- routing dựng lại khớp bản đã lưu;
- mọi manifest được mã hoá rồi giải mã lại khớp;
- dữ liệu chỉ đi từ node thật sự giữ mảnh, chỉ đi qua gateway, và chỉ tới cell cần nó;
- đường về CL đi đúng cây `toCL`;
- số mảnh thiếu chỉ giảm.
