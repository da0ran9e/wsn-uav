# compare

**Lệnh**

```bash
python3 tools/meander_compare.py --set kmedoids "/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/W/k[468]" --set lane "/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/ML/k*" --set meander "/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MM/k*" --draws 100 --out docs/data/meander/ns3 --figs docs/figures
```

**Kết quả**

```text
k4 kmedoids  clusters 4 crits 27 pathKm 11.15 team1 326.6 Dmean 4191.0 DkBmean 414.9 doneMean 24.45 doneP90 46.31 doneMax 59.99 L3mean 44.33 missing 0 ready 313.8 endMean 734.0 endCI 32.4 endP90 914.9 foundMean 523.4 visits 2.17
k4 lane      clusters 7 crits 34 pathKm 17.62 team1 564.4 Dmean 3154.7 DkBmean 312.3 doneMean 21.86 doneP90 61.7 doneMax 104.78 L3mean 26.77 missing 0 ready 489.3 endMean 764.4 endCI 34.5 endP90 996.3 foundMean 553.9 visits 2.03
k4 meander   clusters 6 crits 26 pathKm 17.04 team1 482.7 Dmean 4599.7 DkBmean 455.4 doneMean 41.37 doneP90 74.8 doneMax 114.97 L3mean 51.39 missing 0 ready 454.5 endMean 867.1 endCI 41.1 endP90 1118.2 foundMean 667.8 visits 2.35
k6 kmedoids  clusters 6 crits 45 pathKm 16.22 team1 559.9 Dmean 4211.2 DkBmean 416.9 doneMean 17.92 doneP90 31.9 doneMax 71.28 L3mean 32.66 missing 0 ready 482.0 endMean 865.8 endCI 47.5 endP90 1166.3 foundMean 606.0 visits 1.79
k6 lane      clusters 9 crits 47 pathKm 25.58 team1 785.7 Dmean 3920.0 DkBmean 388.1 doneMean 27.59 doneP90 64.38 doneMax 112.72 L3mean 42.23 missing 0 ready 684.0 endMean 1077.8 endCI 47.3 endP90 1379.3 foundMean 799.1 visits 2.08
k6 meander   clusters 11 crits 51 pathKm 25.38 team1 769.7 Dmean 3659.5 DkBmean 362.3 doneMean 17.88 doneP90 46.56 doneMax 67.4 L3mean 30.6 missing 0 ready 690.0 endMean 999.1 endCI 50.5 endP90 1329.7 foundMean 724.0 visits 2.35
k8 kmedoids  clusters 8 crits 52 pathKm 20.85 team1 679.7 Dmean 4159.2 DkBmean 411.8 doneMean 15.82 doneP90 35.85 doneMax 46.13 L3mean 29.37 missing 0 ready 567.0 endMean 906.0 endCI 53.0 endP90 1256.0 foundMean 622.1 visits 1.94
k8 lane      clusters 11 crits 63 pathKm 31.72 team1 933.8 Dmean 4095.3 DkBmean 405.4 doneMean 33.9 doneP90 86.0 doneMax 138.8 L3mean 47.8 missing 0 ready 884.0 endMean 1044.0 endCI 68.1 endP90 1488.9 foundMean 766.6 visits 2.16
k8 meander   clusters 11 crits 60 pathKm 32.24 team1 929.1 Dmean 4861.7 DkBmean 481.3 doneMean 65.91 doneP90 163.67 doneMax 191.78 L3mean 80.07 missing 0 ready 823.3 endMean 1105.7 endCI 72.1 endP90 1577.4 foundMean 822.0 visits 2.07
```
