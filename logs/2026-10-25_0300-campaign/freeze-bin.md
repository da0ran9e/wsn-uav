# freeze-bin

- Bắt đầu: 2026-10-25 02:37:02, chạy 1 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
cp -rL /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN2 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN && cd /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN && ls -la && sha256sum deploy-bin pass-bin river-bin && find lib pass-lib -type f | sort | xargs sha256sum | sha256sum && du -sh .
```

**Kết quả**

```text
total 824
drwxr-xr-x  4 root root   4096 Oct 25 02:37 .
drwx------ 46 root root   4096 Oct 25 02:37 ..
-rwxr-xr-x  1 root root 170200 Oct 25 02:37 deploy-bin
drwxr-xr-x  2 root root   4096 Oct 25 02:37 lib
-rwxr-xr-x  1 root root 241728 Oct 25 02:37 pass-bin
drwxr-xr-x  2 root root   4096 Oct 25 02:37 pass-lib
-rwxr-xr-x  1 root root 407064 Oct 25 02:37 river-bin
e38d9e5efe2d696ebf742c97f5962c3a99df4a3c71f8f7c47bad57a3a797faac  deploy-bin
8ca6282c47610521a1928dfad4e0772c9d719c99dd6e957e7ade675c82101d07  pass-bin
ed66896e909daf7d31dc00e68eb739f267dc440e97b4f38da8253dc9473c6f0e  river-bin
d76c29c5068308d100175ef590facc1bad05cef15111d94724fdbbd7885016fe  -
27M	.
```
