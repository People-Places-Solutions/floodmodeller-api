import pprint
from pathlib import Path

import numpy as np
import pandas as pd

from floodmodeller_api import DAT

NETWORK_MAP_COL = [
    "type",
    "sub_type",
    "no.nodes",
    "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10",
    ]

LABEL_MAP_COL = [
    "unit",
    "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10",
    ]

ZZT_TYPES = {
    1: "QTBDY",
    2: "HTBDY",
    3: "QHBDY",
    4: "", # No longer used
    5: "TIDAL",
    6: "JUNCO",
    7: "RESO",
    8: "RPTDS",
    9: "CONQH",
    10: "WEIR",
    11: "BERLOS",
    12: "RNDSC",
    13: "SIPHON",
    14: "RNTDS",
    15: "RNTRS",
    16: "LTFTDS",
    17: "LOSS",
    18: "RNWEIR",
    19: "RIVER", # (all types, except MUSK) i.e.: CONDUIT, INTERPOLATE, REPLICATE
    20: "SPILL4",
    21: "SLCVRT",
    22: "SLCRAD",
    23: "BARIER",
    24: "NTWEIR",
    25: "SCWEIR",
    26: "CRUMP",
    27: "BUTFLY",
    28: "TIDBDY",
    29: "HQBDY",
    30: "FSRQT",
    31: "SCSBDY",
    32: "LDPUMP",
    33: "MUSK", # (all-types), i.e.: MUSKINGUM, MUSK-VPMC, MUSK-XSEC, MUSK-RSEC
    34: "IRRDEM",
    35: "ABSTRA",
    36: "QHRAT",
    37: "JUNCR",
    38: "WEIRVC",
    39: "SYPHON",
    40: "USER1",
    41: "USER2",
    42: "ORIFCE",
    43: "BRIDUS",
    44: "ARCHBR",
    45: "HEDLOS",
    46: "FPUMP",
    47: "CULBND",
    48: "CULINL",
    49: "CULOUT",
    50: "POND",
    51: "BREACH",
    52: "BLOCK",
    53: "REBDY",
    54: "LATFLOW",
    55: "NCDBDY",
    56: "GAUGE",
    57: "URBAN",
    58: "URBTFLOW",
    59: "DESBORDES",
    60: "JAPANESE",
    61: "FRQSIM",
    62: "CONQHH",
    63: "REFHBDY",
    64: "FLATV",
    65: "MANHOLE",
    66: "LABYRINTH",
    67: "GERRBDY",
    68: "PIERLOSSBR",
    69: "SUPERBRIDGE",
    70: "SUPERWEIR",
}


def _read_ztt(filepath: Path) -> list[str]:
    with open(zzt_filepath, encoding="cp1252") as zzt_file:
        raw_data: list[str] = [line.rstrip("\n") for line in zzt_file]
    return raw_data

def _update_zzt_structure(raw_data):

    title_block_length: int = 4
    in_node_label = False
    in_label_map = False
    in_network_map = False

    node_label: list[dict] = []
    label_map: list[dict] = []
    network_map: list[dict] = []

    # Dummy values
    node_label_idx: int = 0
    label_map_idx: int = 0
    network_map_idx: int = 0

    for idx, line in enumerate(raw_data):
        if line == "node number assignment of labels":
            in_node_label = True
            node_label_idx = idx + title_block_length

        if line == "label map":
            in_node_label = False

        if line == "network map":
            in_network_map = True
            network_map_idx = idx + title_block_length

        if line == "store map":
            in_network_map = False

        if in_node_label and idx > node_label_idx:
            parts = line.split()
            node_label.extend(
                {"node": int(parts[i]), "label": str(parts[i+1])}
                for i in range(0, len(parts), 2))

        if in_network_map and idx > network_map_idx:
            parts = line.split()
            if parts:
                parts = [int(part) for part in parts]
                network_map.append(dict(zip(NETWORK_MAP_COL, parts, strict=True)))

    return node_label, network_map

def get_network_zzt(zzt_filepath: Path):
    """Provide results in same format as DAT.get_network()"""
    raw_data = _read_ztt(zzt_filepath)
    node_label, network_map = _update_zzt_structure(raw_data=raw_data)

    node_cols = ["n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10"]

    network_map = pd.DataFrame(network_map)
    print(network_map.tail(25))
    node_type = pd.Series(network_map["type"], index=network_map["n1"]).to_dict()
    pprint.pp(node_type)

    for col in node_cols:
        if not network_map[col].any(): # Skip if the column is all zeros
            continue
        network_map[f"{col}_type"] = network_map[col].replace(node_type).astype(int)

    # node_label["type"] = node_label[].replace()

    # network_map[node_cols] = network_map[node_cols].replace(node_label)
    # network_map["type"] = network_map["type"].replace(ZZT_TYPES)

    return network_map

if __name__ == "__main__":

    zzt_filepath = Path(r"floodmodeller_api/test/test_data/network.zzt")
    network = get_network_zzt(zzt_filepath=zzt_filepath)
    print(network)

    # dat = DAT(r"floodmodeller_api/test/test_data/network.dat")
    # nodes, edges = dat.get_network()
    # edges = {tuple(x.unique_name for x in y) for y in edges}
    # unzip_edges = list(zip(*edges))
    # edges_df = pd.DataFrame({"edge1": unzip_edges[0], "edge2": unzip_edges[1]})
    # pprint.pp(nodes)
