"""Check the schematic's connectivity against the build guide's connection list.

    kicad-cli sch export netlist --format kicadsexpr -o out.net hardware/kicad/diy-distortion-pedal.kicad_sch
    python3 tools/check_netlist.py out.net
"""
import sys

from sexp import find, first, parse

EXPECTED = {
    'VIN':    {'J3.1', 'D3.2', 'J7.2'},
    '+9V':    {'D3.1', 'C5.1', 'C6.1', 'R6.1', 'R8.1', 'IC1.7'},
    'GND':    {'J1.2', 'J2.2', 'J3.2', 'R1.2', 'R7.2', 'C2.2', 'C4.2', 'C5.2', 'C6.2',
               'C7.2', 'D1.1', 'D2.2', 'RV2.1', 'IC1.4', 'J5.S', 'J6.S', 'J7.1',
               'BT1.2', 'SW1.6'},
    'VREF':   {'R6.2', 'R7.1', 'C7.1', 'R2.2'},
    'FX_IN':  {'J1.1', 'R1.1', 'C1.1', 'SW1.1'},
    'NONINV': {'C1.2', 'R2.1', 'IC1.3'},
    'INV':    {'IC1.2', 'R3.1', 'R4.1'},
    'OPOUT':  {'IC1.6', 'R3.2', 'C3.1'},
    'GAIN':   {'R4.2', 'RV1.3'},
    'WIPER':  {'RV1.2', 'RV1.1', 'C2.1'},
    'C3N':    {'C3.2', 'R5.1'},
    'CLIP':   {'R5.2', 'D1.2', 'D2.1', 'C4.1', 'RV2.3'},
    'FX_OUT': {'RV2.2', 'J2.1', 'SW1.2'},
    'LED_A':  {'R8.2', 'J4.1', 'D4.2'},
    'LED_K':  {'D4.1', 'SW1.3'},
    'IN_TIP': {'J5.T', 'SW1.4'},
    'OUT_TIP': {'J6.T', 'SW1.5'},
    'BYPASS': {'SW1.7', 'SW1.8'},
    'BATT':   {'J7.3', 'BT1.1'},
}
# Polarity is encoded by pin numbers: C_Polarized pin 1 = +, diode pin 1 = K, 2 = A.
UNCONNECTED_OK = {'IC1.1', 'IC1.5', 'IC1.8', 'SW1.9'}


def main(path):
    tree = parse(open(path).read())
    got = []
    for net in find(first(tree, 'nets'), 'net'):
        nodes = {'%s.%s' % (first(n, 'ref')[1], first(n, 'pin')[1])
                 for n in find(net, 'node')}
        got.append((first(net, 'name')[1], nodes))
    ok = True
    multi = [(n, s) for n, s in got if len(s) > 1 or not (s <= UNCONNECTED_OK)]
    for name, want in EXPECTED.items():
        if not any(s == want for _, s in multi):
            ok = False
            close = [(n, s) for n, s in multi if s & want]
            print('MISMATCH %-8s want %s' % (name, sorted(want)))
            for n, s in close:
                print('           got %s %s' % (n, sorted(s)))
    for n, s in multi:
        if not any(s == w for w in EXPECTED.values()) and not s <= UNCONNECTED_OK:
            if len(s) == 1:
                ok = False
                print('DANGLING  %s %s' % (n, sorted(s)))
    print('OK: netlist matches the connection list' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
