# extract

- Bắt đầu: 2026-11-12 17:17:57, chạy 94 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
i=0; while read f; do i=$((i+1)); k=$(printf p%02d $i); python3 -I tools/papers/pdf_extract.py "/tmp/claude-0/-home-user-wsn-uav/f17c66bf-3568-51e2-9dc3-d9bb032c7154/scratchpad/pdf/$f" $k /tmp/claude-0/-home-user-wsn-uav/f17c66bf-3568-51e2-9dc3-d9bb032c7154/scratchpad/papers >/dev/null 2>&1 || echo FAIL $k $f; n=$(grep -c '=== tr' /tmp/claude-0/-home-user-wsn-uav/f17c66bf-3568-51e2-9dc3-d9bb032c7154/scratchpad/papers/$k/pages.txt); c=$(wc -c < /tmp/claude-0/-home-user-wsn-uav/f17c66bf-3568-51e2-9dc3-d9bb032c7154/scratchpad/papers/$k/pages.txt); fg=$(ls /tmp/claude-0/-home-user-wsn-uav/f17c66bf-3568-51e2-9dc3-d9bb032c7154/scratchpad/papers/$k/fig/*.png 2>/dev/null | wc -l); echo "$k $f pages=$n chars=$c figs=$fg"; done < /tmp/claude-0/-home-user-wsn-uav/f17c66bf-3568-51e2-9dc3-d9bb032c7154/scratchpad/files.txt
```

**Kết quả**

```text
p01 hui2004.pdf pages=14 chars=77728 figs=12
p02 gallager1976.pdf pages=14 chars=74865 figs=7
p03 minsky2003.pdf pages=6 chars=39156 figs=0
p04 du2017.pdf pages=14 chars=87558 figs=14
p05 IEEE_WTran08_Stojanovic_Wu_Sharif_Starobinski_rev4.pdf pages=7 chars=33967 figs=4
p06 savla2008.pdf pages=14 chars=62590 figs=6
p07 babel2017.pdf pages=12 chars=58398 figs=18
p08 al-hourani2014.pdf pages=4 chars=18802 figs=6
p09 matolak2017.pdf pages=13 chars=61125 figs=1
p10 nekrasov2019.pdf pages=17 chars=54127 figs=10
p11 techy2009.pdf pages=11 chars=46248 figs=11
p12 02_kulkarnis_mnp.pdf pages=10 chars=57900 figs=6
p13 FZMT2012.pdf pages=14 chars=88883 figs=8
p14 infocom-reliability.pdf pages=5 chars=24638 figs=2
p15 nsdi13-final22.pdf pages=14 chars=71714 figs=8
p16 main.pdf pages=9 chars=38851 figs=12
p17 gudmundson1991.pdf pages=2 chars=12764 figs=0
p18 nelson2007.pdf pages=11 chars=36459 figs=16
p19 park2007.pdf pages=11 chars=50408 figs=17
p20 dubins1957.pdf pages=21 chars=47273 figs=0
p21 leny2007.pdf pages=6 chars=33948 figs=2
p22 rathinam2007.pdf pages=7 chars=35806 figs=13
p23 s10732-020-09440-2.pdf pages=28 chars=57073 figs=17
p24 noon1993.pdf pages=7 chars=20936 figs=0
p25 helsgaun2000.pdf pages=25 chars=90171 figs=9
p26 obermeyer2009.pdf pages=11 chars=31926 figs=5
p27 penicka2017.pdf pages=8 chars=41785 figs=6
p28 10.1007@s10514-019-09844-5.pdf pages=20 chars=93575 figs=11
p29 Joint_Rate_and_Coverage_Design_for_UAV-Enabled_Wireless_Networks_with_Underlaid_D2D_Communications.pdf pages=5 chars=19876 figs=6
p30 Fixed-Wing-UAV-Coverage-Path-Planning-Based-on-Turning-Span-Selection.pdf pages=15 chars=70136 figs=21
p31 978-3-540-77690-1_17.pdf pages=2 chars=5993 figs=0
p32 shkel2001.pdf pages=24 chars=66477 figs=12
p33 ma2006.pdf pages=6 chars=31672 figs=7
p34 faigl2017.pdf pages=7 chars=41486 figs=4
p35 vana2017.pdf pages=6 chars=34244 figs=6
p36 sensors-23-06432.pdf pages=28 chars=91566 figs=9
p37 sensors-23-02560-v2.pdf pages=18 chars=53238 figs=19
p38 1-s2.0-S2214914725000170-main.pdf pages=19 chars=81554 figs=16
p39 Deep_Reinforcement_Learning_for_AoI_Minimization_in_UAV-Aided_Data_Collection_for_WSN_and_IoT_Applications_A_Survey.pdf pages=41 chars=179432 figs=20
p40 An_Optimized_LTE-Based_Technique_for_Drone_Base_Station_Dynamic_3D_Placement_and_Resource_Allocation_in_Delay-Sensitive_M2M_Networks.pdf pages=12 chars=70076 figs=8
p41 Coverage_Maximization_for_Heterogeneous_Aerial_Networks.pdf pages=5 chars=26894 figs=5
p42 Coverage_Optimization_for_Reliable_UAV-Assisted_5G_6G_Communication_Systems.pdf pages=10 chars=55713 figs=9
p43 Energy_and_Service-Priority_aware_Trajectory_Design_for_UAV-BSs_using_Double_Q-Learning.pdf pages=4 chars=20953 figs=4
p44 Multi-UAV_Assisted_Network_Coverage_Optimization_for_Rescue_Operations_using_Reinforcement_Learning.pdf pages=6 chars=29611 figs=5
p45 UAV-Assisted_Cellular_Communication_Joint_Trajectory_and_Coverage_Optimization.pdf pages=6 chars=28720 figs=7
p46 tan2003.pdf pages=6 chars=32596 figs=6
```
