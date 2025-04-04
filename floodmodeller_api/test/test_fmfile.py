from pathlib import Path

import pytest

from floodmodeller_api import read_file


@pytest.mark.parametrize(
    "file",
    ["BRIDGE.DAT", "network.dat", "Domain1_W.xml", "T5.ief", "network.ied"],
)
def test_crlf_line_endings(test_workspace: Path, tmp_path: Path, file: str):
    obj = read_file(test_workspace / file)
    new_path = tmp_path / file
    obj.save(new_path)
    with open(new_path, "rb") as f:
        contents = f.readlines()

    # Check all line endings except last
    assert all(line.endswith(b"\r\n") for line in contents[:-1])
