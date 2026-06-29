# Build configuration for wsn-uav module v1
# Fragment dissemination for UAV-assisted IoT networks

build_lib(
  LIBNAME wsn-uav

  SOURCE_FILES
    models/common/stub.cc
    models/common/log.cc
    models/common/uav-trajectory.cc
    models/common/kmeans-model.cc
    models/common/sar-fragment.cc
    models/common/sar-metrics.cc
    models/network/scenario1-network.cc
    models/network/sar-network.cc
    models/application/basestation-app.cc
    models/application/uav-app.cc
    models/application/uav-flight-controller.cc
    models/application/ground-node-app.cc
    models/application/sar-uav-app.cc
    models/application/sar-ground-app.cc
    helper/scenario0-1/scenario0-1-config.cc
    helper/scenario0-1/scenario0-1-mac.cc
    helper/scenario0-2/scenario0-2-config.cc
    helper/scenario0-2/scenario0-2-network.cc
    helper/scenario0-3/scenario0-3-config.cc
    helper/scenario0-3/scenario0-3-energy.cc
    helper/scenario1/scenario1-config.cc
    helper/sar/sar-config.cc

  HEADER_FILES
    models/common/log.h
    models/common/uav-trajectory.h
    models/common/kmeans-model.h
    models/common/sar-types.h
    models/common/sar-fragment.h
    models/common/sar-metrics.h
    models/network/scenario1-network.h
    models/network/sar-network.h
    models/application/basestation-app.h
    models/application/uav-app.h
    models/application/uav-flight-controller.h
    models/application/ground-node-app.h
    models/application/sar-uav-app.h
    models/application/sar-ground-app.h
    helper/scenario0-1/scenario0-1-config.h
    helper/scenario0-1/scenario0-1-mac.h
    helper/scenario0-2/scenario0-2-config.h
    helper/scenario0-2/scenario0-2-network.h
    helper/scenario0-3/scenario0-3-config.h
    helper/scenario0-3/scenario0-3-energy.h
    helper/scenario1/scenario1-config.h
    helper/sar/sar-config.h

  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}
    ${liblr-wpan}
    ${libenergy}
)
