# Tools

Scripts used to generate and check the design. You don't need any of them to build the pedal.

| Script | What it does |
| --- | --- |
| `export.sh` | Runs ERC, DRC and schematic-parity checks, then exports the schematic PDF/SVG/PNG, BOM, Gerbers + drill files, assembly drawing and 3D renders. Run from the repo root after editing the KiCad files. Needs KiCad 10+ (`kicad-cli`). |
| `check_netlist.py` | Compares a netlist exported from the schematic with the build guide's connection list. |
| `gen_schematic.py` | Generated the first version of the schematic and the project symbol library. |
| `gen_pcb.py` | Generated the first version of the PCB: placed footprints from the netlist, autorouted with [Freerouting](https://github.com/freerouting/freerouting), added the ground pours. Run with KiCad's bundled Python. |
| `gen_wiring_svg.py` | Draws `docs/images/wiring-diagram.svg` and checks each wire against the netlist. |
| `render_pcb.sh` | Quick PNG preview of chosen PCB layers (macOS). |
| `sexp.py` | Tiny reader/writer for KiCad's S-expression files, used by the scripts above. |

**The two `gen_*` scripts overwrite the KiCad files.** They made the starting design; once you've edited the schematic or PCB in KiCad, don't run them again.

To check the full connection list (including the off-board parts, which normal netlists leave out):

```sh
mkdir -p build/check && cp hardware/kicad/{*.kicad_pro,sym-lib-table,fp-lib-table} build/check/
CHECK_ALL=1 OUT_DIR=build/check python3 tools/gen_schematic.py
kicad-cli sch export netlist -o build/check/all.net build/check/diy-distortion-pedal.kicad_sch
python3 tools/check_netlist.py build/check/all.net
```
