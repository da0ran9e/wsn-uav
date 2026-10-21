#include "river-plan.h"

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>

namespace ns3::uavcoop2 {

namespace {

[[noreturn]] void Bad(const std::string& file, const std::string& line) {
    std::fprintf(stderr, "%s: malformed line: %s\n", file.c_str(), line.c_str());
    std::exit(1);
}

Hex ReadHex(std::istringstream& in) {
    Hex h;
    in >> h.q >> h.r;
    return h;
}

std::vector<Hex> ReadPath(std::istringstream& in) {
    size_t n = 0;
    in >> n;
    std::vector<Hex> p(n);
    for (Hex& h : p) h = ReadHex(in);
    return p;
}

}  // namespace

Plan ReadPlan(const std::string& file) {
    std::ifstream f(file);
    if (!f) {
        std::fprintf(stderr, "cannot open %s\n", file.c_str());
        std::exit(1);
    }
    Plan p;
    std::string line;
    while (std::getline(f, line)) {
        if (line.empty()) continue;
        std::istringstream in(line);
        std::string tag;
        in >> tag;
        if (tag == "N") {
            in >> p.packets;
        } else if (tag == "AXE") {
            PlanAxe x;
            x.a = ReadHex(in);
            in >> x.first >> x.last;
            p.axe.push_back(x);
        } else if (tag == "BANK") {
            PlanBank x;
            x.a = ReadHex(in);
            in >> x.side;
            x.b = ReadHex(in);
            x.path = ReadPath(in);
            p.banks.push_back(x);
        } else if (tag == "CRIT") {
            p.crit.push_back(ReadHex(in));
        } else if (tag == "NEED") {
            PlanNeed x;
            x.k = ReadHex(in);
            in >> x.first >> x.last;
            p.need.push_back(x);
        } else if (tag == "CIRC") {
            PlanCirc x;
            x.k = ReadHex(in);
            x.m = ReadHex(in);
            x.a = ReadHex(in);
            x.b = ReadHex(in);
            x.path = ReadPath(in);
            p.circ.push_back(x);
        } else if (tag == "DIRECT") {
            PlanDirect x;
            x.k = ReadHex(in);
            x.a = ReadHex(in);
            x.path = ReadPath(in);
            p.direct.push_back(x);
        } else if (tag == "CSET") {
            PlanCset x;
            x.k = ReadHex(in);
            in >> x.n;
            x.m = ReadHex(in);
            in >> x.first >> x.last;
            p.cset.push_back(x);
        } else if (tag == "CSRC") {
            PlanCirc x;
            x.k = ReadHex(in);
            x.m = ReadHex(in);
            x.a = ReadHex(in);
            x.b = ReadHex(in);
            x.path = ReadPath(in);
            p.csrc.push_back(x);
        } else if (tag == "CLINK") {
            PlanLink x;
            x.k = ReadHex(in);
            x.m = ReadHex(in);
            x.path = ReadPath(in);
            p.clink.push_back(x);
        } else {
            Bad(file, line);
        }
        if (in.fail()) Bad(file, line);
    }
    return p;
}

}  // namespace ns3::uavcoop2
