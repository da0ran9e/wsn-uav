# uav-coop examples.

# Step 1: hex lattice -> random contiguous region -> random nodes, with checks.
build_lib_example(
  NAME uav-coop-deploy
  SOURCE_FILES coop-deploy.cc
  LIBRARIES_TO_LINK
    ${libuav-coop}
    ${libcore}
)

# Step 3: the UAV flies the step-2 path and broadcasts a numbered stream.
build_lib_example(
  NAME uav-coop-pass
  SOURCE_FILES coop-pass.cc
  LIBRARIES_TO_LINK
    ${libuav-coop}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
)

# Step 4: inside each cell, a short summary of what the cell holds, up to the CL.
build_lib_example(
  NAME uav-coop-summary
  SOURCE_FILES coop-summary.cc
  LIBRARIES_TO_LINK
    ${libuav-coop}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libpropagation}
    ${liblr-wpan}
)

# Step 5 (trial, logic level): the base manifest phase between cells.
build_lib_example(
  NAME uav-coop-manifest
  SOURCE_FILES coop-manifest.cc
  LIBRARIES_TO_LINK
    ${libuav-coop}
    ${libcore}
)
