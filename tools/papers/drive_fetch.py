"""List and download the PDFs of a PUBLIC Google Drive folder (link sharing on) into a local folder.

    python3 tools/papers/drive_fetch.py FOLDER_URL OUTDIR

Writes OUTDIR/<name>.pdf for each file (skips files already there) and OUTDIR/files.tsv (drive id, name).
Only the first page of the folder listing is parsed (enough for a few hundred files); private folders return nothing.
Keep OUTDIR outside the repo (scratchpad): the PDFs are not committed (research_notes/literature/METHOD-vi.md).
"""
import html, os, re, subprocess, sys

url, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
page = subprocess.run(["curl", "-s", "-L", "-m", "60", url], capture_output=True, text=True).stdout
files = []
for m in re.finditer(r'data-id="([A-Za-z0-9_-]{20,})"', page):
    n = re.search(r'data-tooltip="([^"]+?\.pdf) PDF"', page[m.end():m.end() + 6000])
    if n and (m.group(1), html.unescape(n.group(1))) not in files:
        files.append((m.group(1), html.unescape(n.group(1))))
with open(os.path.join(out, "files.tsv"), "w") as f:
    for i, n in files:
        f.write(f"{i}\t{n}\n")
for i, n in files:
    p = os.path.join(out, n)
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        subprocess.run(["curl", "-s", "-L", "-m", "120", "-o", p, f"https://drive.google.com/uc?export=download&id={i}"])
    print(f"{os.path.getsize(p):>9}  {n}")
print(f"{len(files)} files")
