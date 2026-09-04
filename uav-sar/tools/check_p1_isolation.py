"""Fail if the new Phase-1 subtree reaches into the old system.

The old and new systems model the SAME THINGS in different ways -- local
evidence, reference data, cell leadership, coverage. When both are linked into
one binary, an old idea reaches the new pipeline through an include and nothing
complains: two kAlertThresholds on two different scales compile fine.

So the separation is a TEST, not a discipline. models/p1/ may include only its
own headers and the C++ standard library. Nothing from models/common/,
models/application/, models/network/ or helper/. If the new system needs
something the old one has, it gets its own version and a check that the two
agree -- that is a verified duplicate, which is safe, rather than a shared
symbol, which is not.

    python3 tools/check_p1_isolation.py [P1DIR]
"""
import os, re, sys

INCLUDE = re.compile(r'^\s*#\s*include\s*"([^"]+)"')


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "models/p1"
    own = set(os.listdir(root)) if os.path.isdir(root) else set()
    if not own:
        print(f"FAIL: {root} is empty or missing")
        return 1
    bad, n = [], 0
    for name in sorted(own):
        if not name.endswith((".h", ".cc")):
            continue
        path = os.path.join(root, name)
        for i, line in enumerate(open(path), 1):
            m = INCLUDE.match(line)
            if not m:
                continue
            n += 1
            inc = m.group(1)
            if os.path.basename(inc) not in own or "/" in inc:
                bad.append(f"{path}:{i}: reaches outside the subtree -> {inc}")
    for b in bad:
        print("FAIL " + b)
    print(f"{'FAIL' if bad else 'OK'}: {len(own)} files, {n} local includes, "
          f"{len(bad)} escapes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
