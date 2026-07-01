# Build configuration for wsn-uav module v1
# Fragment dissemination for UAV-assisted IoT networks

build_lib(
  LIBNAME wsn-uav

  SOURCE_FILES
    models/common/stub.cc
    models/common/log.cc
    models/common/uav-trajectory.cc
    models/common/kmeans-model.cc
    models/common/semantic-fragment.cc
    models/common/cell-layer.cc
    models/common/local-clue.cc
    models/common/cooperation-phy-mac.cc
    models/network/scenario1-network.cc
    models/network/a2g-log-distance-loss.cc
    models/application/basestation-app.cc
    models/application/uav-dissemination-model.cc
    models/application/uav-app.cc
    models/application/uav-flight-controller.cc
    models/application/ground-node-app.cc
    helper/scenario0-1/scenario0-1-config.cc
    helper/scenario0-1/scenario0-1-mac.cc
    helper/scenario0-2/scenario0-2-config.cc
    helper/scenario0-2/scenario0-2-network.cc
    helper/scenario0-3/scenario0-3-config.cc
    helper/scenario0-3/scenario0-3-energy.cc
    helper/scenario1/scenario1-config.cc

  HEADER_FILES
    models/common/log.h
    models/common/uav-trajectory.h
    models/common/kmeans-model.h
    models/common/semantic-fragment.h
    models/common/cell-layer.h
    models/common/hex-cells-reference.h
    models/common/local-clue.h
    models/common/cooperation-phy-mac.h
    models/network/scenario1-network.h
    models/network/a2g-log-distance-loss.h
    models/application/basestation-app.h
    models/application/uav-dissemination-model.h
    models/application/uav-app.h
    models/application/uav-flight-controller.h
    models/application/ground-node-app.h
    helper/scenario0-1/scenario0-1-config.h
    helper/scenario0-1/scenario0-1-mac.h
    helper/scenario0-2/scenario0-2-config.h
    helper/scenario0-2/scenario0-2-network.h
    helper/scenario0-3/scenario0-3-config.h
    helper/scenario0-3/scenario0-3-energy.h
    helper/scenario1/scenario1-config.h

  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}
    ${liblr-wpan}
    ${libenergy}
)
