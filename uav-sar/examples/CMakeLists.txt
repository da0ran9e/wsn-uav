# uav-sar examples. Skeleton: one smoke example that proves the build/run
# pipeline. Scenario examples are added as the design is implemented.

build_lib_example(
  NAME uav-sar-hello
  SOURCE_FILES uav-sar-hello.cc
  LIBRARIES_TO_LINK
    ${libuav-sar}
    ${libcore}
)
