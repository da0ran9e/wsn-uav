# uav-coop module -- UAV-assisted dissemination with edge cooperation inside wide
# clusters. Starts from the parameter set measured in uav-sar's a2g-*/g2g-*
# experiments (urban branch). Step 1: hex lattice, random contiguous region,
# random node deployment.

build_lib(
  LIBNAME uav-coop

  SOURCE_FILES
    models/common/hex-grid.cc
    models/common/region.cc
    models/common/deploy.cc

  HEADER_FILES
    models/common/coop-params.h
    models/common/coop-rng.h
    models/common/hex-grid.h
    models/common/region.h
    models/common/deploy.h

  LIBRARIES_TO_LINK
    ${libcore}
)
