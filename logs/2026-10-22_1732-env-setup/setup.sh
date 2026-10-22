#!/bin/bash
# Rebuild the ns-3.46 tree the project expects at /home/user/ns3-dev (container was fresh).
set -e
cd /home/user
curl -sSL https://gitlab.com/nsnam/ns-3-dev/-/archive/ns-3.46/ns-3-dev-ns-3.46.tar.gz -o ns3.tgz
tar xzf ns3.tgz && mv ns-3-dev-ns-3.46 ns3-dev && rm ns3.tgz
for m in uav-sar uav-coop uav-coop2; do ln -s /home/user/wsn-uav/$m /home/user/ns3-dev/src/$m; done
cd ns3-dev
python3 ./ns3 configure -d optimized --enable-examples --disable-tests --enable-modules="uav-sar;uav-coop;uav-coop2"
cmake --build cmake-cache -j 4
ls -la build/src/uav-coop/examples/ build/src/uav-coop2/examples/
