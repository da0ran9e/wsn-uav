# extract

- Bắt đầu: 2026-11-12 16:13:52, chạy 6 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 tools/papers/pdf_extract.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/gdrive/pdf/leny2012.pdf leny2012-dtsp /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/papers && python3 tools/papers/pdf_extract.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/gdrive/pdf/1708.06478v1.pdf zeng2018-multicast /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/papers && python3 tools/papers/pdf_extract.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/gdrive/pdf/isaacs2011.pdf isaacs2011-dtspn /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/papers
```

**Kết quả**

```text
leny2012-dtsp: 6 pages, 7022 words, 4 figures, doi 10.1109/tac.2011.2166311
  On the Dubins Traveling Salesman Problem | IEEE Transactions on Automatic Control | 2012
  leny2012-dtsp-fig1.png (tr. 3) Fig. 1. A path between X and Y contained in the shaded region D \ D is called a direct pat
  leny2012-dtsp-fig2.png (tr. 3) Fig. 2. Waypoint conﬁgurations that are hard instances for some proposed or- dering method
  leny2012-dtsp-fig3.png (tr. 5) Fig. 3. Average tour length versus number of points n in a 10  10 square, on a log-log sc
  leny2012-dtsp-fig4.png (tr. 5) Fig. 4. Dubins tours through 50 points randomly distributed in a 10  10 square. The turni
zeng2018-multicast: 13 pages, 11675 words, 8 figures, doi 10.1109/twc.2018.2790401
  Trajectory Design for Completion Time Minimization in UAV-Enabled Multicasting | IEEE Transactions on Wireless Communications | 2018
  zeng2018-multicast-fig1.png (tr. 2) Fig. 1: UAV-enabled information multicasting.
  zeng2018-multicast-fig2.png (tr. 5) Fig. 2: Illustration of the lower bound derivation for Pk,succ.
  zeng2018-multicast-fig3.png (tr. 7) Fig. 3: A toy example for illustrating the inefﬁcacy of directly
  zeng2018-multicast-fig4.png (tr. 9) Fig. 4: Comparison of the UAV trajectories with different waypoint designs. Small circles 
  zeng2018-multicast-fig5.png (tr. 10) Fig. 5: Numerical veriﬁcation of the lower bound for the succuss
  zeng2018-multicast-fig6.png (tr. 10) Fig. 6: Mission completion time versus D.
  zeng2018-multicast-fig7.png (tr. 10) Fig. 7: Average mission completion time versus the number of GTs.
  zeng2018-multicast-fig8.png (tr. 11) Fig. 8: Number of successful GTs versus transmission time for the
isaacs2011-dtspn: 6 pages, 2789 words, 1 figures, doi 10.1109/acc.2011.5991501
  Algorithms for the traveling Salesman Problem with Neighborhoods involving a dubins vehicle | Proceedings of the 2011 American Control Conference | 2011
  isaacs2011-dtspn-fig6.png (tr. 6) Fig. 6. Simulation results for the 100 sample test.
```
