"""Checks that every building block and every example gives a closed, printable mesh.

Run with pytest (`pytest -q`) or without it (`python3 tests/test_watertight.py`).
A part passes when its mesh is watertight, consistently wound, in one piece (or one piece plus sealed chambers
where that is the point), sits on z = 0 and has nothing facing down more than 45 degrees above the bed.
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from manifold3d import Manifold  # noqa: E402
from sauna_bits import cad, parts  # noqa: E402


def check(m, surfaces=1, max_overhang=1.0, on_bed=True):
    tm = cad.to_trimesh(m)
    assert tm.is_watertight, "mesh is not watertight"
    assert tm.is_winding_consistent, "inconsistent winding"
    assert tm.body_count == surfaces, f"{tm.body_count} surfaces, expected {surfaces}"
    if on_bed:
        assert abs(tm.bounds[0][2]) < 1e-6, f"lowest point at z = {tm.bounds[0][2]:.3f}, not on the bed"
        assert cad.overhang_area(tm) <= max_overhang, f"{cad.overhang_area(tm):.1f} mm2 overhang"
    return tm


def plate(t=6.0):
    return cad.rect(-30, -30, 30, 30).extrude(t)


def test_peg():
    check(plate() + parts.peg().translate((0, 0, 5.99)))


def test_countersunk_hole():
    check(plate() - parts.countersunk_hole(plate_t=6.0))


def test_teardrop_hole():
    block = Manifold.cube((40, 40, 30)).translate((-20, -20, 0))
    check(block - parts.teardrop_hole(5.0, 50).translate((0, 0, 15)))
    check(block - parts.teardrop_hole(5.0, 50, axis="x").translate((0, 0, 15)))


def test_pilot_hole():
    block = Manifold.cube((20, 20, 20)).translate((-10, -10, 0))
    check(block - parts.pilot_hole().translate((0, 0, -0.5)))


def test_jigsaw_joint_fits():
    a = (cad.rect(0, -20, 50, 20) + parts.jigsaw_knob().translate((50, 0))).extrude(5)
    b = (cad.rect(50, -20, 100, 20) - parts.jigsaw_knob(grow=0.2).translate((50, 0))).extrude(5)
    check(a), check(b)
    assert (a ^ b).volume() < 1e-6, "knob and socket overlap"


def test_dovetail_slides():
    track = cad.along_x(parts.dovetail_profile(30, 3.0, z0=3.0), -1, 61)
    base = Manifold.cube((60, 50, 6)).translate((0, -25, 0)) - track
    slider = cad.along_x(parts.dovetail_profile(30 - 0.5, 2.7, z0=0.0), 0, 40).translate((10, 0, 3.05))
    check(base)
    assert (base ^ slider).volume() < 1e-6, "slider overlaps the track"


def test_spigot_tube():
    check(parts.spigot_tube())


def test_cup_volume():
    z = parts.level_for_volume(100, 64.0)
    v = parts.cup_cavity(64.0, z).volume() / 1000
    assert abs(v - 100) < 0.05, v
    cup = Manifold.cylinder(z + 10, 34.4, 34.4, 128) - parts.cup_cavity(64.0, z + 11)
    check(cup - parts.v_groove_ring(32.0, z) - parts.v_groove_ring(34.4, z, inside=False))


def test_cone_cavity():
    dome = cad.poly([(0, 0), (50, 0), (50, 20), (30, 45), (0, 50)]).revolve(96)
    check(dome - parts.cone_cavity(44.0))


def test_sealed_chambers():
    prof = cad.poly([(8, 0), (40, 0), (40, 30), (8, 30)])
    cells = parts.gable_ring_cells(10, 38, 30, 2.0, cells=2) ^ prof.offset(-2.0)
    check(prof.revolve(96) - cells.revolve(96), surfaces=3)


def _example(name):
    path = os.path.join(ROOT, "examples", name)
    spec = importlib.util.spec_from_file_location(name[:-3].replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_example_peg_rail():
    for m in _example("01_peg_rail.py").build().values():
        check(m)


def test_example_name_tag():
    try:
        from sauna_bits import text
        text.find_font()
    except (ImportError, FileNotFoundError):
        return                                         # no font on this machine: nothing to test
    for m in _example("02_name_tag.py").build().values():
        check(m)


def test_example_measuring_cup():
    ex = _example("03_measuring_cup.py")
    for m in ex.build().values():
        check(m)
        for ml, z in zip(ex.MARKS, ex.levels()):
            assert abs(ex.water_in(m, z) - ml) < 0.5


def test_example_float():
    built, env = _example("04_float.py").build()
    for m in built.values():
        check(m, surfaces=3)
        assert env.volume() / 1000 > m.volume() / 1000 * 1.27, "it would sink"


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok    {name}")
            except AssertionError as e:
                failed += 1
                print(f"FAIL  {name}: {e}")
    sys.exit(1 if failed else 0)
