from floodmodeller_api import DAT
import pprint
from pathlib import Path
import pandas as pd
import numpy as np


ZZT_TYPES = {
    1: "QTBDY",
    3: "QHBDY",
    6: "JUNCTION",
    11: "BERNOULLI",
    18: "RNWEIR",
    19: "RIVER",
    20: "SPILL",
    30: "FSSR16BDY",
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
    in_store_map = False
    in_elevation_map = False

    node_label: dict[int, str] = {}
    label_map: dict[int, list] = {}
    network_map: list[dict] = []

    node_label_idx: int = 0
    label_map_idx: int = 0
    network_map_idx: int = 0

    network_map_col = [
        "type",
        "sub_type",
        "no.nodes",
        "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10",
        ]

    for idx, line in enumerate(raw_data):
        if line == "node number assignment of labels":
            in_node_label = True
            node_label_idx = idx + title_block_length

        if line == "label map":
            in_node_label = False
            in_label_map = True
            label_map_idx = idx + title_block_length

        if line == "network map":
            in_label_map = False
            in_network_map = True
            network_map_idx = idx + title_block_length

        if line == "store map":
            in_network_map = False

        # TODO: Set up with DataFrame instead to allow types to be added as a seperate column
        if in_node_label and idx > node_label_idx:
            parts = line.split()
            for i in range(0, len(parts), 2):
                node_label.update({int(parts[i]): str(parts[i+1])})

        if in_label_map and idx > label_map_idx:
            parts = line.split()
            if parts:
                label_map.update({int(parts[0]): parts[1:]})

        if in_network_map and idx > network_map_idx:
            parts = line.split()
            if parts:
                parts = [int(part) for part in parts]
                network_map.append(dict(zip(network_map_col, parts)))

    node_label = dict(sorted(node_label.items(), key=lambda item: item[0]))

    return node_label, label_map, network_map

def get_network_zzt(zzt_filepath: Path):
    """Provide results in same format as DAT.get_network()"""
    raw_data = _read_ztt(zzt_filepath)
    node_label, _, network_map = _update_zzt_structure(raw_data=raw_data)

    node_cols = ["n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10"]

    # TODO: Replace with node label with type, in format TYPE_LABEL
    network_map = pd.DataFrame(network_map)
    network_map[node_cols] = network_map[node_cols].replace(node_label)
    network_map["type"] = network_map["type"].replace(ZZT_TYPES)

    return network_map

if __name__ == "__main__":

    zzt_filepath = Path(r"floodmodeller_api/test/test_data/network.zzt")
    network = get_network_zzt(zzt_filepath=zzt_filepath)

    dat = DAT(r"floodmodeller_api/test/test_data/network.dat")
    nodes, edges = dat.get_network()
    edges = {tuple(x.unique_name for x in y) for y in edges}
    unzip_edges = list(zip(*edges))
    edges_df = pd.DataFrame({"edge1": unzip_edges[0], "edge2": unzip_edges[1]})
    pprint.pp(nodes)
