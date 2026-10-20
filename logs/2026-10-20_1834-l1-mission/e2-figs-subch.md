# e2-figs-subch

- Bắt đầu: 2026-10-20 22:15:59, chạy 4 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
bash ../logs/2026-10-20_1834-l1-mission/e2-figs.sh
```

**Kết quả**

```text
/home/user/wsn-uav/uav-l2/tools/l1_compare.py:79: RuntimeWarning: Mean of empty slice
  Tall=round(float(np.nanmean([float(r["Tall"]) for r in Y])), 1),
row                                                    k2                      k4                      k6                      k8
kmedoids P*                           408± 14    +0  0/10     566± 24    +0  0/10     675± 28    +0  0/10     769± 43    +0  0/10
kmedoids leave at first report        482± 15   +74  0/10     624± 27   +58  0/10     716± 28   +41  0/10     796± 49   +27  0/10
kmedoids River report only            416± 17    +8  3/10     576± 26   +10  1/10     681± 30    +6  1/10     776± 45    +6  1/10
kmedoids B4                           434± 18   +26  0/10     622± 42   +56  0/10     734± 42   +59  0/10     838± 58   +68  1/10
kmedoids beta 0                       420± 14   +12  2/10     600± 21   +34  0/10     708± 30   +33  1/10     813± 48   +43  1/10
kmedoids beta 1                       416± 16    +8  3/10     591± 30   +26  0/10     731± 33   +56  0/10     839± 45   +70  0/10
kmedoids P* redirect                  403± 14    -5  7/10     554± 26   -11  9/10     662± 31   -13 10/10     754± 45   -15 10/10
kmedoids P old                        513± 25  +105  0/10     678± 29  +112  0/10     783± 26  +108  0/10     867± 45   +98  0/10
kmedoids B1                           897± 90  +489  0/10    1699±120 +1133  0/10    2498±144 +1823  0/10    3083±160 +2314  0/10
kmedoids B7                           245± 10  -163 10/10     287±  9  -279 10/10     314± 12  -361 10/10     347± 10  -423 10/10
subch P*                              423± 13   +15  2/10     617± 43   +52  1/10     717± 44   +42  4/10     830± 40   +61  1/10
subch leave at first report           490± 21   +81  0/10     659± 43   +93  0/10     747± 43   +72  1/10     858± 40   +89  0/10
subch River report only               428± 16   +20  2/10     624± 41   +58  0/10     720± 40   +45  4/10     834± 42   +65  1/10
subch B4                              447± 17   +39  0/10     659± 50   +94  0/10     783± 38  +108  0/10     875± 31  +106  0/10
subch beta 0                          434± 18   +26  3/10     637± 34   +72  0/10     735± 35   +60  2/10     867± 55   +98  0/10
subch beta 1                          430± 17   +22  2/10     651± 52   +86  0/10     779± 43  +104  0/10     914± 41  +144  0/10
subch P* redirect                     411± 17    +3  4/10     599± 45   +34  3/10     704± 44   +29  4/10     813± 40   +44  2/10
subch P old                           517± 31  +109  0/10     698± 50  +132  0/10     776± 41  +101  0/10     913± 54  +144  0/10
subch B1                              838± 74  +430  0/10    1641±111 +1075  0/10    2342±169 +1667  0/10    2866±177 +2097  0/10
subch B7                              243±  9  -165 10/10     289±  9  -277 10/10     312± 12  -363 10/10     346± 11  -423 10/10
meander P*                                                                                                                       
meander leave at first report                                                                                                    
meander River report only                                                                                                        
meander B4                                                                                                                       
meander beta 0                                                                                                                   
meander beta 1                                                                                                                   
meander P* redirect                                                                                                              
meander P old                                                                                                                    
meander B1                                                                                                                       
meander B7                                                                                                                       
/home/user/wsn-uav/uav-l2/tools/l1_compare.py:79: RuntimeWarning: Mean of empty slice
  Tall=round(float(np.nanmean([float(r["Tall"]) for r in Y])), 1),
row                                                    k2                      k4                      k6                      k8
kmedoids P*                           408± 14    +0  0/10     566± 24    +0  0/10     675± 28    +0  0/10     769± 43    +0  0/10
subch P*                              423± 13   +15  2/10     617± 43   +52  1/10     717± 44   +42  4/10     830± 40   +61  1/10
meander P*                                                                                                                       
kmedoids B4                           434± 18   +26  0/10     622± 42   +56  0/10     734± 42   +59  0/10     838± 58   +68  1/10
subch B4                              447± 17   +39  0/10     659± 50   +94  0/10     783± 38  +108  0/10     875± 31  +106  0/10
meander B4                                                                                                                       
kmedoids B7                           245± 10  -163 10/10     287±  9  -279 10/10     314± 12  -361 10/10     347± 10  -423 10/10
subch B7                              243±  9  -165 10/10     289±  9  -277 10/10     312± 12  -363 10/10     346± 11  -423 10/10
meander B7
```
