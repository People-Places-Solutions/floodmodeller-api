"""Read ZZT diagnostic maps and translate solver reaches into DAT unit edges."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from .units._base import Unit


# Solver unit numbers use different names from the DAT format. Subtypes whose
# solver numbers differ are included in the key; ZZT subtype numbers are not
# DAT subtype names (e.g. INTERPOLATE and RIVER SECTION both use type 19).
_UNIT_CODES = {
    "QTBDY": 1,
    "HTBDY": 2,
    "QHBDY": 3,
    "JUNCTION": 6,
    "RESERVOIR": 7,
    "QH CONTROL": 9,
    "WEIR": 10,
    "BERNOULLI": 11,
    "INVERTED SYPHON": 13,
    "RNWEIR": 18,
    "RIVER": 19,
    "CONDUIT": 19,
    "INTERPOLATE": 19,
    "REPLICATE": 19,
    "SPILL": 20,
    "SLUICE VERTICAL": 21,
    "SLUICE RADIAL": 22,
    "NOTWEIR": 24,
    "SCWEIR": 25,
    "CRUMP": 26,
    "TIDBDY": 28,
    "FEHBDY": 30,
    "FSRBDY": 30,
    "FSSR16BDY": 30,
    "SCSBDY": 31,
    "ABSTRACTION": 35,
    "QRATING": 36,
    "GATED WEIR": 38,
    "SYPHON": 39,
    "ORIFICE": 42,
    "OUTFALL": 42,
    "BRIDGE USBPR1978": 43,
    "BRIDGE ARCH": 44,
    "OCPUMP": 46,
    "CULVERT BEND": 47,
    "CULVERT INLET": 48,
    "CULVERT OUTLET": 49,
    "POND": 50,
    "BREACH": 51,
    "BLOCKAGE": 52,
    "REBDY": 53,
    "LATERAL": 54,
    "NCDBDY": 55,
    "GAUGE": 56,
    "FRQSIM": 61,
    "REFHBDY": 63,
    "FLAT-V WEIR": 64,
    "MANHOLE": 65,
    "LABYRINTH WEIR": 66,
    "GERRBDY": 67,
    "BRIDGE PIERLOSS": 68,
    "BRIDGE INTEGRATED": 69,
}
_MUSKINGUM_CODE = 33
_SUBTYPED_UNITS = {"BRIDGE", "SLUICE", "CULVERT"}


@dataclass(frozen=True)
class _NetworkRow:
    type_code: int
    subtype_code: int
    nodes: tuple[int, ...]


def _unit_code(unit: Unit) -> int:
    if unit.unit == "RIVER" and str(unit.subtype).startswith("MUSK"):
        return _MUSKINGUM_CODE
    key = unit.unit
    if key in _SUBTYPED_UNITS:
        key = f"{key} {unit.subtype}"
    try:
        return _UNIT_CODES[key]
    except KeyError as err:
        msg = f"No ZZT unit number is known for DAT unit type {key!r}."
        raise ValueError(msg) from err


def _table_lines(lines: list[str], title: str) -> list[str]:
    """Find a named map and return its rows after the dashed header separator."""
    try:
        start = next(i for i, line in enumerate(lines) if line.strip().lower() == title)
        start = next(
            i + 1
            for i in range(start + 1, len(lines))
            if lines[i].strip() and set(lines[i].strip()) == {"-"}
        )
    except StopIteration as err:
        msg = f"ZZT is missing the {title!r} table or its header."
        raise ValueError(msg) from err
    end = start
    while end < len(lines) and lines[end].strip():
        end += 1
    if end == start:
        msg = f"ZZT {title!r} table is empty."
        raise ValueError(msg)
    return lines[start:end]


def _read_maps(filepath: Path, encoding: str) -> tuple[dict[int, str], list[_NetworkRow]]:
    lines = filepath.read_text(encoding=encoding).splitlines()
    node_labels: dict[int, str] = {}
    for line in _table_lines(lines, "node number assignment of labels"):
        fields = line.split()
        if len(fields) % 2:
            msg = f"Invalid ZZT node assignment: {line.strip()!r}."
            raise ValueError(msg)
        for number, label in zip(fields[::2], fields[1::2]):
            node = int(number)
            if node <= 0 or node in node_labels or label in node_labels.values():
                msg = f"Invalid or duplicate ZZT node assignment: {number} {label}."
                raise ValueError(msg)
            node_labels[node] = label

    rows = []
    for line in _table_lines(lines, "network map"):
        values = [int(field) for field in line.split()]
        if len(values) < 4:  # noqa: PLR2004
            msg = f"Invalid ZZT network map row: {line.strip()!r}."
            raise ValueError(msg)
        type_code, subtype_code, count = values[:3]
        nodes = tuple(values[3 : 3 + count])
        if count < 1 or len(nodes) != count or any(values[3 + count :]):
            msg = f"Invalid node count in ZZT network map row: {line.strip()!r}."
            raise ValueError(msg)
        if any(node not in node_labels for node in nodes):
            msg = f"ZZT network map references an unassigned node: {line.strip()!r}."
            raise ValueError(msg)
        rows.append(_NetworkRow(type_code, subtype_code, nodes))
    return node_labels, rows


def _match_rows(
    graph_units: list[Unit],
    node_labels: dict[int, str],
    rows: list[_NetworkRow],
) -> dict[int, _NetworkRow]:
    lookup: dict[tuple[int, str | None], list[int]] = {}
    for index, unit in enumerate(graph_units):
        lookup.setdefault((_unit_code(unit), unit.name), []).append(index)

    matched = {}
    for number, row in enumerate(rows, start=1):
        name = node_labels[row.nodes[0]]
        candidates = lookup.get((row.type_code, name), [])
        if len(candidates) != 1:
            msg = (
                f"ZZT unit {number} (type {row.type_code}, label {name!r}) does not "
                "match exactly one DAT unit. Check that the ZZT was generated from this DAT."
            )
            raise ValueError(msg)
        index = candidates[0]
        if index in matched:
            msg = f"Multiple ZZT rows match DAT unit {graph_units[index].unique_name}."
            raise ValueError(msg)
        matched[index] = row
    return matched


def get_network_from_zzt(
    graph_units: list[Unit],
    filepath: Path,
    encoding: str,
) -> tuple[list[Unit], list[tuple[Unit, ...]]]:
    node_labels, rows = _read_maps(filepath, encoding)
    label_nodes = {label: node for node, label in node_labels.items()}
    matched = _match_rows(graph_units, node_labels, rows)
    members: dict[int, list[int]] = {}
    sections: dict[int, list[int]] = {}
    reaches: list[tuple[int, int]] = []

    for index, unit in enumerate(graph_units):
        ports, downstream_node = _unit_ports(unit, matched.get(index), node_labels, label_nodes)
        if downstream_node is not None:
            reaches.append((index, downstream_node))
        for node in set(ports):
            members.setdefault(node, []).append(index)
        if hasattr(unit, "dist_to_next") and unit.name is not None:
            sections.setdefault(label_nodes[unit.name], []).append(index)

    pairs: set[tuple[int, int]] = set()
    for indices in members.values():
        pairs.update(combinations(indices, 2))
    for index, downstream_node in reaches:
        targets = sections.get(downstream_node, [])
        if len(targets) != 1 or targets[0] == index:
            msg = (
                f"ZZT reach from {graph_units[index].unique_name} does not resolve to "
                f"exactly one downstream DAT section at {node_labels[downstream_node]!r}."
            )
            raise ValueError(msg)
        # Retain get_network's DAT-order convention, including lateral links.
        pairs.add((min(index, targets[0]), max(index, targets[0])))

    connected = {index for pair in pairs for index in pair}
    for index, unit in enumerate(graph_units):
        if index not in connected:
            logging.warning(
                "%s (%s %s) is an orphan unit and not connected to anything.",
                unit.machine_name,
                unit.unit,
                unit.name,
            )
    return graph_units, [(graph_units[a], graph_units[b]) for a, b in sorted(pairs)]


def _unit_ports(
    unit: Unit,
    row: _NetworkRow | None,
    node_labels: dict[int, str],
    label_nodes: dict[str, int],
) -> tuple[tuple[int, ...], int | None]:
    is_section = hasattr(unit, "dist_to_next")
    if row is None:
        # End sections have no solver reach of their own. Recover their
        # explicit node references rather than dropping the DAT objects.
        if (
            not is_section
            or getattr(unit, "dist_to_next", None) != 0
            or not unit.all_labels <= label_nodes.keys()
        ):
            msg = f"DAT unit {unit.unique_name} is missing from the ZZT. Regenerate the ZZT."
            raise ValueError(msg)
        return tuple(label_nodes[label] for label in unit.all_labels), None

    ports = row.nodes
    downstream_node = None
    if is_section:
        if len(ports) < 2:  # noqa: PLR2004
            msg = f"ZZT reach for {unit.unique_name} has no downstream node."
            raise ValueError(msg)
        downstream_node = ports[1]
        # n2 is the next section, not another label on this section.
        ports = (ports[0], *ports[2:])
    labels = {node_labels[node] for node in ports}
    if not unit.all_labels <= labels:
        msg = f"ZZT labels do not match DAT unit {unit.unique_name}. Regenerate the ZZT."
        raise ValueError(msg)
    return ports, downstream_node
