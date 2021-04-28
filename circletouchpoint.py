#!/usr/bin/env python3
import math
from solid import *
from solid.utils import *
import pathlib
import copy

debugo = []


def debug(o):
    debugo.append(o)


def main():
    d = 2
    r = 100 / 2
    R = r / cos(30)
    POINTS = [
        [r, R / 2],
        [-5, R / 2 + 2],
        [0, R],
    ]
    # POINTS = [
    #     [48.5, -28.001488055696846],
    #     [0.75, 56.00297611139369],
    #     [48.5, 28.001488055696846],
    # ]
    POINTS = [[0, -57.735026918962575], [0, 0], [50.0, 0]]
    POINTS = [[0, 0], [50.0, -28.867513459481287], [0, -57.735026918962575]]

    debug(translate(POINTS[0])(circle(d=1)))
    debug(translate(POINTS[1])(circle(d=2)))
    debug(translate(POINTS[2])(circle(d=3)))

    c1 = circlepoint(POINTS, d / 2)
    print(c1, c1[X] - POINTS[1][X], c1[Y] - POINTS[1][Y])
    circ = circle(d=d).set_modifier("#")

    o = polyline(POINTS).set_modifier("%")
    o += translate(c1)(circ)

    o += color("green")(debugo)
    saveasscad(o)


UP, DOWN, LEFT, RIGHT = 1 << 0, 1 << 1, 1 << 2, 1 << 3
X, Y = 0, 1


def lineangle(p1, p2):
    w = p1[0] - p2[0]
    h = p1[1] - p2[1]
    if h == 0:
        return 0
    return atan(w / h)


def pointlocation(p1, p2):
    """Location of p2 relative to p1 as a bitmask of UP,DOWN,LEFT,RIGHT"""

    ret = 0
    if p2[X] > p1[X]:
        ret = RIGHT
    elif p2[X] < p1[X]:
        ret = LEFT
    if p2[Y] > p1[Y]:
        ret |= UP
    elif p2[Y] < p1[Y]:
        ret |= DOWN
    return ret


def rotatepoints(points, angle):
    sina = sin(angle)
    cosa = cos(angle)
    i = 1
    for p in points:
        p[X], p[Y] = p[X] * cosa - p[Y] * sina, p[X] * sina + p[Y] * cosa
        i += 1
    return points


def circlepoint(points, r):
    """For a set of 3 points, finds the center of a circle that will touch both sides

    points: A list of points, the middle point will be the target of the circle
    r: The radius of the circle that is to be inside the lines between points
    """
    points = copy.deepcopy(points)

    # ᴪ = lineangle(points[0], points[1])
    # Rotate the triangle such that points[0] and points[1] are vertical, with
    # points[2] on the right side
    rotate = 0
    while 1:
        p0loc = pointlocation(points[1], points[0])
        p2loc = pointlocation(points[1], points[2])
        if points[0][X] == points[1][X] or points[2][X] == points[1][X]:
            rotate += 1
            rotatepoints(points, 1)
            continue
        if p0loc & RIGHT or p0loc & UP or p2loc & UP:
            rotate += 45
            rotatepoints(points, 45)
        else:
            break
        if rotate >= 365:
            break
            raise ValueError("Couldn't handle triangle!")
    # for i in range(1):
    #     rotatepoints(points, 45)
    #     p0loc = pointlocation(points[1], points[0])
    #     p2loc = pointlocation(points[1], points[2])
    #     if p0loc & RIGHT or p0loc & UP or p2loc & LEFT or p2loc & UP:
    #         print("FAIL")
    #     print("up, down, left, right", UP, DOWN, LEFT, RIGHT)
    #     print("Locations", p0loc, p2loc)
    ᴪ = lineangle(points[0], points[1])

    p1۷0 = lineangle(points[0], points[1])
    p1۷2 = lineangle(points[2], points[1])

    p1۷ = p1۷0 - p1۷2
    𝛼 = p1۷ / 2
    ol = r / tan(𝛼)
    diffx = sin(ᴪ) * ol
    diffy = cos(ᴪ) * ol
    cx = cos(ᴪ) * r
    cy = -sin(ᴪ) * r
    cp = [points[1][X] - diffx, points[1][Y] - diffy]
    cent = [cx + cp[X], cy + cp[Y]]
    cent = rotatepoints([cent], -rotate)[0]
    return cent


def line(p1, p2, w=0.1):
    return hull()(
        translate(p1)(
            circle(
                r=w,
            )
        ),
        translate(p2)(
            circle(
                r=w,
            )
        ),
    )


def polyline(points, w=0.1):
    o = []
    for index in range(len(points) - 1):
        o.append(line(points[index], points[index + 1], w))

    return union()(*o)


def saveasscad(obj):
    fn = pathlib.Path(__file__)
    outfn = fn.parent / (f"{fn.stem}.scad")
    scad_render_to_file(obj, outfn, file_header="$fn = 100;\n")


def hexpoints(width):
    """Returns the points for the 6 sides of the hex.

    width: The distance between 2 opposite parallel edges
    """
    r = width / 2
    R = r / cos(30)
    return [
        [-r, -R / 2],
        [-r, R / 2],
        [0, R],
        [r, R / 2],
        [r, -R / 2],
        [0, -R],
        [-r, -R / 2],
    ]


def roundedcutouts(points):
    """Creates a divider, with the walls between points and the rounded corners/base

    Designed exclusively for cutouts in the main hex
    """

    parts = []
    for x, y in points:
        parts.append(translate)


def roundedHex(side, height, radius, sidesonly=False):
    if sidesonly:
        innerheight = height
        innerz = 0
    else:
        innerheight = height - radius * 2
        innerz = radius
    innerwidth = side - radius * 2
    # o = linear_extrude(height=innerheight)(polygon(points=hexpoints(innerwidth)))
    # Round each vertical
    parts = []
    if sidesonly:
        for x, y in hexpoints(innerwidth):
            parts.append(translate([x, y, innerz])(cylinder(r=radius, h=innerheight)))
    else:
        for x, y in hexpoints(innerwidth):
            parts.append(translate([x, y, innerz])(sphere(r=radius).set_modifier("#")))
            parts.append(
                translate([x, y, height - innerz])(sphere(r=radius).set_modifier("#"))
            )

    return hull()(*parts)


def cos(angle):
    """Return the cos of a given angle in degrees"""
    return math.cos(math.radians(angle))


def sin(angle):
    """Return the sin of a given angle in degrees"""
    return math.sin(math.radians(angle))


def tan(angle):
    """Return the tan of a given angle in degrees"""
    return math.tan(math.radians(angle))


def atan(val):
    """Return the atan of a given angle in degrees"""
    return math.degrees(math.atan(val))


if __name__ == "__main__":
    main()
