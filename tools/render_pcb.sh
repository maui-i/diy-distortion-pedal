#!/bin/sh
# Render PCB layers to PNG for a quick look: render_pcb.sh board.kicad_pcb out.png [layers]
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
LAYERS=${3:-Edge.Cuts,F.Cu,B.Cu,F.SilkS,F.CrtYd,B.CrtYd,F.Fab}
OUT=$(cd "$(dirname "$2")" && pwd)
NAME=$(basename "$2" .png)
$K pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet -l "$LAYERS" -o "$OUT/$NAME.svg" "$1" >/dev/null 2>&1
(cd "$OUT" && qlmanage -t -s 1600 -o . "$NAME.svg" >/dev/null 2>&1)
mv "$OUT/$NAME.svg.png" "$2" && rm "$OUT/$NAME.svg"
