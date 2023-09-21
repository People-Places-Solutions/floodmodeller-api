from floodmodeller_api import DAT
import csv

dat_file_path = r"C:\FloodModellerJacobs\Structure Log\DAT_for_API\Bourn_Rea_OBC_BLN_DEF_006.dat"
csv_output_path = r"C:\FloodModellerJacobs\Structure Log\output\structure_log.csv"

dat = DAT(dat_file_path)

with open(csv_output_path, "w", newline="") as file:
    writer = csv.writer(file)
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

    for conduit in dat.conduits.values():
        length = 0.0
        inlet = ""
        outlet = ""
        previous = dat.prev(conduit)
        if hasattr(previous, "subtype"):
            if previous.subtype == "INLET":
                inlet = previous.ki
        current_conduit = conduit
        while current_conduit.dist_to_next != 0:
            length += current_conduit.dist_to_next
            current_conduit = dat.next(current_conduit)
        if length == 0:
            continue
        next = dat.next(current_conduit)
        if hasattr(next, "subtype"):
            if next.subtype == "OUTLET":
                outlet = next.loss_coefficient
        culvert_loss = ""
        if inlet != "" and outlet != "":
            culvert_loss = f"Ki: {inlet}, Ko: {outlet}"
        elif inlet != "":
            culvert_loss = f"Ki: {inlet}"
        elif outlet != "":
            culvert_loss = f"Ko: {outlet}"
        friction = ""
        dimensions = ""
        if conduit.subtype == "CIRCULAR":
            dimensions = f"dia: {conduit.diameter:.2f} x l: {length:.2f}"
            all_mannings = [
                conduit.friction_above_axis,
                conduit.friction_below_axis,
            ]
            mannings_set = set([min(all_mannings), max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"
        elif conduit.subtype == "SPRUNGARCH":
            dimensions = f"(Springing: {conduit.height_crown:.2f}, Crown: {conduit.height_springing:.2f}) x w: {conduit.width:.2f} x l: {length:.2f}"
            all_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set([min(all_mannings), max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"
        elif conduit.subtype == "RECTANGULAR":
            dimensions = f"h: {conduit.height:.2f} x w: {conduit.width:.2f} x l: {length:.2f}"
            all_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set([min(all_mannings), max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"
        elif conduit.subtype == "SECTION":
            x_list = conduit.coords.x.tolist()
            width = (max(x_list) - min(x_list)) * 2
            y_list = conduit.coords.y.tolist()
            height = max(y_list) - min(
                y_list
            )  # currently this means that height goes to the top of the spike,
            # it is only meannt to go up to the height of the majority of the area
            dimensions = f"h: {height:.2f} x w: {width:.2f} x l: {length:.2f}"
            all_cw_frictions = conduit.coords.cw_friction.tolist()
            cw_frictions_set = set([min(all_cw_frictions), max(all_cw_frictions)])
            if len(cw_frictions_set) == 1:
                friction = f"Colebrook-White: {cw_frictions_set.pop()}"
            else:
                friction = f"Colebrook-White: [min: {cw_frictions_set.pop()}, max: {cw_frictions_set.pop()}]"
        elif conduit.subtype == "SPRUNG":
            dimensions = f"(Springing: {conduit.height_crown:.2f}, Crown: {conduit.height_springing:.2f}) x w: {conduit.width:.2f} x l: {length:.2f}"
            all_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set([min(all_mannings), max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"

        writer.writerow(
            [
                conduit.name,
                conduit._unit,
                conduit.subtype,
                conduit.comment,
                friction,
                dimensions,
                "",
                culvert_loss,
            ]
        )

    for structure in dat.structures.values():
        friction = ""
        dimensions = ""
        weir_coefficient = ""
        if structure._unit == "ORIFICE":
            if structure.shape == "RECTANGLE":
                height = structure.soffit - structure.invert
                width = structure.bore_area / height
                dimensions = f"h: {height:.2f} x w: {width:.2f}"
            elif structure.shape == "CIRCULAR":
                diameter = structure.soffit - structure.invert
                dimensions = f"dia: {diameter:.2f}"
        elif structure._unit == "SPILL":
            elevation = min(structure.data.Y.tolist())
            x_list = structure.data.X.tolist()
            width = max(x_list) - min(x_list)
            dimensions = f"Elevation: {elevation:.2f} x w: {width:.2f}"
            weir_coefficient = structure.weir_coefficient
        elif structure._unit == "SLUICE":
            dimensions = f"Crest Elevation: {structure.crest_elevation:.2f} x w: {structure.weir_breadth:.2f} x l: {structure.weir_length:.2f}"
        elif structure._unit == "RNWEIR":
            dimensions = f"Crest Elevation: {structure.weir_elevation:.2f} x w: {structure.weir_breadth:.2f} x l: {structure.weir_length:.2f}"
        elif structure._unit == "WEIR":
            dimensions = (
                f"Crest Elevation: {structure.weir_elevation:.2f} x w: {structure.weir_breadth:.2f}"
            )
            # Need weir coefficient (the velocity attribute??)
        elif structure._unit == "BRIDGE":
            all_mannings = structure.section_data["Mannings n"].tolist()
            mannings_set = set([min(all_mannings), max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"
            height = structure.opening_data.values[0][3] - min(structure.section_data.Y.tolist())
            width = structure.opening_data.values[0][1] - structure.opening_data.values[0][0]
            dimensions = f"h: {height:.2f} x w: {width:.2f}"

        writer.writerow(
            [
                structure.name,
                structure._unit,
                structure.subtype,
                structure.comment,
                friction,
                dimensions,
                weir_coefficient,
                "",
            ]
        )
