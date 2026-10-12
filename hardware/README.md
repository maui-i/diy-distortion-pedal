# Hardware

| Path | What it is |
| --- | --- |
| `schematic.pdf` | Printable schematic (A4). |
| `kicad/diy-distortion-pedal.kicad_pro` | KiCad project. Open this in KiCad 10 or newer. |
| `kicad/diy-distortion-pedal.kicad_sch` | Schematic, including the off-board wiring (jacks, footswitch, DC jack, battery, LED). Those parts are marked "not on board" so they appear in the BOM but not on the PCB. |
| `kicad/diy-distortion-pedal.kicad_pcb` | PCB layout. |
| `kicad/pedal.kicad_sym` | Project symbol: `SW_3PDT`, a 9-lug footswitch whose pin numbers match the build guide's lug numbering. |
| `kicad/pedal.pretty/Pot_16mm_PCB.kicad_mod` | Project footprint: 16 mm PCB-mount pot, legs at 5 mm pitch, 7.5 mm from the shaft. |
| `fabrication/diy-distortion-pedal-gerbers.zip` | Gerber and Excellon drill files, ready to upload to a PCB maker. |
| `fabrication/bom.csv` | Bill of materials exported from the schematic (all parts, on and off the board). |
| `fabrication/assembly-top.pdf` | Component-side silkscreen and copper, for placing parts. |

## Board specs

| | |
| --- | --- |
| Size | 50 × 48 mm, 2 mm corner radius |
| Layers | 2, 1.6 mm FR-4, ground pour on both sides |
| Tracks | 0.4 mm signal, 0.7 mm for +9V, VIN and GND; 0.25 mm clearance |
| Holes | 0.8–1.2 mm plated, no vias |
| Parts | All through-hole; pots on the back, everything else on the front |

## Checks

All of these pass with zero errors or warnings, and `tools/export.sh` re-runs them:

- **ERC** (electrical rules check) on the schematic.
- **DRC** (design rules check) on the PCB: clearances, courtyards, silkscreen, unconnected pads.
- **Schematic parity**: the PCB's footprints and nets match the schematic.
- **Connection list**: `tools/check_netlist.py` compares the schematic's netlist with the connection list in `docs/build-guide.md` (including footswitch, jacks and power), so the PCB and the guide describe the same circuit.

## Editing

Open the `.kicad_pro` file in KiCad and edit as usual. After changes, run `tools/export.sh` from the repo root to refresh the Gerbers, BOM, PDFs and images. If you move parts, re-route by hand or with KiCad's router, then refill zones (press **B**) before exporting.
