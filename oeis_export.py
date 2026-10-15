"""Export OEIS_SUBMISSION.md to paste-ready plain text.

Writes oeis/submission.txt (one block per sequence, each form field on
unwrapped lines, Data cut to the OEIS 260-character limit at a term boundary)
and the b-files oeis/b<A-number>.txt, named from the section headings.
"""

import os
import re
import textwrap

SRC = "OEIS_SUBMISSION.md"
OUT = "oeis"
DATA_LIMIT = 260

md = open(SRC, encoding="utf-8").read()
body, bfiles = md.split("## b-file data")
seqs = re.split(r"^## Sequence \d+ \((A\d+)\): ", body, flags=re.M)[1:]
seqs = [(seqs[i], seqs[i + 1]) for i in range(0, len(seqs), 2)]  # (A-number, text)
bparts = re.split(r"^### Sequence \d+ ", bfiles, flags=re.M)[1:]


def fields(section):
    """Map field name -> raw markdown text."""
    out, name, buf = {}, None, []
    for line in section.splitlines():
        m = re.match(r"\*\*(\w[\w ()-]*):\*\*\s*(.*)", line)
        if m:
            if name:
                out[name] = "\n".join(buf).strip()
            name, buf = m.group(1), [m.group(2)]
        else:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf).strip()
    return {k: re.sub(r"\n---\s*$", "", v).strip() for k, v in out.items()}


def unwrap(text):
    """Join wrapped lines; keep bullets/paragraphs as separate lines."""
    paras, cur = [], []
    for line in text.splitlines():
        if not line.strip():
            if cur:
                paras.append(" ".join(cur))
                cur = []
        elif line.startswith("- ") and cur:
            paras.append(" ".join(cur))
            cur = [line[2:].strip()]
        else:
            cur.append(line.strip()[2:].strip() if line.startswith("- ") else line.strip())
    if cur:
        paras.append(" ".join(cur))
    return "\n".join(paras)


def cut_data(data):
    terms = [t.strip() for t in data.replace("\n", " ").split(",") if t.strip()]
    kept = []
    for t in terms:
        if len(", ".join(kept + [t])) > DATA_LIMIT:
            break
        kept.append(t)
    return ", ".join(kept), len(kept), len(terms)


os.makedirs(OUT, exist_ok=True)
blocks = []
anums = []
for i, (anum, sec) in enumerate(seqs, 1):
    anums.append(anum)
    title = f"{anum}: " + sec.splitlines()[0].strip()
    f = fields(sec)
    data, nkept, ntotal = cut_data(f["Data"])
    if "Program (Python)" in f:
        prog = re.search(r"```python\n(.*?)```", f["Program (Python)"], re.S).group(1).rstrip()
        prog1 = prog
    else:  # quadrant version: same walk DP without the full-plane conversion
        prog = re.sub(r"\n    r = .*\n    wall = .*\n    return .*", "\n    return Q", prog1)
    lines = [
        "=" * 72,
        f"SEQUENCE {i}: {title}",
        "=" * 72,
        "",
        "[Name]",
        unwrap(f["Name"]),
        "",
        "[Offset]",
        f["Offset"],
        "",
        f"[Data]  ({nkept} of {ntotal} terms; the rest are in b{anum[1:]}.txt)",
        data,
        "",
        "[Comments]  (one comment per line)",
        unwrap(f["Comments"]),
        "",
    ]
    if "Formula" in f:
        lines += ["[Formula]", unwrap(f["Formula"]), ""]
    if "Example" in f:
        lines += ["[Example]", unwrap(f["Example"]), ""]
    lines += [
        "[Program]",
        "(Python)",
        prog,
        "",
        "[Crossrefs]",
        "Cf. " + unwrap(f["Crossrefs"]).rstrip(".") + ".",
        "",
        "[Keywords]",
        f["Keywords"],
        "",
        "",
    ]
    blocks.append("\n".join(lines))

open(f"{OUT}/submission.txt", "w", encoding="utf-8").write(
    "OEIS submission text, generated from OEIS_SUBMISSION.md by oeis_export.py.\n"
"\n"
    + "".join(blocks))

for i, part in enumerate(bparts, 1):
    rows = re.findall(r"^(\d+) (\d+)$", part, re.M)
    name = f"b{anums[i - 1][1:]}.txt"
    open(f"{OUT}/{name}", "w").write("".join(f"{n} {v}\n" for n, v in rows))
    print(f"{name}: {len(rows)} rows")
print("wrote", f"{OUT}/submission.txt")
