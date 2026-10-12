# uav-coop2 module -- the River scheme (layer 3 of phase 1) on the uav-coop deployment,
# flight path and broadcast. The plan comes from tools/river_export.py.

build_lib(
  LIBNAME uav-coop2

  SOURCE_FILES
    models/river-plan.cc

  HEADER_FILES
    models/river-plan.h

  LIBRARIES_TO_LINK
    ${libuav-coop}
    ${libcore}
)
