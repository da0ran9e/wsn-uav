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
