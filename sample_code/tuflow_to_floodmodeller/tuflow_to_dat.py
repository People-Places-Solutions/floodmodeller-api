from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import LineString, Point

from floodmodeller_api.units._helpers import to_float
from floodmodeller_api.units.comment import COMMENT
from floodmodeller_api.units.conduits import CONDUIT
from floodmodeller_api.units.sections import RIVER

if TYPE_CHECKING:
    from floodmodeller_api import DAT


class TuflowToDat:
    def _process_shapefile(self, path):
        attributes = gpd.read_file(path)
        return attributes.dropna(how="all", axis=1)

    def _read_in(self, model_path, nwk_paths, xs_paths):
        #   File paths for model, xs and nwk, read in

        self._model_path = model_path
        self._nwk_paths = nwk_paths
        self._xs_paths = xs_paths
        self._xs_attributes = pd.concat([self._process_shapefile(shp) for shp in self._xs_paths])
        self._nwk_attributes = pd.concat([self._process_shapefile(shp) for shp in self._nwk_paths])

    def _clean_df_1(self):
        #   Clean up dataframes
        self._culvert_attributes = self._nwk_attributes.query(
            "Type.str.lower() == 'r' | Type.str.lower() == 'c'",
        )
        self._nwk_attributes = self._nwk_attributes.query("Type.str.lower() == 's'")

        self._nwk_attributes = self._nwk_attributes.dropna(subset=["geometry"])
        self._xs_attributes = self._xs_attributes.dropna(subset=["geometry"])
        self._culvert_attributes = self._culvert_attributes.dropna(subset=["geometry"])
        if self._nwk_attributes.unary_union is not None:
            self._xs_attributes = self._xs_attributes[
                self._xs_attributes.intersects(self._nwk_attributes.unary_union)
            ]

    def _extract_geometry_data(self):
        #   Extract geometry data
        self._nwk_attributes["length"] = self._nwk_attributes.length
        self._nwk_attributes["start"] = self._nwk_attributes["geometry"].apply(
            lambda g: Point(g.coords[0]),
        )
        self._nwk_attributes["end"] = self._nwk_attributes["geometry"].apply(
            lambda g: Point(g.coords[-1]),
        )
        self._culvert_attributes["start"] = self._culvert_attributes["geometry"].apply(
            lambda g: Point(g.coords[0]),
        )
        self._culvert_attributes["end"] = self._culvert_attributes["geometry"].apply(
            lambda g: Point(g.coords[-1]),
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
                self._xs_attributes.loc[index, "intersect"] = row["mid_intersect"]

    def _find_ds_intersect(self):
        #   nwk find connected network line ds
        self._nwk_attributes["connected"] = [[]] * len(self._nwk_attributes)
        self._nwk_attributes["Flag"] = ""

        for i, row in self._nwk_attributes.iterrows():
            end_point = row["end"]
            intersected_rows = self._nwk_attributes[
                ~(self._nwk_attributes.index == i)
                & self._nwk_attributes.geometry.intersects(end_point)
            ]
            next_ids = intersected_rows["ID"].tolist()
            self._nwk_attributes.loc[i, "connected"] = next_ids

    def _find_us_intersect(self):
        #   Find the us connection
        self._nwk_attributes["before"] = [[]] * len(self._nwk_attributes)

        for i, row in self._nwk_attributes.iterrows():
            start_point = row["start"]
            intersected_rows = self._nwk_attributes[
                ~(self._nwk_attributes.index == i)
                & self._nwk_attributes.geometry.intersects(start_point)
            ]
            previous_ids = intersected_rows["ID"].tolist()
            self._nwk_attributes.loc[i, "before"] = previous_ids

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
                filtered_df["ID"][filtered_df["connected"].apply(lambda x: len(x) == 1)],
            ),
            "Flag",
        ] = "join_start"
        self._nwk_attributes.loc[
            self._nwk_attributes["ID"].isin(
                filtered_df["ID"][filtered_df["connected"].apply(lambda x: len(x) != 1)],
            ),
            "Flag",
        ] = "join_end"
        self._nwk_attributes.loc[
            self._nwk_attributes["connected"].apply(lambda x: len(x) == 0),
            "Flag",
        ] = "end"
        self._nwk_attributes.loc[
            self._nwk_attributes["before"].apply(lambda x: len(x) == 0),
            "Flag",
        ] = "start"

        non_empty_rows = self._nwk_attributes[self._nwk_attributes["Flag"] != ""]
        id_flag_dict = non_empty_rows.set_index("ID")[["Flag", "n_nF_Cd", "length", "end"]].to_dict(
            orient="index",
        )
        self._full_flag_dict = self._nwk_attributes.set_index("ID")[
            ["Flag", "n_nF_Cd", "length", "start", "end"]
        ].to_dict(orient="index")

        self._end_dict = {
            key: value for key, value in id_flag_dict.items() if value["Flag"] == "end"
        }
        self._start_dict = {
            key: value for key, value in id_flag_dict.items() if value["Flag"] == "start"
        }
        self._join_start_dict = {
            key: value for key, value in id_flag_dict.items() if value["Flag"] == "join_start"
        }
        self._join_end_dict = {
            key: value for key, value in id_flag_dict.items() if value["Flag"] == "join_end"
        }

    def _add_to_xs_data(self):
        #   add to the xs data
        self._xs_attributes["Flag"] = ""
        self._xs_attributes.loc[
            self._xs_attributes["end_intersect"].isin(self._end_dict.keys()),
            "Flag",
        ] = "end"
        self._xs_attributes.loc[
            self._xs_attributes["intersect"].isin(self._start_dict.keys()),
            "Flag",
        ] = "start"
        self._xs_attributes.loc[
            self._xs_attributes["intersect"].isin(self._join_end_dict.keys()),
            "Flag",
        ] = "join_end"
        self._xs_attributes.loc[
            self._xs_attributes["intersect"].isin(self._join_start_dict.keys()),
            "Flag",
        ] = "join_start"

        self._xs_attributes["dist_to_next"] = ""
        self._xs_attributes["mannings"] = ""
        self._xs_attributes["location"] = ""
        self._xs_attributes["end_point"] = ""
        for key, values in self._full_flag_dict.items():
            mask = self._xs_attributes["intersect"] == key
            self._xs_attributes.loc[mask, "dist_to_next"] = values["length"]
            self._xs_attributes.loc[mask, "mannings"] = values["n_nF_Cd"]
            self._xs_attributes.loc[mask, "location"] = values["start"].wkt
            self._xs_attributes.loc[mask, "end_point"] = values["end"].wkt

        self._xs_attributes["dist_to_next"] = self._xs_attributes["dist_to_next"].replace(
            "",
            0,
            regex=True,
        )
        for key, values in self._end_dict.items():
            mask = self._xs_attributes["end_intersect"] == key
            self._xs_attributes.loc[mask, "mannings"] = values["n_nF_Cd"]
            self._xs_attributes.loc[mask, "location"] = values["end"].wkt
            self._xs_attributes.loc[mask, "end_point"] = values["end"].wkt

        self._xs_attributes["location"] = self._xs_attributes["location"].apply(wkt.loads)
        self._xs_attributes["end_point"] = self._xs_attributes["end_point"].apply(wkt.loads)

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

    def _organise_df(self):
        # FIXME: Currently works but misses out last XS in series
        #   organise df
        self._xs_attributes["order"] = 0
        order_counter = 1
        for i, row in self._xs_attributes.iterrows():
            # Check if the row is a start or join_start
            if not ("start" in row["Flag"] or "join_start" in row["Flag"]):
                continue
            self._xs_attributes.loc[i, "order"] = order_counter
            order_counter += 1
            intersect_value = row["intersect"]
            next_row_index = self._xs_attributes[
                (self._xs_attributes["end_intersect"] == intersect_value)
                & (self._xs_attributes["Flag"] == "")
            ].index
            while not next_row_index.empty:
                next_row_index = next_row_index[0]
                self._xs_attributes.loc[next_row_index, "order"] = order_counter
                order_counter += 1

                intersect_value = self._xs_attributes.loc[next_row_index, "intersect"]
                next_row_index = self._xs_attributes[
                    (self._xs_attributes["end_intersect"] == intersect_value)
                    & (self._xs_attributes["Flag"] == "")
                ].index

            if next_row_index.empty:
                next_row_index = self._xs_attributes[
                    self._xs_attributes["end_intersect"] == intersect_value
                ].index
                next_row_index = next_row_index[0]
                self._xs_attributes.loc[next_row_index, "order"] = order_counter
                order_counter += 1
                self._xs_attributes.loc[next_row_index, "order"] = order_counter
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
        rows_to_add = []
        for _, row in self._cross_sections.iterrows():
            unit_csv_name = str(row["Source"])
            unit_csv = pd.read_csv(
                Path(self._xs_paths[0].parent, unit_csv_name).resolve(),
                skiprows=[0],
            )
            unit_csv.columns = ["X", "Z"]
            unit_data = pd.DataFrame(columns=self._headings)
            unit_data["X"] = unit_csv["X"]
            unit_data["Y"] = unit_csv["Z"]
            unit_data["Mannings n"] = row["mannings"]
            unit_data["Panel"] = unit_data["Panel"].fillna(False)
            unit_data["RPL"] = unit_data["RPL"].fillna(1.0)
            unit_data["Marker"] = unit_data["Marker"].fillna(False)
            unit_data["SP. Marker"] = unit_data["SP. Marker"].fillna(0)

            unit = RIVER(
                name=row["Name"],
                data=unit_data,
                density=1000.0,
                dist_to_next=row["dist_to_next"],
                slope=0.0001,
            )
            self._dat.insert_unit(unit, add_at=-1)
            if row["Flag"] == "end" or row["Flag"] == "join_end":
                if row["dist_to_next"] > 0:
                    # End of reach but still needs an extra section to close
                    unit = RIVER(
                        name=f"{row['Name']}d",
                        data=unit_data,
                        density=1000.0,
                        dist_to_next=0,
                        slope=0.0001,
                    )
                    self._dat.insert_unit(unit, add_at=-1)
                    new_row = row.to_dict()
                    new_row["Name"] = f"{row['Name']}d"
                    new_row["dist_to_next"] = 0.0
                    reach = LineString([new_row["location"], new_row["end_point"]])
                    new_point = reach.line_interpolate_point(0.9, normalized=True)
                    new_row["easting"] = new_point.coords[0][0]
                    new_row["northing"] = new_point.coords[0][1]

                    rows_to_add.append(new_row)
                self._dat.insert_unit(self._comment, add_at=-1)

        # Add extra cross section rows
        self._cross_sections = pd.concat([self._cross_sections, pd.DataFrame(rows_to_add)])

    def _add_culverts(self):
        self._culvert_comment = COMMENT(text="End of Culvert")
        # iterate through adding xs
        for index, row in self._culvert_attributes.iterrows():
            if row["Type"] == "R":
                subtype = "RECTANGULAR"
                width = to_float(row["Width_or_D"])
                height = to_float(row["Height_or_"])
                friction_on_walls = to_float(row["n_nF_Cd"])
                friction_on_invert = to_float(row["n_nF_Cd"])
                friction_on_soffit = to_float(row["n_nF_Cd"])
            elif row["Type"] == "C":
                subtype = "CIRCULAR"
                diameter = to_float(row["Width_or_D"])
                friction_below_axis = to_float(row["n_nF_Cd"])
                friction_above_axis = to_float(row["n_nF_Cd"])
            else:
                continue
            comment = ""
            name = f"UNIT{index:03d}"
            spill = ""
            length = row["Len_or_ANA"]
            dist_to_next = 0.0
            friction_eq = "MANNING"
            invert = 0.0

            for i in range(2):
                if i == 0:
                    name_ud = name + "u"
                    next_dist = length
                    invert = to_float(row["US_Invert"])
                else:
                    name_ud = name + "d"
                    next_dist = dist_to_next
                    invert = to_float(row["DS_Invert"])

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
        for _, row in self._cross_sections.iterrows():
            file_contents += f"[RIVER_SECTION_{row['Name']}]\n"
            file_contents += f"x={row['easting']:.2f}\n"
            file_contents += f"y={row['northing']:.2f}\n\n"

        for index, row in self._culvert_attributes.iterrows():
            if row["Type"] == "R":
                subtype = "RECTANGULAR"
            elif row["Type"] == "C":
                subtype = "CIRCULAR"
                # add circular *params
            else:
                continue
            # upstream conduit for the culvert
            file_contents += f"[CONDUIT_{subtype}_UNIT{index:03d}u]\n"
            file_contents += f"x={row['start'].x:.2f}\n"
            file_contents += f"y={row['start'].y:.2f}\n"
            # downstream conduit for the culvert
            file_contents += f"[CONDUIT_{subtype}_UNIT{index:03d}d]\n"
            file_contents += f"x={row['end'].x:.2f}\n"
            file_contents += f"y={row['end'].y:.2f}\n"

        self._dat._gxy_data = file_contents

    def convert(
        self,
        model_path: str,
        nwk_paths: list[Path],
        xs_paths: list[Path],
        empty_dat: DAT,
    ):
        self._read_in(model_path, nwk_paths, xs_paths)

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
