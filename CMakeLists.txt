# Build configuration for wsn-uav module v1
# Fragment dissemination for UAV-assisted IoT networks

build_lib(
  LIBNAME wsn-uav

  SOURCE_FILES
    models/common/stub.cc
    models/common/log.cc
    models/network/scenario1-network.cc
    models/application/basestation-app.cc
    models/application/uav-app.cc
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
    models/network/scenario1-network.h
    models/application/basestation-app.h
    models/application/uav-app.h
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
