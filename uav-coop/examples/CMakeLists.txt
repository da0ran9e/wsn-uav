# uav-coop examples.

# Step 1: hex lattice -> random contiguous region -> random nodes, with checks.
build_lib_example(
  NAME uav-coop-deploy
  SOURCE_FILES coop-deploy.cc
  LIBRARIES_TO_LINK
    ${libuav-coop}
    ${libcore}
)
