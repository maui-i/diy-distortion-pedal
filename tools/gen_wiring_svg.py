"""Draw docs/images/wiring-diagram.svg: everything that is wired, not soldered
onto the PCB (jacks, footswitch, DC jack, battery, LED).

    python3 tools/gen_wiring_svg.py

The connections here must match the schematic's off-board section; the list
in WIRES is checked against tools/check_netlist.py's EXPECTED nets below.
"""
import os

from check_netlist import EXPECTED

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'docs', 'images', 'wiring-diagram.svg')

COL = {'in': '#d9a400', 'out': '#2e9e44', 'gnd': '#222222', 'pwr': '#d32f2f',
       'led': '#1e6fd9', 'byp': '#8a8a8a'}

# Board seen from the pot side (as it sits under the lid): 6 px per mm,
# mirrored left/right compared with the KiCad view.
BX, BY, S = 350, 140, 6


def pad(x_mm, y_mm):
    return (BX + (50 - x_mm) * S, BY + y_mm * S)


PADS = {  # name: (position, node in the netlist, label)
    'J3.1': (pad(2.5, 4.0), '9V'), 'J3.2': (pad(2.5, 6.54), 'GND'),
    'J4.1': (pad(47.5, 4.0), 'LED+'),
    'J1.1': (pad(2.5, 31.0), 'IN'), 'J1.2': (pad(2.5, 33.54), 'GND'),
    'J2.1': (pad(46.5, 21.0), 'OUT'), 'J2.2': (pad(46.5, 23.54), 'GND'),
}
P = {k: v[0] for k, v in PADS.items()}

LUG = {n: (440 + 60 * ((n - 1) % 3), 500 + 60 * ((n - 1) // 3)) for n in range(1, 10)}
for n, xy in LUG.items():
    P['SW1.%d' % n] = xy
P.update({
    'J7.1': (570, 95), 'J7.2': (610, 95), 'J7.3': (650, 95),      # DC jack
    'BT1.1': (720, 90), 'BT1.2': (760, 90),                        # battery + / -
    'J5.S': (800, 341), 'J5.T': (830, 370),                        # input jack
    'J6.S': (200, 281), 'J6.T': (170, 310),                        # output jack
    'D4.1': (600, 470), 'D4.2': (640, 470),                        # LED K / A
})

# (from, to, colour, route) - route is the list of bends between the two ends
WIRES = [
    ('J7.2', 'J3.1', 'pwr', [(610, 164)]),
    ('J7.1', 'J3.2', 'gnd', [(570, 179)]),
    ('J7.3', 'BT1.1', 'pwr', [(650, 115), (720, 115)]),
    ('BT1.2', 'J3.2', 'gnd', [(760, 179)]),
    ('J5.S', 'J1.2', 'gnd', []),
    ('J5.T', 'SW1.4', 'in', [(830, 530), (470, 530)]),
    ('SW1.1', 'J1.1', 'in', [(440, 450), (610, 450), (610, 326)]),
    ('SW1.2', 'J2.1', 'out', [(500, 470), (390, 470), (390, 266)]),
    ('J6.S', 'J2.2', 'gnd', []),
    ('J6.T', 'SW1.5', 'out', [(170, 590), (470, 590)]),
    ('SW1.7', 'SW1.8', 'byp', []),
    ('SW1.6', 'J1.2', 'gnd', [(680, 560), (680, 341)]),
    ('D4.1', 'SW1.3', 'led', [(560, 470)]),
    ('D4.2', 'J4.1', 'led', [(740, 470), (740, 128), (BX + 2.5 * S, 128)]),
]


def check():
    """Every wire must join two nodes of the same net in the schematic."""
    net_of = {node: name for name, nodes in EXPECTED.items() for node in nodes}
    for a, b, _, _ in WIRES:
        assert net_of[a] == net_of[b], (a, b, net_of[a], net_of[b])


# ------------------------------------------------------------------ drawing

def crossings(seg, others):
    (x1, y1), (x2, y2) = seg
    out = []
    for (u1, v1), (u2, v2) in others:
        if y1 == y2 and u1 == u2:          # horizontal vs vertical
            if min(x1, x2) < u1 < max(x1, x2) and min(v1, v2) < y1 < max(v1, v2):
                out.append((u1, y1))
        elif x1 == x2 and v1 == v2:        # vertical vs horizontal
            if min(y1, y2) < v1 < max(y1, y2) and min(u1, u2) < x1 < max(u1, u2):
                out.append((x1, v1))
    return out


def path_with_hops(pts, drawn, r=6):
    d = 'M%g %g' % pts[0]
    for a, b in zip(pts, pts[1:]):
        hops = crossings((a, b), drawn)
        horiz = a[1] == b[1]
        sign = 1 if (b[0] - a[0] if horiz else b[1] - a[1]) > 0 else -1
        hops.sort(key=lambda c: sign * (c[0] if horiz else c[1]))
        for cx, cy in hops:
            if horiz:
                d += ' L%g %g A%d %d 0 0 %d %g %g' % (cx - sign * r, cy, r, r,
                                                      1 if sign > 0 else 0, cx + sign * r, cy)
            else:
                d += ' L%g %g A%d %d 0 0 %d %g %g' % (cx, cy - sign * r, r, r,
                                                      0 if sign > 0 else 1, cx, cy + sign * r)
        d += ' L%g %g' % b
    return d


def text(x, y, s, size=13, anchor='middle', weight='normal', fill='#222'):
    return ('<text x="%g" y="%g" font-size="%d" text-anchor="%s" font-weight="%s" '
            'fill="%s">%s</text>' % (x, y, size, anchor, weight, fill, s))


def box(x1, y1, x2, y2, fill='#f2f2f2', stroke='#555', rx=6, dash=False):
    extra = ' stroke-dasharray="6 5"' if dash else ''
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%d" fill="%s" stroke="%s" '
            'stroke-width="1.5"%s/>' % (x1, y1, x2 - x1, y2 - y1, rx, fill, stroke, extra))


def build():
    check()
    o = []
    o.append(box(140, 20, 860, 700, fill='none', stroke='#9a9a9a', rx=24, dash=True))
    o.append(text(150, 690, 'enclosure outline (not to scale)', 12, 'start', fill='#777'))
    # PCB
    o.append(box(BX, BY, BX + 50 * S, BY + 48 * S, fill='#e8f1e8', stroke='#2f6b3a', rx=12))
    for cx, name in ((12.5, 'GAIN'), (37.5, 'LEVEL')):
        x, y = pad(cx, 8.5)
        o.append('<circle cx="%g" cy="%g" r="48" fill="#ffffff" stroke="#2f6b3a" '
                 'stroke-dasharray="5 4"/>' % (x, y))
        o.append(text(x, y + 5, name + ' pot', 14, weight='bold', fill='#2f6b3a'))
    o.append(text(BX + 25 * S, BY + 48 * S - 40, 'PCB, seen from the pot side', 14,
                  weight='bold', fill='#2f6b3a'))
    o.append(text(BX + 25 * S, BY + 48 * S - 22, '(all other parts are on the far side)', 12,
                  fill='#2f6b3a'))
    # off-board parts
    o.append(box(545, 30, 675, 95))
    o.append(text(610, 47, 'DC jack', 13, weight='bold'))
    o.append(text(610, 62, '2.1 mm, centre −', 11))
    o.append(box(695, 40, 785, 90))
    o.append(text(740, 62, '9 V battery', 13, weight='bold'))
    o.append(text(720, 84, '+', 14, weight='bold', fill=COL['pwr']))
    o.append(text(760, 84, '−', 14, weight='bold'))
    o.append(box(800, 310, 880, 370))
    o.append(text(840, 333, 'INPUT', 13, weight='bold'))
    o.append(text(840, 349, 'jack', 12))
    o.append(box(120, 250, 200, 310))
    o.append(text(160, 273, 'OUTPUT', 13, weight='bold'))
    o.append(text(160, 289, 'jack', 12))
    o.append(box(410, 480, 590, 650, fill='#f7f7f7'))
    o.append(text(500, 670, '3PDT footswitch, lugs seen from underneath', 13, weight='bold'))
    # wires
    drawn = []
    for a, b, colour, route in WIRES:
        pts = [P[a]] + route + [P[b]]
        if all(p[0] == q[0] or p[1] == q[1] for p, q in zip(pts, pts[1:])):
            d = path_with_hops(pts, drawn)
        else:
            d = 'M' + ' L'.join('%g %g' % p for p in pts)
        width = 3 if colour != 'byp' else 4
        o.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (d, COL[colour], width))
        drawn += [(p, q) for p, q in zip(pts, pts[1:]) if p[0] == q[0] or p[1] == q[1]]
    # LED symbol on top of its wires
    o.append('<polygon points="634,460 634,480 606,470" fill="#cfe0fb" stroke="%s" '
             'stroke-width="2"/>' % COL['led'])
    o.append('<line x1="606" y1="459" x2="606" y2="481" stroke="%s" stroke-width="3"/>'
             % COL['led'])
    o.append(text(620, 498, 'LED', 12, weight='bold', fill=COL['led']))
    o.append(text(598, 492, 'K', 11, 'end', fill=COL['led']))
    o.append(text(642, 492, 'A', 11, 'start', fill=COL['led']))
    # pads, lugs and terminal dots
    for n, (xy, lab) in PADS.items():
        o.append('<rect x="%g" y="%g" width="12" height="12" fill="#c9a227" stroke="#7a5f00"/>'
                 % (xy[0] - 6, xy[1] - 6))
        # label above the upper pad of a pair, below the lower one (wires enter sideways)
        if n == 'J4.1':                     # clear of the LEVEL pot outline
            o.append(text(xy[0] - 20, xy[1] + 4, lab, 12, 'end', 'bold', '#2f6b3a'))
            continue
        above = n.endswith('.1')
        o.append(text(xy[0], xy[1] - 11 if above else xy[1] + 20, lab, 12,
                      'middle', 'bold', '#2f6b3a'))
    for n, (x, y) in LUG.items():
        o.append('<circle cx="%g" cy="%g" r="12" fill="#ffffff" stroke="#555" '
                 'stroke-width="1.5"/>' % (x, y))
        o.append(text(x, y + 4, str(n), 12, weight='bold'))
    for n in ('J7.1', 'J7.2', 'J7.3', 'BT1.1', 'BT1.2', 'J5.S', 'J5.T', 'J6.S', 'J6.T'):
        o.append('<circle cx="%g" cy="%g" r="4" fill="#555"/>' % P[n])
    for n, lab, dx, dy, anchor in (('J7.1', 'centre', 0, -9, 'middle'),
                                   ('J7.2', 'sleeve', 0, -9, 'middle'),
                                   ('J7.3', 'switch', 0, -9, 'middle'),
                                   ('J5.S', 'S', -8, -6, 'end'), ('J5.T', 'T', 8, 14, 'start'),
                                   ('J6.S', 'S', 8, -6, 'start'), ('J6.T', 'T', -8, 14, 'end')):
        o.append(text(P[n][0] + dx, P[n][1] + dy, lab, 11, anchor, fill='#555'))
    # legend
    items = [('in', 'input signal'), ('out', 'output signal'), ('pwr', '+9 V'),
             ('gnd', 'ground'), ('led', 'LED'), ('byp', 'bypass jumper (lug 7 to 8)')]
    x = 150
    for key, lab in items:
        o.append('<line x1="%d" y1="735" x2="%d" y2="735" stroke="%s" stroke-width="4"/>'
                 % (x, x + 26, COL[key]))
        o.append(text(x + 32, 739, lab, 12, 'start'))
        x += 40 + 7 * len(lab)
    o.append(text(500, 765, 'Little hops mark wires that cross without touching.', 12,
                  fill='#555'))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 780" '
           'width="1000" height="780" font-family="Helvetica, Arial, sans-serif">\n'
           '<title>Off-board wiring diagram</title>\n'
           '<rect width="1000" height="780" fill="#ffffff"/>\n' + '\n'.join(o) + '\n</svg>\n')
    with open(OUT, 'w') as f:
        f.write(svg)
    print('wrote', OUT)


if __name__ == '__main__':
    build()
