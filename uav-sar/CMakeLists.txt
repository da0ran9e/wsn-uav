# uav-sar module — Multi-UAV Search-and-Rescue over a PECEE cell substrate.
# Pure ns-3: depends ONLY on standard modules (no CC2420 / no custom wsn module).
# Skeleton stage: only a version stub is wired; simulation logic comes next.

build_lib(
  LIBNAME uav-sar

  SOURCE_FILES
    models/common/sar-info.cc
    models/common/cell-grid.cc
    models/common/lane-plan.cc
    models/common/node-capability.cc
    models/p1/p1-params.cc
    models/p1/p1-sensing.cc
    models/p1/p1-cells.cc
    models/common/inter-cell-routing.cc
    models/network/air-ground-loss.cc
    models/network/pair-shadowing-loss.cc
    models/network/phy-stats.cc
    models/network/forest-a2g-loss.cc
    models/network/sar-network.cc
    models/common/target-profile.cc
    models/common/clue-field.cc
    models/common/sar-metrics.cc
    models/application/flight-controller.cc
    models/application/region-coordinator.cc
    models/application/sar-ground-app.cc
    models/application/sar-fast-uav-app.cc
    models/application/sar-data-uav-app.cc
    models/application/sar-bs-app.cc
    helper/sar-config.cc

  HEADER_FILES
    models/common/sar-info.h
    models/common/sar-params.h
    models/common/cell-grid.h
    models/common/lane-plan.h
    models/common/node-capability.h
    models/p1/p1-types.h
    models/p1/p1-hex.h
    models/p1/p1-params.h
    models/p1/p1-sensing.h
    models/p1/p1-cells.h
    models/common/inter-cell-routing.h
    models/network/air-ground-loss.h
    models/network/pair-shadowing-loss.h
    models/network/phy-stats.h
    models/network/forest-a2g-loss.h
    models/network/sar-network.h
    models/common/target-profile.h
    models/common/clue-field.h
    models/common/sar-types.h
    models/common/sar-metrics.h
    models/common/gmc.h
    models/application/flight-controller.h
    models/application/region-coordinator.h
    models/application/sar-ground-app.h
    models/application/sar-fast-uav-app.h
    models/application/sar-data-uav-app.h
    models/application/sar-bs-app.h
    helper/sar-config.h

  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
    ${libenergy}
)
