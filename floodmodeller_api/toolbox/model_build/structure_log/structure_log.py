import csv

from floodmodeller_api import DAT


class StructureLogBuilder:
    def __init__(self, input_path, output_path) -> None:
        self.dat_file_path = input_path
        self.csv_output_path = output_path

    def _add_fields(self):
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
        self._writer.writerow(field)

    def _conduit_data(self, conduit):
        length = 0.0
        inlet = ""
        outlet = ""
        previous = self._dat.prev(conduit)
        if hasattr(previous, "subtype") and previous.subtype == "INLET":
            inlet = previous.ki
        current_conduit = conduit
        while current_conduit.dist_to_next != 0:
            length += current_conduit.dist_to_next
            current_conduit = self._dat.next(current_conduit)
        next_conduit = self._dat.next(current_conduit)
        if hasattr(next_conduit, "subtype") and next_conduit.subtype == "OUTLET":
            outlet = next_conduit.loss_coefficient
        return [length, inlet, outlet]

    def _culvert_loss_data(self, inlet, outlet):
        culvert_loss = ""
        if inlet != "" and outlet != "":
            culvert_loss = f"Ki: {inlet}, Ko: {outlet}"
        elif inlet != "":
            culvert_loss = f"Ki: {inlet}"
        elif outlet != "":
            culvert_loss = f"Ko: {outlet}"
        return culvert_loss

    def _circular_data(self, conduit, length):
        dimensions = f"dia: {conduit.diameter:.2f} x l: {length:.2f}"
        all_mannings = [
            conduit.friction_above_axis,
            conduit.friction_below_axis,
        ]
        mannings_set = {min(all_mannings), max(all_mannings)}
        if len(mannings_set) == 1:
            friction = f"Mannings: {mannings_set.pop()}"
        else:
            friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"

        return [friction, dimensions]

    def _sprungarch_data(self, conduit, length):
        dimensions = f"(Springing: {conduit.height_crown:.2f}, Crown: {conduit.height_springing:.2f}) x w: {conduit.width:.2f} x l: {length:.2f}"
        all_mannings = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        mannings_set = {min(all_mannings), max(all_mannings)}
        if len(mannings_set) == 1:
            friction = f"Mannings: {mannings_set.pop()}"
        else:
            friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"

        return [friction, dimensions]

    def _rectangular_data(self, conduit, length):
        dimensions = f"h: {conduit.height:.2f} x w: {conduit.width:.2f} x l: {length:.2f}"
        all_mannings = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        mannings_set = {min(all_mannings), max(all_mannings)}
        if len(mannings_set) == 1:
            friction = f"Mannings: {mannings_set.pop()}"
        else:
            friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"

        return [friction, dimensions]

    def _section_data(self, conduit, length):
        x_list = conduit.coords.x.tolist()
        width = (max(x_list) - min(x_list)) * 2
        y_list = conduit.coords.y.tolist()
        height = max(y_list) - min(y_list)
        # currently this means that height goes to the top of the spike,
        # it is only meant to go up to the height of the majority of the area
        dimensions = f"h: {height:.2f} x w: {width:.2f} x l: {length:.2f}"
        all_cw_frictions = conduit.coords.cw_friction.tolist()
        cw_frictions_set = {min(all_cw_frictions), max(all_cw_frictions)}
        if len(cw_frictions_set) == 1:
            friction = f"Colebrook-White: {cw_frictions_set.pop()}"
        else:
            friction = (
                f"Colebrook-White: [min: {cw_frictions_set.pop()}, max: {cw_frictions_set.pop()}]"
            )

        return [friction, dimensions]

    def _sprung_data(self, conduit, length):
        dimensions = f"(Springing: {conduit.height_crown:.2f}, Crown: {conduit.height_springing:.2f}) x w: {conduit.width:.2f} x l: {length:.2f}"
        all_mannings = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        mannings_set = {min(all_mannings), max(all_mannings)}
        if len(mannings_set) == 1:
            friction = f"Mannings: {mannings_set.pop()}"
        else:
            friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"

        return [friction, dimensions]

    def _add_conduits(self):
        for conduit in self._dat.conduits.values():
            if conduit.subtype not in [
                "CIRCULAR",
                "SPRUNGARCH",
                "RECTANGULAR",
                "SECTION",
                "SPRUNG",
            ]:
                print(f"Conduit subtype: {conduit.subtype} not currently supported")
                self._write(conduit.name, conduit._unit, conduit.subtype)
                continue
            conduit_data = self._conduit_data(conduit)
            length = conduit_data[0]
            inlet = conduit_data[1]
            outlet = conduit_data[2]

            if length == 0:
                continue

            culvert_loss = self._culvert_loss_data(inlet, outlet)
            friction = ""
            dimensions = ""
            if conduit.subtype == "CIRCULAR":
                circular_data = self._circular_data(conduit, length)
                friction = circular_data[0]
                dimensions = circular_data[1]
            elif conduit.subtype == "SPRUNGARCH":
                sprungarch_data = self._sprungarch_data(conduit, length)
                friction = sprungarch_data[0]
                dimensions = sprungarch_data[1]
            elif conduit.subtype == "RECTANGULAR":
                rectangular_data = self._rectangular_data(conduit, length)
                friction = rectangular_data[0]
                dimensions = rectangular_data[1]
            elif conduit.subtype == "SECTION":
                section_data = self._section_data(conduit, length)
                friction = section_data[0]
                dimensions = section_data[1]
            elif conduit.subtype == "SPRUNG":
                sprung_data = self._sprung_data(conduit, length)
                friction = sprung_data[0]
                dimensions = sprung_data[1]

            self._write(
                conduit.name,
                conduit._unit,
                conduit.subtype,
                conduit.comment,
                friction,
                dimensions,
                "",
                culvert_loss,
            )

    def _orifice_dimensions(self, structure):
        if structure.shape == "RECTANGLE":
            height = structure.soffit - structure.invert
            width = structure.bore_area / height
            dimensions = f"h: {height:.2f} x w: {width:.2f}"
        elif structure.shape == "CIRCULAR":
            diameter = structure.soffit - structure.invert
            dimensions = f"dia: {diameter:.2f}"
        return dimensions

    def _spill_data(self, structure):
        elevation = min(structure.data.Y.tolist())
        x_list = structure.data.X.tolist()
        width = max(x_list) - min(x_list)
        dimensions = f"Elevation: {elevation:.2f} x w: {width:.2f}"
        weir_coefficient = structure.weir_coefficient
        return [dimensions, weir_coefficient]

    def _bridge_data(self, structure):
        all_mannings = structure.section_data["Mannings n"].tolist()
        mannings_set = {min(all_mannings), max(all_mannings)}
        if len(mannings_set) == 1:
            friction = f"Mannings: {mannings_set.pop()}"
        else:
            friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"
        height = structure.opening_data.values[0][3] - min(structure.section_data.Y.tolist())
        width = structure.opening_data.values[0][1] - structure.opening_data.values[0][0]
        dimensions = f"h: {height:.2f} x w: {width:.2f}"
        return [friction, dimensions]

    def _add_structures(self):
        for structure in self._dat.structures.values():
            friction = ""
            dimensions = ""
            weir_coefficient = ""
            if structure._unit == "ORIFICE":
                dimensions = self._orifice_dimensions(structure)
            elif structure._unit == "SPILL":
                spill_data = self._spill_data(structure)
                dimensions = spill_data[0]
                weir_coefficient = spill_data[1]
            elif structure._unit == "SLUICE":
                dimensions = f"Crest Elevation: {structure.crest_elevation:.2f} x w: {structure.weir_breadth:.2f} x l: {structure.weir_length:.2f}"
            elif structure._unit == "RNWEIR":
                dimensions = f"Crest Elevation: {structure.weir_elevation:.2f} x w: {structure.weir_breadth:.2f} x l: {structure.weir_length:.2f}"
            elif structure._unit == "WEIR":
                dimensions = f"Crest Elevation: {structure.weir_elevation:.2f} x w: {structure.weir_breadth:.2f}"
                # Need weir coefficient (the velocity attribute??)
            elif structure._unit == "BRIDGE":
                bridge_data = self._bridge_data(structure)
                friction = bridge_data[0]
                dimensions = bridge_data[1]
            else:
                print(f"Structure: {structure._unit} not currently supported in structure log")
                self._write(structure.name, structure._unit, structure.subtype)
                continue

            self._write(
                structure.name,
                structure._unit,
                structure.subtype,
                structure.comment,
                friction,
                dimensions,
                weir_coefficient,
                "",
            )

    def _write(  # noqa: PLR0913
        self,
        name,
        unit,
        subtype,
        comment="",
        friction="",
        dimensions="",
        weir_coefficient="",
        culvert_loss="",
    ):
        self._writer.writerow(
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

    def create(self):
        # Read in the .dat file
        self._dat = DAT(self.dat_file_path)

        # Create a new .csv file
        with open(self.csv_output_path, "w", newline="") as file:
            self._writer = csv.writer(file)

            self._add_fields()

            self._add_conduits()

            self._add_structures()
