# uav-sar examples. Skeleton: one smoke example that proves the build/run
# pipeline. Scenario examples are added as the design is implemented.

build_lib_example(
  NAME uav-sar-hello
  SOURCE_FILES uav-sar-hello.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
)

# Phase 1 substrate verification (pure logic; no ns-3 sim).
build_lib_example(
  NAME uav-sar-substrate-test
  SOURCE_FILES substrate-test.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
)

# Phase 2 channel smoke test (PDR vs distance/altitude).
build_lib_example(
  NAME uav-sar-channel-test
  SOURCE_FILES channel-test.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
)

# Phase 3 fragment + clue verification (pure logic).
build_lib_example(
  NAME uav-sar-signal-test
  SOURCE_FILES signal-test.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
)

# End-to-end SAR scenario.
build_lib_example(
  NAME scenario-sar
  SOURCE_FILES scenario-sar.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
)

# Packet-level PHY error validation (PER waterfall + drop causes).
build_lib_example(
  NAME uav-sar-phy-error-test
  SOURCE_FILES phy-error-test.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
)

# Phase 1 subtree verification (pure logic; no ns-3 sim).
build_lib_example(
  NAME uav-sar-p1-test
  SOURCE_FILES p1-test.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
)
