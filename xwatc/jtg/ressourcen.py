import pathlib

PATH = pathlib.Path(__file__).parent.absolute()

with open(PATH / "frauennamen.txt") as file:
    FRAUENNAMEN = file.read().split("\n")