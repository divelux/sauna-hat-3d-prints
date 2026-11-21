"""Preview renders for the soap dish (not needed for printing)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import soap_dish as sd
from manifold3d import Manifold
from dvx_cad import rect, rounded, to_trimesh
from render import render, sheet
from PIL import Image

C1 = (214, 170, 120); SOAP = (236, 226, 200); WATER = (150, 185, 205)
d = os.path.join(HERE, "img"); os.makedirs(d, exist_ok=True)
dish = sd.soap_dish()
soap = rounded(rect(-45, -30, 45, 30), 14).extrude(24).translate((0, 4, sd.RIB_TOP + 0.05))
render([(to_trimesh(dish), C1), (to_trimesh(soap), SOAP)], az=25, el=32, size=(1000, 800)).save(os.path.join(d, "dish-with-soap.png"))
render([(to_trimesh(dish), C1)], az=25, el=42, size=(1000, 800)).save(os.path.join(d, "dish-empty.png"))
# cut through the middle, seen from the side: the floor falls toward the spout
half = dish ^ Manifold.cube((200, 200, 50)).translate((-200.0, -100, -1))
render([(to_trimesh(half), C1)], az=-90, el=8, size=(1000, 600)).save(os.path.join(d, "dish-section.png"))
sd.SLOTS = True
render([(to_trimesh(sd.soap_dish()), C1)], az=25, el=55, size=(1000, 800)).save(os.path.join(d, "dish-with-slots.png"))
tiles = [(Image.open(os.path.join(d, f)), cap) for f, cap in [
    ("dish-with-soap.png", "The bar sits on six level ribs"), ("dish-empty.png", "Water runs to the spout at the front"),
    ("dish-section.png", "Cut through: the floor falls 2.6 mm to the spout"), ("dish-with-slots.png", "Variant with drain slots")]]
sheet(tiles, 2, os.path.join(d, "dish-preview.png"), "Soap dish with drain", tile=(700, 520))
