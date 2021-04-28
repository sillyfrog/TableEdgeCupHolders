#!/usr/bin/env python3
import math
from solid import *
from solid.utils import *
import pathlib
from circletouchpoint import circlepoint

WALL = 1.5


INSIDE_RADIUS = 7


def gencomponentorganiser(diameter, height, sections, floor):
    o = cylinder(d=diameter, h=height)
    roundedangle = atan(
        (WALL / 2 + INSIDE_RADIUS) / (diameter / 2 - WALL - INSIDE_RADIUS)
    )
    sectionangle = 360 / sections
    x = cos(90 - sectionangle) * diameter / 2
    y = sin(90 - sectionangle) * diameter / 2
    outerpoints = [[0, diameter / 2], [0, 0], [x, y]]

    spherelocations = []
    if sections > 2:
        spherelocations.append(circlepoint(outerpoints, INSIDE_RADIUS + WALL / 2))

    spherelocations.append(
        [
            (WALL / 2 + INSIDE_RADIUS),
            (cos(roundedangle) * (diameter / 2 - WALL - INSIDE_RADIUS)),
        ]
    )
    angle = sectionangle - roundedangle
    spherelocations.append(
        [
            (sin(angle) * (diameter / 2 - WALL - INSIDE_RADIUS)),
            (cos(angle) * (diameter / 2 - WALL - INSIDE_RADIUS)),
        ]
    )
    sph = sphere(r=INSIDE_RADIUS)
    spheres = [translate(l + [INSIDE_RADIUS + floor])(sph) for l in spherelocations]
    sectionbase = union()(
        translate([0, 0, floor])(
            rotate([0, 0, -roundedangle])(
                roundedarc(
                    diameter / 2 - WALL, INSIDE_RADIUS, sectionangle - roundedangle * 2
                )
            )
        ),
        *spheres,
    )
    section = hull()(sectionbase, up(height * 2)(sectionbase))
    for i in range(sections):
        o -= rotate([0, 0, sectionangle * i])(section)

    o -= translate([0, 0, -0.1])(cylinder(d=25, h=0.5) - cylinder(d=25 - 0.4, h=0.5))

    # saveasscad(o)
    return o


def roundedarc(r=float, curver=float, angle=float) -> "OpenSCADObject":
    """Returns a rounded arc slice of angle degrees with a rounded base of curver

    Only the width of curve is included, use 2 with hull() to make a cylinder
    """
    return rotate([0, 0, 90 - angle])(
        translate([0, 0, curver])(
            rotate_extrude(angle=angle)(translate([r - curver, 0, 0])(circle(r=curver)))
        )
    )


def saveasscad(obj):
    fn = pathlib.Path(__file__)
    outfn = fn.parent / (f"{fn.stem}-{VER}.scad")
    scad_render_to_file(obj, outfn, file_header="$fn= 300;\n")


def sin(angle):
    """Return the sin of a given angle in degrees"""
    return math.sin(math.radians(angle))


def cos(angle):
    """Return the cos of a given angle in degrees"""
    return math.cos(math.radians(angle))


def atan(ratio):
    """atan in degrees of ratio"""
    return math.degrees(math.atan(ratio))


if __name__ == "__main__":
    main()
