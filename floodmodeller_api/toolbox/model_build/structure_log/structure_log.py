from __future__ import annotations

import copy
import csv
import logging
from typing import TYPE_CHECKING

from floodmodeller_api import DAT

if TYPE_CHECKING:
    from floodmodeller_api._base import Unit
    from floodmodeller_api.units import (
        BRIDGE,
        CONDUIT,
        ORIFICE,
        REPLICATE,
        RNWEIR,
        SLUICE,
        SPILL,
        WEIR,
    )


def extract_attrs(object_input, keys):
    """Extract attributes and their values from a given object and return as a dict.

    No handling for where attributes don't exist but can ignore for when this is an issue, shouldn't be an issue here
    """
    return {key: getattr(object_input, key) for key in keys}


def serialise_keys(old_dict):
    """Exchange tuple keys in dict for string keys.

    Dictionary keys must be unique; but in FM the node label isn't always unique
    however the (label,type) pair will always be unique; so we have to use that as our key.
    json doesn't like tuples as keys so we have to convert them first if we need to serialise our dictionary output.

    Replaces tuple keys with string versions of themselves, wrapped in ()

    """
    return {f"({','.join(key)})": value for key, value in old_dict.items()}


class StructureLogBuilder:
    def __init__(self, input_path: str | None = None, output_path: str | None = None) -> None:
        self.dat_file_path = input_path
        self.csv_output_path = output_path
        self._conduit_chains: dict[str | None, list[str | None]] = {}
        self._already_in_chain: set[str | None] = set()
        self.unit_store: dict[(str, str)] = {}
        self._replicate_mimics: dict[str | None, str | None] = {}

    def _add_fields(self, writer) -> None:
        field = [
            "Unit Name",
            "Unit Type",
            "Unit Subtype",
            "Comment",
            "Friction",
            "Dimensions (m)",
            "Weir Coefficient",
            "Culvert Inlet/Outlet Loss",
        ]
        writer.writerow(field)

    def _conduit_data(self, conduit: CONDUIT | REPLICATE) -> tuple[dict, Unit | None]:
        conduit_data = {"length": conduit.dist_to_next}
        # modified conduit crawler script
        add_to_conduit_stack = None

        # check if the previous node is an inlet
        previous = self.dat.prev(conduit)
        if hasattr(previous, "subtype") and previous.subtype == "INLET":
            conduit_data["inlet"] = previous.ki

        current_conduit = conduit

        if current_conduit.name not in self._already_in_chain:
            # if this conduit isn't part of a chain already, then it must be part of a new chain
            total_length = 0
            chain = []
            while True:
                self._already_in_chain.add(current_conduit.name)
                chain.append(current_conduit.name)

                if current_conduit._unit not in ("CONDUIT", "REPLICATE"):
                    # This occurs in cases where a conduit chain doesnt 'legally' end.
                    break

                if current_conduit.dist_to_next == 0:
                    break

                total_length += current_conduit.dist_to_next
                current_conduit = self.dat.next(current_conduit)

            self._conduit_chains[conduit.name] = chain.copy()
            conduit_data["total_length"] = total_length

        next_conduit = self.dat.next(conduit)
        if next_conduit is not None:
            if hasattr(next_conduit, "subtype") and next_conduit.subtype == "OUTLET":
                conduit_data["outlet"] = next_conduit.loss_coefficient

            if next_conduit._unit == "REPLICATE":
                # for replicates, pass down the label of the unit it's copying from.
                if current_conduit._unit == "REPLICATE":
                    self._replicate_mimics[next_conduit.name] = self._replicate_mimics[
                        current_conduit.name
                    ]
                else:
                    self._replicate_mimics[next_conduit.name] = current_conduit.name

                # Replicates aren't in the DAT.structures dict so we need to add them manually.
                add_to_conduit_stack = copy.deepcopy(next_conduit)

        return conduit_data, add_to_conduit_stack

    def _circular_data(self, conduit: CONDUIT) -> dict:
        dimensions = extract_attrs(conduit, {"diameter", "invert"})
        all_friction = [
            conduit.friction_above_axis,
            conduit.friction_below_axis,
        ]
        friction_set = sorted(set(all_friction))
        friction = {
            "friction_eq": conduit.friction_eq,
            "friction_set": friction_set,
            "all_friction": all_friction,
        }

        return {"dimensions": dimensions, "friction": friction}

    def _sprungarch_data(self, conduit: CONDUIT) -> dict:
        dimensions = extract_attrs(
            conduit,
            {"width", "height_springing", "height_crown", "elevation_invert"},
        )
        # invert attribute is different for these, making homogenous
        dimensions["invert"] = dimensions.pop("elevation_invert")
        all_friction = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        friction_set = sorted(set(all_friction))
        friction = {
            "friction_eq": conduit.equation,
            "friction_set": friction_set,
            "all_friction": all_friction,
        }
        return {"dimensions": dimensions, "friction": friction}

    def _rectangular_data(self, conduit):
        dimensions = extract_attrs(conduit, {"width", "height", "invert"})
        all_friction = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        friction_set = sorted(set(all_friction))
        friction = {
            "friction_eq": conduit.friction_eq,
            "friction_set": friction_set,
            "all_friction": all_friction,
        }

        return {"dimensions": dimensions, "friction": friction}

    def _section_data(self, conduit: CONDUIT) -> dict:
        # Symmetrical conduits
        # these have a lot of weirdness in terms of data validity and FM will rearrange data that it thinks is wrong
        # so it's mostly worth just trusting the modeller here

        x_list = conduit.coords.x.tolist()
        y_list = conduit.coords.y.tolist()
        all_friction = conduit.coords.cw_friction.tolist()
        # want to serialise coords so converting out of dataframe
        width = max(x_list) * 2
        height = max(y_list) - min(y_list)
        elevation_invert = min(y_list)
        dimensions = {
            "width": width,
            "height": height,
            "invert": elevation_invert,
            "section_data": {"x": x_list, "y": y_list},
        }

        all_friction = conduit.coords.cw_friction.tolist()
        friction_set = sorted(set(all_friction))
        friction = {
            "friction_eq": "COLEBROOK-WHITE",
            "friction_set": friction_set,
            "all_friction": all_friction,
        }

        return {"dimensions": dimensions, "friction": friction}

    def _sprung_data(self, conduit: CONDUIT) -> dict:
        dimensions = extract_attrs(
            conduit,
            {"width", "height_springing", "height_crown", "elevation_invert"},
        )
        # invert attribute is different for these, making homogenous
        dimensions["invert"] = dimensions.pop("elevation_invert")
        all_friction = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        friction_set = sorted(set(all_friction))
        friction = {
            "friction_eq": conduit.equation,
            "friction_set": friction_set,
            "all_friction": all_friction,
        }

        return {"dimensions": dimensions, "friction": friction}

    def _replicate_data(self, replicate: REPLICATE) -> dict:
        dimensions = {
            "bed_level_drop": replicate.bed_level_drop,
            "mimic": self._replicate_mimics[replicate.name],
        }

        return {"dimensions": dimensions}

    def add_conduits(self):
        conduit_stack = copy.deepcopy(list(self.dat.conduits.values()))

        # this is a stack/while-loop because I want to add units to it as we go, to detail inline replicate units
        while len(conduit_stack) > 0:
            conduit = conduit_stack.pop(0)
            self.unit_store[(conduit.name, conduit._unit)] = {
                "name": conduit.name,
                "type": conduit._unit,
                "subtype": conduit.subtype,
                "comment": conduit.comment,
            }
            if (conduit._unit, conduit.subtype) not in [
                ("CONDUIT", "CIRCULAR"),
                ("CONDUIT", "SPRUNGARCH"),
                ("CONDUIT", "RECTANGULAR"),
                ("CONDUIT", "SECTION"),
                ("CONDUIT", "SPRUNG"),
                ("REPLICATE", None),
            ]:
                logging.warning(
                    "Conduit subtype: %s not currently supported in structure log",
                    conduit.subtype,
                )
                self._write(conduit.name, conduit._unit, conduit.subtype)
                continue
            conduit_dict, add_to_conduit_stack = self._conduit_data(conduit)
            self.unit_store[(conduit.name, conduit._unit)]["conduit_data"] = conduit_dict
            # now use individual functions to get friction and dimensional data in a way that is appropriate for each conduit type
            match (conduit._unit, conduit.subtype):
                case ("CONDUIT", "CIRCULAR"):
                    self.unit_store[(conduit.name, conduit._unit)] |= self._circular_data(conduit)
                case ("CONDUIT", "SPRUNGARCH"):
                    self.unit_store[(conduit.name, conduit._unit)] |= self._sprungarch_data(conduit)
                case ("CONDUIT", "RECTANGULAR"):
                    self.unit_store[(conduit.name, conduit._unit)] |= self._rectangular_data(conduit)  # fmt: skip
                case ("CONDUIT", "SECTION"):
                    self.unit_store[(conduit.name, conduit._unit)] |= self._section_data(conduit)
                case ("CONDUIT", "SPRUNG"):
                    self.unit_store[(conduit.name, conduit._unit)] |= self._sprung_data(conduit)
                case ("REPLICATE", None):
                    self.unit_store[(conduit.name, conduit._unit)] |= self._replicate_data(conduit)
                case _:
                    pass

            if add_to_conduit_stack is not None:
                conduit_stack.insert(0, add_to_conduit_stack)

    def _orifice_dimensions(self, structure: ORIFICE) -> dict:
        dimensions = {
            "shape": structure.shape,
            "invert": structure.invert,
            "soffit": structure.soffit,
            "bore_area": structure.bore_area,
        }
        dimensions["height"] = structure.soffit - structure.invert
        if structure.shape == "RECTANGLE":
            dimensions["width"] = structure.bore_area / dimensions["height"]
            dimensions["bore_area"] = structure.bore_area
        elif structure.shape == "CIRCULAR":
            dimensions["width"] = dimensions["height"]
            # calcuate bore area from given diameter
            dimensions["bore_area"] = (dimensions["height"] ** 2) * (3.1415 * 0.25)
        return {"dimensions": dimensions}

    def _spill_data(self, structure: SPILL) -> dict:
        x_list = structure.data.X.tolist()
        y_list = structure.data.Y.tolist()
        dimensions = {
            "invert": min(y_list),
            "width": max(x_list) - min(x_list),
            "weir_coefficient": structure.weir_coefficient,
            "section_data": {"x": x_list, "y": y_list},
        }
        return {"dimensions": dimensions}

    def _bridge_data(self, structure: BRIDGE) -> dict:
        section_df = structure.section_data
        all_friction = section_df["Mannings n"].tolist()
        friction_set = sorted(set(all_friction))
        friction = {"friction_set": friction_set, "all_friction": all_friction}

        orifice_data = extract_attrs(
            structure,
            {
                "orifice_flow",
                "orifice_lower_transition_dist",
                "orifice_upper_transition_dist",
                "orifice_discharge_coefficient",
            },
        )
        orifice_data["transition_width"] = (
            structure.orifice_upper_transition_dist + structure.orifice_lower_transition_dist
        )

        opening_data = []
        # if it has openings, not sure why it wouldn't but worth checking.
        if structure.opening_nrows > 0:
            opening_df = structure.opening_data
            # this isn't 'proper' for a df but there should be few rows and we're doing special stuff
            for _, row in opening_df.iterrows():
                opening = {}
                opening["width"] = row["Finish"] - row["Start"]

                temp_df = section_df.loc[
                    (row["Start"] <= section_df["X"]) & (section_df["X"] <= row["Finish"])
                ]
                opening["bed_minimum"] = temp_df["Y"].min()

                opening["soffit_level"] = row["Soffit Level"]
                opening["opening_height"] = opening["soffit_level"] - opening["bed_minimum"]

                opening_data.append(opening)

        culvert_data = []
        if hasattr(structure, "culvert_data") and structure.culvert_data.shape[0] > 1:
            for _, row in structure.culvert_data.iterrows():
                culvert = {
                    "invert": row["Invert"],
                    "soffit": row["Soffit"],
                    "bore_area": "Section Area",
                }
                culvert["height"] = culvert["soffit"] - culvert["invert"]
                culvert["average_width"] = culvert["bore_area"] / culvert["height"]
                culvert_data.append(culvert)

        return {
            "opening_data": opening_data,
            "friction": friction,
            "orifice_data": orifice_data,
            "culvert_data": culvert_data,
        }

    def _sluice_data(self, structure: SLUICE) -> dict:
        dimensions = extract_attrs(structure, {"crest_elevation", "weir_breadth", "weir_length"})

        return {"dimensions": dimensions}

    def _weir_data(self, structure: RNWEIR | WEIR) -> dict:
        dimensions = extract_attrs(structure, {"weir_elevation", "weir_breadth"})

        if structure._unit == "RNWEIR":
            dimensions |= extract_attrs(
                structure,
                {"weir_length", "upstream_crest_height", "downstream_crest_height"},
            )

        return {"dimensions": dimensions}

    def add_structures(self):
        for structure in self.dat.structures.values():
            self.unit_store[(structure.name, structure._unit)] = {
                "name": structure.name,
                "type": structure._unit,
                "subtype": structure.subtype,
                "comment": structure.comment,
            }
            if structure._unit == "ORIFICE":
                self.unit_store[(structure.name, structure._unit)] |= self._orifice_dimensions(
                    structure,
                )
            elif structure._unit == "SPILL":
                self.unit_store[(structure.name, structure._unit)] |= self._spill_data(structure)
            elif structure._unit == "SLUICE":
                self.unit_store[(structure.name, structure._unit)] |= self._sluice_data(structure)
            elif structure._unit in {"WEIR", "RNWEIR"}:
                self.unit_store[(structure.name, structure._unit)] |= self._weir_data(structure)
                # Need weir coefficient (the velocity attribute??)
            elif structure._unit == "BRIDGE":
                self.unit_store[(structure.name, structure._unit)] |= self._bridge_data(structure)
            else:
                logging.warning(
                    "Structure: %s not currently supported in structure log",
                    structure._unit,
                )
                self._write(structure.name, structure._unit, structure.subtype)
                continue

    def _format_friction(self, unit_dict):
        text = ""

        if "friction" not in unit_dict:
            return ""

        try:
            match unit_dict["friction"]["friction_eq"]:
                case "MANNING":
                    text += "Mannings: "
                case "COLEBROOK-WHITE":
                    text += "Colebrook-White: "
        except KeyError:
            text += "Mannings: "

        friction_set = unit_dict["friction"]["friction_set"]
        if len(friction_set) == 1:
            text += f"{friction_set[0]:.3f}"
        else:
            text += f"[min: {friction_set[0]:.3f}, max: {friction_set[-1]:.3f}]"

        return text

    def _format_bridge_dimensions(self, unit_dict):
        if len(unit_dict["opening_data"]) == 1:
            opening = unit_dict["opening_data"][0]
            height = opening["opening_height"]
            width = opening["width"]
            return f"h: {height:.2f} x w: {width:.2f}"

        text = ""

        for n, opening in enumerate(unit_dict["opening_data"]):
            height = opening["opening_height"]
            width = opening["width"]

            text += f"Opening {n+1}: h: {height:.2f} x w: {width:.2f} "

        return text.rstrip()

    def _format_orifice_dimensions(self, unit_dict):
        height = unit_dict["dimensions"]["height"]
        width = unit_dict["dimensions"]["width"]
        match unit_dict["dimensions"]["shape"]:
            case "RECTANGLE":
                return f"h: {height:.2f} x w: {width:.2f}"
            case "CIRCULAR":
                return f"dia: {width:.2f}"

    def _format_spill_dimensions(self, unit_dict):
        invert = unit_dict["dimensions"]["invert"]
        width = unit_dict["dimensions"]["width"]

        return f"Elevation: {invert:.2f} x w: {width:.2f}"

    def _format_weir_dimensions(self, unit_dict):
        text = ""
        elevation = unit_dict["dimensions"]["weir_elevation"]
        breadth = unit_dict["dimensions"]["weir_breadth"]

        text += f"Crest Elevation: {elevation:.2f} x w: {breadth:.2f}"

        if "weir_length" in unit_dict["dimensions"]:
            length = unit_dict["dimensions"]["weir_length"]
            text += f" x l: {length:.2f}"
        return text

    def _format_sluice_dimensions(self, unit_dict):
        elevation = unit_dict["dimensions"]["crest_elevation"]
        breadth = unit_dict["dimensions"]["weir_breadth"]
        length = unit_dict["dimensions"]["weir_length"]

        return f"Crest Elevation: {elevation:.2f} x w: {breadth:.2f} x l: {length:.2f}"

    def _format_conduit_dimensions(self, unit_dict):
        text = ""
        culvert_loss = ""
        match unit_dict["subtype"]:
            case "CIRCULAR":
                text += f'dia: {unit_dict["dimensions"]["diameter"]:.2f} x l: {unit_dict["conduit_data"]["length"]:.2f}'
            case "SPRUNGARCH" | "SPRUNG":
                text += f'(Springing: {unit_dict["dimensions"]["height_springing"]:.2f}, Crown: {unit_dict["dimensions"]["height_crown"]:.2f}) x w: {unit_dict["dimensions"]["width"]:.2f} x l: {unit_dict["conduit_data"]["length"]:.2f}'
            case "RECTANGULAR":
                text += f'h: {unit_dict["dimensions"]["height"]:.2f} x w: {unit_dict["dimensions"]["width"]:.2f} x l: {unit_dict["conduit_data"]["length"]:.2f}'
            case "SECTION":
                text += f'h: {unit_dict["dimensions"]["height"]:.2f} x w: {unit_dict["dimensions"]["width"]:.2f} x l: {unit_dict["conduit_data"]["length"]:.2f}'
            case _:
                return "", ""

        if "total_length" in unit_dict["conduit_data"]:
            text += f' (Total conduit length: {unit_dict["conduit_data"]["total_length"]:.2f})'

        if "inlet" in unit_dict["conduit_data"]:
            culvert_loss += f'Ki: {unit_dict["conduit_data"]["inlet"]}, '

        if "outlet" in unit_dict["conduit_data"]:
            culvert_loss += f'Ko: {unit_dict["conduit_data"]["outlet"]}, '

        culvert_loss = culvert_loss.rstrip(", ")

        return text, culvert_loss

    def _write(  # noqa: PLR0913
        self,
        writer,
        name,
        unit,
        subtype,
        comment="",
        friction="",
        dimensions="",
        weir_coefficient="",
        culvert_loss="",
    ):
        writer.writerow(
            [
                name,
                unit,
                subtype,
                comment,
                friction,
                dimensions,
                weir_coefficient,
                culvert_loss,
            ],
        )

    def write_csv_output(self, file):
        """
        Take the current state of the instance (unit_store etc) and write it to the specified output file.
        """

        writer = csv.writer(file)

        self._add_fields(writer)

        for unit_dict in self.unit_store.values():
            name = unit_dict["name"]
            unit_type = unit_dict["type"]
            subtype = unit_dict["subtype"]
            comment = unit_dict["comment"]

            friction = self._format_friction(unit_dict)

            culvert_loss = ""

            match unit_type:
                case "BRIDGE":
                    dimensions = self._format_bridge_dimensions(unit_dict)
                case "ORIFICE":
                    dimensions = self._format_orifice_dimensions(unit_dict)
                case "WEIR" | "RNWEIR":
                    dimensions = self._format_weir_dimensions(unit_dict)
                case "SLUICE":
                    dimensions = self._format_sluice_dimensions(unit_dict)
                case "SPILL":
                    dimensions = self._format_spill_dimensions(unit_dict)
                case "CONDUIT":
                    dimensions, culvert_loss = self._format_conduit_dimensions(unit_dict)
                case _:
                    dimensions = ""

            try:
                weir_coefficient = unit_dict["dimensions"]["weir_coefficient"]
            except KeyError:
                weir_coefficient = ""

            self._write(
                writer,
                name,
                unit_type,
                subtype,
                comment,
                friction,
                dimensions,
                weir_coefficient,
                culvert_loss,
            )

    def create(self):
        """
        When using the toolbox wrapper or commandline entry point, this is the entrypoint to the structure logger code
        """
        self.dat = DAT(self.dat_file_path)
        self.add_conduits()
        self.add_structures()
        with open(self.csv_output_path, "w", newline="") as file:
            self.write_csv_output(file)
