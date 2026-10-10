"""Helpers used by the book's chapters: plot style and BNGL listings.

Chapters import this module in a hidden setup cell. Simulation code stays in
the chapters themselves so readers see every bngsim call.
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"

COLORS = ["#1B365D", "#C8102E", "#1F7A8C", "#D39B1E", "#3A7D44", "#5B6770"]

mpl.rcParams.update({
    "figure.figsize": (6.0, 3.4),
    "figure.dpi": 110,
    "axes.prop_cycle": mpl.cycler(color=COLORS),
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "legend.frameon": False,
    "lines.linewidth": 2.0,
    "savefig.bbox": "tight",
})


def model_path(chapter, name):
    """Path to a model file, e.g. model_path("ch01", "stat_step1_binding")."""
    return MODELS / chapter / f"{name}.bngl"


def _fence(lines):
    print("```bngl")
    print("\n".join(lines).rstrip())
    print("```")


def show_bngl(chapter, name, start=None, end=None, strip_header=True):
    """Print a model file (or a line range) as a BNGL code block.

    Use in a cell with ``#| output: asis``. ``start`` and ``end`` are
    substrings: the listing begins at the first line containing ``start`` and
    stops after the first following line containing ``end``.
    """
    lines = model_path(chapter, name).read_text().splitlines()
    if strip_header:
        while lines and (lines[0].startswith("#") or not lines[0].strip()):
            lines.pop(0)
    if start is not None:
        i = next(k for k, l in enumerate(lines) if start in l)
        lines = lines[i:]
    if end is not None:
        j = next(k for k, l in enumerate(lines) if end in l)
        lines = lines[: j + 1]
    _fence(lines)


def show_new(chapter, name):
    """Print only the lines marked as new in a cumulative step model.

    Step models mark additions with ``# new`` (parameters, molecule types,
    species, observables) or a ``(new)`` rule comment followed by the rule.
    Lines are grouped under their block headers.
    """
    lines = model_path(chapter, name).read_text().splitlines()
    out, block, take_next = [], None, False
    for line in lines:
        s = line.strip()
        if s.startswith("begin ") and s != "begin model":
            block, header_done = s, False
            continue
        if s.startswith("end ") and s != "end model":
            if block and header_done:
                out.append(s)
            block = None
            continue
        if block is None:
            continue
        keep = False
        if take_next:
            keep, take_next = True, False
        elif "(new)" in s:
            keep, take_next = True, True
            line = line.replace(" (new)", "")
        elif "# new" in s:
            keep = True
            line = line.replace("# new: ", "# ").replace("  # new", "").replace(" # new", "")
        if keep:
            if not header_done:
                out.append(block)
                header_done = True
            out.append(line.rstrip())
    _fence(out)


def show_lines(chapter, name, *keys, comments=True):
    """Print the lines of a model that start with any of ``keys``.

    Matching is on the stripped line, so ``"Sbind:"`` selects the rule labeled
    Sbind and ``"R("`` selects a molecule-type or species line for R. With
    ``comments=True`` a comment line directly above a match is included, and
    end-of-line comments are kept.
    """
    lines = model_path(chapter, name).read_text().splitlines()
    out = []
    for i, line in enumerate(lines):
        s = line.strip()
        if any(s.startswith(k) for k in keys):
            prev = lines[i - 1].strip() if i > 0 else ""
            if comments and prev.startswith("#") and (not out or out[-1] != lines[i - 1].rstrip()):
                out.append(lines[i - 1].rstrip())
            out.append(line.rstrip() if comments else line.split("#")[0].rstrip())
    _fence([l[2:] if l.startswith("  ") else l for l in out])


def rule_count(chapter, name):
    """Number of reaction rules (labeled lines) in a model file."""
    import re
    text = model_path(chapter, name).read_text()
    block = text.split("begin reaction rules")[1].split("end reaction rules")[0]
    return sum(1 for l in block.splitlines() if re.match(r"\s*[A-Za-z0-9_]+:", l))


def generated_network(chapter, name):
    """Run BioNetGen on a model and return its species and reactions.

    Returns (species, reactions), where species is a list of species strings
    and reactions is a list of (reactants, products, rate, rule) tuples with
    species written out in full.
    """
    import os, shutil, subprocess, sys, tempfile
    exe = shutil.which("bionetgen") or os.path.join(os.path.dirname(sys.executable), "bionetgen")
    with tempfile.TemporaryDirectory() as d:
        subprocess.run([exe, "run", "-i", str(model_path(chapter, name)), "-o", d],
                       check=True, capture_output=True)
        net = open(os.path.join(d, f"{name}.net")).read()
    block = lambda b: net.split(f"begin {b}")[1].split(f"end {b}")[0].strip().splitlines()
    species = [l.split()[1] for l in block("species") if l.strip()]
    params = {}
    for l in block("parameters"):
        f = l.split("#")[0].split()
        if len(f) >= 3:
            try:
                params[f[1]] = eval(f[2].replace("^", "**"), {}, params)
            except Exception:
                pass
    reactions = []
    for l in block("reactions"):
        body, _, comment = l.partition("#")
        f = body.split()
        side = lambda s: [] if s == "0" else [species[int(i) - 1] for i in s.split(",")]
        rule, *extra = comment.split()
        rate = " ".join(f[3:])
        conv = next((e.split("=", 1)[1] for e in extra if e.startswith("unit_conversion=")), None)
        if conv:
            rate = _scaled_rate(rate, conv, params)
        reactions.append((side(f[1]), side(f[2]), rate, rule))
    return species, reactions


def _scaled_rate(rate, conv, params):
    """Rewrite a compartment-scaled rate such as 1.66e-06*kon, with
    unit_conversion=1/(V_CP*NA_pL), as kon/(V_CP*NA_pL), keeping any
    statistical factor (2*kon/(V_CP*NA_pL))."""
    import re
    m = re.match(r"([0-9.eE+-]+)\*(.+)$", rate)
    if not m or not conv.startswith("1/"):
        return rate
    factor = float(m.group(1)) / eval(conv.replace("^", "**"), {}, params)
    denom = conv[2:]
    if not denom.startswith("("):
        denom = f"({denom})"
    denom = re.sub(r"\(\(\((\w+)\*(\w+)\)\*(\w+)\)\*(\w+)\)", r"(\1*\2*\3*\4)", denom)
    n = round(factor)
    prefix = "" if abs(factor - 1) < 1e-6 else (f"{n}*" if abs(factor - n) < 1e-6 else f"{factor:g}*")
    return f"{prefix}{m.group(2)}/{denom}"


def show_net(chapter, name, rules=None):
    """Print the reactions BioNetGen generates from a model, one per line.

    Use in a cell with ``#| output: asis``. ``rules`` limits the listing to
    reactions generated by the named rules.
    """
    _, reactions = generated_network(chapter, name)
    lines = []
    for lhs, rhs, rate, rule in reactions:
        base = rule.replace("_reverse_", "")
        if rules and not set(base.split(",")) & set(rules):
            continue
        lhs_s = " + ".join(lhs) if lhs else "0"
        rhs_s = " + ".join(rhs) if rhs else "0"
        label = f"{base}, reverse" if rule.startswith("_reverse_") else rule
        lines.append(f"{lhs_s} -> {rhs_s}  {rate}  [{label}]")
    print("```bngl")
    print("\n".join(lines))
    print("```")


def bng_xml(chapter, name):
    """Write the BNG-XML file for a model and return its path.

    Network-free simulators read the model's rules from this XML file rather
    than from a generated network. The file is written by BioNetGen's
    ``writeXML`` action into a cache folder that persists between calls.
    """
    import os, re, shutil, subprocess, sys, tempfile
    exe = shutil.which("bionetgen") or os.path.join(os.path.dirname(sys.executable), "bionetgen")
    out = Path(tempfile.gettempdir()) / "bookutils-xml" / chapter
    out.mkdir(parents=True, exist_ok=True)
    text = model_path(chapter, name).read_text()
    model = text[: text.index("end model") + len("end model")]
    src = out / f"{name}.bngl"
    src.write_text(model + "\nwriteXML()\n")
    subprocess.run([exe, "run", "-i", str(src), "-o", str(out)], check=True, capture_output=True)
    return out / f"{name}.xml"


def aggregate_sizes(species_file, molecule):
    """Number of ``molecule`` in each complex listed in a .species file.

    Returns one entry per complex (a species with count n contributes n
    entries), so ``sizes.max()`` is the size of the largest aggregate.
    """
    import numpy as np
    sizes = []
    for line in Path(species_file).read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            pattern, count = line.rsplit(None, 1)
            sizes += [pattern.count(f"{molecule}(")] * int(float(count))
    return np.array(sizes)
