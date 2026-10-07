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

## 1. Thuật ngữ

| | |
|---|---|
| **cell biên** | cell có ít nhất một cạnh lục giác giáp ngoài cụm (seed 1: 40 / 109 cell) |
| **cell kế tiếp** của cell X | cell đầu tiên trên đường chính từ CL của X về CH, đi qua gateway (ROUTING-vi.md) |
| **cell cận biên** | cell không phải biên, và là cell kế tiếp của ít nhất một cell biên |
| **trạng thái của cell** | hợp các mảnh mà mọi node trong cell có; CL biết chính xác sau bước tóm tắt (SUMMARY-vi.md) |
| **node quan trọng** | CL và các node mạnh của cell (điểm năng lực > trung bình của cell) |

## 2. Gói manifest

Một manifest mô tả **trạng thái của cell gốc**: cell đó *có* gì, theo từng file. Theo ví
dụ (c):
- Có 3 file: A = gói 1–3, B = 4–6, C = 7–9.
- Manifest `A4689` = có đủ A; với B có 4, 6 (thiếu 5); với C có 8, 9 (thiếu 7).

```
loại (MANIFEST / MANIFEST NGƯỢC) | cell gốc (q, r) | seq | TTL
cho mỗi file:  fileId | ĐỦ                      -- "A"
                      | đoạn manifest (manifest.h) của các gói CÓ / THIẾU, dạng nào ngắn hơn
```
Mỗi file là một mục riêng. File đã đủ chỉ tốn một cờ, nên manifest của cell gần đủ rất
ngắn.

## 3. Hành vi (pha cơ sở)

1. **Kích hoạt (cell biên).** Cell biên chủ động khi thoả cả hai điều kiện:
   - tóm tắt nội cell đã xong;
   - UAV đã ra khỏi tầm theo kế hoạch bay — đề xuất 2, (c) đồng ý.

   Nếu cell biên thiếu thì gửi manifest tới **cell kế tiếp**. Cell biên đủ thì im lặng.
2. **Cell cận biên** chờ một khoảng T_chờ, rồi xét **trạng thái của chính mình** (c-1):
   - đủ → không làm gì (cell biên "ít nhiều cũng có được thông tin");
   - thiếu, mà một cell biên lẽ ra phải gửi manifest tới mình lại im lặng → gửi
     **manifest ngược** (trạng thái của mình) tới cell biên đó.

   Các cell khác không chờ.
3. **Nhận manifest, tại mỗi cell trên đường đi:**
   - đối chiếu với trạng thái của mình;
   - **gửi ngay** những gói mình có mà cell gốc thiếu, ngược về cell gốc theo đúng đường
     manifest đã đi;
   - **sửa manifest** cho các gói vừa gửi thành "có" (ví dụ `A4689` → `AB89`), rồi
     chuyển cho cell kế tiếp của mình.

   Manifest đã đủ mọi file thì không đi tiếp nữa.
4. **Dữ liệu đi ngược về.** Mỗi cell dữ liệu đi qua, nếu chính nó thiếu gói đó, **lưu một
   bản sao** (b, c-3). Gói nhận được lưu tại **CL và các node mạnh** của cell.
5. **Nhận manifest ngược, tại cell biên.** Cell biên "tự hiểu tình hình":
   - nó gửi cho cell cận biên những gói nó có mà cell kia thiếu;
   - nếu chính nó thiếu (kể cả chưa nhận được gì) thì từ giờ coi như đã được kích hoạt:
     gửi manifest của mình như bước 1.
6. **Tới CH.** Manifest tới CH mà vẫn còn thiếu: CH ghi nhận hướng đang thiếu, **pha cơ sở
   dừng**. Phần còn lại thuộc **pha manifest thứ cấp**, chạy song song với nhiệm vụ nhận
   diện (chưa bàn).
7. **Song song:** trong lúc manifest chạy, các cell vẫn trao đổi dữ liệu nội cell.
8. **Kênh:** mỗi cặp gateway có kênh riêng cho liên lạc giữa hai cell; cần lịch cho
   gateway (đề xuất 4, (c) đồng ý).

## 4. Bản cài thử đầu tiên: phạm vi và giả định

`uav-coop-manifest` là bản thử **mức logic**, chưa có radio. Mục tiêu là kiểm tra luồng
manifest: ai gửi, ai đáp ứng, cắt manifest, lưu bản sao, manifest ngược, dừng ở CH. Bản
này đếm gói và số hop, chưa mô phỏng kênh.

| | bản thử |
|---|---|
| trạng thái ban đầu của mỗi cell | hợp các mảnh từ các lượt bay thật (bitmap của uav-coop-pass, gấp về K mảnh) |
| thời điểm cell biên kích hoạt | lúc CL của nó xong tóm tắt (summary-cells.csv của cùng lượt bay) |
| file | nhiều file: K mảnh chia đều thành F file (mặc định F = 4, K = 2 000) |
| đường đi | đường chính về CH và đúng các gateway, từ routing dựng sẵn |
| chi phí | đếm frame × hop: trong cell (theo bảng routing) và qua gateway |
| thời gian | mỗi frame-hop một khe 10 ms, không mất gói, không tranh chấp: **cận dưới lạc quan** |
| lưu ở CL + node mạnh | tính số hop để phát mảnh tới các node đó (cây đường ngắn nhất trong cell) |
| chưa có | radio, mất gói, ACK/phát lại (đề xuất 5), lịch gateway (đề xuất 4), trao đổi nội cell song song (bước 7) |

**Điểm còn để ngỏ:** cell bên trong (không phải cận biên) tự thiếu thì chờ pha thứ cấp.
Theo dữ liệu 120 lượt bay, chuyện này xảy ra 5 lần, trong đó 3 lần có gói không nằm trong
manifest nào đi qua.

## 5. Kết quả bản thử (120 lượt bay, K = 2 000 mảnh chia thành 4 file)

Bố trí seed 1:
- 109 cell: **40 cell biên**, **22 cell cận biên**, 47 cell còn lại;
- node quan trọng (CL + node mạnh): trung bình 7.6 mỗi cell.

| | |
|---|---|
| cell thiếu lúc đầu | 504 lần trên 13 080 lần cell: **499 cell biên**, 5 cell cận biên |
| sau pha cơ sở | **còn 1 lần** (6 / 10 783 mảnh) — xem 6.1 |
| manifest được gửi | 497 manifest + 6 manifest ngược; trung bình mỗi manifest đi **1.01 cell** |
| manifest tới CH | **0** — pha cơ sở luôn xong trước khi tới CH |
| kích thước manifest | trung vị 169 B cho cả lượt bay (mọi manifest cộng lại); các file đủ chỉ tốn 1 byte |
| thời gian từ lúc cell sẵn sàng tới khi đủ | **trung vị 80 ms**, p90 0.9 s, tối đa 2.05 s (cận dưới lạc quan, mục 4) |
| frame × hop mỗi lượt bay (trung vị) | manifest 28, dữ liệu 199, **lưu tại CL + node mạnh 805** |

- **Lưu bản sao tại CL và node mạnh tốn gấp 4 lần việc chở dữ liệu tới cell.** Một mảnh
  tới gateway rồi còn phải đi tới khoảng 7–8 node trong cell.
- **"Các cell còn lại đều hưởng lợi"** chỉ thấy rõ trong kịch bản thiếu nhiều. Ở dữ liệu
  thật, manifest chỉ đi một cell nên chỉ có 5 lần một cell khác giữ được bản sao.

**Kịch bản kiểm tra `--blank`** (cho một cell coi như không nhận được gói nào):

| | kết quả |
|---|---|
| cell biên (3,−5) **và** cell cận biên (2,−4) cùng trắng | cell cận biên chờ 2 s, thiếu, nên gửi manifest ngược → cell biên "tự hiểu", gửi manifest "cần tất cả" → cell kế tiếp gửi 2 000 mảnh; cell cận biên giữ bản sao trên đường. **Cả hai đủ sau 22.3 s.** |
| chỉ cell biên (3,−5) trắng, cell cận biên đủ | theo (c-1), cell cận biên đủ nên không làm gì → **cell biên trắng không bao giờ được đánh thức** — xem 6.3 |

## 6. Phát hiện cần quyết định

1. **Cell cận biên tự thiếu nhưng vẫn nghe được manifest của cell biên.** Nó không gửi
   manifest ngược, vì cell biên không im lặng. Nhưng manifest đi qua không chứa mảnh nó
   cần, nên mảnh đó không bao giờ được đáp ứng. Xảy ra 1 / 13 080 lần.

   Cách sửa đơn giản: khi manifest đi qua, cell cận biên thêm phần mình thiếu vào (đề xuất
   3 cũ). Hoặc để mảnh đó cho pha thứ cấp.
2. **13 / 40 cell biên có cell kế tiếp cũng là cell biên.** Theo (c-1), chỉ cell cận biên
   (không phải biên) mới chờ. Vậy không ai chờ manifest của 13 cell biên này. Nếu một
   trong số chúng không nhận được gói nào, nó không bao giờ được đánh thức (thử với
   (−5, 9) → (−5, 8)).

   Cách sửa: vai trò "chờ và gửi manifest ngược" thuộc về **cell kế tiếp của mỗi cell biên,
   bất kể nó là gì**.
3. **Cell biên trắng cạnh một cell cận biên đủ.** Quy tắc (c-1) giả định rằng nếu cell cận
   biên đủ thì cell biên "ít nhiều cũng có được thông tin". Trong 120 lượt bay thật giả
   định này luôn đúng: mọi node nhận được ít nhất 350 gói. Nhưng nếu UAV bay lệch hẳn
   khỏi một mép cụm, cell biên ở đó sẽ bị bỏ sót tới pha thứ cấp.
4. **Chi phí lưu ở node quan trọng.** Có thể chỉ lưu ở CL ngay, còn việc chép sang node
   mạnh làm sau trong trao đổi nội cell, cho nhanh và nhẹ hơn.

## 7. Chạy lại

```bash
M=/home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-manifest-optimized
$M --nodes=deploy-nodes-s35.csv --routes=deploy-routes-s35.csv --bits=bits-r{r}.bin \
   --summary=summary-cells.csv --K=2000 --files=4 --wait=2 --runs=120 --out=manifest
$M ... --runs=1 --blank=3:-5,2:-4 --out=blank    # cell trắng: kiểm tra manifest ngược
```

`docs/data/manifest-cells.csv` có một dòng cho mỗi lượt bay × cell, với các cột:
- vai trò (0 biên, 1 cận biên, 2 khác);
- lúc sẵn sàng; số mảnh thiếu trước và sau; lúc đủ;
- số manifest đã gửi / chuyển tiếp / manifest ngược;
- số mảnh đã gửi đi / giữ bản sao / nhận.

`manifest-missions.csv`: tổng theo lượt bay.

Bản thử chạy rất nhanh (120 lượt bay trong khoảng 18 s) và có khoảng 5.6 × 10⁸ CHECK, tất
cả qua:
- routing dựng lại khớp `deploy-routes-s35.csv`;
- mọi manifest được mã hoá rồi giải mã lại khớp;
- dữ liệu chỉ đi từ node thật sự giữ mảnh, và chỉ đi qua gateway;
- số mảnh thiếu chỉ giảm, không bao giờ tăng.
