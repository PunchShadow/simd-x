#!/usr/bin/env python3
"""
Utility to turn a SNAP edge-list (.txt) into the CSR binaries that SIMD-X expects.

The output matches the layout consumed by lib/graph.hpp:
  - <prefix>.mtx_beg_pos.bin : int64_t array with (vertex_count + 1) entries
  - <prefix>.mtx_csr.bin     : int64_t array with edge_count entries

Example:
    python3 snap_to_simdx.py \
        --input ../../datasets/SNAP/test/test_small.ungraph.txt \
        --output-prefix ../../datasets/SNAP/test/test_small \
        --undirected auto
"""

from __future__ import annotations

import argparse
import os
import sys
from array import array
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, List


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the SNAP *.txt edge-list file.",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Output prefix. Files '<prefix>.mtx_beg_pos.bin' and '<prefix>.mtx_csr.bin' are created.",
    )
    parser.add_argument(
        "--undirected",
        choices=("auto", "true", "false"),
        default="auto",
        help="Treat the input as undirected (duplicate edges in both directions). "
        "'auto' enables this when the filename contains 'ungraph' or 'undirected'.",
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Sort adjacency lists for deterministic binaries (slower for large graphs).",
    )
    parser.add_argument(
        "--weight-value",
        type=int,
        default=None,
        help="If set, also emit '<prefix>.mtx_weight.bin' filled with this constant (useful for"
        " BFS/SSSP runs that expect a weight buffer).",
    )
    return parser.parse_args()


def _detect_undirected(path: Path, mode: str) -> bool:
    if mode == "true":
        return True
    if mode == "false":
        return False
    lower = path.name.lower()
    return "ungraph" in lower or "undirected" in lower or "sym" in lower


def _write_binary(values: List[int], out_path: Path) -> None:
    arr = array("q", values)
    with out_path.open("wb") as fh:
        arr.tofile(fh)


def main() -> None:
    args = _parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        sys.exit(f"Input file does not exist: {input_path}")
    out_prefix = Path(args.output_prefix).expanduser().resolve()
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    undirected = _detect_undirected(input_path, args.undirected)

    declared_nodes = None
    declared_edges = None
    neighbors: DefaultDict[int, List[int]] = defaultdict(list)
    min_vertex = None
    max_vertex = -1

    with input_path.open("r") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                if "Nodes:" in line and "Edges:" in line:
                    parts = line.replace("#", "").replace("\t", " ").split()
                    try:
                        nodes_idx = parts.index("Nodes:") + 1
                        edges_idx = parts.index("Edges:") + 1
                        declared_nodes = int(parts[nodes_idx])
                        declared_edges = int(parts[edges_idx])
                    except (ValueError, IndexError):
                        pass
                continue

            fields = line.split()
            if len(fields) < 2:
                continue
            src = int(fields[0])
            dst = int(fields[1])
            neighbors[src].append(dst)
            max_vertex = max(max_vertex, src, dst)
            if min_vertex is None:
                min_vertex = min(src, dst)
            else:
                min_vertex = min(min_vertex, src, dst)
            if undirected and src != dst:
                neighbors[dst].append(src)

    if max_vertex < 0:
        sys.exit(f"No edges parsed from {input_path}")

    vert_count = max(
        max_vertex + 1,
        declared_nodes if declared_nodes is not None else 0,
    )
    if min_vertex is not None and min_vertex > 0 and declared_nodes is None:
        print(
            f"[snap_to_simdx] WARNING: smallest vertex id is {min_vertex}; "
            "arrays will be zero-padded.",
            file=sys.stderr,
        )

    prefix = out_prefix
    beg_pos_path = prefix.with_suffix(".mtx_beg_pos.bin")
    csr_path = prefix.with_suffix(".mtx_csr.bin")
    weight_path = (
        prefix.with_suffix(".mtx_weight.bin") if args.weight_value is not None else None
    )

    beg_pos: List[int] = [0] * (vert_count + 1)
    adj: List[int] = []
    cursor = 0
    for vid in range(vert_count):
        nbrs = neighbors.get(vid, [])
        if args.sort and len(nbrs) > 1:
            nbrs.sort()
        adj.extend(nbrs)
        cursor += len(nbrs)
        beg_pos[vid + 1] = cursor

    if declared_edges is not None and (not undirected) and cursor != declared_edges:
        print(
            f"[snap_to_simdx] WARNING: parsed edge count {cursor} "
            f"does not match declared {declared_edges}",
            file=sys.stderr,
        )

    _write_binary(beg_pos, beg_pos_path)
    _write_binary(adj, csr_path)
    if weight_path is not None:
        _write_binary([args.weight_value] * cursor, weight_path)

    print("SNAP -> SIMD-X CSR conversion complete")
    print(f" Input file : {input_path}")
    print(f" Vertices   : {vert_count}")
    print(f" Edges      : {cursor}")
    print(f" Undirected : {undirected}")
    outputs = [str(beg_pos_path), str(csr_path)]
    if weight_path is not None:
        outputs.append(str(weight_path))
    print(f" Outputs    : {', '.join(outputs)}")


if __name__ == "__main__":
    main()
