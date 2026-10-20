"""Run a shell command and keep its log as Markdown (CLAUDE.md §8 items 94, 106).

    python3 tools/runlog.py logs/<YYYY-MM-DD_HHMM>-<name>/<step>.md "<command>" [--cwd DIR] [--title TEXT]

The command runs in bash (from --cwd, default the current directory); its output is shown live and written to
the .md file with the command, working directory, start and end time, duration and exit code. The exit code is
passed on.
"""
import argparse, datetime, os, subprocess, sys, time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("command")
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    t0, start = time.time(), datetime.datetime.now()
    p = subprocess.Popen(["bash", "-c", a.command], cwd=a.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = []
    for line in p.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        out.append(line)
    rc = p.wait()
    os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
    fence = "````" if any("```" in l for l in out) else "```"
    with open(a.log, "w") as f:
        f.write(f"# {a.title or os.path.splitext(os.path.basename(a.log))[0]}\n\n")
        f.write(f"- Bắt đầu: {start:%Y-%m-%d %H:%M:%S}, chạy {time.time() - t0:.0f} s, mã thoát {rc}\n")
        f.write(f"- Thư mục: `{os.path.abspath(a.cwd)}`\n\n**Lệnh**\n\n```bash\n{a.command.strip()}\n```\n\n")
        f.write(f"**Kết quả**\n\n{fence}text\n{''.join(out).rstrip() or '(không có đầu ra)'}\n{fence}\n")
    sys.exit(rc)


if __name__ == "__main__":
    main()
