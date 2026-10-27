# Dựng lại deploy, pass, river từ mã hiện tại

- Bắt đầu: 2026-10-27 17:14:44, chạy 33 s, mã thoát 0
- Thư mục: `/home/user/ns3-dev`

**Lệnh**

```bash
cmake --build cmake-cache -j 4 --target uav-coop-deploy uav-coop-pass uav-coop2-river 2>&1 | tail -15
```

**Kết quả**

```text
[0/2] Re-checking globbed directories...
[1/6] Building CXX object src/uav-coop/examples/CMakeFiles/uav-coop-deploy.dir/coop-deploy.cc.o
[2/6] Building CXX object src/uav-coop/examples/CMakeFiles/uav-coop-pass.dir/coop-pass.cc.o
[3/6] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-deploy-optimized
[4/6] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-pass-optimized
[5/6] Building CXX object src/uav-coop2/examples/CMakeFiles/uav-coop2-river.dir/coop2-river.cc.o
[6/6] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop2/examples/ns3.46-uav-coop2-river-optimized
```
