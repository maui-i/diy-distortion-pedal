# DIY Distortion Pedal

A beginner-friendly guitar distortion pedal based on the classic MXR Distortion+ circuit: one op-amp, two germanium diodes, two knobs (**Gain** and **Level**), true bypass and an LED. About 20 parts and $15–30.

This repo has everything to build it:

- a step-by-step guide that starts on a solderless breadboard,
- a KiCad schematic,
- a ready-to-order printed circuit board (PCB),
- a wiring diagram for the jacks, footswitch and power.

| PCB (3D render) | Schematic |
| --- | --- |
| ![Top of the PCB](docs/images/pcb-3d-top.png) | ![Schematic](docs/images/schematic.png) |

## Three ways to build it

| Path | Soldering | Good for | Start here |
| --- | --- | --- | --- |
| **1. Breadboard** | Only the jack wires | Hearing it work in an afternoon, trying mods | [Build guide, parts 1–2](docs/build-guide.md#step-by-step-part-1-build-it-on-a-breadboard) |
| **2. Perfboard** | Yes | Making the breadboard version permanent, no PCB order needed | [Build guide, part 3](docs/build-guide.md#step-by-step-part-3-make-it-permanent) |
| **3. Custom PCB** | Yes, easiest of the soldered options | A tidy, quiet pedal that fits a 1590B box | [PCB build guide](docs/pcb-build.md) |

Whichever path you take, building the breadboard version first is the best way to learn the circuit and to check your parts.

## What's in the repo

```
docs/
  build-guide.md          Full beginner guide: parts, tools, breadboard, perfboard, troubleshooting, mods
  pcb-build.md            Ordering and assembling the PCB, off-board wiring
  how-it-works.md         The circuit explained, with the numbers behind each part
  images/                 Schematic, PCB renders, assembly view, wiring diagram
hardware/
  schematic.pdf           Printable schematic
  kicad/                  KiCad 10 project (schematic, PCB, project libraries)
  fabrication/
    diy-distortion-pedal-gerbers.zip   Upload this to a PCB maker
    bom.csv                            Bill of materials exported from the schematic
    assembly-top.pdf                   Printable parts placement
tools/                    Scripts that generated and check the design (see tools/README.md)
```

## The circuit at a glance

Guitar → input jack → footswitch → **gain stage** (TL071 op-amp, up to about 214× with the GAIN knob) → **clipping** (two 1N34A germanium diodes) → **LEVEL** knob → footswitch → output jack → amp.

It runs on a 9 V battery or a standard 9 V center-negative pedal supply and draws only a few milliamps. Read [how it works](docs/how-it-works.md) for the details.

## PCB at a glance

- 50 × 48 mm, 2 layers, all through-hole parts, no vias
- Pots mount on the back of the board so their shafts go through the enclosure lid
- Clearly labelled pads for IN, OUT, 9V, GND and LED+
- Design checks pass: KiCad ERC and DRC show 0 errors, and the board matches the schematic

![Wiring diagram](docs/images/wiring-diagram.svg)

## Safety

9 V DC only, never mains power. Treat the soldering iron with respect, and turn your amp down before plugging anything in. See the [safety section](docs/build-guide.md#safety) of the guide.

## License

MIT, see [LICENSE](LICENSE). The Distortion+ circuit itself is a decades-old classic that's widely documented; this repo's guide, drawings and PCB layout are original.
