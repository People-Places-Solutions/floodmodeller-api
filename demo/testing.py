import pprint
import numpy as np
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
    in_network_map = False

    node_label: list[dict] = []
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

def _set_general_nodes(network: pd.DataFrame, node_cols: list[str]) -> pd.DataFrame:
    for ni in node_cols:
        # Checking whether the label in nx exists in n1, meaning the type can be inferred
        network[f"{ni}_in_n1"] = network[ni].map(network["n1"].value_counts())

        # Removing unnecessary rows from n1, and setting to a pd.Series for mapping
        trimmed_network = network[network["n1"].isin(network[ni])]
        n1_type_lookup = trimmed_network.set_index("n1")["type"]

        # Infer the type in column nx, based on the type set in column n1
        network[f"type_{ni}"] = np.where(
            network[f"{ni}_in_n1"] == 1,
            network[ni].map(n1_type_lookup),
            0,
        )

        # Drop temporary column
        network = network.drop(columns=f"{ni}_in_n1")

    return network

def _set_boundary_nodes(network: pd.DataFrame) -> pd.DataFrame:

    # If there is no label in n2 (i.e. no downstream element), the row represents a boundary
    network["is_boundary"] = ~network["n2"].astype(bool)

    for idx in network[network["is_boundary"]].index:

        # Removing the row in question for searching the rest of the dataframe
        nw_with_row_omitted = network.drop(index=idx)

        # If the node label from the row in question doesn't appear elsewhere in the dataframe,
        # this is an outflow boundary and can be removed (it is covered in the unit upstream)
        if network["n1"][idx] not in nw_with_row_omitted["n1"].to_numpy():
            network = network.drop(index=idx)
            continue

        # Set the downstream label and type using the other same-name node, for inflows
        network["n2"][idx] = network["n1"][idx]
        network["type_n2"][idx] = nw_with_row_omitted[
            nw_with_row_omitted["n1"] == network["n1"][idx]
            ]["type"]

    # Drop temporary column
    network = network.drop(columns="is_boundary")

    return network

def _set_ghost_nodes(network: pd.DataFrame, node_cols: list[str]) -> pd.DataFrame:
    for ni in node_cols:
        network[f"type_{ni}_missing"] = ~network[f"type_{ni}"].astype(bool)

        for idx in network[network[f"type_{ni}_missing"]].index:
            # Removing the row in question for searching the rest of the dataframe
            nw_with_row_omitted = network.drop(index=idx)

            for nx in node_cols:
                print(network[ni][idx])

                # TODO: Fix these lines (currently setting a series to a signe value)
                network[ni][idx] = nw_with_row_omitted[
                    nw_with_row_omitted[nx] == network[ni][idx]
                    ]["n1"]

                network[f"type_{ni}"][idx] = nw_with_row_omitted[
                    nw_with_row_omitted[nx] == network[f"type_{ni}"i][idx]
                    ]["type"]

                if network[ni][idx] != 0 and network[f"type_{ni}"][idx] != 0:
                    break

    # TODO: Delete spill lines

    return network

# TODO: Set up function to spread the rows i.e. (a, b, c) to (a, b), (a, c)
# TODO: Convert result to written text

def get_network_zzt(zzt_filepath: Path):
    """Provide results in same format as DAT.get_network()"""
    raw_data = _read_ztt(zzt_filepath)
    node_label, network_map = _update_zzt_structure(raw_data=raw_data)

    network_original = pd.DataFrame(network_map)
    network = network_original.copy()

    # Remove empty columns
    node_cols = ["n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10"]
    for col in node_cols:
        if not network[col].any():
            network = network.drop(columns=col)
    node_cols = [col for col in network.columns if col in node_cols]

    network = _set_general_nodes(network, node_cols)
    network = _set_boundary_nodes(network)
    network = _set_ghost_nodes(network, node_cols)

    print(network.head(20)) 

    return network

if __name__ == "__main__":

    zzt_filepath = Path(r"floodmodeller_api/test/test_data/network.zzt")
    network = get_network_zzt(zzt_filepath=zzt_filepath)
    # print(network_df.head())
    # network_df.to_csv(r"demo\network_map2.csv")

    # dat = DAT(r"floodmodeller_api/test/test_data/network.dat")
    # nodes, edges = dat.get_network()
    # edges = {tuple(x.unique_name for x in y) for y in edges}
    # unzip_edges = list(zip(*edges))
    # edges_df = pd.DataFrame({"edge1": unzip_edges[0], "edge2": unzip_edges[1]})
    # pprint.pp(nodes)
