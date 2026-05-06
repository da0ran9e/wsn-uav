build_lib_example(
  NAME scenario-1-single-uav
  SOURCE_FILES scenario-1-single-uav.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}
)

build_lib_example(
  NAME scenario-2-multi-uav-2
  SOURCE_FILES scenario-2-multi-uav-2.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}
)

build_lib_example(
  NAME scenario-3-load-balanced-fragments
  SOURCE_FILES scenario-3-load-balanced-fragments.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}
)
