"""Native BioNetGen fixtures for the BNGL reference and its semantic tests.

Temporary output directories keep builds away from shared source files.
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def native_model(name):
    """Run an appendix model, returning text exports and named data columns."""
    executable = Path(sys.executable).parent / "bionetgen"
    source = ROOT / "models" / "appendix_b" / f"{name}.bngl"
    with tempfile.TemporaryDirectory(prefix="bngl-reference-") as directory:
        process = subprocess.run(
            [str(executable), "run", "-i", str(source), "-o", directory],
            capture_output=True, text=True, timeout=120,
        )
        log = process.stdout + process.stderr
        if process.returncode or re.search(r"\b(?:ABORT|ERROR)\b", log):
            raise RuntimeError(f"BioNetGen failed for {name}:\n{log}")
        texts, data = {}, {}
        for path in Path(directory).iterdir():
            if path.suffix in (".net", ".xml", ".scan", ".gml", ".graphml", ".bngl", ".m"):
                texts[path.name] = path.read_text()
            if path.suffix in (".gdat", ".cdat", ".fdat"):
                header = path.read_text().splitlines()[0].lstrip("#").split()
                values = np.loadtxt(path, comments="#", ndmin=2)
                data[path.name] = dict(zip(header, values.T))
        version = re.search(r"Created by BioNetGen ([^\n]+)", texts[f"{name}.net"]).group(1)
        return {"texts": texts, "data": data, "version": version, "log": log}
