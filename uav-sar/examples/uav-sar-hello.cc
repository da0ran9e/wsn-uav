// Smoke example for the uav-sar skeleton: proves the module builds, links and
// runs under a pure-ns-3 (no CC2420) tree. Real SAR scenarios come next.

#include "ns3/core-module.h"
#include "../models/common/sar-info.h"

#include <iostream>

using namespace ns3;

int main(int argc, char* argv[]) {
    CommandLine cmd;
    cmd.Parse(argc, argv);
    std::cout << ns3::uavsar::ModuleInfo() << std::endl;
    Simulator::Stop(Seconds(1.0));
    Simulator::Run();
    Simulator::Destroy();
    return 0;
}
