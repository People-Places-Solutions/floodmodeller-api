from floodmodeller_api import IEF, XML2D, DAT
#from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller.convert_estry_001_oop import (
#    TuflowToDat,
#)
from pathlib import Path
from shapely.geometry import LineString
from shapely.ops import split
from typing import List, Tuple, Union
import geopandas as gpd
import pandas as pd
import numpy as np
import math
from floodmodeller_api.units.helpers import (
    _to_float,
)
from floodmodeller_api.units.sections import RIVER
from floodmodeller_api.units.conduits import CONDUIT
from floodmodeller_api.units.comment import COMMENT
from shapely.geometry import Point


def concat(gdf_list: List[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))


def rename_and_select(df: pd.DataFrame, mapper: dict) -> pd.DataFrame:
    mapper_subset = {k: v for k, v in mapper.items() if k in df.columns}
    return df.rename(columns=mapper_subset)[mapper_subset.values()]


def filter(gdf: gpd.GeoDataFrame, column: str, value: int) -> gpd.GeoDataFrame:
    is_selected = gdf.loc[:, column] == value
    is_selected = is_selected[is_selected].index
    return gdf.iloc[is_selected].drop(columns=column)


class ComponentConverter:
    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def edit_fm_file(self) -> None:
        raise NotImplementedError("Abstract method not overwritten")


class ComponentConverterIEF(ComponentConverter):
    def __init__(self, folder: Path) -> None:
        super().__init__(folder)


class SchemeConverterIEF(ComponentConverterIEF):
    def __init__(
        self,
        ief: IEF,
        folder: Path,
        time_step: float,
    ) -> None:
        super().__init__(folder)
        self._ief = ief
        self._time_step = time_step

    def edit_fm_file(self) -> None:
        self._ief.Timestep = self._time_step


class ComponentConverterDAT(ComponentConverter):
    def __init__(self, folder: Path) -> None:
        super().__init__(folder)


class NetworkConverterDAT(ComponentConverterDAT):
    def __init__(
        self,
        dat: DAT,
        folder: Path,
        parent_folder: str,
        nwk_paths: List[str],
        xs_path: str,
    ) -> None:
        super().__init__(folder)
        self._dat = dat
        self.parent_folder = parent_folder
        self.nwk_paths = nwk_paths
        self.xs_path = xs_path

    def edit_fm_file(self) -> None:
        tuf2dat = TuflowToDat()
        tuf2dat.convert(self.parent_folder, self.nwk_paths, self.xs_path, self._dat)


class TuflowToDat:
    def _process_shapefile(self, path):
        attributes = ""
        attributes = gpd.read_file(path)
        attributes.dropna(how="all", axis=1, inplace=True)
        return attributes

    def _read_in(self, model_path, nwk_paths, xs_path):
        #   File paths for model, xs and nwk, read in

        self._model_path = model_path
        self._nwk_paths = nwk_paths
        self._xs_path = xs_path
        # self._model_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model"
        # self._nwk_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_nwk_EG14_channels_001_L.shp"
        # self._xs_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_xs_EG14_001_L.shp"

        shapefiles = nwk_paths
        shapefiles.append(xs_path)
        for shapefile in shapefiles:
            attributes = self._process_shapefile(shapefile)
            if "xs" in shapefile:
                self._xs_attributes = attributes
            elif "channels" in shapefile:
                self._nwk_attributes = attributes
            elif "culverts" in shapefile:
                self._culvert_attributes = attributes

    def _clean_df_1(self):
        #   Clean up dataframes
        self._nwk_attributes = self._nwk_attributes.query("Type.str.lower() == 's'")
        self._culvert_attributes = self._culvert_attributes.query(
            "Type.str.lower() == 'r' | Type.str.lower() == 'c'"
        )
        self._nwk_attributes = self._nwk_attributes.dropna(subset=["geometry"])
        self._xs_attributes = self._xs_attributes.dropna(subset=["geometry"])
        self._culvert_attributes = self._culvert_attributes.dropna(
            subset=["geometry"]
        )
        if not (self._nwk_attributes.unary_union == None):
            self._xs_attributes = self._xs_attributes[
                self._xs_attributes.intersects(self._nwk_attributes.unary_union)
            ]

    def _extract_geometry_data(self):
        #   Extract geometry data
        self._nwk_attributes["length"] = self._nwk_attributes.length
        self._nwk_attributes["start"] = self._nwk_attributes["geometry"].apply(
            lambda g: Point(g.coords[0])
        )
        self._nwk_attributes["end"] = self._nwk_attributes["geometry"].apply(
            lambda g: Point(g.coords[-1])
        )
        self._culvert_attributes["end"] = self._culvert_attributes["geometry"].apply(
            lambda g: Point(g.coords[0])
        )
        self._culvert_attributes["start"] = self._culvert_attributes["geometry"].apply(
            lambda g: Point(g.coords[-1])
        )

    def _find_xs_intersect(self):
        #   Find which network line the xs intersects and where
        self._xs_attributes["intersect"] = [
            next(
                (
                    row["ID"]
                    for _, row in self._nwk_attributes.iterrows()
                    if row["start"].intersects(xs_geometry)
                ),
                None,
            )
            for xs_geometry in self._xs_attributes["geometry"]
        ]
        self._xs_attributes["mid_intersect"] = [
            next(
                (
                    river_row["ID"]
                    for river_index, river_row in self._nwk_attributes.iterrows()
                    if xs_geometry.intersects(river_row["geometry"])
                    and not xs_geometry.touches(river_row["geometry"])
                ),
                None,
            )
            for xs_geometry in self._xs_attributes["geometry"]
        ]
        self._xs_attributes["end_intersect"] = [
            next(
                (
                    row["ID"]
                    for _, row in self._nwk_attributes.iterrows()
                    if row["end"].intersects(xs_geometry)
                ),
                None,
            )
            for xs_geometry in self._xs_attributes["geometry"]
        ]

        #   Put mid intersect in intersect column if nothing there
        for index, row in self._xs_attributes.iterrows():
            if row["mid_intersect"] is not None:
                self._xs_attributes.at[index, "intersect"] = row["mid_intersect"]

    def _find_ds_intersect(self):
        #   nwk find connected network line ds
        self._nwk_attributes["end"] = self._nwk_attributes["end"].apply(
            lambda x: Point(x)
        )
        self._nwk_attributes["connected"] = [[]] * len(self._nwk_attributes)
        self._nwk_attributes["Flag"] = ""

        for i, row in self._nwk_attributes.iterrows():
            end_point = row["end"]
            intersected_rows = self._nwk_attributes[
                ~self._nwk_attributes.index.isin([i])
                & self._nwk_attributes.geometry.intersects(end_point)
            ]
            next_ids = intersected_rows["ID"].tolist()
            self._nwk_attributes.at[i, "connected"] = next_ids

    def _find_us_intersect(self):
        #   Find the us connection
        self._nwk_attributes["before"] = [[]] * len(self._nwk_attributes)

        for i, row in self._nwk_attributes.iterrows():
            start_point = row["start"]
            intersected_rows = self._nwk_attributes[
                ~self._nwk_attributes.index.isin([i])
                & self._nwk_attributes.geometry.intersects(start_point)
            ]
            previous_ids = intersected_rows["ID"].tolist()
            self._nwk_attributes.at[i, "before"] = previous_ids

    def _highlight_flag(self):
        #   Highlight flag from nwk and map length/ maning/gxy stuff to xs
        filtered_df = self._nwk_attributes[
            self._nwk_attributes["connected"].apply(lambda x: len(x) > 1)
        ]
        lists = filtered_df["connected"].tolist()
        master_list = [item for sublist in lists for item in sublist]
        master_list = list(set(master_list))
        filtered_df = self._nwk_attributes[self._nwk_attributes["ID"].isin(master_list)]

        self._nwk_attributes.loc[
            self._nwk_attributes["ID"].isin(
                filtered_df["ID"][filtered_df["connected"].apply(lambda x: len(x) == 1)]
            ),
            "Flag",
        ] = "join_start"
        self._nwk_attributes.loc[
            self._nwk_attributes["ID"].isin(
                filtered_df["ID"][filtered_df["connected"].apply(lambda x: len(x) != 1)]
            ),
            "Flag",
        ] = "join_end"
        self._nwk_attributes.loc[
            self._nwk_attributes["connected"].apply(lambda x: len(x) == 0), "Flag"
        ] = "end"
        self._nwk_attributes.loc[
            self._nwk_attributes["before"].apply(lambda x: len(x) == 0), "Flag"
        ] = "start"

        non_empty_rows = self._nwk_attributes[self._nwk_attributes["Flag"].notna()]
        id_flag_dict = non_empty_rows.set_index("ID")[
            ["Flag", "n_nF_Cd", "length", "end"]
        ].to_dict(orient="index")
        self._full_flag_dict = self._nwk_attributes.set_index("ID")[
            ["Flag", "n_nF_Cd", "length", "start"]
        ].to_dict(orient="index")

        self._end_dict = {
            key: value for key, value in id_flag_dict.items() if value["Flag"] == "end"
        }
        self._start_dict = {
            key: value
            for key, value in id_flag_dict.items()
            if value["Flag"] == "start"
        }
        self._join_start_dict = {
            key: value
            for key, value in id_flag_dict.items()
            if value["Flag"] == "join_start"
        }
        self._join_end_dict = {
            key: value
            for key, value in id_flag_dict.items()
            if value["Flag"] == "join_end"
        }

    def _add_to_xs_data(self):
        #   add to the xs data
        self._xs_attributes["Flag"] = ""
        self._xs_attributes.loc[
            self._xs_attributes["end_intersect"].isin(self._end_dict.keys()), "Flag"
        ] = "end"
        self._xs_attributes.loc[
            self._xs_attributes["intersect"].isin(self._start_dict.keys()), "Flag"
        ] = "start"
        self._xs_attributes.loc[
            self._xs_attributes["intersect"].isin(self._join_end_dict.keys()), "Flag"
        ] = "join_end"
        self._xs_attributes.loc[
            self._xs_attributes["intersect"].isin(self._join_start_dict.keys()), "Flag"
        ] = "join_start"

        self._xs_attributes["dist_to_next"] = ""
        for key, values in self._full_flag_dict.items():
            mask = self._xs_attributes["intersect"] == key
            self._xs_attributes.loc[mask, "dist_to_next"] = values["length"]
        self._xs_attributes.dist_to_next.replace("", 0, regex=True, inplace=True)

        self._xs_attributes["mannings"] = ""
        for key, values in self._full_flag_dict.items():
            mask = self._xs_attributes["intersect"] == key
            self._xs_attributes.loc[mask, "mannings"] = values["n_nF_Cd"]
        for key, values in self._end_dict.items():
            mask = self._xs_attributes["end_intersect"] == key
            self._xs_attributes.loc[mask, "mannings"] = values["n_nF_Cd"]

        self._xs_attributes["location"] = ""  # self._xs_attributes['start']
        for key, values in self._full_flag_dict.items():
            mask = self._xs_attributes["intersect"] == key
            self._xs_attributes.loc[mask, "location"] = values["start"]
        for key, values in self._end_dict.items():
            mask = self._xs_attributes["end_intersect"] == key
            self._xs_attributes.loc[mask, "location"] = values["end"]
        # for index, row in self._xs_attributes.iterrows():
        #    if row['location'] == '':
        #        self._xs_attributes = self._xs_attributes.drop(index)

    def _get_coordinates(self, point):
        #   take xs intersect, map to start point from nwk, set x as east, y as north
        return point.x, point.y

    def _set_eastings_northings(self):
        geoseries = gpd.GeoSeries(self._xs_attributes["location"])
        coords = geoseries.apply(self._get_coordinates).str  # type: ignore
        easting = coords[0]
        northing = coords[1]
        self._xs_attributes["easting"] = easting
        self._xs_attributes["northing"] = northing

    # this method needs fixing apparently
    def _organise_df(self):
        ###### Currently works but misses out last XS in series
        #   organise df
        self._xs_attributes["order"] = 0
        order_counter = 1
        for i, row in self._xs_attributes.iterrows():
            # Check if the row is a start or join_start
            if not ("start" in row["Flag"] or "join_start" in row["Flag"]):
                continue
            self._xs_attributes.at[i, "order"] = order_counter
            order_counter += 1
            intersect_value = row["intersect"]
            next_row_index = self._xs_attributes[
                (self._xs_attributes["end_intersect"] == intersect_value)
                & (self._xs_attributes["Flag"] == "")
            ].index
            while not next_row_index.empty:
                next_row_index = next_row_index[0]
                self._xs_attributes.at[next_row_index, "order"] = order_counter
                order_counter += 1

                intersect_value = self._xs_attributes.at[next_row_index, "intersect"]
                end_intersect_value = self._xs_attributes.at[
                    next_row_index, "end_intersect"
                ]
                next_row_index = self._xs_attributes[
                    (self._xs_attributes["end_intersect"] == intersect_value)
                    & (self._xs_attributes["Flag"] == "")
                ].index

            if next_row_index.empty:
                next_row_index = self._xs_attributes[
                    self._xs_attributes["end_intersect"] == intersect_value
                ].index
                next_row_index = next_row_index[0]
                self._xs_attributes.at[next_row_index, "order"] = order_counter
                order_counter += 1
                self._xs_attributes.at[next_row_index, "order"] = order_counter
                order_counter += 1

        # Sort the dataframe based on the order column
        self._xs_attributes = self._xs_attributes.sort_values("order")

    def _clean_df_2(self):
        # clean up df
        col_to_drop = [
            "Type",
            "Z_Incremen",
            "Z_Maximum",
            "mid_intersect",
            "geometry",
            "intersect",
            "end_intersect",
            "location",
            "order",
        ]
        self._cross_sections = self._xs_attributes.drop(col_to_drop, axis=1)
        self._cross_sections["Name"] = [
            "RIV" + str(i).zfill(3) for i in range(1, len(self._cross_sections) + 1)
        ]

    def _make_dat(self, empty_dat):
        self._dat = empty_dat
        self._comment = COMMENT(text="End of Reach")
        self._headings = [
            "X",
            "Y",
            "Mannings n",
            "Panel",
            "RPL",
            "Marker",
            "Easting",
            "Northing",
            "Deactivation",
            "SP. Marker",
        ]
        self._dat._gxy_data = None

    def _add_xss(self):
        # iterate through adding xs
        for index, row in self._cross_sections.iterrows():
            unit_csv_name = str(row["Source"])  #'..\\csv\\1d_xs_M14_C99.csv' pulled out
            unit_csv = pd.read_csv(
                self._model_path + unit_csv_name.lstrip(".."), skiprows=[0]
            )
            unit_csv.columns = ["X", "Z"]
            unit_data = pd.DataFrame(columns=self._headings)
            unit_data["X"] = unit_csv["X"]
            unit_data["Y"] = unit_csv["Z"]
            unit_data["Mannings n"] = row["mannings"]
            unit_data["Panel"].fillna(False, inplace=True)
            unit_data["RPL"].fillna(1.0, inplace=True)
            unit_data["Marker"].fillna(False, inplace=True)
            unit_data["SP. Marker"].fillna(0, inplace=True)

            unit = RIVER(
                name=row["Name"],
                data=unit_data,
                density=1000.0,
                dist_to_next=row["dist_to_next"],
                slope=0.0001,
            )
            self._dat.insert_unit(unit, add_at=-1)
            if row["Flag"] == "end" or row["Flag"] == "join_end":
                self._dat.insert_unit(self._comment, add_at=-1)

    def _add_culverts(self):
        self._culvert_comment = COMMENT(text="End of Culvert")
        # iterate through adding xs
        for index, row in self._culvert_attributes.iterrows():
            if row["Type"] == "R":
                subtype = "RECTANGULAR"
                width = _to_float(row["Width_or_D"])
                height = _to_float(row["Height_or_"])
                friction_on_walls = _to_float(row["n_nF_Cd"])
                friction_on_invert = _to_float(row["n_nF_Cd"])
                friction_on_soffit = _to_float(row["n_nF_Cd"])
            elif row["Type"] == "C":
                subtype = "CIRCULAR"
                diameter = _to_float(row["Width_or_D"])
                friction_below_axis = _to_float(row["n_nF_Cd"])
                friction_above_axis = _to_float(row["n_nF_Cd"])
            else:
                subtype = "SECTION"
            comment = ""
            name = "UNIT{:03d}".format(index)
            spill = ""
            length = row["Len_or_ANA"]
            dist_to_next = 0.0
            friction_eq = "MANNING"
            invert = 0.0
            
            for i in range (0,2):
                if i == 0:
                    name_ud = name+"u"
                    next_dist = length
                    invert = _to_float(row["US_Invert"])
                else:
                    name_ud = name+"d"
                    next_dist = dist_to_next
                    invert = _to_float(row["DS_Invert"])

                if row["Type"] == "R":
                    unit = CONDUIT(
                        name=name_ud,
                        spill=spill,
                        comment=comment,
                        dist_to_next=next_dist,
                        subtype=subtype,
                        friction_eq=friction_eq,
                        invert=invert,
                        width=width,
                        height=height,
                        friction_on_walls=friction_on_walls,
                        friction_on_invert=friction_on_invert,
                        friction_on_soffit=friction_on_soffit,
                    )
                elif row["Type"] == "C":
                    unit = CONDUIT(
                        name=name_ud,
                        spill=spill,
                        comment=comment,
                        dist_to_next=next_dist,
                        subtype=subtype,
                        friction_eq=friction_eq,
                        invert=invert,
                        diameter=diameter,
                        friction_below_axis=friction_below_axis,
                        friction_above_axis=friction_above_axis,
                    )

                self._dat.insert_unit(unit, add_at=-1)
            self._dat.insert_unit(self._culvert_comment, add_at=-1)

    def _add_gxy_data(self):
        #   Write out .gxy
        file_contents = ""
        for index, row in self._cross_sections.iterrows():
            file_contents += "[RIVER_SECTION_{}]\n".format(row["Name"])
            file_contents += "x={:.2f}\n".format(row["easting"])
            file_contents += "y={:.2f}\n\n".format(row["northing"])
        
        for index, row in self._culvert_attributes.iterrows():
            if row["Type"] == "R":
                subtype = "RECTANGULAR"
            elif row["Type"] == "C":
                subtype = "CIRCULAR"
                # add circular *params
            else:
                subtype = "SECTION"
            # upstream conduit for the culvert
            file_contents += "[CONDUIT_{}_{}]\n".format(subtype,"UNIT{:03d}d".format(index))
            file_contents += "x={:.2f}\n".format(row["start"].x)
            file_contents += "y={:.2f}\n\n".format(row["start"].y)
            # downstream conduit for the culvert
            file_contents += "[CONDUIT_{}_{}]\n".format(subtype,"UNIT{:03d}u".format(index))
            file_contents += "x={:.2f}\n".format(row["end"].x)
            file_contents += "y={:.2f}\n\n".format(row["end"].y)

        self._dat._gxy_data = file_contents

    def convert(
        self, model_path: str, nwk_paths: List[str], xs_path: str, empty_dat: DAT
    ):
        self._read_in(model_path, nwk_paths, xs_path)

        self._clean_df_1()

        self._extract_geometry_data()

        self._find_xs_intersect()

        self._find_ds_intersect()

        self._find_us_intersect()

        self._highlight_flag()

        self._add_to_xs_data()

        self._set_eastings_northings()

        self._organise_df()

        self._clean_df_2()

        self._make_dat(empty_dat)

        self._add_xss()

        self._add_culverts()

        self._add_gxy_data()

        # self._dat.save(output_path)

        # return self._dat


class ComponentConverterXML2D(ComponentConverter):
    def __init__(self, xml: XML2D, folder: Path, domain_name: str) -> None:
        super().__init__(folder)
        self._xml = xml
        self._domain_name = domain_name


class ComputationalAreaConverter2D(ComponentConverterXML2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        xll: float,
        yll: float,
        dx: float,
        lx_ly: Tuple[float],
        all_areas: List[gpd.GeoDataFrame],
        rotation: float = None,
    ) -> None:
        super().__init__(xml, folder, domain_name)

        self._xll = xll
        self._yll = yll
        self._dx = dx
        self._nrows = int(lx_ly[0] / self._dx)
        self._ncols = int(lx_ly[1] / self._dx)
        self._rotation = rotation

        self._active_area_path = None
        self._deactive_area_path = None

        all_areas_concat = concat([self.standardise_areas(x) for x in all_areas])

        for name, code in {"active": 1, "deactive": 0}.items():
            area = filter(all_areas_concat, "code", code)
            area_exists = len(area.index) > 0
            if not area_exists:
                continue
            path = Path.joinpath(folder, f"{name}_area.shp")
            setattr(self, f"_{name}_area_path", path)
            area.to_file(path)

    @staticmethod
    def standardise_areas(file: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_file = file.iloc[:, :]
        new_file.columns = ["code", "geometry"]
        return new_file

    def edit_fm_file(self) -> None:
        comp_area_dict = {
            "xll": self._xll,
            "yll": self._yll,
            "dx": self._dx,
            "nrows": self._nrows,
            "ncols": self._ncols,
        }

        if self._rotation:
            comp_area_dict["rotation"] = self._rotation

        if self._active_area_path:
            comp_area_dict["active_area"] = self._active_area_path

        if self._deactive_area_path:
            comp_area_dict["deactive_area"] = self._deactive_area_path

        self._xml.domains[self._domain_name]["computational_area"] = comp_area_dict


class LocLineConverter2D(ComputationalAreaConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        dx: float,
        lx_ly: tuple,
        all_areas: List[gpd.GeoDataFrame],
        loc_line: LineString,
    ) -> None:
        x1, y1 = loc_line.coords[0]
        x2, y2 = loc_line.coords[1]

        theta_rad = math.atan2(y2 - y1, x2 - x1)
        if theta_rad < 0:
            theta_rad += 2 * math.pi
        rotation = round(math.degrees(theta_rad), 3)

        super().__init__(
            xml, folder, domain_name, x1, y1, dx, lx_ly, all_areas, rotation
        )


class TopographyConverter2D(ComponentConverterXML2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        rasters: List[Path],
        vectors: List[Union[Tuple[gpd.GeoDataFrame], gpd.GeoDataFrame]],
    ) -> None:
        super().__init__(xml, folder, domain_name)

        self._raster_paths = [str(x) for x in rasters]

        self._vector_paths = []
        for i, value in enumerate(vectors):
            vector_path = str(Path.joinpath(folder, f"topography_{i}.shp"))
            self._vector_paths.append(vector_path)
            if type(value) != tuple:
                value = (value,)
            self.combine_layers(value).to_file(vector_path)

    def edit_fm_file(self) -> None:
        self._xml.domains[self._domain_name]["topography"] = (
            self._raster_paths + self._vector_paths
        )

    @classmethod
    def combine_layers(cls, layers: Tuple[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
        all_types = concat([cls.standardise_topography(x) for x in layers])

        lines = all_types[all_types.geometry.geometry.type == "LineString"]
        points = all_types[all_types.geometry.geometry.type == "Point"]
        polygons = all_types[all_types.geometry.geometry.type == "Polygon"]

        lines_present = len(lines.index) > 0
        points_present = len(points.index) > 0
        polygons_present = len(polygons.index) > 0

        if lines_present and points_present and not polygons_present:
            return cls.convert_lines_and_points(lines, points)

        elif polygons_present and not (points_present or lines_present):
            return cls.convert_polygons(polygons)

        else:
            spatial_types = []
            if lines_present:
                spatial_types.append("lines")
            if points_present:
                spatial_types.append("points")
            if polygons_present:
                spatial_types.append("polygons")
            spatial_types_display = ", ".join(spatial_types)

            raise RuntimeError(f"Combination not supported: {spatial_types_display}")

    @staticmethod
    def standardise_topography(file: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_file = file.iloc[:, :]
        new_file.columns = ["z", "dz", "width", "options", "geometry"]
        return new_file

    @staticmethod
    def convert_lines_and_points(
        lines: gpd.GeoDataFrame, points: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        # split lines according to points

        # split() causes: RuntimeWarning: invalid value encountered in line_locate_point: return lib.line_locate_point(line, other)
        segments = gpd.GeoDataFrame(
            list(split(lines.geometry.unary_union, points.geometry.unary_union).geoms),
            crs=lines.crs,
            columns=["geometry"],
        )

        # get line endpoints
        segments[["point1", "point2"]] = pd.DataFrame(
            segments.apply(lambda x: list(x.geometry.boundary.geoms), axis=1).tolist()
        )
        segments["point1"] = gpd.GeoSeries(segments["point1"])
        segments["point2"] = gpd.GeoSeries(segments["point2"])

        # get endpoint heights & line thickness
        segments = (
            segments.merge(
                rename_and_select(points, {"z": "height1", "geometry": "point1"}),
                on="point1",
            )
            .drop(columns="point1")
            .merge(
                rename_and_select(points, {"z": "height2", "geometry": "point2"}),
                on="point2",
            )
            .drop(columns="point2")
            .astype({"height1": float, "height2": float})
        )

        return segments

    @staticmethod
    def convert_polygons(polygons: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_polygons = polygons.iloc[:, [0, 3, 4]]
        new_polygons.columns = ["height", "method", "geometry"]

        method_is_add = new_polygons["method"] == "ADD"
        new_polygons.loc[method_is_add, "method"] = "add"
        new_polygons.loc[~method_is_add, "method"] = np.nan

        return new_polygons


class RoughnessConverter2D(ComponentConverterXML2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        law: str,
        global_material: int,
        file_material: List[gpd.GeoDataFrame],
        mapping: pd.DataFrame,
    ) -> None:
        super().__init__(xml, folder, domain_name)

        self._law = law
        self._material = concat([self.standardise_material(x) for x in file_material])
        self._mapping = self.standardise_mapping(mapping)

        is_global = self._mapping["material_id"] == global_material
        self._global_value = float(self._mapping.loc[is_global, "value"])

        self._file_material_path = Path.joinpath(folder, "roughness.shp")

        roughness = self.material_to_roughness(self._material, self._mapping)
        roughness.to_file(self._file_material_path)

    @staticmethod
    def standardise_material(file: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_file = file.iloc[:, [0, -1]]
        new_file.columns = ["material_id", "geometry"]
        return new_file

    @staticmethod
    def standardise_mapping(file: pd.DataFrame) -> pd.DataFrame:
        new_file = file.iloc[:, :2]
        new_file.columns = ["material_id", "value"]
        return new_file

    @staticmethod
    def material_to_roughness(
        material: gpd.GeoDataFrame, mapping: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        return pd.merge(material, mapping, on="material_id")[["value", "geometry"]]

    def edit_fm_file(self) -> None:
        self._xml.domains[self._domain_name]["roughness"] = [
            {
                "type": "global",
                "law": self._law,
                "value": self._global_value,
            },
            {
                "type": "file",
                "law": self._law,
                "value": self._file_material_path,
            },
        ]


class SchemeConverter2D(ComponentConverterXML2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        time_step: float,
        start_offset: float,
        total: float,
        scheme: str,
        hardware: str,
    ) -> None:
        super().__init__(xml, folder, domain_name)
        self._time_step = time_step
        self._start_offset = start_offset
        self._total = total

        use_tvd_gpu = scheme == "HPC" and hardware == "GPU"
        self._scheme = "TVD" if use_tvd_gpu else "ADI"
        self._processor = "GPU" if use_tvd_gpu else "CPU"

    def edit_fm_file(self) -> None:
        self._xml.domains[self._domain_name]["time"] = {
            "start_offset": self._start_offset,
            "total": self._total,
        }
        self._xml.domains[self._domain_name]["run_data"] = {
            "time_step": self._time_step,
            "scheme": self._scheme,
        }
        self._xml.processor = {"type": self._processor}


class BoundaryConverter2D(ComponentConverterXML2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        vectors: List[gpd.GeoDataFrame],
    ) -> None:
        super().__init__(xml, folder, domain_name)
