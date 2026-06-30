# uav-sar module — Multi-UAV Search-and-Rescue over a PECEE cell substrate.
# Pure ns-3: depends ONLY on standard modules (no CC2420 / no custom wsn module).
# Skeleton stage: only a version stub is wired; simulation logic comes next.

build_lib(
  LIBNAME uav-sar

  SOURCE_FILES
    models/common/sar-info.cc

  HEADER_FILES
    models/common/sar-info.h

  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
    ${libenergy}
)
