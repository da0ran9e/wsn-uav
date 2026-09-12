"""Build provenance, per AGENT-BRIEF 6.5.

For pure-Python experiments there is no compiled binary, so the role of
binary_mtime/binary_size is taken by the computing SOURCE TREE: we stamp
mtime+size of the module that computes the numbers (src/screening/model.py)
and a sha256 over every tracked .py file. assert_one_build.py refuses to
aggregate runs whose stamps disagree, which is the same guarantee the brief
asks for: behaviour cannot change without the stamp changing.
"""
from __future__ import annotations

import hashlib
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def source_sha256() -> str:
    h = hashlib.sha256()
    for f in sorted(list((ROOT / "src").rglob("*.py")) + list((ROOT / "tools").rglob("*.py"))):
        h.update(f.relative_to(ROOT).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def config_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp(config_path: Path | None = None) -> dict:
    model = ROOT / "src" / "screening" / "model.py"
    st = model.stat()
    d = {
        "schema_version": SCHEMA_VERSION,
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": 1 if _git("status", "--porcelain") else 0,
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "binary_mtime": int(st.st_mtime),
        "binary_size": st.st_size,
        "binary_path": "src/screening/model.py",
        "source_sha256": source_sha256(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
    }
    if config_path is not None:
        d["config_path"] = str(Path(config_path).resolve().relative_to(ROOT))
        d["config_sha256"] = config_sha256(config_path)
    # Compact stamp carried on every data row. The full stamp lives in
    # config.txt; repeating two 64-char hashes per row would triple the size of
    # the committed CSVs for no extra guarantee.
    d["prov_id"] = hashlib.sha256(
        f'{d["schema_version"]}|{d["source_sha256"]}|{d.get("config_sha256","-")}'
        f'|{d["binary_mtime"]}|{d["binary_size"]}'.encode()).hexdigest()[:16]
    return d


def write_config_txt(path: Path, resolved: dict, config_path: Path | None = None) -> None:
    """config.txt: every resolved parameter, flattened, plus provenance."""
    lines = []
    def flat(prefix: str, obj) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                flat(f"{prefix}.{k}" if prefix else str(k), v)
        elif isinstance(obj, (list, tuple)):
            lines.append(f"{prefix}={','.join(str(x) for x in obj)}")
        else:
            lines.append(f"{prefix}={obj}")
    flat("", resolved)
    for k, v in stamp(config_path).items():
        lines.append(f"{k}={v}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n")


def write_env_txt(path: Path) -> None:
    def run(*c):
        try:
            return subprocess.run(c, capture_output=True, text=True, timeout=30).stdout.strip() or "ABSENT"
        except Exception:
            return "ABSENT"
    pkgs = {}
    for mod in ("numpy", "scipy", "yaml", "shapely", "pytest"):
        try:
            m = __import__(mod)
            pkgs[mod] = getattr(m, "__version__", "unknown")
        except ImportError:
            pkgs[mod] = "ABSENT"
    lines = [
        "# uav-screening-depth environment record (AGENT-BRIEF 4)",
        f"python_executable={sys.executable}",
        f"python_version={sys.version.split()[0]}",
        f"python3.10_version={run('/usr/bin/python3.10', '--version')}",
        f"cmake_version={run('cmake', '--version').splitlines()[0] if run('cmake','--version')!='ABSENT' else 'ABSENT'}",
        f"platform={platform.platform()}",
        f"cpu_count={os.cpu_count()}",
        *(f"pkg.{k}={v}" for k, v in pkgs.items()),
        "",
        "# --- Declared-but-absent tooling (AGENT-BRIEF 4 says these are available; they are NOT) ---",
        f"ns3_tree={'PRESENT' if Path('/home/user/ns3-dev').exists() else 'ABSENT'}  # blocks E3, E7",
        f"lkh_solver={run('which', 'LKH')}  # blocks E5 (ATSP)",
        "pecee=ABSENT  # blocks E2 (Phase-0 clustering adapter)",
        "# E0 is pure numerics and needs none of the above.",
        "",
        *(f"{k}={v}" for k, v in stamp().items()),
    ]
    Path(path).write_text("\n".join(lines) + "\n")
