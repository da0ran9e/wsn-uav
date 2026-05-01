# Build configuration for wsn-uav module
# Fragment dissemination for UAV-assisted IoT networks
# Reproduces paper baseline: "Joint Fragment Dissemination and Edge Fusion
#   for Fast Target Detection in UAV-Assisted Urban IoT"

build_lib(
  LIBNAME wsn-uav

  SOURCE_FILES
    models/common/statistics-collector.cc
    models/common/packet-header.cc
    models/application/fragment-model.cc
    models/application/confidence-model.cc
    models/application/fragment-dissemination-app.cc
    models/mac/wsn-uav-mac.cc
    helper/topology-helper.cc
    helper/trajectory-helper.cc
    helper/result-writer.cc
    helper/wsn-network-helper.cc

  HEADER_FILES
    models/common/parameters.h
    models/common/types.h
    models/common/statistics-collector.h
    models/common/packet-header.h
    models/application/fragment-model.h
    models/application/confidence-model.h
    models/application/fragment-dissemination-app.h
    models/mac/wsn-uav-mac.h
    helper/topology-helper.h
    helper/trajectory-helper.h
    helper/result-writer.h
    helper/wsn-network-helper.h
    helper/wsn-uav-helper.h

  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}
)
