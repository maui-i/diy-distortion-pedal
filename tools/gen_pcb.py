"""Generate the PCB from the schematic's netlist, autoroute it, pour ground.

Needs KiCad's bundled Python (it imports pcbnew) and Java for Freerouting:
    kicad-cli sch export netlist -o build/pedal.net hardware/kicad/diy-distortion-pedal.kicad_sch
    $KICAD_PYTHON tools/gen_pcb.py build/pedal.net path/to/freerouting.jar

Like gen_schematic.py this made the first version of the board; once you edit
the board in KiCad, don't re-run it.
"""
import os
import subprocess
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import find, first, parse  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KDIR = os.path.join(HERE, '..', 'hardware', 'kicad')
BOARD_PATH = os.path.join(KDIR, 'diy-distortion-pedal.kicad_pcb')
FP_ROOT = os.environ.get(
    'KICAD_FOOTPRINTS', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')

# Board: 50 x 40 mm, origin top-left at (100, 100). Coordinates are the
# footprint origin (pad 1 for most THT parts); rotation in degrees CCW.
# Seen from the component side. Pots go on the BACK so their shafts point
# through the enclosure lid; from the lid, LEVEL is on the left, GAIN on
# the right, input pad on the right (pedal convention).
X0, Y0, W, H = 100.0, 100.0, 50.0, 48.0
# Nothing with through-holes goes under the pot bodies (their metal cans would
# short the solder joints); only R6/R7 sit in the gap between the pots.
PLACE = {
    # ref: (x, y, rot, back)
    'RV1': (112.5, 108.5, 180, True),     # GAIN
    'RV2': (137.5, 108.5, 180, True),     # LEVEL
    'J3':  (102.5, 104.0, 0, False),      # 9V in
    'J4':  (147.5, 104.0, 0, False),      # LED+
    'R6':  (123.5, 104.0, 270, False),
    'R7':  (126.5, 104.0, 270, False),
    # row A: input, gain stage, clipping
    'R1':  (104.8, 120.0, 270, False),
    'C1':  (108.0, 121.0, 270, False),
    'R2':  (111.2, 120.0, 270, False),
    'IC1': (115.5, 121.0, 0, False),
    'R4':  (126.3, 120.0, 270, False),
    'C2':  (129.5, 121.0, 270, False),
    'C4':  (132.7, 121.0, 270, False),
    'R5':  (135.9, 120.0, 270, False),
    'D1':  (139.1, 120.0, 270, False),
    'D2':  (142.3, 127.62, 90, False),
    'J2':  (146.5, 121.0, 0, False),      # OUT
    # row B
    'J1':  (102.5, 131.0, 0, False),      # IN
    'R3':  (115.5, 132.0, 0, False),
    'C3':  (130.0, 132.5, 0, False),
    # row C: power
    'D3':  (105.0, 141.0, 0, False),
    'C5':  (119.6, 141.5, 0, False),
    'C6':  (125.8, 131.8, 270, False),  # close to IC1 pin 7
    'C7':  (134.0, 141.5, 0, False),
    'R8':  (139.0, 141.0, 0, False),
}
SILK = [  # (text, x, y, layer, size)
    ('9V', 102.5, 101.9, 'F.SilkS', 0.9),
    ('GND', 102.5, 108.7, 'F.SilkS', 0.8),
    ('LED+', 147.5, 106.5, 'F.SilkS', 0.8),
    ('OUT', 146.5, 119.0, 'F.SilkS', 0.9),
    ('GND', 146.5, 125.7, 'F.SilkS', 0.8),
    ('IN', 102.5, 129.0, 'F.SilkS', 0.9),
    ('GND', 102.5, 135.7, 'F.SilkS', 0.8),
    ('DIY DISTORTION+  rev 1.0', 125.0, 146.6, 'F.SilkS', 0.9),
    ('GAIN pot (on back)', 112.5, 113.8, 'F.SilkS', 0.8),
    ('LEVEL pot (on back)', 137.5, 113.8, 'F.SilkS', 0.8),
    ('GAIN', 112.5, 104.2, 'B.SilkS', 1.2),
    ('LEVEL', 137.5, 104.2, 'B.SilkS', 1.2),
    ('github.com/maui-i/diy-distortion-pedal', 125.0, 146.0, 'B.SilkS', 0.8),
]


LAYER = {'F.SilkS': pcbnew.F_SilkS, 'B.SilkS': pcbnew.B_SilkS,
         'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}


def mm(x, y):
    return pcbnew.VECTOR2I_MM(x, y)


def load_netlist(path):
    tree = parse(open(path).read())
    comps = {}
    for c in find(first(tree, 'components'), 'comp'):
        ref = first(c, 'ref')[1]
        comps[ref] = dict(value=first(c, 'value')[1],
                          footprint=first(c, 'footprint')[1],
                          tstamp=first(c, 'tstamps')[1])
    nets = {}
    for n in find(first(tree, 'nets'), 'net'):
        name = first(n, 'name')[1]
        for node in find(n, 'node'):
            nets[(first(node, 'ref')[1], first(node, 'pin')[1])] = name
    return comps, nets


def lib_path(lib):
    if lib == 'pedal':
        return os.path.join(KDIR, 'pedal.pretty')
    return os.path.join(FP_ROOT, lib + '.pretty')


def add_text(board, s, x, y, layer, size):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(mm(x, y))
    t.SetLayer(LAYER[layer])
    t.SetTextSize(mm(size, size))
    t.SetTextThickness(pcbnew.FromMM(size * 0.15))
    if layer.startswith('B.'):
        t.SetMirrored(True)
    board.Add(t)


def set_netclasses(board):
    # same values as hardware/kicad/diy-distortion-pedal.kicad_pro
    ns = board.GetDesignSettings().m_NetSettings
    default = ns.GetDefaultNetclass()
    default.SetTrackWidth(pcbnew.FromMM(0.4))
    default.SetClearance(pcbnew.FromMM(0.25))
    default.SetViaDiameter(pcbnew.FromMM(0.9))
    default.SetViaDrill(pcbnew.FromMM(0.45))
    power = pcbnew.NETCLASS('Power')
    power.SetTrackWidth(pcbnew.FromMM(0.7))
    power.SetClearance(pcbnew.FromMM(0.25))
    power.SetViaDiameter(pcbnew.FromMM(0.9))
    power.SetViaDrill(pcbnew.FromMM(0.45))
    power.SetPriority(0)
    ns.SetNetclass('Power', power)
    for net in ('+9V', 'GND', '/VIN'):
        ns.SetNetclassPatternAssignment(net, 'Power')


def build(netlist):
    comps, pinnets = load_netlist(netlist)
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    set_netclasses(board)
    nets = {}
    for name in sorted(set(pinnets.values())):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        nets[name] = ni
    for ref, c in sorted(comps.items()):
        lib, name = c['footprint'].split(':')
        fp = pcbnew.FootprintLoad(lib_path(lib), name)
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(c['value'])
        fp.SetPath(pcbnew.KIID_PATH('/' + c['tstamp']))
        board.Add(fp)
        x, y, rot, back = PLACE[ref]
        fp.SetPosition(mm(x, y))
        if back:
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            net = pinnets.get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(nets[net])
        ref_text = fp.Reference()
        ref_text.SetTextSize(mm(0.9, 0.9))
        ref_text.SetTextThickness(pcbnew.FromMM(0.14))
        if ref.startswith(('J', 'RV')):
            ref_text.SetVisible(False)          # labelled with SILK text instead
        else:
            # put the reference inside the part outline so dense rows stay readable
            pads = list(fp.Pads())
            cx = sum(p.GetPosition().x for p in pads) // len(pads)
            cy = sum(p.GetPosition().y for p in pads) // len(pads)
            if 'CP_Radial' in c['footprint']:
                cy -= pcbnew.FromMM(4.0)        # above the can, clear of the pads
                ref_text.SetTextAngleDegrees(0)
            else:
                ref_text.SetTextAngleDegrees(rot % 180 if ref != 'IC1' else 90)
            ref_text.SetPosition(pcbnew.VECTOR2I(cx, cy))
        fp.Value().SetVisible(False)
    # outline with 2 mm rounded corners
    r = 2.0
    corners = [(X0, Y0), (X0 + W, Y0), (X0 + W, Y0 + H), (X0, Y0 + H)]
    edge = pcbnew.Edge_Cuts
    segs = [((X0 + r, Y0), (X0 + W - r, Y0)), ((X0 + W, Y0 + r), (X0 + W, Y0 + H - r)),
            ((X0 + W - r, Y0 + H), (X0 + r, Y0 + H)), ((X0, Y0 + H - r), (X0, Y0 + r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(mm(*a)); s.SetEnd(mm(*b)); s.SetLayer(edge)
        s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)
    for (cx, cy), (sx, sy) in zip(corners, [(1, 1), (-1, 1), (-1, -1), (1, -1)]):
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        ccx, ccy = cx + sx * r, cy + sy * r
        k = r / 2 ** 0.5
        s.SetArcGeometry(mm(cx, ccy), mm(ccx - sx * k, ccy - sy * k), mm(ccx, cy))
        s.SetLayer(edge)
        s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)
    for args in SILK:
        add_text(board, *args)
    return board


def add_ground_pours(board):
    gnd = board.FindNet('GND')
    for layer in ('F.Cu', 'B.Cu'):
        z = pcbnew.ZONE(board)
        z.SetLayer(LAYER[layer])
        z.SetNet(gnd)
        z.SetLocalClearance(pcbnew.FromMM(0.4))
        z.SetMinThickness(pcbnew.FromMM(0.3))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(pcbnew.FromMM(0.4))
        z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
        poly = z.Outline()
        poly.NewOutline()
        for x, y in ((X0, Y0), (X0 + W, Y0), (X0 + W, Y0 + H), (X0, Y0 + H)):
            poly.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
        board.Add(z)
    # Zones are filled afterwards with: kicad-cli pcb drc --refill-zones --save-board
    # (ZONE_FILLER crashes when pcbnew runs outside the KiCad GUI).


def main(netlist, jar):
    board = build(netlist)
    board.SynchronizeNetsAndNetClasses(True)
    work = os.path.join(KDIR, '..', '..', 'build')
    os.makedirs(work, exist_ok=True)
    pcbnew.SaveBoard(os.path.join(work, 'placed.kicad_pcb'), board)
    if jar == '--place-only':
        return
    dsn = os.path.join(work, 'pedal.dsn')
    ses = os.path.join(work, 'pedal.ses')
    pcbnew.ExportSpecctraDSN(board, dsn)
    subprocess.run(['java', '-jar', jar, '-de', dsn, '-do', ses, '-mp', '100',
                    '--gui.enabled=false'], check=True)
    pcbnew.ImportSpecctraSES(board, ses)
    add_ground_pours(board)
    pcbnew.SaveBoard(BOARD_PATH, board)
    print('wrote', BOARD_PATH)


if __name__ == '__main__':
    main(*sys.argv[1:3])
