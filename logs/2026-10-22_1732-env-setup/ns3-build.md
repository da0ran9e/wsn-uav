# Dựng lại cây ns-3.46 tại /home/user/ns3-dev

- Bắt đầu: 2026-10-22 17:32:54, chạy 193 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
bash logs/2026-10-22_1732-env-setup/setup.sh
```

**Kết quả**

```text
Warn about uninitialized values.
-- The CXX compiler identification is GNU 13.3.0
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Using default output directory /home/user/ns3-dev/build
-- Performing Test GCC_WORKING_PEDANTIC_SEMICOLON
-- Performing Test GCC_WORKING_PEDANTIC_SEMICOLON - Success
-- [33mProceeding without cmake-format[0m
-- Performing Test STACKTRACE_LIBRARY_ENABLED
-- Performing Test STACKTRACE_LIBRARY_ENABLED - Success
-- Performing Test STACKTRACE_LIBRARY_IS_LINKED
-- Performing Test STACKTRACE_LIBRARY_IS_LINKED - Success
-- Found Git: /usr/bin/git (found version "2.43.0") 
-- Found Python3: /usr/bin/python3 (found version "3.13.16") found components: Interpreter 
-- [33mPython: development libraries were not found[0m
-- [33mBoost was not found[0m
-- [33mdocs: doxygen documentation not enabled due to missing dependencies: doxygen dot dia[0m
-- Failed to locate sphinx-build executable (missing: SPHINX_EXECUTABLE) 
-- [33mdocs: sphinx documentation not enabled due to missing dependencies: Sphinx epstopdf pdflatex latexmk dvipng dia[0m
-- Performing Test HAVE_UINT128_T
-- Performing Test HAVE_UINT128_T - Failed
-- Performing Test HAVE___UINT128_T
-- Performing Test HAVE___UINT128_T - Success
-- Looking for C++ include sys/types.h
-- Looking for C++ include sys/types.h - found
-- Looking for C++ include sys/stat.h
-- Looking for C++ include sys/stat.h - found
-- Looking for C++ include dirent.h
-- Looking for C++ include dirent.h - found
-- Looking for C++ include signal.h
-- Looking for C++ include signal.h - found
-- Looking for C++ include netpacket/packet.h
-- Looking for C++ include netpacket/packet.h - found
-- Looking for getenv
-- Looking for getenv - found
-- Processing src/uav-coop
-- Processing src/uav-coop2
-- Processing src/uav-sar
-- Processing src/core
-- Looking for include files boost/units/quantity.hpp, boost/units/systems/si.hpp
-- Looking for include files boost/units/quantity.hpp, boost/units/systems/si.hpp - not found
-- Boost Units are an optional feature of length.cc.  Ubuntu ships it within the libboost-dev package.  You may need to clean up the CMake cache after installing it to pass this check.
-- Performing Test COMPILER_HAS_HIDDEN_VISIBILITY
-- Performing Test COMPILER_HAS_HIDDEN_VISIBILITY - Success
-- Performing Test COMPILER_HAS_HIDDEN_INLINE_VISIBILITY
-- Performing Test COMPILER_HAS_HIDDEN_INLINE_VISIBILITY - Success
-- Performing Test COMPILER_HAS_DEPRECATED_ATTR
-- Performing Test COMPILER_HAS_DEPRECATED_ATTR - Success
-- Processing src/network
-- Processing src/stats
-- Processing src/mobility
-- Processing src/antenna
-- Performing Test HAVE_STD_BESSEL_FUNC
-- Performing Test HAVE_STD_BESSEL_FUNC - Success
-- Standard library Bessel function has been found
-- Processing src/spectrum
-- Processing src/propagation
-- Processing src/buildings
-- Processing src/lr-wpan
-- Processing src/energy
-- ---- Summary of ns-3 settings:
Build profile                 : optimized
Build directory               : /home/user/ns3-dev/build
Build with runtime asserts    : OFF (not requested)
Build with runtime logging    : OFF (not requested)
Build version embedding       : OFF (not requested)
BRITE Integration             : [31mOFF (missing dependency)[0m
DES Metrics event collection  : OFF (not requested)
DPDK NetDevice                : OFF (not requested)
Emulation FdNetDevice         : [31mOFF (missing dependency)[0m
Examples                      : [32mON[0m
File descriptor NetDevice     : [31mOFF (missing dependency)[0m
GNU Scientific Library (GSL)  : [31mOFF (GSL was not found)[0m
GtkConfigStore                : [31mOFF (Harfbuzz is required by GTK3 and was not found)[0m
LibXml2 support               : [31mOFF (LibXML2 was not found)[0m
MPI Support                   : OFF (not requested)
ns-3 Click Integration        : [31mOFF (missing dependency)[0m
ns-3 OpenFlow Integration     : [31mOFF (missing dependency)[0m
Netmap emulation FdNetDevice  : [31mOFF (missing dependency)[0m
PyViz visualizer              : [31mOFF (Python Bindings are disabled)[0m
Python Bindings               : OFF (not requested)
SQLite support                : [32mON[0m
Eigen3 support                : [31mOFF (Eigen was not found)[0m
Tap Bridge                    : [32mON[0m
Tap FdNetDevice               : [31mOFF (missing dependency)[0m
Tests                         : OFF (not requested)


Modules configured to be built:
antenna                   buildings                 core                      
energy                    lr-wpan                   mobility                  
network                   propagation               spectrum                  
stats                     uav-coop                  uav-coop2                 
uav-sar                   


-- Configuring done (5.9s)
-- Generating done (0.1s)
-- Build files have been written to: /home/user/ns3-dev/cmake-cache
Finished executing the following commands:
mkdir cmake-cache
/usr/bin/cmake -S /home/user/ns3-dev -B /home/user/ns3-dev/cmake-cache -DCMAKE_BUILD_TYPE=release -DNS3_ASSERT=OFF -DNS3_LOG=OFF -DNS3_WARNINGS_AS_ERRORS=OFF -DNS3_NATIVE_OPTIMIZATIONS=ON -DNS3_EXAMPLES=ON -DNS3_TESTS=OFF -DNS3_ENABLED_MODULES=uav-sar;uav-coop;uav-coop2 -G Ninja --warn-uninitialized
[0/2] Re-checking globbed directories...
[1/509] Building CXX object src/uav-coop/CMakeFiles/uav-coop.dir/models/common/hex-grid.cc.o
[2/509] Building CXX object src/uav-coop/CMakeFiles/uav-coop.dir/models/common/dubins.cc.o
[3/509] Building CXX object src/uav-coop/CMakeFiles/uav-coop.dir/models/common/deploy.cc.o
[4/509] Building CXX object src/uav-coop/CMakeFiles/uav-coop.dir/models/common/path.cc.o
[5/509] Building CXX object src/uav-coop/CMakeFiles/uav-coop.dir/models/common/manifest.cc.o
[6/509] Building CXX object src/uav-coop/CMakeFiles/uav-coop.dir/models/common/region.cc.o
[7/509] Building CXX object src/uav-coop/CMakeFiles/uav-coop.dir/models/common/routing.cc.o
[8/509] Building CXX object src/uav-coop/examples/CMakeFiles/uav-coop-deploy.dir/coop-deploy.cc.o
[9/509] Building CXX object src/uav-coop2/CMakeFiles/uav-coop2.dir/models/river-plan.cc.o
[10/509] Building CXX object src/uav-coop/examples/CMakeFiles/uav-coop-pass.dir/coop-pass.cc.o
[11/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/sar-info.cc.o
[12/509] Building CXX object src/uav-coop/examples/CMakeFiles/uav-coop-summary.dir/coop-summary.cc.o
[13/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/cell-grid.cc.o
[14/509] Building CXX object src/uav-coop/examples/CMakeFiles/uav-coop-manifest.dir/coop-manifest.cc.o
[15/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/node-capability.cc.o
[16/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/p1/p1-params.cc.o
[17/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/p1/p1-sensing.cc.o
[18/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/lane-plan.cc.o
[19/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/p1/p1-field.cc.o
[20/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/p1/p1-dubins.cc.o
[21/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/p1/p1-demand.cc.o
[22/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/p1/p1-cells.cc.o
[23/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/p1/p1-partition.cc.o
[24/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/inter-cell-routing.cc.o
[25/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/network/air-ground-loss.cc.o
[26/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/network/pair-shadowing-loss.cc.o
[27/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/network/forest-a2g-loss.cc.o
[28/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/target-profile.cc.o
[29/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/clue-field.cc.o
[30/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/network/sar-network.cc.o
[31/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/network/phy-stats.cc.o
[32/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/common/sar-metrics.cc.o
/home/user/ns3-dev/src/uav-sar/models/common/sar-metrics.cc: In member function ‘void ns3::uavsar::SarMetrics::Finalize(const std::string&)’:
/home/user/ns3-dev/src/uav-sar/models/common/sar-metrics.cc:172:54: warning: converting from ‘void (ns3::uavsar::SarMetrics::*)(const std::string&)’ {aka ‘void (ns3::uavsar::SarMetrics::*)(const std::__cxx11::basic_string<char>&)’} to ‘const void*’ [-Wpedantic]
  172 |             if (dladdr(reinterpret_cast<const void*>(&SarMetrics::Finalize), &info) && info.dli_fname &&
      |                                                      ^~~~~~~~~~~~~~~~~~~~~
[33/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/application/flight-controller.cc.o
[34/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/application/region-coordinator.cc.o
[35/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/application/sar-fast-uav-app.cc.o
[36/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/application/sar-ground-app.cc.o
[37/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/application/sar-bs-app.cc.o
[38/509] Building CXX object src/uav-coop2/examples/CMakeFiles/uav-coop2-river.dir/coop2-river.cc.o
[39/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/models/application/sar-data-uav-app.cc.o
[40/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-substrate-test.dir/substrate-test.cc.o
[41/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-hello.dir/uav-sar-hello.cc.o
[42/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-signal-test.dir/signal-test.cc.o
[43/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-channel-test.dir/channel-test.cc.o
[44/509] Building CXX object src/uav-sar/CMakeFiles/uav-sar.dir/helper/sar-config.cc.o
[45/509] Building CXX object src/uav-sar/examples/CMakeFiles/scenario-sar.dir/scenario-sar.cc.o
[46/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-p1-test.dir/p1-test.cc.o
[47/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-phy-error-test.dir/phy-error-test.cc.o
[48/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-p1-plan-dump.dir/p1-plan-dump.cc.o
[49/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-p1-scaling-test.dir/p1-scaling-test.cc.o
[50/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-p1-antenna-test.dir/p1-antenna-test.cc.o
[51/509] Building CXX object src/core/CMakeFiles/core.dir/model/int64x64-128.cc.o
[52/509] Building CXX object src/core/CMakeFiles/core.dir/model/unix-fd-reader.cc.o
[53/509] Building CXX object src/core/CMakeFiles/core.dir/model/example-as-test.cc.o
[54/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-a2g-run-test.dir/a2g-run-test.cc.o
[55/509] Building CXX object src/core/CMakeFiles/core.dir/helper/csv-reader.cc.o
[56/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-g2g-chain-test.dir/g2g-chain-test.cc.o
[57/509] Building CXX object src/uav-sar/examples/CMakeFiles/uav-sar-a2g-sweep-test.dir/a2g-sweep-test.cc.o
[58/509] Building CXX object src/core/CMakeFiles/core.dir/helper/random-variable-stream-helper.cc.o
[59/509] Building CXX object src/core/CMakeFiles/core.dir/helper/event-garbage-collector.cc.o
[60/509] Building CXX object src/core/CMakeFiles/core.dir/model/event-id.cc.o
[61/509] Building CXX object src/core/CMakeFiles/core.dir/model/scheduler.cc.o
[62/509] Building CXX object src/core/CMakeFiles/core.dir/model/list-scheduler.cc.o
[63/509] Building CXX object src/core/CMakeFiles/core.dir/model/map-scheduler.cc.o
[64/509] Building CXX object src/core/CMakeFiles/core.dir/model/time.cc.o
[65/509] Building CXX object src/core/CMakeFiles/core.dir/model/heap-scheduler.cc.o
[66/509] Building CXX object src/core/CMakeFiles/core.dir/model/event-impl.cc.o
[67/509] Building CXX object src/core/CMakeFiles/core.dir/model/priority-queue-scheduler.cc.o
[68/509] Building CXX object src/core/CMakeFiles/core.dir/model/calendar-scheduler.cc.o
[69/509] Building CXX object src/core/CMakeFiles/core.dir/model/simulator-impl.cc.o
[70/509] Building CXX object src/core/CMakeFiles/core.dir/model/simulator.cc.o
[71/509] Building CXX object src/core/CMakeFiles/core.dir/model/timer.cc.o
[72/509] Building CXX object src/core/CMakeFiles/core.dir/model/default-simulator-impl.cc.o
[73/509] Building CXX object src/core/CMakeFiles/core.dir/model/watchdog.cc.o
[74/509] Building CXX object src/core/CMakeFiles/core.dir/model/breakpoint.cc.o
[75/509] Building CXX object src/core/CMakeFiles/core.dir/model/synchronizer.cc.o
[76/509] Building CXX object src/core/CMakeFiles/core.dir/model/environment-variable.cc.o
[77/509] Building CXX object src/core/CMakeFiles/core.dir/model/attribute-construction-list.cc.o
[78/509] Building CXX object src/core/CMakeFiles/core.dir/model/log.cc.o
[79/509] Building CXX object src/core/CMakeFiles/core.dir/model/object.cc.o
[80/509] Building CXX object src/core/CMakeFiles/core.dir/model/object-base.cc.o
[81/509] Building CXX object src/core/CMakeFiles/core.dir/model/type-id.cc.o
[82/509] Building CXX object src/core/CMakeFiles/core.dir/model/rng-seed-manager.cc.o
[83/509] Building CXX object src/core/CMakeFiles/core.dir/model/rng-stream.cc.o
[84/509] Building CXX object src/core/CMakeFiles/core.dir/model/test.cc.o
[85/509] Building CXX object src/core/CMakeFiles/core.dir/model/attribute.cc.o
[86/509] Building CXX object src/core/CMakeFiles/core.dir/model/boolean.cc.o
[87/509] Building CXX object src/core/CMakeFiles/core.dir/model/integer.cc.o
[88/509] Building CXX object src/core/CMakeFiles/core.dir/model/random-variable-stream.cc.o
[89/509] Building CXX object src/core/CMakeFiles/core.dir/model/uinteger.cc.o
[90/509] Building CXX object src/core/CMakeFiles/core.dir/model/double.cc.o
[91/509] Building CXX object src/core/CMakeFiles/core.dir/model/int64x64.cc.o
[92/509] Building CXX object src/core/CMakeFiles/core.dir/model/string.cc.o
[93/509] Building CXX object src/core/CMakeFiles/core.dir/model/command-line.cc.o
[94/509] Building CXX object src/core/CMakeFiles/core.dir/model/pointer.cc.o
[95/509] Building CXX object src/core/CMakeFiles/core.dir/model/trace-source-accessor.cc.o
[96/509] Building CXX object src/core/CMakeFiles/core.dir/model/object-ptr-container.cc.o
[97/509] Building CXX object src/core/CMakeFiles/core.dir/model/global-value.cc.o
[98/509] Building CXX object src/core/CMakeFiles/core.dir/model/object-factory.cc.o
[99/509] Building CXX object src/core/CMakeFiles/core.dir/model/callback.cc.o
[100/509] Building CXX object src/core/CMakeFiles/core.dir/model/fatal-impl.cc.o
[101/509] Building CXX object src/core/CMakeFiles/core.dir/model/vector.cc.o
[102/509] Building CXX object src/core/CMakeFiles/core.dir/model/names.cc.o
[103/509] Building CXX object src/core/CMakeFiles/core.dir/model/config.cc.o
[104/509] Building CXX object src/core/CMakeFiles/core.dir/model/hash-function.cc.o
[105/509] Building CXX object src/core/CMakeFiles/core.dir/model/hash-murmur3.cc.o
[106/509] Building CXX object src/core/CMakeFiles/core.dir/model/hash-fnv.cc.o
[107/509] Building CXX object src/core/CMakeFiles/core.dir/model/hash.cc.o
[108/509] Building CXX object src/core/CMakeFiles/core.dir/model/ascii-file.cc.o
[109/509] Building CXX object src/core/CMakeFiles/core.dir/model/node-printer.cc.o
[110/509] Building CXX object src/core/CMakeFiles/core.dir/model/des-metrics.cc.o
[111/509] Building CXX object src/core/CMakeFiles/core.dir/model/show-progress.cc.o
[112/509] Building CXX object src/core/CMakeFiles/core.dir/model/time-printer.cc.o
[113/509] Building CXX object src/core/CMakeFiles/core.dir/model/system-wall-clock-timestamp.cc.o
[114/509] Building CXX object src/core/CMakeFiles/core.dir/model/system-wall-clock-ms.cc.o
[115/509] Building CXX object src/core/CMakeFiles/core.dir/model/trickle-timer.cc.o
[116/509] Building CXX object src/core/CMakeFiles/core.dir/model/system-path.cc.o
[117/509] Building CXX object src/core/CMakeFiles/core.dir/model/length.cc.o
[118/509] Building CXX object src/core/CMakeFiles/core.dir/model/realtime-simulator-impl.cc.o
[119/509] Building CXX object src/core/CMakeFiles/core.dir/model/wall-clock-synchronizer.cc.o
[120/509] Building CXX object src/core/CMakeFiles/core.dir/model/demangle.cc.o
[121/509] Building CXX object src/core/CMakeFiles/core.dir/model/matrix-array.cc.o
[122/509] Building CXX object src/core/examples/CMakeFiles/fatal-example.dir/fatal-example.cc.o
[123/509] Building CXX object src/core/examples/CMakeFiles/assert-example.dir/assert-example.cc.o
[124/509] Building CXX object src/core/examples/CMakeFiles/length-example.dir/length-example.cc.o
[125/509] Building CXX object src/core/examples/CMakeFiles/command-line-example.dir/command-line-example.cc.o
[126/509] Building CXX object src/core/examples/CMakeFiles/main-ptr.dir/main-ptr.cc.o
[127/509] Building CXX object src/core/examples/CMakeFiles/hash-example.dir/hash-example.cc.o
[128/509] Building CXX object src/core/examples/CMakeFiles/main-callback.dir/main-callback.cc.o
[129/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-core-optimized.so
[130/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-uav-coop-optimized.so
[131/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-deploy-optimized
[132/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-manifest-optimized
[133/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-uav-coop2-optimized.so
[134/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-assert-example-optimized
[135/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-command-line-example-optimized
[136/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-fatal-example-optimized
[137/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-hash-example-optimized
[138/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-length-example-optimized
[139/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-main-callback-optimized
[140/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-main-ptr-optimized
[141/509] Building CXX object src/core/examples/CMakeFiles/sample-random-variable.dir/sample-random-variable.cc.o
[142/509] Building CXX object src/core/examples/CMakeFiles/sample-log-time-format.dir/sample-log-time-format.cc.o
[143/509] Building CXX object src/core/examples/CMakeFiles/sample-random-variable-stream.dir/sample-random-variable-stream.cc.o
[144/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-sample-random-variable-optimized
[145/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-sample-random-variable-stream-optimized
[146/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-sample-log-time-format-optimized
[147/509] Building CXX object src/core/examples/CMakeFiles/sample-simulator.dir/sample-simulator.cc.o
[148/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-sample-simulator-optimized
[149/509] Building CXX object src/core/examples/CMakeFiles/test-string-value-formatting.dir/test-string-value-formatting.cc.o
[150/509] Building CXX object src/core/examples/CMakeFiles/system-path-examples.dir/system-path-examples.cc.o
[151/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-test-string-value-formatting-optimized
[152/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-system-path-examples-optimized
[153/509] Building CXX object src/core/examples/CMakeFiles/sample-show-progress.dir/sample-show-progress.cc.o
[154/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-sample-show-progress-optimized
[155/509] Building CXX object src/core/examples/CMakeFiles/main-test-sync.dir/main-test-sync.cc.o
[156/509] Building CXX object src/network/CMakeFiles/network.dir/helper/application-container.cc.o
[157/509] Building CXX object src/core/examples/CMakeFiles/empirical-random-variable-example.dir/empirical-random-variable-example.cc.o
[158/509] Building CXX object src/core/examples/CMakeFiles/log-example.dir/log-example.cc.o
[159/509] Building CXX object src/network/CMakeFiles/network.dir/helper/application-helper.cc.o
[160/509] Building CXX object src/network/CMakeFiles/network.dir/helper/net-device-container.cc.o
[161/509] Building CXX object src/network/CMakeFiles/network.dir/helper/delay-jitter-estimation.cc.o
[162/509] Building CXX object src/network/CMakeFiles/network.dir/helper/packet-socket-helper.cc.o
[163/509] Building CXX object src/network/CMakeFiles/network.dir/helper/node-container.cc.o
[164/509] Building CXX object src/network/CMakeFiles/network.dir/model/address.cc.o
[165/509] Building CXX object src/network/CMakeFiles/network.dir/model/application.cc.o
[166/509] Building CXX object src/network/CMakeFiles/network.dir/helper/simple-net-device-helper.cc.o
[167/509] Building CXX object src/network/CMakeFiles/network.dir/model/byte-tag-list.cc.o
[168/509] Building CXX object src/network/CMakeFiles/network.dir/model/buffer.cc.o
[169/509] Building CXX object src/network/CMakeFiles/network.dir/helper/trace-helper.cc.o
[170/509] Building CXX object src/network/CMakeFiles/network.dir/model/channel.cc.o
[171/509] Building CXX object src/network/CMakeFiles/network.dir/model/chunk.cc.o
[172/509] Building CXX object src/network/CMakeFiles/network.dir/model/header.cc.o
[173/509] Building CXX object src/network/CMakeFiles/network.dir/model/channel-list.cc.o
[174/509] Building CXX object src/network/CMakeFiles/network.dir/model/net-device.cc.o
[175/509] Building CXX object src/network/CMakeFiles/network.dir/model/nix-vector.cc.o
[176/509] Building CXX object src/network/CMakeFiles/network.dir/model/node-list.cc.o
[177/509] Building CXX object src/network/CMakeFiles/network.dir/model/packet-tag-list.cc.o
[178/509] Building CXX object src/network/CMakeFiles/network.dir/model/packet-metadata.cc.o
[179/509] Building CXX object src/network/CMakeFiles/network.dir/model/socket-factory.cc.o
[180/509] Building CXX object src/network/CMakeFiles/network.dir/model/packet.cc.o
[181/509] Building CXX object src/network/CMakeFiles/network.dir/model/tag-buffer.cc.o
[182/509] Building CXX object src/network/CMakeFiles/network.dir/model/node.cc.o
[183/509] Building CXX object src/network/CMakeFiles/network.dir/model/tag.cc.o
[184/509] Building CXX object src/network/CMakeFiles/network.dir/model/socket.cc.o
[185/509] Building CXX object src/network/CMakeFiles/network.dir/model/trailer.cc.o
[186/509] Building CXX object src/network/CMakeFiles/network.dir/utils/crc32.cc.o
[187/509] Building CXX object src/network/CMakeFiles/network.dir/utils/address-utils.cc.o
[188/509] Building CXX object src/network/CMakeFiles/network.dir/utils/bit-deserializer.cc.o
[189/509] Building CXX object src/network/CMakeFiles/network.dir/utils/bit-serializer.cc.o
[190/509] Building CXX object src/network/CMakeFiles/network.dir/utils/data-rate.cc.o
[191/509] Building CXX object src/network/CMakeFiles/network.dir/utils/drop-tail-queue.cc.o
[192/509] Building CXX object src/network/CMakeFiles/network.dir/utils/error-channel.cc.o
[193/509] Building CXX object src/network/CMakeFiles/network.dir/utils/ethernet-header.cc.o
[194/509] Building CXX object src/network/CMakeFiles/network.dir/utils/dynamic-queue-limits.cc.o
[195/509] Building CXX object src/network/CMakeFiles/network.dir/utils/ethernet-trailer.cc.o
[196/509] Building CXX object src/network/CMakeFiles/network.dir/utils/flow-id-tag.cc.o
[197/509] Building CXX object src/network/CMakeFiles/network.dir/utils/error-model.cc.o
[198/509] Building CXX object src/network/CMakeFiles/network.dir/utils/inet-socket-address.cc.o
[199/509] Building CXX object src/network/CMakeFiles/network.dir/utils/inet6-socket-address.cc.o
[200/509] Building CXX object src/network/CMakeFiles/network.dir/utils/llc-snap-header.cc.o
[201/509] Building CXX object src/network/CMakeFiles/network.dir/utils/ipv4-address.cc.o
[202/509] Building CXX object src/network/CMakeFiles/network.dir/utils/mac16-address.cc.o
[203/509] Building CXX object src/network/CMakeFiles/network.dir/utils/ipv6-address.cc.o
[204/509] Building CXX object src/network/CMakeFiles/network.dir/utils/mac48-address.cc.o
[205/509] Building CXX object src/network/CMakeFiles/network.dir/utils/mac64-address.cc.o
[206/509] Building CXX object src/network/CMakeFiles/network.dir/utils/mac8-address.cc.o
[207/509] Building CXX object src/network/CMakeFiles/network.dir/utils/output-stream-wrapper.cc.o
[208/509] Building CXX object src/network/CMakeFiles/network.dir/utils/net-device-queue-interface.cc.o
[209/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-burst.cc.o
[210/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-data-calculators.cc.o
[211/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-socket-address.cc.o
[212/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-socket-factory.cc.o
[213/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-socket-client.cc.o
[214/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-probe.cc.o
[215/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-socket-server.cc.o
[216/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packet-socket.cc.o
[217/509] Building CXX object src/network/CMakeFiles/network.dir/utils/pcap-file.cc.o
[218/509] Building CXX object src/network/CMakeFiles/network.dir/utils/pcap-file-wrapper.cc.o
[219/509] Building CXX object src/network/CMakeFiles/network.dir/utils/queue-limits.cc.o
[220/509] Building CXX object src/network/CMakeFiles/network.dir/utils/queue-item.cc.o
[221/509] Building CXX object src/network/CMakeFiles/network.dir/utils/packetbb.cc.o
[222/509] Building CXX object src/network/CMakeFiles/network.dir/utils/queue-size.cc.o
[223/509] Building CXX object src/network/CMakeFiles/network.dir/utils/radiotap-header.cc.o
[224/509] Building CXX object src/network/CMakeFiles/network.dir/utils/simple-channel.cc.o
[225/509] Building CXX object src/network/CMakeFiles/network.dir/utils/sll-header.cc.o
[226/509] Building CXX object src/network/CMakeFiles/network.dir/utils/timestamp-tag.cc.o
[227/509] Building CXX object src/network/examples/CMakeFiles/bit-serializer.dir/bit-serializer.cc.o
[228/509] Building CXX object src/network/examples/CMakeFiles/main-packet-header.dir/main-packet-header.cc.o
[229/509] Building CXX object src/network/examples/CMakeFiles/main-packet-tag.dir/main-packet-tag.cc.o
[230/509] Building CXX object src/network/CMakeFiles/network.dir/utils/queue.cc.o
[231/509] Building CXX object src/network/CMakeFiles/network.dir/utils/simple-net-device.cc.o
[232/509] Building CXX object src/network/examples/CMakeFiles/lollipop-comparisons.dir/lollipop-comparisons.cc.o
[233/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/sqlite-data-output.cc.o
[234/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/sqlite-output.cc.o
[235/509] Building CXX object src/network/examples/CMakeFiles/packet-socket-apps.dir/packet-socket-apps.cc.o
[236/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/basic-data-calculators.cc.o
[237/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/data-calculator.cc.o
[238/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/boolean-probe.cc.o
[239/509] Building CXX object src/stats/CMakeFiles/stats.dir/helper/file-helper.cc.o
[240/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/data-collection-object.cc.o
[241/509] Building CXX object src/stats/CMakeFiles/stats.dir/helper/gnuplot-helper.cc.o
[242/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/data-output-interface.cc.o
[243/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/data-collector.cc.o
[244/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/get-wildcard-matches.cc.o
[245/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/file-aggregator.cc.o
[246/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/gnuplot.cc.o
[247/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/double-probe.cc.o
[248/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/gnuplot-aggregator.cc.o
[249/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/histogram.cc.o
[250/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/probe.cc.o
[251/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/time-data-calculators.cc.o
[252/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/omnet-data-output.cc.o
[253/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/time-probe.cc.o
[254/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/time-series-adaptor.cc.o
[255/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/uinteger-16-probe.cc.o
[256/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/uinteger-32-probe.cc.o
[257/509] Building CXX object src/stats/examples/CMakeFiles/gnuplot-example.dir/gnuplot-example.cc.o
[258/509] Building CXX object src/stats/CMakeFiles/stats.dir/model/uinteger-8-probe.cc.o
[259/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-stats-optimized.so
[260/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-empirical-random-variable-example-optimized
[261/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-network-optimized.so
[262/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-main-test-sync-optimized
[263/509] Linking CXX executable /home/user/ns3-dev/build/src/core/examples/ns3.46-log-example-optimized
[264/509] Linking CXX executable /home/user/ns3-dev/build/src/network/examples/ns3.46-bit-serializer-optimized
[265/509] Linking CXX executable /home/user/ns3-dev/build/src/network/examples/ns3.46-main-packet-header-optimized
[266/509] Linking CXX executable /home/user/ns3-dev/build/src/network/examples/ns3.46-main-packet-tag-optimized
[267/509] Linking CXX executable /home/user/ns3-dev/build/src/network/examples/ns3.46-packet-socket-apps-optimized
[268/509] Building CXX object src/stats/examples/CMakeFiles/gnuplot-aggregator-example.dir/gnuplot-aggregator-example.cc.o
[269/509] Linking CXX executable /home/user/ns3-dev/build/src/network/examples/ns3.46-lollipop-comparisons-optimized
[270/509] Linking CXX executable /home/user/ns3-dev/build/src/stats/examples/ns3.46-gnuplot-example-optimized
[271/509] Linking CXX executable /home/user/ns3-dev/build/src/stats/examples/ns3.46-gnuplot-aggregator-example-optimized
[272/509] Building CXX object src/stats/examples/CMakeFiles/double-probe-example.dir/double-probe-example.cc.o
[273/509] Linking CXX executable /home/user/ns3-dev/build/src/stats/examples/ns3.46-double-probe-example-optimized
[274/509] Building CXX object src/stats/examples/CMakeFiles/time-probe-example.dir/time-probe-example.cc.o
[275/509] Linking CXX executable /home/user/ns3-dev/build/src/stats/examples/ns3.46-time-probe-example-optimized
[276/509] Building CXX object src/stats/examples/CMakeFiles/file-aggregator-example.dir/file-aggregator-example.cc.o
[277/509] Linking CXX executable /home/user/ns3-dev/build/src/stats/examples/ns3.46-file-aggregator-example-optimized
[278/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/helper/group-mobility-helper.cc.o
[279/509] Building CXX object src/stats/examples/CMakeFiles/gnuplot-helper-example.dir/gnuplot-helper-example.cc.o
[280/509] Linking CXX executable /home/user/ns3-dev/build/src/stats/examples/ns3.46-gnuplot-helper-example-optimized
[281/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/helper/mobility-helper.cc.o
[282/509] Building CXX object src/stats/examples/CMakeFiles/file-helper-example.dir/file-helper-example.cc.o
[283/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/box.cc.o
[284/509] Linking CXX executable /home/user/ns3-dev/build/src/stats/examples/ns3.46-file-helper-example-optimized
[285/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/constant-acceleration-mobility-model.cc.o
[286/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/constant-position-mobility-model.cc.o
[287/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/constant-velocity-helper.cc.o
[288/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/helper/ns2-mobility-helper.cc.o
[289/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/constant-velocity-mobility-model.cc.o
[290/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/geocentric-constant-position-mobility-model.cc.o
[291/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/geographic-positions.cc.o
[292/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/gauss-markov-mobility-model.cc.o
[293/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/hierarchical-mobility-model.cc.o
[294/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/random-direction-2d-mobility-model.cc.o
[295/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/mobility-model.cc.o
[296/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/position-allocator.cc.o
[297/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/random-waypoint-mobility-model.cc.o
[298/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/rectangle.cc.o
[299/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/random-walk-2d-mobility-model.cc.o
[300/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/waypoint.cc.o
[301/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/steady-state-random-waypoint-mobility-model.cc.o
[302/509] Building CXX object src/mobility/CMakeFiles/mobility.dir/model/waypoint-mobility-model.cc.o
[303/509] Building CXX object src/mobility/examples/CMakeFiles/bonnmotion-ns2-example.dir/bonnmotion-ns2-example.cc.o
[304/509] Building CXX object src/mobility/examples/CMakeFiles/constant-mobility-example.dir/constant-mobility-example.cc.o
[305/509] Building CXX object src/mobility/examples/CMakeFiles/main-random-topology.dir/main-random-topology.cc.o
[306/509] Building CXX object src/mobility/examples/CMakeFiles/main-random-walk.dir/main-random-walk.cc.o
[307/509] Building CXX object src/mobility/examples/CMakeFiles/main-grid-topology.dir/main-grid-topology.cc.o
[308/509] Building CXX object src/mobility/examples/CMakeFiles/ns2-mobility-trace.dir/ns2-mobility-trace.cc.o
[309/509] Building CXX object src/mobility/examples/CMakeFiles/mobility-trace-example.dir/mobility-trace-example.cc.o
[310/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/circular-aperture-antenna-model.cc.o
[311/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/angles.cc.o
[312/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/antenna-model.cc.o
[313/509] Building CXX object src/mobility/examples/CMakeFiles/reference-point-group-mobility-example.dir/reference-point-group-mobility-example.cc.o
[314/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/isotropic-antenna-model.cc.o
[315/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/parabolic-antenna-model.cc.o
[316/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/cosine-antenna-model.cc.o
[317/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/phased-array-model.cc.o
[318/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/three-gpp-antenna-model.cc.o
[319/509] Building CXX object src/antenna/CMakeFiles/antenna.dir/model/uniform-planar-array.cc.o
[320/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-antenna-optimized.so
[321/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-mobility-optimized.so
[322/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-bonnmotion-ns2-example-optimized
[323/509] Building CXX object src/antenna/examples/CMakeFiles/adjacency-matrix-example.dir/adjacency-matrix-example.cc.o
[324/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-constant-mobility-example-optimized
[325/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-main-random-topology-optimized
[326/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-main-random-walk-optimized
[327/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-ns2-mobility-trace-optimized
[328/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-mobility-trace-example-optimized
[329/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-main-grid-topology-optimized
[330/509] Linking CXX executable /home/user/ns3-dev/build/src/antenna/examples/ns3.46-adjacency-matrix-example-optimized
[331/509] Linking CXX executable /home/user/ns3-dev/build/src/mobility/examples/ns3.46-reference-point-group-mobility-example-optimized
[332/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/helper/spectrum-helper.cc.o
[333/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/helper/tv-spectrum-transmitter-helper.cc.o
[334/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/helper/spectrum-analyzer-helper.cc.o
[335/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/helper/adhoc-aloha-noack-ideal-phy-helper.cc.o
[336/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/aloha-noack-mac-header.cc.o
[337/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/helper/waveform-generator-helper.cc.o
[338/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/constant-spectrum-propagation-loss.cc.o
[339/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/half-duplex-ideal-phy-signal-parameters.cc.o
[340/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/friis-spectrum-propagation-loss.cc.o
[341/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/ism-spectrum-value-helper.cc.o
[342/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/hexagonal-wraparound-model.cc.o
[343/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/aloha-noack-net-device.cc.o
[344/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/microwave-oven-spectrum-value-helper.cc.o
[345/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/matrix-based-channel-model.cc.o
[346/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/half-duplex-ideal-phy.cc.o
[347/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/phased-array-spectrum-propagation-loss-model.cc.o
[348/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/non-communicating-net-device.cc.o
[349/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/single-model-spectrum-channel.cc.o
[350/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/multi-model-spectrum-channel.cc.o
[351/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-converter.cc.o
[352/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-analyzer.cc.o
[353/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-error-model.cc.o
[354/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-interference.cc.o
[355/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-model-300kHz-300GHz-log.cc.o
[356/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-model-ism2400MHz-res1MHz.cc.o
[357/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-channel.cc.o
[358/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-model.cc.o
[359/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-phy.cc.o
[360/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-propagation-loss-model.cc.o
[361/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-signal-parameters.cc.o
[362/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-transmit-filter.cc.o
[363/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/spectrum-value.cc.o
[364/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/trace-fading-loss-model.cc.o
[365/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/three-gpp-spectrum-propagation-loss-model.cc.o
[366/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/tv-spectrum-transmitter.cc.o
[367/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/wraparound-model.cc.o
[368/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/waveform-generator.cc.o
[369/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/two-ray-spectrum-propagation-loss-model.cc.o
[370/509] Building CXX object src/spectrum/examples/CMakeFiles/tv-trans-example.dir/tv-trans-example.cc.o
[371/509] Building CXX object src/spectrum/examples/CMakeFiles/tv-trans-regional-example.dir/tv-trans-regional-example.cc.o
[372/509] Building CXX object src/spectrum/CMakeFiles/spectrum.dir/model/three-gpp-channel-model.cc.o
[373/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/channel-condition-model.cc.o
[374/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/cost231-propagation-loss-model.cc.o
[375/509] Building CXX object src/spectrum/examples/CMakeFiles/three-gpp-ntn-channel-example.dir/three-gpp-ntn-channel-example.cc.o
[376/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/itu-r-1411-los-propagation-loss-model.cc.o
[377/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/jakes-process.cc.o
[378/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/jakes-propagation-loss-model.cc.o
[379/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/kun-2600-mhz-propagation-loss-model.cc.o
[380/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/itu-r-1411-nlos-over-rooftop-propagation-loss-model.cc.o
[381/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/propagation-delay-model.cc.o
[382/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/okumura-hata-propagation-loss-model.cc.o
[383/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/probabilistic-v2v-channel-condition-model.cc.o
[384/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/three-gpp-v2v-propagation-loss-model.cc.o
[385/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/propagation-loss-model.cc.o
[386/509] Building CXX object src/propagation/examples/CMakeFiles/jakes-propagation-model-example.dir/jakes-propagation-model-example.cc.o
[387/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/helper/building-container.cc.o
[388/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/helper/building-allocator.cc.o
[389/509] Building CXX object src/propagation/CMakeFiles/propagation.dir/model/three-gpp-propagation-loss-model.cc.o
[390/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-propagation-optimized.so
[391/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/helper/buildings-helper.cc.o
[392/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/helper/building-position-allocator.cc.o
[393/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/building-list.cc.o
[394/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/buildings-channel-condition-model.cc.o
[395/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/buildings-propagation-loss-model.cc.o
[396/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/building.cc.o
[397/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/itu-r-1238-propagation-loss-model.cc.o
[398/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/hybrid-buildings-propagation-loss-model.cc.o
[399/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/mobility-building-info.cc.o
[400/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/oh-buildings-propagation-loss-model.cc.o
[401/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/three-gpp-v2v-channel-condition-model.cc.o
[402/509] Building CXX object src/buildings/CMakeFiles/buildings.dir/model/random-walk-2d-outdoor-mobility-model.cc.o
[403/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-buildings-optimized.so
[404/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-spectrum-optimized.so
[405/509] Linking CXX executable /home/user/ns3-dev/build/src/spectrum/examples/ns3.46-tv-trans-example-optimized
[406/509] Linking CXX executable /home/user/ns3-dev/build/src/spectrum/examples/ns3.46-tv-trans-regional-example-optimized
[407/509] Linking CXX executable /home/user/ns3-dev/build/src/spectrum/examples/ns3.46-three-gpp-ntn-channel-example-optimized
[408/509] Linking CXX executable /home/user/ns3-dev/build/src/propagation/examples/ns3.46-jakes-propagation-model-example-optimized
[409/509] Building CXX object src/buildings/examples/CMakeFiles/outdoor-random-walk-example.dir/outdoor-random-walk-example.cc.o
[410/509] Linking CXX executable /home/user/ns3-dev/build/src/buildings/examples/ns3.46-outdoor-random-walk-example-optimized
[411/509] Building CXX object src/buildings/examples/CMakeFiles/outdoor-group-mobility-example.dir/outdoor-group-mobility-example.cc.o
[412/509] Linking CXX executable /home/user/ns3-dev/build/src/buildings/examples/ns3.46-outdoor-group-mobility-example-optimized
[413/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-error-model.cc.o
[414/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-csmaca.cc.o
[415/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-fields.cc.o
[416/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-interference-helper.cc.o
[417/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-lqi-tag.cc.o
[418/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-mac-header.cc.o
[419/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/helper/lr-wpan-helper.cc.o
[420/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-mac-trailer.cc.o
[421/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-mac-pl-headers.cc.o
[422/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-mac-base.cc.o
[423/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-spectrum-signal-parameters.cc.o
[424/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-spectrum-value-helper.cc.o
[425/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-net-device.cc.o
[426/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-phy.cc.o
[427/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-data.dir/lr-wpan-data.cc.o
[428/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-packet-print.dir/lr-wpan-packet-print.cc.o
[429/509] Building CXX object src/lr-wpan/CMakeFiles/lr-wpan.dir/model/lr-wpan-mac.cc.o
[430/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-lr-wpan-optimized.so
[431/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-pass-optimized
[432/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop/examples/ns3.46-uav-coop-summary-optimized
[433/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-coop2/examples/ns3.46-uav-coop2-river-optimized
[434/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-data-optimized
[435/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-packet-print-optimized
[436/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-phy-test.dir/lr-wpan-phy-test.cc.o
[437/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-phy-test-optimized
[438/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-beacon-mode.dir/lr-wpan-beacon-mode.cc.o
[439/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-beacon-mode-optimized
[440/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-ed-scan.dir/lr-wpan-ed-scan.cc.o
[441/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-ed-scan-optimized
[442/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-active-scan.dir/lr-wpan-active-scan.cc.o
[443/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-active-scan-optimized
[444/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-error-model-plot.dir/lr-wpan-error-model-plot.cc.o
[445/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-error-model-plot-optimized
[446/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/basic-energy-harvester-helper.cc.o
[447/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-error-distance-plot.dir/lr-wpan-error-distance-plot.cc.o
[448/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-error-distance-plot-optimized
[449/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-orphan-scan.dir/lr-wpan-orphan-scan.cc.o
[450/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-orphan-scan-optimized
[451/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/basic-energy-source-helper.cc.o
[452/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/energy-harvester-helper.cc.o
[453/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/energy-harvester-container.cc.o
[454/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/energy-model-helper.cc.o
[455/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/energy-source-container.cc.o
[456/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/li-ion-energy-source-helper.cc.o
[457/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/generic-battery-model-helper.cc.o
[458/509] Building CXX object src/lr-wpan/examples/CMakeFiles/lr-wpan-per-plot.dir/lr-wpan-per-plot.cc.o
[459/509] Linking CXX executable /home/user/ns3-dev/build/src/lr-wpan/examples/ns3.46-lr-wpan-per-plot-optimized
[460/509] Building CXX object src/energy/CMakeFiles/energy.dir/helper/rv-battery-model-helper.cc.o
[461/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/device-energy-model.cc.o
[462/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/device-energy-model-container.cc.o
[463/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/energy-harvester.cc.o
[464/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/energy-source.cc.o
[465/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/basic-energy-source.cc.o
[466/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/basic-energy-harvester.cc.o
[467/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/simple-device-energy-model.cc.o
[468/509] Building CXX object src/energy/examples/CMakeFiles/generic-battery-discharge-example.dir/generic-battery-discharge-example.cc.o
[469/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/generic-battery-model.cc.o
[470/509] Building CXX object src/energy/CMakeFiles/energy.dir/model/rv-battery-model.cc.o
[471/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-energy-optimized.so
[472/509] Linking CXX shared library /home/user/ns3-dev/build/lib/libns3.46-uav-sar-optimized.so
[473/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-hello-optimized
[474/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-substrate-test-optimized
[475/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-channel-test-optimized
[476/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-signal-test-optimized
[477/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-scenario-sar-optimized
[478/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-phy-error-test-optimized
[479/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-p1-test-optimized
[480/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-p1-plan-dump-optimized
[481/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-p1-scaling-test-optimized
[482/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-p1-antenna-test-optimized
[483/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-a2g-run-test-optimized
[484/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-a2g-sweep-test-optimized
[485/509] Linking CXX executable /home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-g2g-chain-test-optimized
[486/509] Linking CXX executable /home/user/ns3-dev/build/src/energy/examples/ns3.46-generic-battery-discharge-example-optimized
[487/509] Building CXX object examples/tutorial/CMakeFiles/hello-simulator.dir/hello-simulator.cc.o
[488/509] Linking CXX executable /home/user/ns3-dev/build/examples/tutorial/ns3.46-hello-simulator-optimized
[489/509] Building CXX object scratch/CMakeFiles/scratch_subdir_scratch-subdir.dir/subdir/scratch-subdir-additional-header.cc.o
[490/509] Building CXX object examples/tutorial/CMakeFiles/fourth.dir/fourth.cc.o
[491/509] Building CXX object scratch/CMakeFiles/scratch_scratch-simulator.dir/scratch-simulator.cc.o
[492/509] Linking CXX executable /home/user/ns3-dev/build/examples/tutorial/ns3.46-fourth-optimized
[493/509] Linking CXX executable /home/user/ns3-dev/build/scratch/ns3.46-scratch-simulator-optimized
[494/509] Building CXX object scratch/nested-subdir/CMakeFiles/scratch-nested-subdir-lib.dir/lib/scratch-nested-subdir-library-source.cc.o
[495/509] Linking CXX static library /home/user/ns3-dev/build/lib/libscratch-nested-subdir-lib.a
[496/509] Building CXX object scratch/CMakeFiles/scratch_subdir_scratch-subdir.dir/subdir/scratch-subdir.cc.o
[497/509] Linking CXX executable /home/user/ns3-dev/build/scratch/subdir/ns3.46-scratch-subdir-optimized
[498/509] Building CXX object examples/channel-models/CMakeFiles/three-gpp-v2v-channel-example.dir/three-gpp-v2v-channel-example.cc.o
[499/509] Linking CXX executable /home/user/ns3-dev/build/examples/channel-models/ns3.46-three-gpp-v2v-channel-example-optimized
[500/509] Building CXX object scratch/nested-subdir/CMakeFiles/scratch_nested-subdir_scratch-nested-subdir-executable.dir/scratch-nested-subdir-executable.cc.o
[501/509] Linking CXX executable /home/user/ns3-dev/build/scratch/nested-subdir/ns3.46-scratch-nested-subdir-executable-optimized
[502/509] Building CXX object utils/CMakeFiles/bench-packets.dir/bench-packets.cc.o
[503/509] Linking CXX executable /home/user/ns3-dev/build/utils/ns3.46-bench-packets-optimized
[504/509] Building CXX object utils/CMakeFiles/bench-scheduler.dir/bench-scheduler.cc.o
[505/509] Linking CXX executable /home/user/ns3-dev/build/utils/ns3.46-bench-scheduler-optimized
[506/509] Building CXX object utils/CMakeFiles/perf-io.dir/perf/perf-io.cc.o
[507/509] Linking CXX executable /home/user/ns3-dev/build/utils/perf/ns3.46-perf-io-optimized
[508/509] Building CXX object utils/CMakeFiles/print-introspected-doxygen.dir/print-introspected-doxygen.cc.o
[509/509] Linking CXX executable /home/user/ns3-dev/build/utils/ns3.46-print-introspected-doxygen-optimized
build/src/uav-coop/examples/:
total 784
drwxr-xr-x 2 root root   4096 Oct 22 17:35 .
drwxr-xr-x 3 root root   4096 Oct 22 17:33 ..
-rwxr-xr-x 1 root root 168216 Oct 22 17:34 ns3.46-uav-coop-deploy-optimized
-rwxr-xr-x 1 root root 137656 Oct 22 17:34 ns3.46-uav-coop-manifest-optimized
-rwxr-xr-x 1 root root 238600 Oct 22 17:35 ns3.46-uav-coop-pass-optimized
-rwxr-xr-x 1 root root 240856 Oct 22 17:35 ns3.46-uav-coop-summary-optimized

build/src/uav-coop2/examples/:
total 368
drwxr-xr-x 2 root root   4096 Oct 22 17:35 .
drwxr-xr-x 3 root root   4096 Oct 22 17:33 ..
-rwxr-xr-x 1 root root 365648 Oct 22 17:35 ns3.46-uav-coop2-river-optimized
```
