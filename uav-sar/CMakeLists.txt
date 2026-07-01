# uav-sar module — Multi-UAV Search-and-Rescue over a PECEE cell substrate.
# Pure ns-3: depends ONLY on standard modules (no CC2420 / no custom wsn module).
# Skeleton stage: only a version stub is wired; simulation logic comes next.

build_lib(
  LIBNAME uav-sar

  SOURCE_FILES
    models/common/sar-info.cc
    models/common/cell-grid.cc
    models/common/inter-cell-routing.cc

  HEADER_FILES
    models/common/sar-info.h
    models/common/sar-params.h
    models/common/cell-grid.h
    models/common/inter-cell-routing.h

  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
    ${libenergy}
)
