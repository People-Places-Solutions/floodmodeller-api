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
        "mannings",
        "dimensions (height x width x length)",
        "weir coefficients",
    ]

    writer.writerow(field)

    for conduit in dat.conduits.values():
        mannings = ""
        dimensions = ""
        weir_coefficient = ""
        if conduit.subtype == "CIRCULAR":
            dimensions = f"dimaeter: {conduit.diameter}"
            min_max_mannings = [
                conduit.friction_above_axis, conduit.friction_below_axis
            ]
            mannings_set = set(min_max_mannings)
            for manning in mannings_set:
                mannings += str(manning) + ", "
            mannings = mannings[:-2]
        if conduit.subtype == "SPRUNGARCH":
            dimensions = f"(s:{conduit.height_crown},c:{conduit.height_springing})x{conduit.width}"
            min_max_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set(min_max_mannings)
            for manning in mannings_set:
                mannings += str(manning) + ", "
            mannings = mannings[:-2]
        if conduit.subtype == "RECTANGULAR":
            dimensions = f"{conduit.height}x{conduit.width}"
            min_max_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set(min_max_mannings)
            for manning in mannings_set:
                mannings += str(manning) + ", "
            mannings = mannings[:-2]
        if conduit.subtype == "SECTION":
            pass
        if conduit.subtype == "SPRUNG":
            dimensions = f"(s:{conduit.height_crown},c:{conduit.height_springing})x{conduit.width}"
            min_max_mannings = [
                conduit.friction_on_invert,
                conduit.friction_on_soffit,
                conduit.friction_on_walls,
            ]
            mannings_set = set(min_max_mannings)
            for manning in mannings_set:
                mannings += str(manning) + ", "
            mannings = mannings[:-2]

        writer.writerow(
            [
                conduit.name,
                conduit._unit,
                conduit.subtype,
                conduit.comment,
                "",
                "",
                mannings,
                dimensions,
                weir_coefficient,
            ]
        )

    for structure in dat.structures.values():
        mannings = ""
        dimensions = ""
        weir_coefficient = ""
        if structure._unit == "ORIFICE":
            pass
        if structure._unit == "SPILL":
            weir_coefficient = structure.weir_coefficient
        if structure._unit == "SLUICE":
            weir_coefficient = structure.weir_flow_coefficient
            dimensions = f"(u:{structure.us_weir_height},d:{structure.ds_weir_height})x{structure.weir_breadth}x{structure.weir_length}"
        if structure._unit == "RNWEIR":
            dimensions = f"(u:{structure.upstream_crest_height},d:{structure.downstream_crest_height})x{structure.weir_breadth}x{structure.weir_length}"
        if structure._unit == "BRIDGE":
            all_mannings = structure.section_data["Mannings n"].tolist()
            min_max_mannings = set([min(all_mannings), max(all_mannings)])
            for manning in min_max_mannings:
                mannings += str(manning) + ", "
            mannings = mannings[:-2]

        writer.writerow(
            [
                structure.name,
                structure._unit,
                structure.subtype,
                structure.comment,
                "",
                "",
                mannings,
                dimensions,
                weir_coefficient,
            ]
        )


print("")
