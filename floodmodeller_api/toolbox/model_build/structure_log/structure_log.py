import csv
import copy
import json

from floodmodeller_api import DAT

def extract_attrs(object,keys):
        """
        extract attributes and their values from a given object and return as a dict

        No handling for where attributes dont exist but can ignore for when this is an issue, shouldnt be an issue here
        """
        return {key:getattr(object,key) for key in keys}

class StructureLogBuilder:

    def __init__(self, input_path, output_path) -> None:
        self.dat_file_path = input_path
        self.csv_output_path = output_path
        self.conduit_chains = (
            {}
        )  # pylint flags these for type hinting, but not sure how to specify, to discuss
        self.already_in_chain = set()

        self.unit_store = {}

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
        # modified conduit crawler script
        length = conduit.dist_to_next
        inlet = ""
        outlet = ""
        total_length = 0.0
        add_to_conduit_stack = None

        # check if the previous node is an inlet
        previous = self._dat.prev(conduit)
        if hasattr(previous, "subtype") and previous.subtype == "INLET":
            inlet = previous.ki

        current_conduit = conduit
        # check if the
        if current_conduit.name not in self.already_in_chain:
            chain = []
            while True:
                self.already_in_chain.add(current_conduit.name)
                chain.append(current_conduit.name)
                if current_conduit.dist_to_next == 0:
                    break

                total_length += current_conduit.dist_to_next
                current_conduit = self._dat.next(current_conduit)

            self.conduit_chains[conduit.name] = chain.copy()

        next_conduit = self._dat.next(conduit)
        if next_conduit is not None:
            if hasattr(next_conduit, "subtype") and next_conduit.subtype == "OUTLET":
                outlet = next_conduit.loss_coefficient
            
            if next_conduit._unit == "REPLICATE":
                # for replicates, pass down the label of the unit its copying from.
                if current_conduit._unit == "REPLICATE":
                    next_conduit.mimic = current_conduit.mimic
                else:
                    next_conduit.mimic = current_conduit.name
                add_to_conduit_stack = copy.deepcopy(next_conduit)

        return {"length":length, "inlet":inlet, "outlet":outlet, "total_length":total_length}, add_to_conduit_stack

    def _culvert_loss_data(self, inlet, outlet):
        culvert_loss = ""
        if inlet != "" and outlet != "":
            culvert_loss = f"Ki: {inlet}, Ko: {outlet}"
        elif inlet != "":
            culvert_loss = f"Ki: {inlet}"
        elif outlet != "":
            culvert_loss = f"Ko: {outlet}"
        return culvert_loss

    def _circular_data(self, conduit):
        dimensions = extract_attrs(conduit,{"diameter","invert"})
        all_friction = [
            conduit.friction_above_axis,
            conduit.friction_below_axis,
        ]
        friction_set = sorted(set(all_friction))
        friction = {"friction_eq":conduit.friction_eq,"friction_set":friction_set,"all_friction":all_friction}

        return {"dimensions":dimensions, "friction": friction}

    def _sprungarch_data(self, conduit):
        dimensions = extract_attrs(conduit,{"width","height_springing","height_crown","elevation_invert"})
        dimensions["invert"] = dimensions.pop("elevation_invert") # invert attribute is different for these, making homogenous
        all_friction = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        friction_set = sorted(set(all_friction))
        friction = {"friction_eq":conduit.equation,"friction_set":friction_set,"all_friction":all_friction}
        return {"dimensions":dimensions, "friction": friction}

    def _rectangular_data(self, conduit):
        dimensions = extract_attrs(conduit,{"width","height","invert"})
        all_friction = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        friction_set = sorted(set(all_friction))
        friction = {"friction_eq":conduit.friction_eq,"friction_set":friction_set,"all_friction":all_friction}

        return {"dimensions":dimensions, "friction": friction}

    def _section_data(self, conduit):
        # Symmetrical conduits
        # these have a lot of weirdness in terms of data validity and FM will rearrange data that it thinks is wrong; so its mostly worth just trusting the modeller here

        x_list = conduit.coords.x.tolist()
        y_list = conduit.coords.y.tolist()
        all_friction = conduit.coords.cw_friction.tolist()
        # want to serialise coords so converting out of dataframe
        width = max(x_list) * 2 
        height = max(y_list) - min(y_list)
        elevation_invert = min(y_list)
        dimensions = {"width":width, "height":height,"invert":elevation_invert,"section_data": {"x":x_list,"y":y_list}}

        all_friction = conduit.coords.cw_friction.tolist()
        friction_set = sorted(set(all_friction))
        friction = {"friction_eq":"COLEBROOK-WHITE","friction_set":friction_set,"all_friction":all_friction} # friction should be CW here; should test this

        return {"dimensions":dimensions, "friction": friction}

    def _sprung_data(self, conduit):
        dimensions = extract_attrs(conduit,{"width","height_springing","height_crown","elevation_invert"})
        dimensions["invert"] = dimensions.pop("elevation_invert") # invert attribute is different for these, making homogenous
        all_friction = [
            conduit.friction_on_invert,
            conduit.friction_on_soffit,
            conduit.friction_on_walls,
        ]
        friction_set = sorted(set(all_friction))
        friction = {"friction_eq":conduit.equation,"friction_set":friction_set,"all_friction":all_friction}

        return {"dimensions":dimensions, "friction": friction}
    
    def _replicate_data(self,conduit):
         # if we get to this point, the replicate unit should have the .mimic attribute that we've tacked on
        dimensions = {"bed_level_drop":conduit.bed_level_drop,"mimic":conduit.mimic}

        return {"dimensions":dimensions}

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
                self.unit_store[conduit.name] = {"name":conduit.name, "type":conduit._unit, "subtype":conduit.subtype}
                continue
            conduit_data = self._conduit_data(conduit)
            length = conduit_data["length"]
            inlet = conduit_data["inlet"]
            outlet = conduit_data["outlet"]
            total_length = conduit_data["total_length"]

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

            if total_length > 0:
                chain = self.conduit_chains[conduit.name]
                dimensions += f" (Total length between {chain[0]} and {chain[-1]}: {total_length}m)"

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

    def _add_conduits(self):
        conduit_stack = copy.deepcopy(list(self._dat.conduits.values()))
        while len(conduit_stack) > 0: # this is a list because I want to add units to it as we go, to detail inline replicate units
            conduit = conduit_stack.pop(0)
            self.unit_store[conduit.name] = {"name":conduit.name, "type":conduit._unit, "subtype":conduit.subtype}
            if (conduit._unit,conduit.subtype) not in [
                    ("CONDUIT","CIRCULAR"),
                    ("CONDUIT","SPRUNGARCH"),
                    ("CONDUIT","RECTANGULAR"),
                    ("CONDUIT","SECTION"),
                    ("CONDUIT","SPRUNG"),
                    ("REPLICATE",None)
                ]:
                print(f"Conduit subtype: {conduit.subtype} not currently supported")
                continue
            conduit_dict, add_to_conduit_stack = self._conduit_data(conduit)
            self.unit_store[conduit.name]["conduit_data"] = conduit_dict
            # now use individual functions to get friction and dimensional data in a way that is appropriate for each conduit type
            match (conduit._unit,conduit.subtype):
                case ("CONDUIT","CIRCULAR"):
                    self.unit_store[conduit.name] |= self._circular_data(conduit)
                case ("CONDUIT","SPRUNGARCH"):
                    self.unit_store[conduit.name] |= self._sprungarch_data(conduit)
                case ("CONDUIT","RECTANGULAR"):
                    self.unit_store[conduit.name] |= self._rectangular_data(conduit)
                case ("CONDUIT","SECTION"):
                    self.unit_store[conduit.name] |= self._section_data(conduit)
                case ("CONDUIT","SPRUNG"):
                    self.unit_store[conduit.name] |= self._sprung_data(conduit)
                case ("REPLICATE",None):
                    self.unit_store[conduit.name] |= self._replicate_data(conduit)
                case _:
                    pass
            
            if add_to_conduit_stack is not None:
                conduit_stack.insert(0,add_to_conduit_stack)
            

    def _orifice_dimensions(self, structure):
        dimensions = {"shape": structure.shape,"invert":structure.invert,"soffit":structure.soffit,"bore_area":structure.bore_area}
        dimensions["height"] = structure.soffit - structure.invert
        if structure.shape == "RECTANGLE":
            dimensions["width"] = structure.bore_area / dimensions["height"]
            dimensions["bore_area"] = structure.bore_area
        elif structure.shape == "CIRCULAR":
            dimensions["width"] = dimensions["height"]
            dimensions["bore_area"] = (dimensions["height"]**2) * (3.1415 * 0.25) # calcuate bore area from given diameter
        return {"dimensions":dimensions}

    def _spill_data(self, structure):
        x_list = structure.data.X.tolist()
        y_list = structure.data.Y.tolist()
        dimensions = {"invert": min(y_list),"width":max(x_list) - min(y_list),"weir_coefficient":structure.weir_coefficient,"section_data":{"x":x_list,"y":y_list}}
        return {"dimensions":dimensions}
    
    def _bridge_data(self, structure):
        section_df = structure.section_data
        all_friction = section_df["Mannings n"].tolist()
        friction_set = sorted(set(all_friction))
        friction = {"friction_set":friction_set,"all_friction":all_friction}

        orifice_data = extract_attrs(structure,{"orifice_flow","orifice_lower_transition_dist","orifice_upper_transition_dist","orifice_discharge_coefficient"})
        orifice_data["transition_width"] = structure.orifice_upper_transition_dist + structure.orifice_lower_transition_dist
        
        opening_data = []
        if structure.opening_nrows > 0: # if it has openings, not sure why it wouldnt but worth checking.
            opening_df = structure.opening_data
            for _,row in opening_df.iterrows(): # this isnt 'proper' for a df but there should be few rows and we're doing special stuff
                opening = {}
                opening["width"] = row["Finish"] - row["Start"] # round here because fp precision looks uncool
                
                # this is crude and can be wrong where the min is on the 'edge' of the section instead of at one of the points, but should be correct 99.9% of the time.
                temp_df = section_df.loc[(row["Start"]<=section_df["X"]) & (section_df["X"]<= row["Finish"])]
                opening["bed_minimum"] = temp_df["Y"].min()

                opening["soffit_level"] = row["Soffit Level"]
                opening["opening_height"] = opening["soffit_level"] - opening["bed_minimum"]

                opening_data.append(opening)

        culvert_data = []
        if hasattr(structure,"culvert_data") and structure.culvert_data.shape[0] > 1:
            for _,row in structure.culvert_data:
                culvert = {"invert":row["Invert"],"soffit":row["Soffit"],"bore_area":"Section Area"}
                culvert["height"] = culvert["soffit"] - culvert["invert"]
                culvert["average_width"] = culvert["bore_area"] / culvert["height"]
                culvert_data.append(culvert)
        
        return {"opening_data":opening_data,"friction":friction,"orifice_data":orifice_data,"culvert_data":culvert_data}
    
    def _sluice_data(self,structure): # these could do with more attention, given more time
        dimensions = extract_attrs(structure,{"crest_elevation","weir_breadth","weir_length"})
        
        return {"dimensions": dimensions}
    
    def _weir_data(self,structure):
        dimensions = extract_attrs(structure,{"weir_elevation","weir_breadth"})

        if structure._unit == "RNWEIR":
            dimensions |= extract_attrs(structure,{"weir_length","upstream_crest_height","downstream_crest_height"})

        return {"dimensions": dimensions}

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

    def _add_structures(self):
        for structure in self._dat.structures.values():
            self.unit_store[structure.name] = {"name":structure.name, "type":structure._unit, "subtype":structure.subtype}
            friction = ""
            dimensions = ""
            weir_coefficient = ""
            if structure._unit == "ORIFICE":
                self.unit_store[structure.name] |= self._orifice_dimensions(structure)
            elif structure._unit == "SPILL":
                self.unit_store[structure.name] |= self._spill_data(structure)
            elif structure._unit == "SLUICE":
                self.unit_store[structure.name] |= self._sluice_data(structure)
            elif structure._unit in {"WEIR","RNWEIR"}:
                self.unit_store[structure.name] |= self._weir_data(structure)
                # Need weir coefficient (the velocity attribute??)
            elif structure._unit == "BRIDGE":
                self.unit_store[structure.name] |= self._bridge_data(structure)
            else:
                print(f"Structure: {structure._unit} not currently supported in structure log")
                continue

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


if __name__ == "__main__":
    dat_path = r"floodmodeller_api/test/test_data/EX18.DAT"
    #dat_path = r"C:\Users\TOLLERJ\OneDrive - Jacobs\Documents\Projects\Bescot\Ford Brook 2023 Review\2023 Ford Brook - Model\2023 Ford Brook - Model\iSIS\DAT files\Design Runs\Ford_Brook_Design_1D_Arboretum_Final_Arup_24.DAT"
    slb = StructureLogBuilder(dat_path, "../ex18_dev.csv")
    slb._dat = DAT(slb.dat_file_path)
    slb._add_conduits()
    

    slb._add_structures()

    with open("../ex18_dev.json","w") as file:
        json.dump(slb.unit_store,file,indent=4)

