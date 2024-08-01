#!/usr/bin/env python3
from solid import *
from solid.utils import *
import pathlib
import math
from componentorganiser import gencomponentorganiser

use("threads.scad")

SHOW_EXTRAS = True
SHOW_EXTRAS = False
# SHOW_PARTS = True

# use <small-parts-text-outlines.scad>;
# use("MCAD/boxes.scad")


def objsum(objs):
    ret = objs[0]
    for o in objs[1:]:
        ret += o
    return ret


CLIP_D = 8.5
CLIP_WALL = 2
CLIP_TOP_BORDER = 3
CLIP_DROP = 40
CLIP_TOTAL_D = 20

TABLE_OVERHANG = 50

TOP_UP = 0.2

CONNECTOR_WIDTH = 15
CONNECTOR_DEPTH = 8
CONNECTOR_HEIGHT = CLIP_DROP
CONNECTOR_INTERFACE_D = 22.5

INTERFACE_MARGIN = 0.3


def rail_clip(h=15, txt=""):
    INNER_UP = -1
    CLIP_TOP_MARGIN = 0.4
    o = translate([CLIP_TOP_MARGIN / 2, -CLIP_D / 2 + INNER_UP, 0])(
        cylinder(d=CLIP_D - CLIP_TOP_MARGIN, h=h)
    )
    o += translate([-CLIP_D / 2 + CLIP_TOP_MARGIN, -CLIP_D / 2 + INNER_UP, 0])(
        cube([CLIP_D - CLIP_TOP_MARGIN, 7 - INNER_UP, h])
    )
    o += translate([-CLIP_D / 2 + CLIP_TOP_MARGIN, -CLIP_WALL / 2, 0])(
        cube(
            [CLIP_D + CLIP_WALL + 10 - CLIP_TOP_MARGIN, 5.5 + TOP_UP + CLIP_WALL / 2, h]
        )
    )
    o -= translate([CLIP_D / 2 + CLIP_WALL / 2 + 0.5 / 2, -CLIP_WALL / 2, -1])(
        cylinder(d=CLIP_WALL + 0.5, h=h + 2)
    )

    o += translate([CLIP_D / 2 + CLIP_WALL + 0.5, -30, 0])(cube([10 - 0.5, 30, h]))
    base_r = 5

    pushcube = cube([CLIP_D + CLIP_WALL * 2 + 10, 20, h]).set_modifier("")
    if txt:
        pushcube -= translate([(CLIP_D + CLIP_WALL * 2 + 5) / 2, 0.4, h / 2])(
            rotate([90, 0, 0])(
                mirror([0, 0, 0])(
                    linear_extrude(0.5)(
                        text(
                            txt,
                            5,
                            font="Arial:style=Bold",
                            valign="center",
                            halign="center",
                        )
                    )
                )
            )
        ).set_modifier("")

    o += translate([-CLIP_D / 2 - CLIP_WALL, -CLIP_DROP - 1, 0])(
        difference()(
            pushcube,
            translate([(CLIP_D + CLIP_WALL * 2 + 10) - base_r, -base_r, -1])(
                cube([base_r * 2, base_r * 2, h + 2])
            ),
        )
        + translate([(CLIP_D + CLIP_WALL * 2 + 10) - base_r, base_r, 0])(
            cylinder(r=base_r, h=h).set_modifier("")
        )
    ).set_modifier("")

    # Finish so everything that should connect is at 0,0
    o = translate([-(CLIP_D / 2 + CLIP_WALL + 10), -5.5 - TOP_UP, 0])(o)

    conn_h = CLIP_DROP
    conn = translate([-CONNECTOR_DEPTH, 0, h / 2])(
        rotate([90, 90, 0])(connector(conn_h))
    )
    conn += translate([-50 - CONNECTOR_DEPTH, -50, 0])(cube([50, 50, h]))
    conn += translate([-50, -50 - conn_h, 0])(cube([50, 50, h]))
    o = intersection()(o, conn)

    # Extra material to help the clip not slip once inserted
    NON_SLIP_R = 7 / 2
    BULGE = 0.8
    nonslip = intersection()(
        right(NON_SLIP_R * 2 - BULGE - 0.1)(cube(NON_SLIP_R * 2, center=True)),
        sphere(r=NON_SLIP_R),
    )
    o += translate([-NON_SLIP_R + BULGE, -35, h / 2])(nonslip)

    # o += translate([-20, -0.0 - CLIP_DROP - 5.5 - TOP_UP - 1, 0])(~cube([25, 0.1, 10]))
    # print(f"Total clip height: {- CLIP_DROP - 5.5 - TOP_UP - 1}")

    return o


def spacer(txt=""):
    TOP_SPACING = 5
    ALU_THICK = 1.5
    WIDTH = 15
    HEIGHT = 22
    o = translate([CLIP_D / 2, 0, -HEIGHT + CLIP_D / 2])(
        rotate([-90, 0, 0])(cylinder(d=CLIP_D, h=WIDTH))
    )
    o += translate([0, 0, -(HEIGHT - CLIP_D / 2)])(
        cube([CLIP_D + 0.2, WIDTH, TOP_SPACING + HEIGHT - CLIP_D / 2])
    )
    o += translate([-ALU_THICK, 0, 0])(cube([CLIP_D, WIDTH, TOP_SPACING]))
    return o


def interface(wall=0, extraheight=0):
    """The interface for the main rail clip"""
    h = 15
    conn = translate(
        [
            -CONNECTOR_DEPTH + INTERFACE_MARGIN - wall,
            -CLIP_DROP - extraheight + 0.01 + INTERFACE_MARGIN,
            0,
        ]
    )(
        cube(
            [
                CONNECTOR_DEPTH - INTERFACE_MARGIN + wall,
                CLIP_DROP + extraheight - INTERFACE_MARGIN,
                h,
            ]
        )
    )
    conn -= hole()(
        translate([-CONNECTOR_DEPTH - wall, 1, h / 2])(
            rotate([90, 90, 0])(
                connector(CLIP_DROP + extraheight + 2, -INTERFACE_MARGIN)
            )
        )
    )
    return conn


def connector(height, margin=0):
    WIDTH = CONNECTOR_WIDTH
    DEPTH = CONNECTOR_DEPTH
    D = 3
    inner_width = WIDTH / 2 - D

    TOP_FRACTION = 3.2
    BOTTOM_FRACTION = 6
    T_DOWN = 3
    SLOPE = 0.5
    o = linear_extrude(height)(
        polygon(
            [
                [0, DEPTH - margin * 1.5],
                [WIDTH / TOP_FRACTION - margin, DEPTH - margin * 1.2],
                [
                    WIDTH / TOP_FRACTION - margin,
                    DEPTH - DEPTH / T_DOWN + margin - SLOPE,
                ],
                [
                    WIDTH / BOTTOM_FRACTION - margin + SLOPE,
                    DEPTH - DEPTH / T_DOWN + margin,
                ],
                [WIDTH / BOTTOM_FRACTION - margin, 0],
                [-1, 0],
            ]
        )
    )
    o += mirror([1, 0, 0])(o)
    return o


def connectorrounded(height, margin=0):
    WIDTH = CONNECTOR_WIDTH
    DEPTH = CONNECTOR_DEPTH
    D = 3
    inner_width = WIDTH / 2 - D

    def edge(height, margin):
        return hull()(
            translate([0, 0, height / 2])(cube([0.01, 0.01, height], center=True)),
            translate([inner_width / 2 - margin, -D / 2, 0])(cylinder(d=D, h=height)),
            translate([0, -DEPTH, height / 2])(cube([0.01, 0.01, height], center=True)),
            translate([WIDTH / 6 - margin, -DEPTH, height / 2])(
                cube([0.01, 0.01, height], center=True)
            ),
        )

    o = edge(height, margin) + translate(
        [WIDTH / 6 + D / 2 - margin, -DEPTH + D / 2, height / 2]
    )(cube([D, D, height], center=True)).set_modifier("")

    o = translate([0, DEPTH, 0])(o)

    move = 6.578 - margin
    dupe = rotate([0, 0, 180])(edge(height + 2, 0)).set_modifier("")
    o -= translate([move, 0, -1])(dupe)
    o += mirror([1, 0, 0])(o)

    # o += translate([-WIDTH / 2, 0, 0])(
    #     cube([WIDTH / 1, DEPTH, height - 1])
    # ).set_modifier("%")

    return o


def rendertestbracket():
    VER = "v1.1"
    H = 15
    holder = cube([45 - 16.25 + 90, 10, H])
    support_r = 25
    holder += translate([0, -support_r, 0])(cube([support_r, support_r, H]))
    holder -= translate([support_r, -support_r, -1])(cylinder(r=support_r, h=H + 2))
    holder -= translate([45 - 16.25 + 90 - 10, 11, H / 2])(
        rotate([90, 0, 0])(cylinder(r=4, h=20))
    ).set_modifier("")
    holder = translate([0, -10, 0])(holder).set_modifier("")
    o = rotate([-90, 0, 0])(interface(wall=2) + holder)
    # o += translate([-2, 0, 0])(rotate([-90, 0, 0])(color("blue")(rail_clip())))

    # o = rotate([-90, 0, 0])(interface(wall=4) + holder)
    # o = intersection()(translate([-50, 0, 0])(cube([50, 50, 10])), o)

    saveasscad(o, "testbracket-" + VER, fn=300)
    return o


def rendercupholder():
    VER = "v2.0"
    INNER_D = 99

    WALL = 6
    THICK = 9
    BACK_SUPPORT = 2.2

    CALC_OVERHANG = TABLE_OVERHANG + WALL - BACK_SUPPORT - CLIP_TOTAL_D

    TOTAL_W = INNER_D + WALL * 2

    # Radius of round bit at back of support
    support_r = 23

    # Support arms to main cylinder, including version
    holder = cube([INNER_D / 2 + CALC_OVERHANG, THICK, CONNECTOR_WIDTH])
    holder -= translate([(INNER_D / 2 + CALC_OVERHANG) / 2, 0.4, CONNECTOR_WIDTH / 2])(
        rotate([90, 0, 0])(
            mirror([0, 0, 0])(
                linear_extrude(0.5)(
                    text(
                        VER,
                        5,
                        font="Arial:style=Bold",
                        valign="center",
                        halign="center",
                    )
                )
            )
        )
    )
    holder += translate([0, 0, TOTAL_W - CONNECTOR_WIDTH])(
        cube([INNER_D / 2 + CALC_OVERHANG, THICK, CONNECTOR_WIDTH])
    )

    # Main cylinder solid
    holder += translate([INNER_D / 2 + CALC_OVERHANG, 0, TOTAL_W / 2])(
        rotate([-90, 0, 0])(cylinder(d=TOTAL_W, h=THICK))
    )

    # Arc support from clips to arms
    holder += translate([-BACK_SUPPORT, THICK - CLIP_DROP + INTERFACE_MARGIN, 0])(
        cube([BACK_SUPPORT, CLIP_DROP - INTERFACE_MARGIN, TOTAL_W])
    )
    holder += translate([0, -support_r, 0])(
        cube([support_r, support_r + THICK, CONNECTOR_WIDTH])
    )
    holder += translate([-0, -support_r, TOTAL_W - CONNECTOR_WIDTH])(
        cube([support_r, support_r + THICK, CONNECTOR_WIDTH])
    )
    holder -= translate([support_r, -support_r, -1])(
        cylinder(r=support_r, h=TOTAL_W + 2)
    )

    # Rotate and position for the insert
    holder = rotate([90, 0, 0])(
        translate([-(INNER_D / 2 + CALC_OVERHANG), 0, -TOTAL_W / 2])(holder)
    )
    # The thread and cover for the insert
    holder -= down(5)(
        metric_thread(
            diameter=INNER_D + 2,
            length=20,
            pitch=3,
            thread_size=6.5,
            leadin=0,
            test=False,
            angle=30,
            groove=False,
        )
    )
    holder += up(THICK - 2)(cylinder(d=INNER_D + WALL * 2, h=2))
    holder -= up(THICK - 2 - 0.01)(cylinder(d=INNER_D - 1.5 * 2, h=3))
    holder -= down(1)(cylinder(d=INNER_D + 2, h=2))

    ointerface = translate([-(INNER_D / 2 + CALC_OVERHANG), 0, THICK])(
        rotate([90, 0, 0])(interface(BACK_SUPPORT + 0.5))
    )
    o = (
        holder
        + translate([0, TOTAL_W / 2, 0])(ointerface)
        + translate([0, -TOTAL_W / 2 + CONNECTOR_WIDTH, 0])(ointerface)
    )
    # o = interface(BACK_SUPPORT) + holder + up(TOTAL_W - 15)(interface(BACK_SUPPORT))

    # Rotate it so it's best for printing
    o = rotate([180, 0, 0])(o)

    saveasscad(o, "cupholder-" + VER, fn=300)


def renderwineglassholder():
    VER = "v1.1"
    ARM_THICK = 9
    rtop = 40 / 2
    rbot = 14 / 2
    angle = 35
    thick = 2.5
    glassmaxr = 50

    thick2 = thick / cos(angle)
    height = (rtop - rbot) / tan(angle)

    supportr = 5
    supportrback = 25
    armxfudge = 5

    BACK_SUPPORT = 2

    # outer base
    arm = cube([rtop, CONNECTOR_WIDTH, height])
    arm += translate([rtop - armxfudge, 0, height - supportr - ARM_THICK])(
        cube([supportr, CONNECTOR_WIDTH, supportr])
    )
    arm -= translate(
        [
            rtop + supportr - armxfudge,
            CONNECTOR_WIDTH + 1,
            height - supportr - ARM_THICK,
        ]
    )(rotate([90, 0, 0])(cylinder(r=supportr, h=CONNECTOR_WIDTH + 2)))
    arm -= translate([rtop - armxfudge, -1, height - supportr - ARM_THICK - supportr])(
        cube([supportr, CONNECTOR_WIDTH + 2, supportr])
    )
    curvebackr = height - supportr - ARM_THICK
    arm -= translate([rtop - armxfudge - curvebackr, -1, -1])(
        cube([curvebackr + 1, CONNECTOR_WIDTH + 2, curvebackr + 1])
    )
    arm += translate([rtop - armxfudge - curvebackr, CONNECTOR_WIDTH, curvebackr])(
        rotate([90, 0, 0])(cylinder(r=curvebackr, h=CONNECTOR_WIDTH))
    )

    # main arm
    supportlen = TABLE_OVERHANG + thick2 + glassmaxr - BACK_SUPPORT - CLIP_TOTAL_D
    arm += translate([0, 0, height - ARM_THICK])(
        cube([supportlen, CONNECTOR_WIDTH, ARM_THICK])
    )

    # Interface to connector
    arm += translate([supportlen, 0, height])(
        rotate([90, 0, 180])(interface(BACK_SUPPORT))
    )

    # inner support curve
    arm += translate(
        [supportlen - supportrback, 0, -supportrback + height - ARM_THICK]
    )(cube([supportrback, CONNECTOR_WIDTH, supportrback]))
    arm -= translate(
        [
            supportlen - supportrback,
            CONNECTOR_WIDTH + 1,
            -supportrback + height - ARM_THICK,
        ]
    )((rotate([90, 0, 0])(cylinder(r=supportrback, h=CONNECTOR_WIDTH + 2))))

    # Glass holder
    # rounded edges at insert
    edger = 3
    cutawaycorner = cube([edger + 1, edger + 1, rtop + thick2]) - cylinder(
        r=edger, h=rtop + thick2 + 2
    )
    # o += ~rotate([-35, 0, 45])(cutaway)
    cutaway = (
        translate([0, -edger, height - edger])(
            rotate([90, 0, 0])(rotate([0, 90, 0])(cutawaycorner))
        )
        + translate([0, edger + 10, height - edger])(
            rotate([180, 0, 0])(rotate([0, 90, 0])(cutawaycorner))
        )
        + cube([rtop + thick2, 10, height])
    )

    o = (
        cylinder(r1=rbot + thick2, r2=rtop + thick2, h=height)
        + translate([0, -CONNECTOR_WIDTH / 2, 0])(arm)
    ) - (
        cylinder(r1=rbot, r2=rtop, h=height + 0.1)
        + rotate([0, 0, 90 + 45 / 2])(translate([0, -5, 0])(cutaway))
    )

    o -= translate([rtop, 0, height - ARM_THICK - 0.1])(
        mirror([1, 0, 0])(
            linear_extrude(0.3)(
                text(
                    VER + " ",
                    5,
                    font="Arial:style=Bold",
                    valign="center",
                    halign="right",
                )
            )
        )
    )

    saveasscad(rotate([180, 0, 0])(o), "wineglassholder-" + VER, fn=300)


# cupdepth: Original depth, plus enough to make it flat when stacked
def renderinsert(partinsertsections=False, deepparts=False, cupdepth=40 + 5):
    """Insert for cups or components. If partinsertsections is set, a component
    organiser is generated with the given number of sections."""
    VER = "v2.6"
    FLOOR = 1.4
    WALL = 1.5
    THREAD_H = 8
    INNER_D = 99
    THREAD_THICK = 3

    componentsdiameter = 95

    if partinsertsections:
        if not deepparts:
            cupdepth = 10
        FLOOR = 1.2

    componentsheight = cupdepth + 3

    o = cylinder(d=INNER_D - THREAD_THICK, h=cupdepth + FLOOR - THREAD_H)

    TAPER_PCG = 0.7
    taper = rotate_extrude()(
        polygon(
            [
                [INNER_D / 2 + WALL, cupdepth + FLOOR + WALL],
                [INNER_D / 2 - WALL * TAPER_PCG, cupdepth + FLOOR],
                [INNER_D / 2, cupdepth + FLOOR - WALL * TAPER_PCG],
                [INNER_D / 2 + WALL, cupdepth + FLOOR - WALL * TAPER_PCG * 1.5],
            ]
        )
    )

    # Rotate by 10° so it screws in square
    # Add 90° for deep inserts so the cards are facing the player
    rotating = -10
    if deepparts:
        rotating += 90
    o += rotate([0, 0, rotating])(
        up(FLOOR + cupdepth - THREAD_H)(
            metric_thread(
                diameter=INNER_D + 1,
                length=THREAD_H,
                pitch=3,
                thread_size=3.5,
                leadin=0,
                test=False,
                angle=30,
                groove=False,
            ),
        )
    )
    o -= taper
    if partinsertsections:
        cutout = componentsdiameter
    else:
        cutout = INNER_D - THREAD_THICK - WALL * 2
    o -= up(FLOOR)(cylinder(d=cutout, h=cupdepth + FLOOR))

    if partinsertsections:
        o += gencomponentorganiser(
            componentsdiameter, componentsheight, partinsertsections, FLOOR
        )

    o -= translate([0, INNER_D / 2 - 1 - THREAD_THICK, -0.1])(
        mirror([1, 0, 0])(
            linear_extrude(0.3)(
                text(
                    VER,
                    5,
                    font="Arial:style=Bold",
                    valign="top",
                    halign="center",
                )
            )
        )
    )

    # Small cutout to make printing prettier
    ringedge = 20
    o -= ~down(0.1)(
        cylinder(d=INNER_D - ringedge, h=0.3)
        - down(0.1)(cylinder(d=INNER_D - ringedge - 0.2, h=0.5))
    )

    # o = intersection()(up(CUP_DEPTH - THREAD_H - 5)(cube([100, 20, 100])), o)
    o = rotate([0, 0, 180])(o)

    if partinsertsections:
        if deepparts:
            fnbase = f"partinsert-deep-{partinsertsections}-"
        else:
            fnbase = f"partinsert-{partinsertsections}-"
    else:
        fnbase = "cupinsert-"
    saveasscad(o, fnbase + VER, fn=300)


def roundedCube(x, y, z, r, oo=False, xo=False, oy=False, xy=False):
    """Return a cube with rounded vertical corners

    oo, xo, oy, xy, corners that should be sharp, in the order
        origin, origin
        x, origin
        origin, y
        x, y
    """
    round = cylinder(r=r, h=z)
    sharp = translate([0, 0, z / 2])(cube([r * 2, r * 2, z], center=True))
    corners = [
        translate([r, r, 0])(round if not oo else sharp),
        translate([x - r, r, 0])(round if not xo else sharp),
        translate([r, y - r, 0])(round if not oy else sharp),
        translate([x - r, y - r, 0])(round if not xy else sharp),
    ]
    return hull()(*corners)


CARD_VER = "v1.2"
TEXT_DEPTH = 0.4


def rendercardholder(stackwidth, stackdepth, stackheight, count, rows=1):
    """Render a card holder to be connected to a pair of clips

    stackwidth: The width of a card container section (dimension that runs away
                from the table)
    stackdepth: The depth of a card container section (dimension that runs parallel
                to the edge of the table, same dimension as count)
    stackheight: The height of the container for the cards.
    count: The number of container sections, the same dimension as the stackdepth
    rows: Number of rows of cards
    """

    FLOOR = 1.4
    WALL = 1.5
    ARM_H = 5
    SUPPORT_W = 3
    R = 5  # Radius of cube curves

    totaldepth = stackdepth * count + WALL * (count + 1)

    armlength = TABLE_OVERHANG + 10 - CONNECTOR_INTERFACE_D

    # Clip interface and back wall
    o = rotate([-90, 0, 0])(interface(extraheight=-1))
    o += translate([0, totaldepth - CONNECTOR_WIDTH, 0])(
        rotate([-90, 0, 0])(interface(extraheight=-1))
    )
    o += cube([WALL, totaldepth, CONNECTOR_HEIGHT - 1])

    # Arms and supports
    arm = cube([armlength + R, CONNECTOR_WIDTH, ARM_H])
    # support is a simple 45° cutout
    support_x = armlength - WALL
    support_h = min(stackheight + FLOOR, CONNECTOR_HEIGHT - 1) - ARM_H * 2
    shortestedge = min(support_x / 2, support_h)

    # shortestsupport = min((armlength - WALL) / 2, support_h - ARM_H)
    # xturn = (armlength - WALL - shortestsupport) / 2
    # supportmiddle = armlength / 2 + WALL
    # supporttop = min(shortestsupport, support_h - ARM_H)
    arm += translate([0, SUPPORT_W / 2 + CONNECTOR_WIDTH / 2, 0])(
        rotate([90, 0, 0])(
            linear_extrude(height=SUPPORT_W)(
                polygon(
                    # [
                    #     [WALL, ARM_H],
                    #     [WALL + shortestedge, ARM_H],
                    #     [WALL + shortestedge, ARM_H + shortestedge],
                    #     [WALL, ARM_H + shortestedge],
                    # ]
                    [
                        [WALL, ARM_H],
                        [WALL + support_x / 2 - shortestedge, ARM_H],
                        [WALL + support_x / 2, ARM_H + min(support_h, shortestedge)],
                        [WALL + support_x / 2 + shortestedge, ARM_H],
                        [armlength + R, ARM_H],
                        [armlength + R, ARM_H * 2 + support_h],
                        [WALL, ARM_H * 2 + support_h],
                    ]
                )
            )
        )
    )

    o += arm
    o += translate([0, totaldepth - CONNECTOR_WIDTH, 0])(arm)

    # Include version in arm
    o -= translate([armlength / 2, CONNECTOR_WIDTH / 2, -0.1])(
        mirror([1, 0, 0])(
            linear_extrude(TEXT_DEPTH + 0.1)(
                text(
                    CARD_VER,
                    5,
                    font="Arial:style=Bold",
                    valign="center",
                    halign="center",
                )
            )
        )
    )
    configtxt = f"{stackwidth},{stackdepth},{stackheight},{count},{rows}"
    o -= translate([armlength / 2, totaldepth - CONNECTOR_WIDTH / 2, -0.1])(
        mirror([1, 0, 0])(
            linear_extrude(TEXT_DEPTH + 0.1)(
                text(
                    configtxt,
                    4,
                    font="Arial:style=Bold",
                    valign="center",
                    halign="center",
                )
            )
        )
    )

    # Card holder
    print(
        f"Card Cube Size:",
        rows * (stackwidth + WALL) + WALL,
        totaldepth,
        stackheight + FLOOR,
    )
    print(
        f"Print Size:",
        rows * (stackwidth + WALL) + WALL + CONNECTOR_DEPTH + armlength,
        totaldepth,
        stackheight + FLOOR,
    )
    o += translate([armlength, 0, 0])(
        roundedCube(
            rows * (stackwidth + WALL) + WALL, totaldepth, stackheight + FLOOR, R
        )
    )
    for j in range(rows):
        for i in range(count):
            oo, xo, oy, xy = True, True, True, True
            if i == 0 and j == 0:
                oo = False
            if i == 0 and j == rows - 1:
                xo = False
            if i == count - 1 and j == 0:
                oy = False
            if i == count - 1 and j == rows - 1:
                xy = False

            o -= translate(
                [
                    armlength + WALL + j * (stackwidth + WALL),
                    WALL + (WALL + stackdepth) * i,
                    FLOOR,
                ]
            )(roundedCube(stackwidth, stackdepth, stackheight * 2, R, oo, xo, oy, xy))

    return o


def rendercardholders():
    specs = [
        # (71, 30, 40, 3),
        # (71, 30, 40, 4, 2),
        # (150, 200, 5, 1),
        (88, 30, int(120 * 0.4), 2, 1),
    ]
    for spec in specs:
        saveasscad(
            rendercardholder(*spec),
            f"cardholder-{'_'.join([str(i) for i in spec])}-{CARD_VER}",
        )


# def renderinserttop():
#     VER = "v0.91"
#     INNER_D = 99
#     R = 9
#     WALL = R
#     H = 8
#     o = cylinder(d=INNER_D + WALL * 2, h=H)
#     o -= down(5)(metric_thread(XXX diameter=INNER_D + 2, length=20, pitch=2, thread_size=6))
#     o += up(H)(cylinder(d=INNER_D + WALL * 2, h=2))
#     o -= up(H - 0.01)(cylinder(d=INNER_D - 1.5 * 2, h=3))
#     o -= down(1)(cylinder(d=INNER_D + 2, h=2))
#     o = rotate([180, 0, 0])(o)
#     saveasscad(o, "cupinserttop-" + VER, fn=300)


def rendertestconnectors():
    VER = "v1.7"
    clip = rail_clip(txt=None)
    clip = intersection()(translate([-12, -10, 0])(cube([50, 10, 50])), clip)
    con = interface(wall=4)
    con = intersection()(translate([-50, -10.01, 0])(cube([50, 50, 50])), con)
    o = clip + translate([-14, -15, 0])(rotate([-90, 0, 0])(con))
    saveasscad(o, "testconnectors-" + VER, fn=300)

    o = translate([-4, 0, 0])(clip) + color("blue")(con)
    o = rotate([90, 0, 90])(o)
    saveasscad(o, "showconnectors-" + VER, fn=300)


def renderrailclip():
    VER = "v2.0"
    saveasscad(rotate([0, 0, 90])(rail_clip(txt=VER)), "railclip-" + VER, fn=300)


def renderspacer():
    VER = "v1.0"
    saveasscad(rotate([180, 0, 90])(spacer(txt=VER)), "spacer-" + VER, fn=300)


def main():
    # renderspacer()
    # rendercupholder()
    # renderwineglassholder()
    # renderrailclip()
    renderinsert(cupdepth=85)
    # renderinsert(2, True)
    # for i in [2, 3, 4, 5, 6]:
    #     renderinsert(i)

    # rendertestbracket()
    # renderinserttop()
    # rendertestconnectors()

    # rendercardholders()


def sin(angle):
    """Return the sin of a given angle in degrees"""
    return math.sin(math.radians(angle))


def cos(angle):
    """Return the cos of a given angle in degrees"""
    return math.cos(math.radians(angle))


def tan(angle):
    """Return the tan of a given angle in degrees"""
    return math.tan(math.radians(angle))


def saveasscad(obj, desc, fn=50):
    pfn = pathlib.Path(__file__)
    outfn = pfn.parent / ("{}.scad".format(desc))
    scad_render_to_file(obj, outfn, file_header=f"$fn = {fn};\n")
    # scad_render_animated_file(
    #     test_bracket,  # A function that takes a float argument
    #     # called '_time' in [0,1)
    #     # and returns an OpenSCAD object
    #     steps=12,  # Number of steps to create one complete motion
    #     back_and_forth=True,  # If true, runs the complete motion
    #     # forward and then in reverse,
    #     # to avoid discontinuity
    #     # out_dir=out_dir,
    #     include_orig_code=True,
    #     file_header=f"$fn = 300;\n",
    # )


if __name__ == "__main__":
    main()
