# 01-cluster-sizes

- Bắt đầu: 2026-11-27 05:38:25, chạy 2 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2/tools`

**Lệnh**

```bash
python3 -c "
from restructure import domain
from partition import partition
import random, collections, math
for K in (8,12,16):
    g=domain(K,1,'')
    land=set(g['domain'])
    owner, med, it, over = partition(land, 80, random.Random(1))
    s=sorted(collections.Counter(owner.values()).values())
    print('K=%d cells=80K=%d land=%d lake=%d ceil(land/80)=%d clusters=%d sizes=%s' % (K, 80*K, len(land), len(g['lake_set']), math.ceil(len(land)/80), len(s), s))
"
```

**Kết quả**

```text
K=8 cells=80K=640 land=617 lake=80 ceil(land/80)=8 clusters=8 sizes=[70, 72, 78, 78, 79, 80, 80, 80]
K=12 cells=80K=960 land=899 lake=119 ceil(land/80)=12 clusters=12 sizes=[53, 65, 70, 73, 78, 80, 80, 80, 80, 80, 80, 80]
K=16 cells=80K=1280 land=1126 lake=160 ceil(land/80)=15 clusters=15 sizes=[57, 63, 68, 70, 73, 75, 80, 80, 80, 80, 80, 80, 80, 80, 80]
```
