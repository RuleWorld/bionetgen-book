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
    reactions = []
    for l in block("reactions"):
        body, _, rule = l.partition("#")
        f = body.split()
        side = lambda s: [] if s == "0" else [species[int(i) - 1] for i in s.split(",")]
        reactions.append((side(f[1]), side(f[2]), " ".join(f[3:]), rule.strip()))
    return species, reactions


def show_net(chapter, name, rules=None):
    """Print the reactions BioNetGen generates from a model, one per line.

    Use in a cell with ``#| output: asis``. ``rules`` limits the listing to
    reactions generated by the named rules.
    """
    _, reactions = generated_network(chapter, name)
    lines = []
    for lhs, rhs, rate, rule in reactions:
        base = rule.replace("_reverse_", "")
        if rules and base not in rules:
            continue
        lhs_s = " + ".join(lhs) if lhs else "0"
        rhs_s = " + ".join(rhs) if rhs else "0"
        label = f"{base}, reverse" if rule.startswith("_reverse_") else rule
        lines.append(f"{lhs_s} -> {rhs_s}  {rate}  [{label}]")
    print("```")
    print("\n".join(lines))
    print("```")
