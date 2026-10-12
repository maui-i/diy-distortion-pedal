"""Generate the KiCad schematic (and the project symbol library) for the pedal.

Run with KiCad's bundled Python or any Python 3:
    python3 tools/gen_schematic.py

This script produced the initial design. Once you start editing the schematic
in KiCad itself, don't re-run it: it overwrites hardware/kicad/*.kicad_sch.
"""
import copy
import math
import os
import uuid

from sexp import Sym, dump, find, first, parse

KICAD_SHARE = os.environ.get(
    'KICAD_SHARE', '/Applications/KiCad/KiCad.app/Contents/SharedSupport')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT_DIR', os.path.join(HERE, '..', 'hardware', 'kicad'))
PROJECT = 'diy-distortion-pedal'
ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, PROJECT + '/root'))

_uid_counter = [0]


def uid():
    _uid_counter[0] += 1
    return str(uuid.uuid5(uuid.NAMESPACE_URL, '%s/%d' % (PROJECT, _uid_counter[0])))


S = Sym  # shorthand for bare atoms

# ---------------------------------------------------------------- libraries


def load_lib(name):
    path = os.path.join(KICAD_SHARE, 'symbols', name + '.kicad_sym')
    return {s[1]: s for s in find(parse(open(path).read()), 'symbol')}


def rename_units(sym, old, new):
    for sub in find(sym, 'symbol'):
        sub[1] = sub[1].replace(old + '_', new + '_', 1)


def flatten(lib, name):
    """Return a standalone copy of a library symbol, resolving `extends`."""
    sym = copy.deepcopy(lib[name])
    ext = first(sym, 'extends')
    if not ext:
        return sym
    parent = copy.deepcopy(lib[ext[1]])
    parent[1] = name
    rename_units(parent, ext[1], name)
    child_props = {p[1]: p for p in find(sym, 'property')}
    for i, item in enumerate(parent):
        if isinstance(item, list) and item[0] == 'property' and item[1] in child_props:
            parent[i] = child_props.pop(item[1])
    insert_at = max(i for i, x in enumerate(parent)
                    if isinstance(x, list) and x[0] == 'property') + 1
    for p in child_props.values():
        parent.insert(insert_at, p)
        insert_at += 1
    return parent


def make_3pdt(switch_lib):
    """3PDT footswitch: three SPDT units numbered like the 3x3 lug grid.

    Unit A: common 4, throws 1/7.  Unit B: common 5, throws 2/8.
    Unit C: common 6, throws 3/9.  Drawn with the common on lugs 1-2-3
    (effect ON).
    """
    spdt = copy.deepcopy(switch_lib['SW_SPDT'])
    spdt[1] = 'SW_3PDT'
    for p in find(spdt, 'property'):
        if p[1] == 'Value':
            p[2] = 'SW_3PDT'
        elif p[1] == 'Description':
            p[2] = '3PDT footswitch (9 lugs) for true bypass with LED'
        elif p[1] == 'ki_keywords':
            p[2] = 'switch 3pdt footswitch true bypass stomp'
    graphics = first(spdt, 'symbol')            # SW_SPDT_0_1, shared by all units
    pins_unit = [s for s in find(spdt, 'symbol') if s[1] == 'SW_SPDT_1_1'][0]
    graphics[1] = 'SW_3PDT_0_1'
    spdt[:] = [x for x in spdt if not (isinstance(x, list) and x[0] == 'symbol')]
    spdt.append(graphics)
    mapping = {1: {'1': '1', '2': '4', '3': '7'},
               2: {'1': '2', '2': '5', '3': '8'},
               3: {'1': '3', '2': '6', '3': '9'}}
    for unit, m in mapping.items():
        u = copy.deepcopy(pins_unit)
        u[1] = 'SW_3PDT_%d_1' % unit
        for pin in find(u, 'pin'):
            num = first(pin, 'number')
            num[1] = m[num[1]]
        spdt.append(u)
    # put pin_names / flags before the units, as KiCad does
    return spdt


LIBS = {n: load_lib(n) for n in [
    'Device', 'Amplifier_Operational', 'Connector_Audio', 'Connector',
    'Connector_Generic', 'Switch', 'power']}

LIB_SYMBOLS = {}


def lib_symbol(lib_id):
    if lib_id not in LIB_SYMBOLS:
        lib, name = lib_id.split(':')
        if lib_id == 'pedal:SW_3PDT':
            sym = make_3pdt(LIBS['Switch'])
        else:
            sym = flatten(LIBS[lib], name)
        LIB_SYMBOLS[lib_id] = sym
    return LIB_SYMBOLS[lib_id]


def pin_table(lib_id):
    """{(unit, number): (x, y)} pin endpoints in library coordinates (y up)."""
    sym = lib_symbol(lib_id)
    name = sym[1]
    out = {}
    for sub in find(sym, 'symbol'):
        unit = int(sub[1][len(name) + 1:].split('_')[0])
        for pin in find(sub, 'pin'):
            at = first(pin, 'at')
            out[(unit, first(pin, 'number')[1])] = (float(at[1]), float(at[2]))
    return out

# ---------------------------------------------------------------- placement


SYMBOLS, WIRES, LABELS, JUNCTIONS, NOCONNECTS, TEXTS, POWERS = [], [], [], [], [], [], []
PARTS = {}          # ref -> placement dict (unit 1)
_pwr = [0]


def to_sheet(x, y, lx, ly, rot, mirror):
    """Library point (lx, ly) -> sheet coordinates for a symbol at (x, y)."""
    if mirror == 'x':
        ly = -ly
    elif mirror == 'y':
        lx = -lx
    r = math.radians(rot)
    rx = lx * math.cos(r) - ly * math.sin(r)
    ry = lx * math.sin(r) + ly * math.cos(r)
    return (round(x + rx, 3), round(y - ry, 3))


def place(ref, lib_id, value, x, y, rot=0, footprint='', unit=1, mirror=None,
          on_board=True, ref_at=None, val_at=None, fields=None, hide_value=False):
    sym = lib_symbol(lib_id)
    p = dict(ref=ref, lib_id=lib_id, value=value, x=x, y=y, rot=rot,
             footprint=footprint, unit=unit, mirror=mirror, on_board=on_board,
             ref_at=ref_at, val_at=val_at, fields=fields or {},
             hide_value=hide_value)
    SYMBOLS.append(p)
    PARTS[(ref, unit)] = p
    return p


def P(ref, num, unit=1):
    """Sheet coordinates of a pin endpoint."""
    p = PARTS[(ref, unit)]
    lx, ly = pin_table(p['lib_id'])[(unit, str(num))]
    return to_sheet(p['x'], p['y'], lx, ly, p['rot'], p['mirror'])


def wire(*pts):
    for a, b in zip(pts, pts[1:]):
        WIRES.append((a, b))


def label(name, at, angle=0):
    LABELS.append((name, at, angle))


def junction(at):
    JUNCTIONS.append(at)


def nc(at):
    NOCONNECTS.append(at)


def text(s, x, y, size=1.27, bold=False):
    TEXTS.append((s, x, y, size, bold))


def power(kind, at, rot=0):
    """kind: '+9V', 'GND' or 'PWR_FLAG'."""
    _pwr[0] += 1
    ref = ('#FLG%02d' if kind == 'PWR_FLAG' else '#PWR%02d') % _pwr[0]
    place(ref, 'power:' + kind, kind, at[0], at[1], rot)


def gnd(at):
    power('GND', at)


def vcc(at):
    power('+9V', at)

# ---------------------------------------------------------------- the circuit


FP = {
    'R': 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
    'Cfilm': 'Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2',
    'Cdisc': 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',
    'CP5': 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',
    'CP6': 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',
    'DO35': 'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal',
    'DO41': 'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal',
    'DIP8': 'Package_DIP:DIP-8_W7.62mm_Socket',
    'POT': 'pedal:Pot_16mm_PCB',
    'H2': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
    'H1': 'Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical',
}


def build():
    # ---------------- input + gain stage
    text('INPUT + GAIN STAGE', 30.48, 50.8, 2.0, True)
    text('Gain = 1 + R3 / (R4 + RV1): about 214x with GAIN fully up', 30.48, 54.61)
    y0 = 63.5
    place('R1', 'Device:R', '1M', 50.8, y0 + 7.62, 0, FP['R'])
    place('C1', 'Device:C', '10n', 60.96, y0, 90, FP['Cfilm'])
    place('R2', 'Device:R', '1M', 71.12, y0 + 7.62, 0, FP['R'])
    place('IC1', 'Amplifier_Operational:TL071', 'TL071', 88.9, y0 + 2.54, 0, FP['DIP8'])
    place('R3', 'Device:R', '1M', 88.9, 83.82, 90, FP['R'])
    place('R4', 'Device:R', '4.7k', 76.2, 91.44, 0, FP['R'])
    place('RV1', 'Device:R_Potentiometer', 'C1M (GAIN)', 76.2, 102.87, 180, FP['POT'],
          ref_at=(81.28, 101.6), val_at=(81.28, 104.14))
    place('C2', 'Device:C', '47n', 66.04, 107.95, 0, FP['Cfilm'])

    label('FX_IN', (40.64, y0), 180)
    wire((40.64, y0), (50.8, y0))
    junction((50.8, y0))
    wire((50.8, y0), P('R1', 1))
    gnd(P('R1', 2))
    wire((50.8, y0), P('C1', 1))
    wire(P('C1', 2), (71.12, y0))
    junction((71.12, y0))
    wire((71.12, y0), P('R2', 1))
    label('VREF', P('R2', 2), 270)
    wire((71.12, y0), P('IC1', 3))
    vcc(P('IC1', 7))
    gnd(P('IC1', 4))
    nc(P('IC1', 1))
    nc(P('IC1', 5))
    inv = (76.2, P('IC1', 2)[1])
    wire(P('IC1', 2), inv)
    node_inv = (76.2, 83.82)
    wire(inv, node_inv)
    junction(node_inv)
    wire(node_inv, P('R3', 1))
    out_node = (101.6, P('IC1', 6)[1])
    wire(P('R3', 2), (101.6, 83.82), out_node)
    wire(P('IC1', 6), out_node)
    junction(out_node)
    wire(node_inv, P('R4', 1))
    wire(P('R4', 2), P('RV1', 3))
    wiper = P('RV1', 2)
    wire(P('RV1', 1), (76.2, 109.22), (wiper[0], 109.22), wiper)
    junction(wiper)
    wire(wiper, (66.04, wiper[1]), P('C2', 1))
    gnd(P('C2', 2))

    # ---------------- clipping + level
    text('CLIPPING + LEVEL', 106.68, 50.8, 2.0, True)
    text('D1 and D2 face opposite ways', 127, 90.17)
    place('C3', 'Device:C_Polarized', '1u', 109.22, out_node[1], 90, FP['CP5'])
    place('R5', 'Device:R', '10k', 120.65, out_node[1], 90, FP['R'])
    place('D1', 'Device:D', '1N34A', 132.08, 73.66, 90, FP['DO35'],
          ref_at=(134.62, 72.39), val_at=(134.62, 74.93))
    place('D2', 'Device:D', '1N34A', 144.78, 73.66, 270, FP['DO35'],
          ref_at=(147.32, 72.39), val_at=(147.32, 74.93))
    place('C4', 'Device:C', '1n', 157.48, 73.66, 0, FP['Cfilm'])
    place('RV2', 'Device:R_Potentiometer', 'A10K (LEVEL)', 170.18, 73.66, 180, FP['POT'],
          ref_at=(172.72, 72.39), val_at=(172.72, 74.93))

    wire(out_node, P('C3', 1))
    wire(P('C3', 2), P('R5', 1))
    yc = out_node[1]
    xs = [P('D1', 2)[0], P('D2', 1)[0], P('C4', 1)[0]]
    wire(P('R5', 2), (xs[0], yc), (xs[1], yc), (xs[2], yc), (170.18, yc))
    wire((170.18, yc), P('RV2', 3))
    for x in xs:
        junction((x, yc))
    label('CLIP', (160.02, yc), 0)
    wire((xs[0], yc), P('D1', 2))      # D1 anode to CLIP
    gnd(P('D1', 1))
    wire((xs[1], yc), P('D2', 1))      # D2 cathode to CLIP
    gnd(P('D2', 2))
    wire((xs[2], yc), P('C4', 1))
    gnd(P('C4', 2))
    gnd(P('RV2', 1))
    w2 = P('RV2', 2)
    wire(w2, (w2[0], 83.82), (177.8, 83.82))
    label('FX_OUT', (177.8, 83.82), 0)

    # ---------------- power
    ox = 10.16
    text('POWER', 55.88 + ox, 128.27, 2.0, True)
    text('9 V DC only. VREF is about 4.5 V (half the supply).', 55.88 + ox, 132.08)
    yr = 139.7
    place('D3', 'Device:D_Schottky', '1N5817', 66.04 + ox, yr, 180, FP['DO41'])
    place('C5', 'Device:C_Polarized', '100u', 81.28 + ox, yr + 7.62, 0, FP['CP6'])
    place('C6', 'Device:C', '100n', 91.44 + ox, yr + 7.62, 0, FP['Cdisc'])
    place('R6', 'Device:R', '100k', 101.6 + ox, yr + 7.62, 0, FP['R'])
    place('R7', 'Device:R', '100k', 101.6 + ox, yr + 22.86, 0, FP['R'])
    place('C7', 'Device:C_Polarized', '10u', 111.76 + ox, yr + 22.86, 0, FP['CP5'])
    place('R8', 'Device:R', '4.7k', 127 + ox, yr + 7.62, 0, FP['R'])
    text('Put C6 right next to IC1 pin 7', 66.04, yr + 20.32)
    power('PWR_FLAG', (66.04, yr + 30.48))
    wire((66.04, yr + 30.48), (66.04, yr + 33.02))
    gnd((66.04, yr + 33.02))

    label('VIN', (55.88 + ox, yr), 180)
    wire((55.88 + ox, yr), P('D3', 2))
    xs = [76.2 + ox, 81.28 + ox, 91.44 + ox, 101.6 + ox]
    wire(P('D3', 1), *[(x, yr) for x in xs], (127 + ox, yr))
    for x in xs:
        junction((x, yr))
    vcc((76.2 + ox, yr))
    power('PWR_FLAG', (111.76, yr))
    for r in ('C5', 'C6', 'R6', 'R8'):
        wire((P(r, 1)[0], yr), P(r, 1)) if r != 'R8' else wire((127 + ox, yr), P(r, 1))
    gnd(P('C5', 2))
    gnd(P('C6', 2))
    vnode = (101.6 + ox, yr + 15.24)
    wire(P('R6', 2), vnode, P('R7', 1))
    junction(vnode)
    cnode = (111.76 + ox, vnode[1])
    wire(vnode, cnode, P('C7', 1))
    junction(cnode)
    wire(cnode, (119.38 + ox, vnode[1]))
    label('VREF', (119.38 + ox, vnode[1]), 0)
    gnd(P('R7', 2))
    gnd(P('C7', 2))
    wire(P('R8', 2), (127 + ox, yr + 15.24))
    label('LED_A', (127 + ox, yr + 15.24), 0)

    # ---------------- board connectors
    text('BOARD PADS', 20.32, 120.65, 2.0, True)
    conns = [('J1', 'IN', 'FX_IN', True), ('J2', 'OUT', 'FX_OUT', True),
             ('J3', '9V IN', 'VIN', True), ('J4', 'LED+', 'LED_A', False)]
    for i, (ref, val, net, has_gnd) in enumerate(conns):
        y = 129.54 + i * 12.7
        lib = 'Connector_Generic:Conn_01x02' if has_gnd else 'Connector_Generic:Conn_01x01'
        place(ref, lib, val, 43.18, y, 0, FP['H2'] if has_gnd else FP['H1'],
              ref_at=(45.72, y - 2.54), val_at=(45.72, y + (5.08 if has_gnd else 2.54)))
        wire(P(ref, 1), (30.48, y))
        label(net, (30.48, y), 180)
        if has_gnd:
            wire(P(ref, 2), (33.02, y + 2.54))
            gnd((33.02, y + 2.54))

    # ---------------- off-board wiring
    text('OFF-BOARD WIRING (not on the PCB)', 190.5, 30.48, 2.0, True)
    text('Footswitch drawn in the EFFECT ON position.', 190.5, 34.29)
    text('Lugs seen from underneath:  1 2 3 / 4 5 6 / 7 8 9', 190.5, 37.465)
    # CHECK_ALL=1 keeps off-board parts in the netlist so check_netlist.py sees them
    of = dict(on_board=bool(os.environ.get('CHECK_ALL')))
    place('J5', 'Connector_Audio:AudioJack2', 'Input jack', 200.66, 48.26, 0,
          mirror='x', **of)
    place('J6', 'Connector_Audio:AudioJack2', 'Output jack', 200.66, 71.12, 0,
          mirror='x', **of)
    for unit, y in ((1, 48.26), (2, 71.12), (3, 93.98)):
        place('SW1', 'pedal:SW_3PDT', '3PDT footswitch', 223.52, y, 0, unit=unit,
              ref_at=(223.52, y - 5.08), val_at=(223.52, y + 5.08), **of)
    place('D4', 'Device:LED', 'LED', 254, P('SW1', 3, 3)[1], 0, **of)

    for jack, unit, common, on, off, net in (('J5', 1, 4, 1, 7, 'FX_IN'),
                                              ('J6', 2, 5, 2, 8, 'FX_OUT')):
        wire(P(jack, 'T'), P('SW1', common, unit))
        s = P(jack, 'S')
        wire(s, (s[0] + 5.08, s[1]))
        gnd((s[0] + 5.08, s[1]))
        a = P('SW1', on, unit)
        wire(a, (a[0] + 7.62, a[1]))
        label(net, (a[0] + 7.62, a[1]), 0)
        b = P('SW1', off, unit)
        wire(b, (b[0] + 7.62, b[1]))
        label('BYPASS', (b[0] + 7.62, b[1]), 0)
    c6 = P('SW1', 6, 3)
    wire(c6, (c6[0] - 5.08, c6[1]))
    gnd((c6[0] - 5.08, c6[1]))
    wire(P('SW1', 3, 3), P('D4', 1))
    nc(P('SW1', 9, 3))
    a = P('D4', 2)
    wire(a, (a[0] + 5.08, a[1]))
    label('LED_A', (a[0] + 5.08, a[1]), 0)
    text('LED anode wires to pad J4 (R8 on the board limits the current).', 190.5, 104.14)

    text('POWER INPUT', 190.5, 113.03, 2.0, True)
    text('J7: 2.1 mm center-negative. Pin 3 touches pin 2 only with no plug in,', 190.5, 116.84)
    text('so plugging in an adapter disconnects the battery.', 190.5, 120.015)
    place('J7', 'Connector:Barrel_Jack_Switch', 'DC jack', 200.66, 132.08, 0,
          mirror='x', **of)
    place('BT1', 'Device:Battery_Cell', '9V', 233.68, 137.16, 0, **of,
          ref_at=(236.22, 134.62), val_at=(236.22, 137.16))
    center, sleeve, switch = P('J7', 1), P('J7', 2), P('J7', 3)
    wire(center, (center[0] + 5.08, center[1]))
    gnd((center[0] + 5.08, center[1]))
    wire(sleeve, (sleeve[0] + 2.54, sleeve[1]), (sleeve[0] + 2.54, 125.73),
         (sleeve[0] + 12.7, 125.73))
    label('VIN', (sleeve[0] + 12.7, 125.73), 0)
    wire(switch, (233.68, switch[1]), P('BT1', 1))
    gnd(P('BT1', 2))

# ---------------------------------------------------------------- output


def font(size=1.27, bold=False):
    f = [S('font'), [S('size'), size, size]]
    if bold:
        f.append([S('bold'), S('yes')])
    return f


def prop(name, value, at, angle=0, hide=False, justify=None, flip=False):
    eff = [S('effects'), font()]
    if justify and flip:
        justify = {'left': 'right', 'right': 'left'}[justify]
    if justify:
        eff.append([S('justify'), S(justify)])
    if hide:
        eff.append([S('hide'), S('yes')])
    return [S('property'), name, value, [S('at'), at[0], at[1], angle], eff]


def symbol_instance(p):
    sym = lib_symbol(p['lib_id'])
    is_power = p['lib_id'].startswith('power:')
    x, y = p['x'], p['y']
    pins = sorted({num for (unit, num) in pin_table(p['lib_id'])
                   if unit in (0, p['unit'])})
    pts = [to_sheet(x, y, lx, ly, p['rot'], p['mirror'])
           for (unit, _), (lx, ly) in pin_table(p['lib_id']).items()
           if unit in (0, p['unit'])]
    vertical = len(pts) == 2 and pts[0][0] == pts[1][0]
    if p['ref_at']:
        ref_at, val_at, just = p['ref_at'], p['val_at'], 'left'
    elif is_power:
        ref_at, val_at, just = (x, y + 6.35), (x, y + (5.08 if 'GND' in p['lib_id'] else -3.81)), None
        if p['lib_id'] == 'power:PWR_FLAG':
            val_at = (x, y - 3.81)
    elif p['lib_id'].startswith('Amplifier'):
        ref_at, val_at, just = (x + 3.81, y - 6.35), (x + 3.81, y + 6.35), 'left'
    elif p['lib_id'].startswith(('Connector', 'pedal')):
        ref_at, val_at, just = (x, y - 7.62), (x, y + 7.62), None
    elif vertical:
        ref_at, val_at, just = (x + 2.54, y - 1.27), (x + 2.54, y + 1.27), 'left'
    else:
        ref_at, val_at, just = (x, y - 3.81), (x, y + 3.81), None
    # field angles/justification are stored relative to the symbol's rotation
    fa = p['rot'] % 180
    flip = (p['rot'] + fa) % 360 == 180
    node = [S('symbol'), [S('lib_id'), p['lib_id']], [S('at'), x, y, p['rot']]]
    if p['mirror']:
        node.append([S('mirror'), S(p['mirror'])])
    node += [[S('unit'), p['unit']],
             [S('exclude_from_sim'), S('no')],
             [S('in_bom'), S('no' if is_power else 'yes')],
             [S('on_board'), S('yes' if p['on_board'] else 'no')],
             [S('dnp'), S('no')],
             [S('uuid'), uid()],
             prop('Reference', p['ref'], ref_at, fa, hide=is_power, justify=just, flip=flip),
             prop('Value', p['value'], val_at, fa, hide=p['hide_value'], justify=just,
                  flip=flip),
             prop('Footprint', p['footprint'], (x, y), 0, hide=True),
             prop('Datasheet', '~', (x, y), 0, hide=True),
             prop('Description', '', (x, y), 0, hide=True)]
    for k, v in p['fields'].items():
        node.append(prop(k, v, (x, y), 0, hide=True))
    for num in pins:
        node.append([S('pin'), num, [S('uuid'), uid()]])
    node.append([S('instances'),
                 [S('project'), PROJECT,
                  [S('path'), '/' + ROOT_UUID,
                   [S('reference'), p['ref']], [S('unit'), p['unit']]]]])
    return node


def named(lib_id, sym):
    sym = copy.deepcopy(sym)
    sym[1] = lib_id
    return sym


def write_schematic():
    build()
    tree = [S('kicad_sch'), [S('version'), S('20250114')],
            [S('generator'), 'eeschema'], [S('generator_version'), '9.0'],
            [S('uuid'), ROOT_UUID], [S('paper'), 'A4'],
            [S('title_block'),
             [S('title'), 'DIY Distortion Pedal (Distortion+ style)'],
             [S('date'), '2026-10-12'], [S('rev'), '1.0'],
             [S('company'), 'github.com/maui-i/diy-distortion-pedal'],
             [S('comment'), 1, 'Op-amp gain stage + germanium diode clipping'],
             [S('comment'), 2, 'Part refs match docs/build-guide.md (GAIN = RV1, LEVEL = RV2)']],
            [S('lib_symbols')] + [named(k, v) for k, v in LIB_SYMBOLS.items()]]
    for at in JUNCTIONS:
        tree.append([S('junction'), [S('at'), at[0], at[1]], [S('diameter'), 0],
                     [S('color'), 0, 0, 0, 0], [S('uuid'), uid()]])
    for at in NOCONNECTS:
        tree.append([S('no_connect'), [S('at'), at[0], at[1]], [S('uuid'), uid()]])
    for a, b in WIRES:
        if a == b:
            continue
        tree.append([S('wire'), [S('pts'), [S('xy'), a[0], a[1]], [S('xy'), b[0], b[1]]],
                     [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
                     [S('uuid'), uid()]])
    for s, x, y, size, bold in TEXTS:
        tree.append([S('text'), s, [S('exclude_from_sim'), S('no')],
                     [S('at'), x, y, 0],
                     [S('effects'), font(size, bold), [S('justify'), S('left'), S('bottom')]],
                     [S('uuid'), uid()]])
    for name, at, angle in LABELS:
        just = [S('justify'), S('right' if angle in (180, 270) else 'left'), S('bottom')]
        tree.append([S('label'), name, [S('at'), at[0], at[1], angle],
                     [S('effects'), font(), just], [S('uuid'), uid()]])
    for p in SYMBOLS:
        tree.append(symbol_instance(p))
    tree.append([S('sheet_instances'), [S('path'), '/', [S('page'), '1']]])
    tree.append([S('embedded_fonts'), S('no')])
    path = os.path.join(OUT, PROJECT + '.kicad_sch')
    with open(path, 'w') as f:
        f.write(dump(tree) + '\n')
    print('wrote', path)

    # project symbol library with the 3PDT
    lib = [S('kicad_symbol_lib'), [S('version'), S('20241209')],
           [S('generator'), 'kicad_symbol_editor'], [S('generator_version'), '9.0'],
           lib_symbol('pedal:SW_3PDT')]
    with open(os.path.join(OUT, 'pedal.kicad_sym'), 'w') as f:
        f.write(dump(lib) + '\n')


if __name__ == '__main__':
    write_schematic()
