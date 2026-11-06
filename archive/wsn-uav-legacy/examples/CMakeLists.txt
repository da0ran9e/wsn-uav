# Build scenario-0 example (CC2420).
# Requires the custom `wsn` (CC2420) module. Only wire it when that module is
# present in the tree; otherwise skip so the rest of the module still builds.
if(libwsn)
  build_lib_example(
    NAME scenario-0-radio-test
    SOURCE_FILES scenario-0-radio-test.cc
    LIBRARIES_TO_LINK
      ${libwsn-uav}
      ${libcore}
      ${libnetwork}
      ${libmobility}
      ${libspectrum}
      ${libwsn}
  )
endif()

# Build scenario-0.1 example (Native LR-WPAN)
build_lib_example(
  NAME scenario-0-1-lr-wpan-test
  SOURCE_FILES scenario-0-1-lr-wpan-test.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${liblr-wpan}
)

# Build scenario-0.2 example (Custom Network Layer over LR-WPAN)
build_lib_example(
  NAME scenario-0-2-custom-network-test
  SOURCE_FILES scenario-0-2-custom-network-test.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${liblr-wpan}
)

# Build scenario-0.3 example (Energy-Aware LR-WPAN)
build_lib_example(
  NAME scenario-0-3-energy-test
  SOURCE_FILES scenario-0-3-energy-test.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${liblr-wpan}
    ${libenergy}
)

# Build scenario-1 example (UAV-Assisted WSN)
build_lib_example(
  NAME scenario-1-test
  SOURCE_FILES scenario-1-test.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${liblr-wpan}
)

# Build SAR example (Multi-UAV Search-and-Rescue, Câu chuyện 1)
build_lib_example(
  NAME scenario-sar
  SOURCE_FILES scenario-sar.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${liblr-wpan}
    ${libenergy}
)
