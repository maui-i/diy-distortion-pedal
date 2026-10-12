#!/bin/sh
# Regenerate every output from the KiCad files: checks, fab files, docs images.
# Usage: tools/export.sh   (from the repo root; needs KiCad 10 or newer)
set -e
KICAD_CLI=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
command -v kicad-cli >/dev/null 2>&1 && KICAD_CLI=kicad-cli
K="$KICAD_CLI"
SCH=hardware/kicad/diy-distortion-pedal.kicad_sch
PCB=hardware/kicad/diy-distortion-pedal.kicad_pcb
FAB=hardware/fabrication
IMG=docs/images
mkdir -p build "$FAB" "$IMG"

echo "== checks"
$K sch erc --exit-code-violations -o build/erc.rpt "$SCH" | grep -i violation
$K pcb drc --exit-code-violations --schematic-parity -o build/drc.rpt "$PCB" | grep Found

echo "== schematic"
$K sch export pdf -o hardware/schematic.pdf "$SCH" >/dev/null
$K sch export svg --exclude-drawing-sheet -o build/sch-svg "$SCH" >/dev/null
cp build/sch-svg/diy-distortion-pedal.svg "$IMG/schematic.svg"

echo "== BOM"
$K sch export bom --fields 'Reference,Value,Footprint,${QUANTITY}' \
  --labels 'Refs,Value,Footprint,Qty' --group-by Value,Footprint \
  --exclude-dnp -o "$FAB/bom.csv" "$SCH" >/dev/null

echo "== gerbers + drill"
rm -rf build/gerbers && mkdir -p build/gerbers
$K pcb export gerbers -l F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts \
  --subtract-soldermask -o build/gerbers "$PCB" >/dev/null
$K pcb export drill --format excellon --generate-map --map-format gerberx2 \
  -o build/gerbers/ "$PCB" >/dev/null
rm -f "$FAB/diy-distortion-pedal-gerbers.zip"
(cd build/gerbers && zip -q -X ../../"$FAB"/diy-distortion-pedal-gerbers.zip *)
$K pcb export pdf --mode-single -l F.Cu,F.SilkS,Edge.Cuts -o "$FAB/assembly-top.pdf" "$PCB" >/dev/null

echo "== renders"
for side in top bottom; do
  $K pcb render --side $side --quality high --background opaque -w 1600 -h 1400 \
    -o "$IMG/pcb-3d-$side.png" "$PCB" >/dev/null
done
$K pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet --black-and-white \
  -l Edge.Cuts,F.Mask,F.SilkS -o build/pcb-assembly.svg "$PCB" >/dev/null
# give it a white background (readable in dark mode) and a sensible display size
python3 - build/pcb-assembly.svg "$IMG/pcb-assembly.svg" <<'PY'
import re, sys
s = open(sys.argv[1]).read()
w, h = re.search(r'viewBox="0\.0000 0\.0000 ([\d.]+) ([\d.]+)"', s).groups()
s = re.sub(r'width="[\d.]+mm" height="[\d.]+mm"',
           'width="%d" height="%d"' % (float(w) * 12, float(h) * 12), s, count=1)
s = s.replace('</desc>', '</desc>\n<rect x="0" y="0" width="%s" height="%s" fill="#ffffff"/>' % (w, h), 1)
open(sys.argv[2], 'w').write(s)
PY
# PNG copies for the README (macOS Quick Look does the rasterising)
if command -v qlmanage >/dev/null 2>&1; then
  (cd hardware && qlmanage -t -s 2400 -o ../build schematic.pdf >/dev/null 2>&1 &&
    mv ../build/schematic.pdf.png ../"$IMG"/schematic.png)
fi
echo "done"
