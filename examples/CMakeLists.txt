add_executable(scenario-1-single-uav scenario-1-single-uav.cc)

target_link_libraries(scenario-1-single-uav
  PRIVATE
    ${libwsn-uav}
    ${libspectrum}
    ${libmobility}
    ${libnetwork}
    ${libcore}
    ${libwsn}
)
