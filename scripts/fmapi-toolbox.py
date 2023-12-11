import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser(
    prog="Flood Modeller API Toolbox",
    description="Utility for exploring installed api tools",
)

parser.add_argument("-l", "-list", action="store_true", help="List all toolbox scripts installed")
parser.add_argument(
    "-ld",
    "-list-detailed",
    action="store_true",
    help="List all toolbox scripts installed including usage",
)
args = parser.parse_args()
if args.l:
    print("API Toolbox scripts installed:")
    for file in Path(__file__).parent.glob("fmapi-*.bat"):
        if file.stem == "fmapi-toolbox":
            continue
        print(f"    -> {file.stem}")

elif args.ld:
    print("API Toolbox scripts installed:")
    for file in Path(__file__).parent.glob("fmapi-*.py"):
        if file.stem == "fmapi-toolbox":
            continue
        print(f"    -> {file.stem}\n")

        try:
            os.system(f'python "{str(file)}" -h')
        except Exception:
            pass
        print("================================================\n")

# TODO: Add functionality to create a bat and py file in scripts, add to setup.py and install to path

