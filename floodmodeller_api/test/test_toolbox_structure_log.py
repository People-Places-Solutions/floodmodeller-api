from floodmodeller_api.toolbox.model_build.structure_log.structure_log import StructureLogBuilder


from pathlib import Path
import os
from shapely.geometry import Point, LineString, Polygon
import pandas as pd
import geopandas as gpd
import numpy as np
import pytest
import csv
import shutil

path_to_cc = (
    "floodmodeller_api.toolbox.model_build.structure_log.structure_log"
)

def test_abc():
    input_path = Path(os.getcwd(),"_temp_test_input.dat")
    output_path = Path(os.getcwd(),"_temp_test_output.csv")
    open(input_path, mode='a').close()
    open(output_path, mode='a').close()
    abc = StructureLogBuilder(input_path, output_path)
    abc.create()

def test_adding_fields():
    abc = StructureLogBuilder("test","test")
    test_file_path = Path(os.getcwd(),"_temp_test.csv")
    with open(test_file_path, "w", newline="") as file:
        abc.writer = csv.writer(file)
        abc._add_fields()
