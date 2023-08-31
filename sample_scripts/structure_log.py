from floodmodeller_api import DAT
import csv

dat_file_path = (
    r"C:\FloodModellerJacobs\Structure Log\DAT_for_API\Bourn_Rea_OBC_BLN_DEF_006.dat"
)
csv_output_path = r"C:\FloodModellerJacobs\Structure Log\output\structure_log.csv"

dat = DAT(dat_file_path)

with open(csv_output_path, "w", newline="") as file:
    writer = csv.writer(file)
    field = [
        "unit name",
        "unit type",
        "unit subtype",
        "comment",
        "description",
        "schematisation",
        "friction",
        "dimensions",
        "weir coefficients",
    ]

    writer.writerow(field)

    for conduit in dat.conduits.values():
        length = 0.0
        current_conduit = conduit
        while current_conduit.dist_to_next != 0:
            length += current_conduit.dist_to_next
            current_conduit = dat.next(current_conduit)
        if length == 0:
            continue
        friction = ""
        dimensions = ""
        if conduit.subtype == "CIRCULAR":
            dimensions = f"dimaeter: {conduit.diameter:.2f} x length: {length:.2f}"
            all_mannings = [
                conduit.friction_above_axis,
                conduit.friction_below_axis,
            ]
            mannings_set = set([min(all_mannings),max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"
        elif conduit.subtype == "SPRUNGARCH":
            dimensions = f"(springing: {conduit.height_crown:.2f}, crown: {conduit.height_springing:.2f}) x width: {conduit.width:.2f} x length: {length:.2f}"
            all_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set([min(all_mannings),max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"
        elif conduit.subtype == "RECTANGULAR":
            dimensions = f"height: {conduit.height:.2f} x width: {conduit.width:.2f} x length: {length:.2f}"
            all_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set([min(all_mannings),max(all_mannings)])
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
               #it is only meannt to go up to the height of the majority of the area
            dimensions = f"height: {height:.2f} x width: {width:.2f} x length: {length:.2f}"
            all_cw_frictions = conduit.coords.cw_friction.tolist()
            cw_frictions_set = set([min(all_cw_frictions),max(all_cw_frictions)])
            if len(cw_frictions_set) == 1:
                friction = f"Colebrook-White Friction: {cw_frictions_set.pop()}"
            else:
                friction = f"Colebrook-White Friction: [min: {cw_frictions_set.pop()}, max: {cw_frictions_set.pop()}]"
        elif conduit.subtype == "SPRUNG":
            dimensions = f"(springing: {conduit.height_crown:.2f}, crown: {conduit.height_springing:.2f}) x width: {conduit.width:.2f} x length: {length:.2f}"
            all_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set([min(all_mannings),max(all_mannings)])
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
                "",
                "",
                friction,
                dimensions,
                "NA",
            ]
        )

    for structure in dat.structures.values():
        friction = ""
        dimensions = ""
        weir_coefficient = ""
        if structure._unit == "ORIFICE":
            pass
        elif structure._unit == "SPILL":
            weir_coefficient = structure.weir_coefficient
        elif structure._unit == "SLUICE":
            weir_coefficient = structure.weir_flow_coefficient
            dimensions = f"crest elevation: {structure.crest_elevation:.2f} x width: {structure.weir_breadth:.2f} x length: {structure.weir_length:.2f}"
        elif structure._unit == "RNWEIR":
            dimensions = f"crest elevation: {structure.weir_elevation:.2f} x width: {structure.weir_breadth:.2f} x height: {structure.weir_length:.2f}"
        elif structure._unit == "BRIDGE":
            all_mannings = structure.section_data["Mannings n"].tolist()
            mannings_set = set([min(all_mannings), max(all_mannings)])
            if len(mannings_set) == 1:
                friction = f"Mannings: {mannings_set.pop()}"
            else:
                friction = f"Mannings: [min: {mannings_set.pop()}, max: {mannings_set.pop()}]"

        writer.writerow(
            [
                structure.name,
                structure._unit,
                structure.subtype,
                structure.comment,
                "",
                "",
                friction,
                dimensions,
                weir_coefficient,
            ]
        )
