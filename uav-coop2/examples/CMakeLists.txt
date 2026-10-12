# uav-coop2 examples.

# The River trial on ns-3: full IEEE 802.15.4 MAC (CSMA/CA, ACK, retries), the PECEE
# cell grid giving the channels (cell colour; one channel per gateway pair).
build_lib_example(
  NAME uav-coop2-river
  SOURCE_FILES coop2-river.cc
  LIBRARIES_TO_LINK
    ${libuav-coop2}
    ${libuav-coop}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
)
