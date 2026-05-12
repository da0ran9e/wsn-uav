# Working with WSN-UAV Repo: Essential Rules & Procedures

**Focus:** Rules, configuration, build process, runtime gotchas  
**For:** Anyone modifying src/wsn-uav/  
**Last Updated:** 2026-05-08

---

## 1. Repository Structure Rules

### Where to Make Changes

**✅ ONLY modify inside `src/wsn-uav/`**
- Models: `src/wsn-uav/models/common/` and `src/wsn-uav/models/application/`
- Helpers: `src/wsn-uav/helper/`
- Examples: `src/wsn-uav/examples/`
- Docs: `src/wsn-uav/docs/`

**❌ DO NOT modify:**
- `src/wsn/` — Use existing CC2420 via linking
- `ns-3-dev-git-ns-3.46/` root files
- Build system outside CMakeLists.txt

### Directory Organization

```
src/wsn-uav/
├── CMakeLists.txt                    ← Only build config file
├── wscript                           ← Empty stub (CMake-only)
├── models/
│   ├── common/                       ← No ns3 dependency
│   │   ├── *.h                       ← Headers only (constexpr)
│   │   └── *.cc                      ← Implementation
│   └── application/                  ← Uses ns3::Application
│       ├── *.h
│       └── *.cc
├── helper/                           ← Orchestrators, exporters
│   ├── *.h
│   └── *.cc
├── examples/                         ← Entry points (main functions)
│   └── scenario-*.cc
└── docs/
    ├── README.md                     ← User guide
    └── progress/                     ← Session notes (this file)
```

---

## 2. Python & Environment Setup

### Python Version is Critical ⚠️

**REQUIRED:** Python 3.10 or 3.13  
**DO NOT use:** Python 3.14+ (breaks ns-3 argparse)

**Setup (one time):**
```bash
# Check which python3.10 is available
which python3.10
# Output: /opt/homebrew/bin/python3.10 (or similar)

# Create alias in ~/.zshrc or ~/.bash_profile:
alias ns3='python3.10 ./ns3'
# Then reload: source ~/.zshrc

# OR set environment variable:
export PYTHON3=/opt/homebrew/bin/python3.10
```

### Build Commands

```bash
# Use whichever syntax works with your environment setup
# Option A (with alias):
ns3 build
ns3 run "scenario-0-radio-test"

# Option B (direct path):
python3.10 ./ns3 build
python3.10 ./ns3 run "scenario-0-radio-test"

# Option C (if ns3 already configured):
./ns3 build  # Only works if Python 3.10 is default
```

**IMPORTANT:** The `./ns3` script detects Python version at runtime. Ensure Python 3.10 is in PATH or use explicit prefix.

---

## 3. Configure & Build Process

### Initial Configuration (if needed)

```bash
cd ns-3-dev-git-ns-3.46

# Check if already configured
ls -la cmake-cache  # If exists, already configured

# Configure ONLY wsn-uav module + examples:
./ns3 configure --enable-examples --enable-modules=wsn-uav

# If reconfiguration needed:
./ns3 clean
./ns3 configure --enable-examples --enable-modules=wsn-uav
```

**NOTE:** 
- Configure only wsn-uav (and its dependencies like wsn)
- Configuration uses `./ns3` script which auto-detects Python
- Ensure Python 3.10 is in PATH or use explicit alias

### Build Sequence

**Use exact order from v0 - DO NOT use `./ns3 build wsn-uav`**

```bash
cd ns-3-dev-git-ns-3.46

# Step 1: Build the entire ns-3 + all modules
./ns3 build

# Step 2: Run the executable directly
./build/scenario-0-radio-test
./build/scenario-1-single-uav --gridSize=10
```

**Why this order:**
- `./ns3 build` builds ns3-core AND all modules including wsn-uav
- Separating build steps can cause dependency issues
- Everything is compiled in one pass

### Configure Command Details

**Configure only wsn-uav module:**
```bash
./ns3 configure --enable-examples --enable-modules=wsn-uav
```

**What this does:**
- Configures only wsn-uav (and its dependency: wsn)
- Enables example executables
- Creates `cmake-cache/` directory
- Skips other modules (faster configuration)

**Parameters:**
```bash
./ns3 configure --enable-examples --enable-modules=wsn-uav
  --enable-examples      ← Include example executables
  --enable-modules=wsn-uav ← Only this module (+ dependencies)
```

**Do NOT use these (configure everything):**
```bash
# DON'T: This configures ALL modules
./ns3 configure --enable-examples

# DON'T: Don't list other modules
./ns3 configure --enable-examples --enable-modules=wsn,wsn-uav,core,network
```

**If configure fails:**
```bash
# Full clean and reconfigure
./ns3 clean
./ns3 configure --enable-examples --enable-modules=wsn-uav
```

### CMakeLists.txt Rules

**Use `build_lib()` macro for libraries:**
```cmake
build_lib(
  LIBNAME wsn-uav
  
  SOURCE_FILES
    models/common/statistics-collector.cc
    models/application/fragment-model.cc
    # ... add all .cc files
    
  HEADER_FILES
    models/common/parameters.h
    models/common/types.h
    # ... add all .h files
    
  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}              # ← Reuse existing CC2420 from libwsn
    
  EXAMPLES_AS_TESTS_SOURCES
    examples/scenario-0-radio-test.cc
    examples/scenario-1-single-uav.cc
)
```

**Key Points:**
- List ALL .cc files in SOURCE_FILES (missing files cause linker errors)
- List ALL .h files in HEADER_FILES
- Always include `${libwsn}` to link CC2420 implementation
- Examples go in EXAMPLES_AS_TESTS_SOURCES

### Troubleshooting Build

**Problem:** "undefined reference to cc2420"
```
Cause: CMakeLists.txt missing ${libwsn} in LIBRARIES_TO_LINK
Fix: Add ${libwsn} to LIBRARIES_TO_LINK section
    Rebuild: ./ns3 build
```

**Problem:** "file not found: models/xxx.cc" during build
```
Cause: SOURCE_FILES in CMakeLists.txt has wrong path or missing file
Fix: 1. List actual files: find src/wsn-uav -name "*.cc" | sort
     2. Update CMakeLists.txt SOURCE_FILES to match
     3. Rebuild: ./ns3 build
```

**Problem:** "ValueError: action 'store_true' not valid for positional arguments"
```
Cause: Python 3.14+ being used (incompatible with ns-3 build system)
Fix: 1. Check: python3.10 --version (should be 3.10.x)
     2. Ensure Python 3.10 in PATH: which python3.10
     3. If not: add alias ns3='python3.10 ./ns3' to ~/.zshrc
     4. Reconfigure: ./ns3 configure --enable-examples
```

**Problem:** "build directory not found" or build artifacts old
```
Cause: Stale build or incomplete previous build
Fix: 1. Full clean: ./ns3 clean
     2. Reconfigure: ./ns3 configure --enable-examples --enable-modules=wsn-uav
     3. Rebuild: ./ns3 build
```

---

## 4. Running Executables

### Two Methods to Run

**Method 1: Direct executable (RECOMMENDED)**
```bash
./build/scenario-1-single-uav --gridSize=10 --seed=1
```

**Method 2: Via ns3 (requires quotes + --)**
```bash
ns3 run "scenario-1-single-uav -- --gridSize=10 --seed=1"
```

### Examples

```bash
./build/scenario-0-radio-test
./build/scenario-1-single-uav --gridSize=10 --seed=1
./build/scenario-3-load-balanced-fragments --gridSize=20 --numFragments=20
```

### Standard Parameters (all scenarios)

```bash
--gridSize=N              # Network size (N×N nodes), default 10
--numFragments=K          # File fragments, default 10
--seed=S                  # Random seed, default 1
--runId=R                 # Run ID for batch, default 1
--simTime=T               # Simulation duration (seconds), default 500
--cooperationThreshold=T  # Coop trigger confidence, default 0.30
--alertThreshold=T        # Detection trigger confidence, default 0.75
--outputDir=PATH          # Output directory (auto-created)
```

---

## 5. Critical Gotchas & Workarounds

### Gotcha 1: Channel Isolation in CC2420

**Problem:** Using separate `Cc2420Helper` instances creates separate channels

**WRONG:**
```cpp
Cc2420Helper groundHelper;
auto groundChannel = groundHelper.CreateChannel();
groundHelper.Install(groundNodes);

Cc2420Helper uavHelper;  // ← WRONG: different instance
uavHelper.Install(uavNodes);
// Result: groundChannel ≠ uavChannel → no communication
```

**CORRECT:**
```cpp
Cc2420Helper cc2420;     // ← Single instance
auto channel = cc2420.CreateChannel();
cc2420.Install(groundNodes);
cc2420.Install(uavNodes);  // ← Same helper, same channel
// Result: Both on same channel → communication works
```

**Rule:** Always use ONE Cc2420Helper instance for ALL nodes

---

### Gotcha 2: Packet Callback Type Varies

**For NS-3 core NetDevice:**
```cpp
device->SetReceiveCallback([](Ptr<NetDevice> dev,
                               Ptr<const Packet> pkt,
                               uint16_t proto,
                               const Address& from) {
    return true;  // consumed
});
```

**For custom devices (check actual signature):**
```
Consult the device's .h file for exact signature
Different devices may have different callback signatures
```

**Rule:** Always check device header for exact callback signature

---

### Gotcha 3: Grid Spacing Mismatch

**v0 Bug:** Used 45m spacing (legacy from old code)  
**Paper Spec:** 20m spacing

**Rule:** Always use GRID_SPACING = 20.0 in parameters.h

---

### Gotcha 4: Output Path Creation

**Problem:** Output directory must exist before writing files

**Solution:**
```cpp
#include <filesystem>

void EnsureDirectoryExists(const std::string& dirPath) {
    std::filesystem::create_directories(dirPath);
}

// In result-writer:
ResultWriter writer(outputDir);
writer.Initialize();  // Creates directory recursively
```

**Rule:** Never assume output directory exists; create it explicitly

---

### Gotcha 5: Fragment Distribution Order

**Critical:** Fragment generation must follow exact pixel-stride algorithm

**Algorithm:**
```
Total pixels = 416 × 416 × 3 = 173,056
For i = 0 to K-1:
    pixelCount_i = floor(totalPixels / K) + (1 if i < remainder else 0)
    evidence_i = 1 - (1 - 0.90)^(pixelCount_i / totalPixels)
```

**Rule:** Don't deviate from this. Paper baseline depends on exact match.

---

### Gotcha 6: Mobility Model Timing

**Problem:** UAV position updates lag behind event callbacks

**Solution:** Use WaypointMobilityModel with explicit arrival times

```cpp
auto mob = node->GetObject<WaypointMobilityModel>();
for (const auto& wp : waypoints) {
    mob->AddWaypoint(ns3::Waypoint(
        Seconds(wp.arrivalTimeSec),  // Absolute time
        Vector(wp.x, wp.y, wp.z)
    ));
}
```

**Rule:** Schedule waypoints with absolute times, not relative times

---

## 6. Git & Version Control

### Branch Policy

**For this project:**
- Work on branches (never direct to main)
- One feature per branch
- Pull request review before merging

### Commit Message Format

```
[component] Short description (50 chars max)

Longer explanation if needed (wrap at 72 chars)

Related: issue/ticket reference
```

Example:
```
[radio] Fix CC2420 channel isolation bug

Changed wsn-network-helper.cc to use single Cc2420Helper
instance instead of separate instances for ground/UAV nodes.
Fixes all UAV-to-ground communication.

Related: HANDOFF_CC2420_FIX.md
```

### DO NOT commit

- Build artifacts: `build/`, `CMakeFiles/`, `*.o`, `*.a`
- Generated data: `data/results/` (add to .gitignore)
- IDE files: `.vscode/`, `.idea/`, `*.swp`
- Dependencies: External libraries

---

## 7. Code Style Rules

### Header Organization

```cpp
#ifndef WSN_UAV_MODEL_FRAGMENT_H
#define WSN_UAV_MODEL_FRAGMENT_H

#include <cstdint>
#include <vector>
#include <map>
#include "ns3/core-module.h"  // Only if using ns3

namespace ns3::wsn::uav {

// ... declarations

}  // namespace ns3::wsn::uav

#endif
```

### Namespace Rules

- **No ns3 dependency:** `namespace ns3::wsn::uav`
- **With ns3 dependency:** `namespace ns3::wsn::uav` inside ns3 context
- **Avoid global namespace** except entry points (main)

### Naming Conventions

```cpp
// Classes: PascalCase
class FragmentModel { };
class ConfidenceModel { };

// Functions: camelCase
void sendPacket();
double calculateConfidence();

// Constants: UPPER_SNAKE_CASE
constexpr double GRID_SPACING = 20.0;
constexpr uint32_t MAX_FRAGMENTS = 1000;

// Member variables: m_camelCase
class MyClass {
    uint32_t m_nodeId;
    double m_confidence;
};

// Local variables: camelCase
uint32_t nodeId = 0;
double confidence = 0.5;
```

---

## 8. Testing Before Committing

### Checklist Before Each Commit

- [ ] Code compiles: `python3.10 ./ns3 build wsn-uav && python3.10 ./ns3 build`
- [ ] No linker errors (all .cc files listed in CMakeLists.txt)
- [ ] No runtime crashes (test with at least one scenario)
- [ ] Output files generated (check data/results/)
- [ ] No debug output left behind (remove std::cout spam)

### Quick Test Commands

```bash
# Build
python3.10 ./ns3 build wsn-uav && python3.10 ./ns3 build

# Test scenario-0
./build/scenario-0-radio-test

# Test scenario-1 (small grid, 100s runtime)
./build/scenario-1-single-uav --gridSize=10 --simTime=100

# Check output
ls -la data/results/scenario-1/run-001/
```

---

## 9. Documentation Rules

### What to Document

1. **Every algorithm:** Explain the math/logic with references
2. **Every parameter:** What does it do, default value, range
3. **Every callback:** When is it called, what does it receive
4. **Build requirements:** Dependencies, Python version, etc.

### What NOT to Overcomplicate

- Architecture diagrams (you'll redesign anyway)
- Multi-page implementation plans
- Line-by-line code comments (use clear variable names instead)

### Documentation Format

```markdown
# Title

## Overview
One sentence describing purpose

## Usage
```cpp
// Code example
```

## Parameters
| Name | Type | Default | Effect |
|------|------|---------|--------|

## Notes
- Important detail 1
- Important detail 2
```

---

## 10. Quick Reference: Full Build-Test Cycle

```bash
# 1. Initial Setup (one time)
cd ns-3-dev-git-ns-3.46
./ns3 configure --enable-examples --enable-modules=wsn-uav

# 2. Edit files in src/wsn-uav/
vim src/wsn-uav/models/common/types.h
vim src/wsn-uav/examples/scenario-0-radio-test.cc
vim src/wsn-uav/CMakeLists.txt

# 3. Build
./ns3 build

# 4. Test
./build/scenario-0-radio-test
./build/scenario-1-single-uav --gridSize=10

# 5. Check results
ls data/results/scenario-1/run-001/
cat data/results/scenario-1/run-001/metrics.csv

# 6. Commit
git add src/wsn-uav/
git commit -m "[module] Description"
```

**Key Points:**
- Configure: `--enable-modules=wsn-uav` (ONLY this module)
- Build: `./ns3 build` (builds configured modules + examples)
- Python 3.10 must be in PATH (or aliased)

---

## Summary: The Rules in One Page

| Rule | Command/Example |
|------|-----------------|
| Configure only wsn-uav module | `./ns3 configure --enable-examples --enable-modules=wsn-uav` |
| Build (not build wsn-uav) | `./ns3 build` |
| Use Python 3.10 only | `which python3.10` → ensure in PATH |
| Single Cc2420Helper for all nodes | One instance, shared channel |
| List ALL .cc files in CMakeLists.txt | `find src/wsn-uav -name "*.cc"` |
| Use GRID_SPACING = 20.0 | In `models/common/parameters.h` |
| Create output directories explicitly | `std::filesystem::create_directories()` |
| Follow pixel-stride algorithm exactly | Don't modify fragment generation |
| Document with math/references | Explain the WHY, not just WHAT |
| Test before committing | `./build/scenario-0-radio-test` |

