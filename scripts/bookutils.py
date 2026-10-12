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


# ---------------------------------------------------------------------------
# Model diagrams: contact maps and rule diagrams
#
# BioNetGen's visualize() action writes these diagrams as GraphML for the yEd
# editor, without a layout (Sekar, Tapia, and Faeder 2017). The functions
# below read that GraphML and lay it out with Graphviz, so the diagrams are
# generated from the model files whenever the book is built. Each molecule is
# drawn as one node, with a port for each component and internal state, so
# that bonds and operations attach to the right site.

_NS = {"g": "http://graphml.graphdrawing.org/xmlns", "y": "http://www.yworks.com/xml/graphml"}
_OP_LABELS = {"AddBond": "add bond", "DeleteBond": "delete bond",
              "ChangeState": "change state", "AddMol": "add molecule",
              "DeleteMol": "delete molecule"}
_MOL_FILL, _COMP_FILL, _STATE_FILL = "#D9DEE5", "#FFFFFF", "#F6D57A"
_OP_FILL, _OP_LINE, _OP_EDGE = "#B9A3E3", "#7A5FC0", "#5B3FA8"
GENERATED = ROOT / "figures" / "generated"


def bng_visualize(chapter, name, kind):
    """Run BioNetGen's visualize action and return the GraphML path.

    ``kind`` is "contactmap" or "ruleviz_operation". Output is cached in a
    temporary folder, as for ``bng_xml``.
    """
    import os, shutil, subprocess, sys, tempfile
    exe = shutil.which("bionetgen") or os.path.join(os.path.dirname(sys.executable), "bionetgen")
    out = Path(tempfile.gettempdir()) / "bookutils-viz" / chapter
    out.mkdir(parents=True, exist_ok=True)
    text = model_path(chapter, name).read_text()
    model = text[: text.index("end model") + len("end model")]
    src = out / f"{name}.bngl"
    src.write_text(model + f'\nvisualize({{type=>"{kind}"}})\n')
    subprocess.run([exe, "run", "-i", str(src), "-o", str(out)], check=True, capture_output=True)
    return out / f"{name}_{kind}.graphml"


def _graphml_node(node):
    label = node.find("g:data/*/y:NodeLabel", _NS)
    if label is None:
        label = node.find("g:data/*/y:Realizers/*/y:NodeLabel", _NS)
    fill = node.find("g:data//y:Fill", _NS)
    sub = node.find("g:graph", _NS)
    return {"id": node.get("id"), "label": label.text if label is not None else None,
            "fill": fill.get("color") if fill is not None else None,
            "children": [_graphml_node(c) for c in sub.findall("g:node", _NS)] if sub is not None else []}


def _read_graphml(path):
    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot()
    nodes = [_graphml_node(n) for n in root.find("g:graph", _NS).findall("g:node", _NS)]
    edges = []
    for e in root.iter("{%s}edge" % _NS["g"]):
        arrows = e.find(".//y:Arrows", _NS)
        edges.append({"source": e.get("source"), "target": e.get("target"),
                      "arrow": arrows is not None and arrows.get("target") != "none"})
    return nodes, edges


def _molecule_order(chapter, name):
    """Components and states of each molecule type, in declaration order."""
    import re
    text = model_path(chapter, name).read_text()
    block = text.split("begin molecule types")[1].split("end molecule types")[0]
    order = {}
    for line in block.splitlines():
        line = line.split("#")[0].strip()
        m = re.match(r"(\w+)\((.*)\)", line)
        if m:
            comps = [c.split("~") for c in m.group(2).split(",") if c]
            order[m.group(1)] = ([c[0] for c in comps], {c[0]: c[1:] for c in comps})
        elif line:
            order[line.rstrip("()")] = ([], {})
    return order


def _is_operation(node):
    return node["label"] in _OP_LABELS


def _molecule_label(mol, order, ports, name):
    """Graphviz HTML label for a molecule; records the port of each part."""
    import html
    comp_order, state_order = order.get(mol["label"], ([], {}))
    rank = {c: i for i, c in enumerate(comp_order)}
    comps = sorted((c for c in mol["children"] if not _is_operation(c)),
                   key=lambda c: rank.get(c["label"], len(rank)))
    cells = []
    for i, comp in enumerate(comps):
        port = f"c{i}"
        ports[comp["id"]] = f"{name}:{port}"
        srank = {s: j for j, s in enumerate(state_order.get(comp["label"], []))}
        states = sorted((s for s in comp["children"] if not _is_operation(s)),
                        key=lambda s: srank.get(s["label"], len(srank)))
        label = html.escape(comp["label"])
        if not states:
            cells.append(f'<TD PORT="{port}" BGCOLOR="{_COMP_FILL}" BORDER="1" STYLE="rounded">{label}</TD>')
            continue
        inner = ""
        for j, s in enumerate(states):
            ports[s["id"]] = f"{name}:{port}s{j}"
            inner += (f'<TD PORT="{port}s{j}" BGCOLOR="{_STATE_FILL}" BORDER="1" STYLE="rounded">'
                      f'<FONT POINT-SIZE="10">{html.escape(s["label"])}</FONT></TD>')
        cells.append(f'<TD PORT="{port}" BGCOLOR="{_COMP_FILL}" BORDER="1" STYLE="rounded">'
                     f'<TABLE BORDER="0" CELLSPACING="2" CELLPADDING="1">'
                     f'<TR><TD COLSPAN="{len(states)}">{label}</TD></TR><TR>{inner}</TR></TABLE></TD>')
    ports[mol["id"]] = name
    head = f'<TR><TD COLSPAN="{max(len(cells), 1)}"><B>{html.escape(mol["label"])}</B></TD></TR>'
    body = f"<TR>{''.join(cells)}</TR>" if cells else ""
    return (f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="3" CELLPADDING="3" '
            f'STYLE="rounded" BGCOLOR="{_MOL_FILL}">{head}{body}</TABLE>>')


def _dot_lines(rankdir):
    return ["graph G {",
            f'  graph [rankdir={rankdir}, fontname="Helvetica", nodesep=0.35, ranksep=0.5, '
            f'overlap=false, splines=true, sep="+12", start=1, bgcolor="transparent"];',
            '  node [shape=plain, fontname="Helvetica", fontsize=12];',
            "  edge [penwidth=1.3];"]


def _render(dot_source, stem, engine):
    """Write figures/generated/<stem>.svg and .pdf; return the path for Markdown."""
    import shutil, subprocess
    exe = shutil.which(engine)
    if exe is None:
        raise RuntimeError(f"Graphviz ({engine}) is required to draw model diagrams")
    GENERATED.mkdir(parents=True, exist_ok=True)
    for fmt in ("svg", "pdf"):
        subprocess.run([exe, f"-T{fmt}", "-o", str(GENERATED / f"{stem}.{fmt}")],
                       input=dot_source, text=True, check=True, capture_output=True)
    return f"../figures/generated/{stem}"


def contact_map(chapter, name, stem=None):
    """Draw the contact map of a model.

    Returns the image path (without extension, so that the HTML and PDF
    builds pick SVG and PDF) and counts of molecule types, components, and
    possible bonds.
    """
    nodes, edges = _read_graphml(bng_visualize(chapter, name, "contactmap"))
    order = _molecule_order(chapter, name)
    rank = {m: i for i, m in enumerate(order)}
    ports, lines = {}, _dot_lines("LR")
    for i, mol in enumerate(sorted(nodes, key=lambda m: rank.get(m["label"], len(rank)))):
        lines.append(f"  m{i} [label={_molecule_label(mol, order, ports, f'm{i}')}];")
    for e in edges:
        lines.append(f'  {ports[e["source"]]} -- {ports[e["target"]]} [color="#333333", len=0.3];')
    lines.append("}")
    path = _render("\n".join(lines), stem or f"{chapter}-{name}-contactmap", "neato")
    n_components = sum(len(m["children"]) for m in nodes)
    return {"path": path, "molecules": len(nodes), "components": n_components, "bonds": len(edges)}


def rule_diagram(chapter, name, rule, stem=None):
    """Draw one rule as a compact rule diagram; return the image path.

    Molecules, components, and states in the rule's reactant patterns are
    drawn as in the contact map. Gray lines are bonds required as context,
    a "+" marks a bond to an unspecified partner, and purple nodes are the
    operations the rule performs, with arrows to the parts they change.
    """
    nodes, edges = _read_graphml(bng_visualize(chapter, name, "ruleviz_operation"))
    order = _molecule_order(chapter, name)
    rnode = next(n for n in nodes if n["label"] == rule)
    ports, lines, ops = {}, _dot_lines("TB"), []

    def collect(n):
        for c in n["children"]:
            if _is_operation(c):
                ops.append(c)
            collect(c)
    collect(rnode)
    mols, wildcards = [], []
    for i, child in enumerate(rnode["children"]):
        if _is_operation(child):
            continue
        node = f"m{i}"
        if child["label"] == "+":
            ports[child["id"]] = node
            wildcards.append(node)
            lines.append(f'  {node} [shape=circle, label="+", width=0.25, fixedsize=true, fontsize=11, '
                         f'style=filled, fillcolor="#EEEEEE", color="#999999"];')
        else:
            mols.append(node)
            lines.append(f"  {node} [label={_molecule_label(child, order, ports, node)}];")
    for j, op in enumerate(ops):
        ports[op["id"]] = f"op{j}"
        lines.append(f'  op{j} [shape=box, style="rounded,filled", fillcolor="{_OP_FILL}", '
                     f'color="{_OP_LINE}", fontsize=11, label="{_OP_LABELS[op["label"]]}"];')
    # One row in pattern order, with each "+" just before the molecule it is attached to.
    owner = {}
    for e in edges:
        for a, b in ((e["source"], e["target"]), (e["target"], e["source"])):
            if ports.get(a) in wildcards and ":" in ports.get(b, ""):
                owner[ports[a]] = ports[b].split(":")[0]
    row = []
    for m in mols:
        row += [w for w, o in owner.items() if o == m] + [m]
    row += [w for w in wildcards if w not in row]
    lines.append("  {rank=same; " + "; ".join(row) + ";}")
    lines += [f"  {a} -- {b} [style=invis];" for a, b in zip(row, row[1:])]
    for e in edges:
        if e["source"] in ports and e["target"] in ports:
            s, t = ports[e["source"]], ports[e["target"]]
            style = f'dir=forward, color="{_OP_EDGE}", arrowsize=0.7' if e["arrow"] else 'color="#555555"'
            lines.append(f"  {s} -- {t} [{style}];")
    lines.append("}")
    return _render("\n".join(lines), stem or f"{chapter}-{name}-{rule}", "dot")


def _parse_species(text):
    """Parse a BNGL species or molecule-type string into molecules.

    Returns a list of (name, [(component, [states], bond)]) where bond is a
    bond label or None. A molecule type lists several states per component.
    """
    import re
    molecules = []
    for mol in text.strip().split("."):
        m = re.match(r"\s*(\w+)(?:\((.*)\))?\s*$", mol)
        comps = []
        for c in filter(None, (m.group(2) or "").split(",")):
            cm = re.match(r"(\w+)((?:~\w+)*)(?:!(\w+|\+|\?))?$", c.strip())
            states = [s for s in cm.group(2).split("~") if s]
            comps.append((cm.group(1), states, cm.group(3)))
        molecules.append((m.group(1), comps))
    return molecules


def _table_label(name, comps, order=None):
    """HTML label for a parsed molecule, in the contact-map style."""
    import html
    if order and name in order:
        rank = {c: i for i, c in enumerate(order[name][0])}
        comps = sorted(comps, key=lambda c: rank.get(c[0], len(rank)))
    cells = []
    for i, (comp, states, _) in enumerate(comps):
        label = html.escape(comp)
        if not states:
            cells.append(f'<TD PORT="c{i}" BGCOLOR="{_COMP_FILL}" BORDER="1" STYLE="rounded">{label}</TD>')
            continue
        inner = "".join(f'<TD BGCOLOR="{_STATE_FILL}" BORDER="1" STYLE="rounded">'
                        f'<FONT POINT-SIZE="10">{html.escape(s)}</FONT></TD>' for s in states)
        cells.append(f'<TD PORT="c{i}" BGCOLOR="{_COMP_FILL}" BORDER="1" STYLE="rounded">'
                     f'<TABLE BORDER="0" CELLSPACING="2" CELLPADDING="1">'
                     f'<TR><TD COLSPAN="{len(states)}">{label}</TD></TR><TR>{inner}</TR></TABLE></TD>')
    head = f'<TR><TD COLSPAN="{max(len(cells), 1)}"><B>{html.escape(name)}</B></TD></TR>'
    body = f"<TR>{''.join(cells)}</TR>" if cells else ""
    return comps, (f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="3" CELLPADDING="3" '
                   f'STYLE="rounded" BGCOLOR="{_MOL_FILL}">{head}{body}</TABLE>>')


def molecule_type_diagram(chapter, name, molecule, stem=None):
    """Draw a molecule type, with all its allowed states, from a model file."""
    order = _molecule_order(chapter, name)
    comps, states = order[molecule]
    _, label = _table_label(molecule, [(c, states[c], None) for c in comps])
    lines = _dot_lines("TB") + [f"  m0 [label={label}];", "}"]
    return _render("\n".join(lines), stem or f"{chapter}-{name}-{molecule}-type", "dot")


def species_diagram(species, stem, chapter=None, name=None):
    """Draw one species: molecules, the state of each component, and bonds.

    ``species`` is a BNGL species string, for example one taken from
    ``model.species_names``. If a model is given, components are drawn in
    the order of its molecule types. Molecules are ranked from top to
    bottom in the order they are first reached through bonds.
    """
    order = _molecule_order(chapter, name) if chapter else None
    lines, ends = _dot_lines("TB"), {}
    for i, (mol, comps) in enumerate(_parse_species(species)):
        comps, label = _table_label(mol, comps, order)
        lines.append(f"  m{i} [label={label}];")
        for j, (_, _, bond) in enumerate(comps):
            if bond and bond not in "+?":
                ends.setdefault(bond, []).append(f"m{i}:c{j}")
    for bond in sorted(ends, key=lambda b: int(b) if b.isdigit() else b):
        a, b = sorted(ends[bond], key=lambda e: int(e.split(":")[0][1:]))
        # bonds leave the bottom of the upper molecule and enter the top of the lower
        lines.append(f'  {a}:s -- {b}:n [color="#333333"];')
    lines.append("}")
    return _render("\n".join(lines), stem, "dot")
