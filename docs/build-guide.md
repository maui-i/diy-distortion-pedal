# DIY Distortion Pedal Build Guide

Oct 9, 2026

## Overview

You'll build a rock distortion pedal based on the classic MXR Distortion+ circuit: about 20 parts, one chip, and a few hours of work. It plugs between your electric guitar and your amp with two standard 1/4" guitar cables, runs on a 9V battery or a 9V pedal power supply, and has two knobs: **Gain** (how much distortion) and **Level** (output volume).

This guide gets the electronics working first on a solderless breadboard, then shows how to make it permanent on a solderable board with jacks, a footswitch and an on/off LED. No enclosure is needed; that can come later.

**How distortion works, in two sentences.** An op-amp chip boosts your guitar signal up to about 200 times louder, far more than the circuit can pass cleanly. Two diodes then chop off ("clip") the tops of the waveform, turning the smooth guitar wave into a squarer one, which your ear hears as the gritty, sustaining rock sound.

**The signal path:** Guitar → input jack → footswitch → gain stage (op-amp + Gain knob) → clipping diodes → Level knob → footswitch → output jack → amp.

Why this circuit for a first build:

- Very few parts, all cheap and easy to find
- Forgiving: small mistakes rarely damage anything
- Easy to modify later (swap diodes or a capacitor and the sound changes noticeably)
- It's a real, recorded-on-classic-albums sound, not a toy

## Materials

The whole parts list costs roughly $15–30 (approximate; prices vary by store). Buy 2–3 extra of each resistor, capacitor and diode: they're pennies each and you will lose or break one. The **Ref** codes (R1, C1…) are used everywhere else in this guide.

### Electronic parts

| Ref | Part | Value / type | Qty | Notes and substitutes |
| --- | --- | --- | --- | --- |
| IC1 | Op-amp chip | TL071CP (8-pin DIP) | 1 | The original used a µA741/LM741, which also works with the same wiring. TL071 is a bit quieter. |
| — | IC socket | 8-pin DIP | 1 | For the permanent build, so you never solder the chip directly. |
| R1, R2, R3 | Resistor | 1 MΩ (1M), 1/4 W | 3 | Metal film preferred. Colors: brown-black-green (+ gold or brown band). |
| R4 | Resistor | 4.7 kΩ, 1/4 W | 1 | Yellow-violet-red. Sets maximum gain. |
| R5 | Resistor | 10 kΩ, 1/4 W | 1 | Brown-black-orange. |
| R6, R7 | Resistor | 100 kΩ, 1/4 W | 2 | Brown-black-yellow. Makes the 4.5 V reference. |
| R8 | Resistor | 4.7 kΩ, 1/4 W | 1 | LED current limiter. 2.2k = brighter, 10k = dimmer. |
| C1 | Film capacitor | 10 nF (code 103) | 1 | Input coupling. Box/film type preferred; ceramic works. |
| C2 | Film capacitor | 47 nF (code 473) | 1 | Gain-loop cap. Sets the bass response. |
| C3 | Electrolytic capacitor | 1 µF, 25 V or higher | 1 | Output coupling. **Polarized**: has a + and − leg. A 1 µF film cap also works (no polarity). |
| C4 | Capacitor | 1 nF (code 102) | 1 | Tames harsh fizz. Film or ceramic. |
| C5 | Electrolytic capacitor | 100 µF, 25 V | 1 | Power-supply smoothing. Polarized. |
| C6 | Ceramic capacitor | 100 nF (code 104) | 1 | Chip power decoupling. No polarity. |
| C7 | Electrolytic capacitor | 10 µF, 25 V | 1 | Steadies the 4.5 V reference. Polarized. |
| D1, D2 | Germanium diode | 1N34A | 2 | The classic sound. Silicon 1N4148/1N914 = harsher and quieter; red LEDs = louder and more open. Buy all three types to experiment. |
| D3 | Schottky diode | 1N5817 | 1 | Reverse-polarity protection. A 1N4001 also works (drops a bit more voltage). |
| D4 | LED | 3 mm or 5 mm, any color | 1 | "Effect on" indicator. Optional for the breadboard stage. |
| GAIN | Potentiometer | 1 MΩ, **C1M** (reverse log) or B1M (linear) | 1 | C1M is original. B1M works; most of the change happens near the end of the turn. |
| LEVEL | Potentiometer | 10 kΩ, **A10K** (log/audio) | 1 | Output volume. |
| — | Knobs | To fit your pots' shafts | 2 | Optional, but much easier to turn. |

Get **PCB-mount 16 mm pots** (three straight legs): their legs plug straight into a breadboard.

### Connectors, switch and power

| Part | Qty | Notes |
| --- | --- | --- |
| 1/4" (6.35 mm) mono jack, open-frame | 2 | Input and output. Switchcraft #11 or a "Cliff-style" jack is easiest to solder. |
| 3PDT footswitch (9 lugs) | 1 | True-bypass on/off switch. Only needed for the permanent build. |
| 9 V battery + battery snap | 1 | Easiest power for testing. |
| 9 V DC jack, 2.1 mm, center-negative | 1 | Optional. Lets you use a standard pedal power supply. |
| 9 V DC pedal power supply, center-negative | 1 | Optional. Must say **9V DC** and show the center-negative symbol ("Boss-style"). Never use any other voltage or an AC adapter. |
| Guitar instrument cables (1/4") | 2 | One guitar → pedal, one pedal → amp. |
| Guitar amp | 1 | Any amp. The pedal cannot drive headphones or speakers by itself. |

### Building materials

| Part | Qty | Notes |
| --- | --- | --- |
| Solderless breadboard, full size (830 points) | 1 | For the first, no-solder build. |
| Breadboard jumper wires | 1 pack | Solid-core, pre-cut kits are tidiest. |
| Solderable breadboard-style perfboard | 1 | E.g. ElectroCookie or Adafruit Perma-Proto, full or half size. Same layout as a breadboard, so you copy your working build hole-for-hole. |
| 22 AWG solid-core hookup wire | 3–4 colors | Red = +9 V, black = ground, other colors = signal. |
| Alligator clip test leads | 5–10 | Handy for temporary connections to jacks and the battery. |

**Where to buy:** Tayda Electronics and Small Bear Electronics (pedal-builder favorites), Mouser or DigiKey (huge selection), or Amazon for assortment kits of resistors and capacitors. A pre-packaged "Distortion+ clone kit" is another option if you'd rather not source parts one by one.

## Tools

The only tool you truly can't skip is a **multimeter**: it's how you check part values, find wiring mistakes and confirm voltages. The soldering gear is needed only for the jacks and the permanent build.

| Tool | Needed for | Notes |
| --- | --- | --- |
| Digital multimeter | Everything | Must measure DC voltage, resistance and continuity (beep mode). A $15–25 model is fine. |
| Soldering iron, temperature-controlled, 40–60 W | Jacks, permanent build | Set to about 330–370 °C (625–700 °F). Comes with or needs a stand. |
| Solder, 0.8 mm (0.031") rosin-core | Jacks, permanent build | 63/37 leaded is easiest to learn with; lead-free works at a slightly higher temperature. |
| Brass-wool tip cleaner or damp sponge | Soldering | Keeps the tip shiny so heat transfers. |
| Desoldering braid (wick) and/or solder sucker | Fixing mistakes | You will use it. |
| Flush cutters | Trimming component legs | Small "side cutters." |
| Wire strippers | Hookup wire | 22 AWG notch. |
| Needle-nose pliers | Bending legs | |
| Helping hands / PCB holder | Holding jacks and boards | Or a lump of Blu-Tack. |
| Safety glasses | Clipping legs, soldering | Clipped legs fly. |
| Small fan or fume extractor | Soldering | Keeps flux smoke out of your face. |
| Masking tape + pen | Labeling | Label pots and wires as you go. |

### Reading part values (do this before you start)

- **Resistors:** read the color bands, but always confirm with the multimeter's resistance (Ω) setting. Metal-film resistors with 5 bands are easy to misread.
- **Film/ceramic capacitors:** the 3-digit code is picofarads: first two digits, then the number of zeros. 102 = 1,000 pF = 1 nF; 103 = 10 nF; 473 = 47 nF; 104 = 100 nF.
- **Electrolytic capacitors:** value printed on the side. The stripe marks the **negative (−) leg**, which is also the shorter leg.
- **Diodes:** the band marks the **cathode**. The 1N34A is a small glass diode; handle it gently, the glass cracks.
- **LED:** the longer leg is the **anode (+)**; the flat edge of the rim marks the cathode (−).
- **Potentiometers:** the letter is the taper (A = audio/log, B = linear, C = reverse log). Hold the pot with the shaft pointing at you and the legs down: legs are **1, 2, 3 from left to right**, and 2 (middle) is the wiper.

Sort your parts into a labeled egg carton or tape them to a sheet of paper with their Ref codes written next to them. This one step prevents most first-build mistakes.

## The circuit

The circuit has three blocks: a **power section** that makes a clean +9 V rail and a 4.5 V "middle" reference, a **gain stage** (the op-amp) that boosts the guitar up to ~214×, and a **clipping + output stage** where the diodes create the distortion and the Level knob sets the volume.

### Signal flow

```
            Footswitch OFF: signal skips the circuit (true bypass)
     +-----------------------------------------------------------+
     |                                                           v
 [ Input ] --> [ Gain stage ] --> [ Clipping ] --> [ Level ] --> [ Output ]
  Guitar in     IC1, R2-R4         C3, R5           LEVEL knob     To amp
  R1, C1        GAIN knob, C2      D1, D2, C4       sets volume    via footswitch
  (clean)       (boosted ~214x)    (clipped =
                      ^             distortion)
                      | +9 V and 4.5 V ref
 [ Power section: 9 V battery or DC jack -> D3 (protection) + C5 (smoothing) -> +9V rail;
                  R6, R7, C7 -> 4.5V ref ]
```

Read it left to right: the clean guitar signal is boosted by the gain stage, flattened by the diodes, then set to a usable volume by the Level knob. The bypass line is the path when the footswitch is off.

### Connection list (your schematic in table form)

Every build step below just makes these connections. Tick them off as you go. Named points used in the table: **+9V rail**, **Ground**, **4.5V ref**, **IN** (signal coming from the input jack), **CLIP** (the point where the diodes sit) and **OUT** (signal going to the output jack).

**Chip pinout (TL071 or 741), viewed from above with the notch on the left:** bottom row left→right = pins 1, 2, 3, 4; top row right→left = pins 5, 6, 7, 8. Pin 2 = inverting input (−), pin 3 = non-inverting input (+), pin 4 = ground (V−), pin 6 = output, pin 7 = +9 V (V+). Pins 1, 5 and 8 are left unconnected.

**Power section**

| Part | One end goes to | Other end goes to | What it does |
| --- | --- | --- | --- |
| Battery snap red / DC jack + | D3 anode (no band) | — | Incoming +9 V. |
| D3 1N5817 | Anode: battery/DC + | Cathode (band): **+9V rail** | Blocks current if the power is connected backwards. |
| Battery snap black / DC jack − | **Ground** | — | Incoming ground. |
| C5 100 µF | + leg: **+9V rail** | − leg (stripe): **Ground** | Smooths the supply, reduces hum. |
| R6 100k | **+9V rail** | **4.5V ref** | Top half of the voltage divider. |
| R7 100k | **4.5V ref** | **Ground** | Bottom half: makes ~4.5 V. |
| C7 10 µF | + leg: **4.5V ref** | − leg: **Ground** | Keeps the reference steady and quiet. |
| IC1 pin 7 | **+9V rail** | — | Powers the chip. |
| IC1 pin 4 | **Ground** | — | Chip ground. |
| C6 100 nF | IC1 pin 7 (as close as possible) | **Ground** | Local decoupling, prevents squeals. |

**Gain stage**

| Part | One end goes to | Other end goes to | What it does |
| --- | --- | --- | --- |
| Input jack tip | **IN** (through footswitch in the permanent build) | — | Guitar signal in. |
| Input jack sleeve | **Ground** | — | Cable shield/ground. |
| R1 1M | **IN** | **Ground** | Pulldown: stops the "pop" when you switch the pedal on. |
| C1 10 nF | **IN** | IC1 pin 3 | Passes the guitar signal, blocks DC. |
| R2 1M | IC1 pin 3 | **4.5V ref** | Biases the chip at the middle of its 0–9 V range so the wave can swing both ways. |
| R3 1M | IC1 pin 6 | IC1 pin 2 | Feedback resistor. Gain = 1 + R3 ÷ (R4 + Gain pot). |
| R4 4.7k | IC1 pin 2 | GAIN pot leg 3 | Sets maximum gain (~214× with the knob fully up). |
| GAIN pot leg 2 | C2 47 nF (one leg) | — | Wiper. Turning clockwise lowers resistance = more gain. |
| GAIN pot leg 1 | Not connected (or jumper to leg 2) | — | |
| C2 47 nF | GAIN pot leg 2 | **Ground** | Sets which frequencies get boosted: at full gain, bass below ~720 Hz is boosted less, which gives the tight, punchy midrange. |

**Clipping and output stage**

| Part | One end goes to | Other end goes to | What it does |
| --- | --- | --- | --- |
| C3 1 µF | + leg: IC1 pin 6 | − leg: R5 | Removes the chip's 4.5 V DC so only audio passes. |
| R5 10k | C3 − leg | **CLIP** | Limits current into the diodes. |
| D1 1N34A | Anode (no band): **CLIP** | Cathode (band): **Ground** | Clips the top half of the wave. |
| D2 1N34A | Cathode (band): **CLIP** | Anode (no band): **Ground** | Clips the bottom half. D1 and D2 point in **opposite** directions. |
| C4 1 nF | **CLIP** | **Ground** | Rolls off harsh fizz above ~16 kHz. |
| LEVEL pot leg 3 | **CLIP** | — | Top of the volume control. |
| LEVEL pot leg 1 | **Ground** | — | Bottom of the volume control. |
| LEVEL pot leg 2 | **OUT** | — | Wiper: your output signal. |
| Output jack tip | **OUT** (through footswitch in the permanent build) | — | Signal to the amp. |
| Output jack sleeve | **Ground** | — | Cable shield/ground. |

**Every ground point is the same connection.** Battery −, jack sleeves, R1, R7, C2, C4, C5, C6, C7, the diodes, LEVEL leg 1 and IC1 pin 4 must all end up joined together.

**Expected voltages** (multimeter black probe on Ground, fresh battery): +9V rail ≈ 8.6–9.3 V (a little below the battery, because of D3); 4.5V ref ≈ 4.3–4.7 V; IC1 pins 2, 3 and 6 all ≈ the same as 4.5V ref; pin 7 = +9V rail; pin 4 = 0 V.

## Step by step, part 1: build it on a breadboard

Build on the breadboard first: it takes about an hour, needs no soldering (except two wires on each jack), and lets you fix mistakes by just moving a part. Always disconnect the battery while adding or moving parts.

**Breadboard basics.** Hold the board with the long side facing you. The numbered columns (1–63) run left to right. In each column, the 5 holes on the **upper half** are connected to each other, and the 5 holes on the **lower half** are connected to each other, but the two halves are separate (the center gap divides them). The long rails along the top and bottom edges connect all the way along their length. Below, "col 22 upper" means any hole in column 22, upper half.

**Rail plan:** top red (+) rail = **+9V rail**; top blue (−) rail = **Ground**; bottom blue (−) rail = **Ground**; bottom red (+) rail = **4.5V ref**. Write these on the board with tape.

**Tip:** trim component legs so parts sit low and flat; long, loopy legs pick up noise and touch each other. If a column runs out of holes, jumper it to an empty column next to it.

1. **Prepare the rails**
    1. Some breadboards split each rail in the middle (look for a gap in the printed line). Check with the multimeter's continuity beep from one end of each rail to the other; if it's split, bridge the gap with a short jumper.
    2. Run a jumper from the top blue rail to the bottom blue rail, so both are Ground.
2. **Build the power section** (battery disconnected)
    1. Put D3 (1N5817) with its anode (no band) in col 5 upper and its cathode (band) in the top red rail.
    2. Plug the battery snap's red wire into col 5 upper and its black wire into the top blue rail. Don't attach the battery yet.
    3. C5 (100 µF): + leg in the top red rail, − leg (stripe) in the top blue rail.
    4. R6 (100k): top red rail → col 12 upper. R7 (100k): col 12 upper → top blue rail.
    5. C7 (10 µF): + leg in col 12 upper, − leg in the top blue rail.
    6. Jumper: col 12 upper → bottom red rail. The bottom red rail is now the 4.5V ref.
3. **Test the power section**
    1. Set the multimeter to DC volts (20 V range if it isn't auto-ranging). Black probe on Ground.
    2. Snap on the battery. Red probe on the top red rail: expect ~8.6–9.3 V. Red probe on the bottom red rail: expect ~4.3–4.7 V.
    3. Wrong readings? Stop and check D3's direction and the electrolytic caps' polarity before going on. Then disconnect the battery.
4. **Place the chip** — IC1 with its notch (or dot) facing **left**, straddling the center gap, with pins 1–4 in cols 20–23 lower and pins 8–5 in cols 20–23 upper. That puts: pin 2 = col 21 lower, pin 3 = col 22 lower, pin 4 = col 23 lower, pin 7 = col 21 upper, pin 6 = col 22 upper.
    1. Jumper: col 21 upper (pin 7) → top red rail.
    2. Jumper: col 23 lower (pin 4) → bottom blue rail.
    3. C6 (100 nF): col 21 upper → top blue rail.
5. **Build the input**
    1. Col 17 lower is your **IN** point.
    2. R1 (1M): col 17 lower → bottom blue rail.
    3. C1 (10 nF): col 17 lower → col 22 lower (pin 3).
    4. R2 (1M): col 22 lower → bottom red rail (4.5V ref).
6. **Build the gain loop**
    1. R3 (1M): col 22 upper (pin 6) → col 21 lower (pin 2). It bridges the center gap; that's fine.
    2. Plug the GAIN pot (1M) into the lower half around cols 30–36, shaft pointing toward you, each leg in its own column. With the shaft toward you, leg 1 is on the left and leg 3 on the right. Write down which column each leg is in.
    3. R4 (4.7k): col 21 lower (pin 2) → the column of GAIN leg 3.
    4. C2 (47 nF): the column of GAIN leg 2 → bottom blue rail. Leave leg 1 unconnected.
7. **Build the output and clipping stage**
    1. C3 (1 µF): + leg in col 22 upper (pin 6), − leg in col 25 upper.
    2. R5 (10k): col 25 upper → col 30 upper. Col 30 upper is your **CLIP** point.
    3. D1 (1N34A): anode (no band) in col 30 upper, cathode (band) in the top blue rail.
    4. D2 (1N34A): cathode (band) in col 30 upper, anode (no band) in the top blue rail. D1 and D2 must face **opposite** ways.
    5. C4 (1 nF): col 30 upper → top blue rail.
8. **Add the Level control**
    1. Plug the LEVEL pot (A10k) into the lower half to the right of the GAIN pot (around cols 42–48), shaft toward you. Note its leg columns.
    2. Jumper: col 30 upper (CLIP) → LEVEL leg 3's column.
    3. Jumper: LEVEL leg 1's column → bottom blue rail.
    4. LEVEL leg 2 is your **OUT** point.
9. **Wire the jacks** (the only soldering at this stage)
    1. Find each jack's tip lug: plug a cable into the jack, set the meter to continuity, touch one probe to the cable plug's tip and find the lug that beeps. The lug that beeps with the plug's sleeve (the long metal barrel) is the sleeve lug.
    2. On each jack, solder a ~15 cm (6") solid-core wire to the tip lug (use a color like yellow or green) and a black wire to the sleeve lug. Strip ~6 mm (1/4") at the breadboard end.
    3. Input jack: tip wire → col 17 lower (IN); sleeve wire → bottom blue rail.
    4. Output jack: tip wire → LEVEL leg 2's column (OUT); sleeve wire → bottom blue rail.
    5. Keep the input and output wires apart from each other; crossed signal wires can make a high-gain circuit squeal.
10. **Final check before power**
    1. Go through the connection list in "The circuit" section and tick off every row.
    2. With the battery disconnected, set the meter to continuity and touch the top red rail and top blue rail. It should **not** beep continuously (a short chirp is just C5 charging). A steady beep means a short: find it before connecting power.
    3. Connect the battery and measure (black probe on Ground): pin 7 ≈ +9V rail, pins 2, 3 and 6 ≈ 4.3–4.7 V, pin 4 = 0 V. If pin 6 sits near 0 V or near 9 V, see Troubleshooting.

This breadboard version is "always on" (no footswitch yet). That's all you need to hear it work.

## Step by step, part 2: plug in your guitar and test

Connect it exactly like a store-bought pedal: guitar → cable → pedal input jack; pedal output jack → cable → amp input.

1. **Set up safely.** Turn the amp **off**, or its volume all the way down. Set both pedal knobs to the middle (noon).
2. **Connect the cables.** Guitar into the input jack, output jack into the amp. Connect the battery.
3. **Power on quietly.** Turn the amp on and bring its volume up slowly, about a quarter of the way. Turn your guitar's volume knob fully up.
4. **Play.** Strum an open chord. You should hear a distorted, sustaining tone.
5. **Test the Gain knob.** Turn it fully left (counter-clockwise): the sound should be mildly crunchy and quieter. Fully right: heavy distortion and long sustain. If it works backwards, move R4 from leg 3 to leg 1 of the GAIN pot.
6. **Test the Level knob.** It should go from silent (fully left) to loud (fully right). If it works backwards, swap the wires on LEVEL legs 1 and 3.
7. **Compare with no pedal.** Plug the guitar straight into the amp for a moment and listen. Then set Level so the pedal and the straight guitar are about equally loud ("unity gain"); this is how most players set a distortion pedal.

### Dialing in sounds

| Sound you want | Gain | Level | Also try |
| --- | --- | --- | --- |
| Bluesy crunch | 9–10 o'clock | 1–2 o'clock | Roll the guitar's volume to ~7 |
| Classic rock rhythm | 12–1 o'clock | 12 o'clock | Bridge pickup |
| Hard rock lead, long sustain | 3–5 o'clock (max) | 11–12 o'clock | Neck pickup for a smoother lead |
| Boost a clean or slightly dirty amp | Fully left | 3 o'clock | Use silicon or LED diodes (see Mods) |

Some hiss and hum at high gain is normal on a breadboard: it's an unshielded open circuit with long wires. It gets much quieter once the circuit is soldered with short wires, and quieter still in a metal enclosure.

When it sounds right, take a photo of the breadboard from above. It's your reference for the permanent build.

## Step by step, part 3: make it permanent

Once the breadboard version sounds right, solder the same circuit onto a **solderable breadboard-style perfboard**. Because its holes are connected exactly like a breadboard's, you copy your working layout hole-for-hole: same columns, same rails. Then you add the footswitch and LED so you can switch the effect on and off.

> **Prefer a printed circuit board?** This repo includes a ready-to-order PCB for the same circuit with the same part references. See the [PCB build guide](pcb-build.md); the soldering basics and footswitch wiring below still apply.

### Soldering basics (practice first)

Solder 10–20 spare resistors onto a scrap of perfboard before touching the real build. A good joint takes 2–4 seconds:

1. Wipe the iron tip on the brass wool and add a tiny blob of solder to the tip ("tinning").
2. Push the part's leg through the hole and bend it slightly outward so it stays put.
3. Touch the iron tip to **both** the copper pad and the leg at the same time. Count 1–2.
4. Feed solder into the joint (where pad meets leg), not onto the iron. Use just enough to make a small shiny cone ("volcano") around the leg.
5. Pull the solder away, then the iron. Don't move the part for 2 seconds while it cools.
6. Clip the leg just above the joint with flush cutters (wear glasses).

A good joint is shiny and cone-shaped. A dull, lumpy ball ("cold joint") or solder that bridges to a neighboring pad must be reheated or removed with braid.

### Build the board

1. **Lay out the board** to match your breadboard photo. Mark the rails with a marker: +9V, Ground, Ground, 4.5V ref.
2. **Solder in this order** (lowest parts first, so the board sits flat while you work):
    1. Wire jumpers (rail-to-rail jumpers, pin 7 and pin 4 jumpers, CLIP jumper).
    2. The 8-pin IC socket, notch facing left. **Do not put the chip in yet.**
    3. Resistors R1–R7. They have no direction.
    4. Diodes D1, D2, D3. Check each band's direction against the connection list twice before soldering. Germanium diodes (D1, D2) are heat-sensitive: solder quickly, and clamp the leg with pliers between the glass body and the joint to soak up heat.
    5. Small capacitors C1, C2, C4, C6. No direction.
    6. Electrolytic capacitors C3, C5, C7. Check the + and − legs. A backwards electrolytic can bulge or pop.
3. **Prepare the off-board wires.** Cut wires about 10–15 cm (4–6") long for the pots, jacks, footswitch and power. Use red for +9 V, black for every ground wire, and other colors for signal. Strip 5 mm, twist the strands (if stranded) and tin the ends.
4. **Connect the pots.** Either solder the PCB-mount pots directly into the board, or solder wires from each pot leg to the same points the breadboard used. Keep the leg 1/2/3 order the same as on the breadboard.
5. **Connect power.** Battery snap red → D3 anode; black → Ground rail.
    1. Optional DC jack: a 2.1 mm center-negative jack has a center pin (Ground), a sleeve lug (+9 V) and often a third "switch" lug. Confirm which is which with the meter: plug in your supply and measure.
    2. Center pin lug → Ground. Sleeve lug → D3 anode.
    3. To keep the battery too: battery red → the switch lug instead of D3. The switch lug touches the sleeve lug only when no plug is inserted, so plugging in the supply disconnects the battery automatically. Confirm with the continuity beep (beeps with no plug, stops with a plug inserted).
6. **Wire the footswitch and LED** (next subsection).
7. **Inspect.** Look at every joint under a bright light (a phone camera zoomed in works). Check for solder bridges between neighboring holes. Re-run the continuity check between +9V and Ground: no steady beep.
8. **Insert the chip** (power disconnected), notch left. Make sure no pins are bent under it.
9. **Power up and measure** the same voltages as on the breadboard: pin 7 ≈ +9V rail; pins 2, 3, 6 ≈ 4.5 V.
10. **Play-test** exactly as in part 2, then test the footswitch: each click should toggle between distorted (LED on) and your clean guitar sound (LED off).

### Wiring the 3PDT footswitch (true bypass with LED)

The footswitch has 9 lugs in a 3×3 grid. Number them, looking at the lugs from underneath:

```
 1  2  3
 4  5  6
 7  8  9
```

The middle row (4, 5, 6) are the common lugs. Each one connects to the lug above it in one switch position and the lug below it in the other. **Check your orientation:** with the meter on continuity, lug 5 should beep with lug 2 in one position and with lug 8 after a click. If it beeps with 4 or 6 instead, rotate your numbering a quarter turn.

| Lug | Connect to |
| --- | --- |
| 4 | Input jack tip |
| 1 | Board **IN** (where the input jack used to go) |
| 7 | Jumper wire to lug 8 |
| 5 | Output jack tip |
| 2 | Board **OUT** (LEVEL pot leg 2) |
| 8 | Jumper wire to lug 7 |
| 6 | Ground |
| 3 | LED cathode (short leg) |
| 9 | Nothing |

Then connect the LED's anode (long leg) through R8 (4.7k) to the +9V rail. Cover bare legs with heat-shrink or tape so they can't touch anything.

**How it works:** in one position, the input jack feeds the circuit, the circuit feeds the output jack, and lug 3 grounds the LED so it lights. Click, and the input jack connects straight to the output jack through the lug 7–8 jumper, completely skipping the circuit ("true bypass"), and the LED goes dark.

Both jack sleeves still go to Ground, exactly as before.

## Troubleshooting

Most first-build problems are a part in the wrong hole, a part facing the wrong way, or a bad solder joint. **Measure the voltages first** (power on, black probe on Ground); they point straight at the problem.

| Symptom | Most likely cause | Fix |
| --- | --- | --- |
| No sound at all, pedal on or off | Jack tip and sleeve wires swapped, or a bad cable | Re-check jack lugs with the continuity method; try different cables. |
| Bypass works, effect on is silent | No power, or chip in backwards | Measure pin 7 (should be ~9 V). Check the notch faces left. Check D3's band faces the +9V rail. |
| +9V rail reads 0 V | Dead battery, D3 backwards, or battery snap in the wrong rail | Measure the battery itself (should be over 8.5 V). Flip D3 if needed. |
| Pin 6 sits near 0 V or near 9 V instead of ~4.5 V | Bias missing: R2, R6, R7 or the 4.5V ref jumper | Measure 4.5V ref and pin 3. Re-check R2 goes to the 4.5V ref rail. |
| Sound is clean, no distortion | GAIN pot not connected; diodes missing or not reaching Ground | Check R4 → GAIN leg 3 and C2 → leg 2. Check D1/D2 land in a Ground rail. |
| Very quiet even with Level up | LEVEL pot wired with legs 1 and 3 swapped, or OUT taken from the wrong leg | Output must come from leg 2 (middle). |
| Gain or Level knob works backwards | Outer pot legs swapped | Swap the connections on legs 1 and 3. |
| Loud hum that changes when you touch the strings | Missing or broken ground connection | Check both jack sleeves reach Ground; check the ground rail jumpers. |
| High-pitched squeal or whistling at high gain | Input and output wires running close together; long wires | Separate and shorten wires; move C6 closer to pin 7. If it persists, add a 100 pF capacitor across R3 (pin 6 to pin 2). |
| Scratchy crackle when turning knobs | DC reaching a pot | Check C3 is in place and its + leg faces pin 6. |
| Loud pop when you click the footswitch | Missing R1 pulldown | Check R1 runs from IN to Ground. |
| Sound cuts in and out | Loose breadboard contact or a cold solder joint | Wiggle parts gently with a chopstick while playing to find it; reheat suspect joints. |
| LED never lights | LED backwards, or R8 missing | Long leg toward R8/+9V, short leg to footswitch lug 3. |
| Distortion sounds "farty" or gated | Weak battery | Replace the battery or use a 9 V supply. |

Still stuck? Take clear, well-lit photos of the board from above and below and compare them, part by part, against the connection list. Pedal-building forums (for example the r/diypedals community and the freestompboxes.org forum) are very friendly to first-timers who post photos.

## Mods and next steps

The breadboard is the perfect place to experiment: swap one part at a time, play, and keep what you like. Each change below is a single part swap.

| Change | Swap | What you'll hear |
| --- | --- | --- |
| Harsher, tighter clipping | D1, D2 → 1N4148 or 1N914 (silicon) | More aggressive, a bit quieter; turn Level up. |
| Louder, more open, "amp-like" | D1, D2 → red LEDs (same direction rules) | Less compression, much louder output. |
| Asymmetric, warmer clipping | D1 = 1N34A, D2 = 1N4148 | Slightly richer, tube-like character. |
| More bass and body | C2 47 nF → 100 nF | Fuller low end at high gain (bass corner drops from ~720 Hz to ~340 Hz). |
| Even more bass (heavier) | C2 → 220 nF | Thick and heavy; can get muddy with chords. |
| Smoother, darker top end | C4 1 nF → 4.7 nF or 10 nF | Less fizz, warmer tone. |
| More maximum gain | R4 4.7k → 2.2k | More saturation at the top of the Gain knob; also more noise. |
| Vintage flavor | IC1 TL071 → µA741 / LM741 | The original chip; slightly grittier and noisier. |

**Add a clipping switch.** Put a small on-off-on toggle switch between CLIP and Ground with germanium diodes on one side and silicon (or LEDs) on the other, and you can choose the clipping flavor live.

**Add a tone knob.** Insert a simple tone control between CLIP and the LEVEL pot: a 10k linear pot and a 22–47 nF capacitor wired as a treble cut. This is a common next mod; try it on the breadboard first.

### When you're ready for an enclosure

- The standard size for this pedal is a **Hammond 1590B** (or "125B" if you want more room) aluminum box.
- Plan the layout on paper first: knobs on top, jacks on the sides (input on the right, output on the left, by pedal convention), DC jack on the top edge.
- Drill with a step bit: about 7 mm for 16 mm pots, 3/8" (9.5 mm) for 1/4" jacks, 12 mm for the footswitch, 12 mm for the DC jack (check your parts' datasheets).
- The metal box must connect to Ground (the jacks' sleeves do this automatically when screwed into bare metal). This shields the circuit and cuts hum noticeably.
- Insulate the bottom of your board with a piece of cardboard or electrical tape so solder joints can't touch the metal.

## Safety

This is a low-voltage, beginner-safe project as long as you stick to 9 V and treat the soldering iron with respect.

- **9 V DC only.** Use a 9 V battery or a 9 V DC, center-negative pedal supply. Never connect the circuit to wall power directly, and never use an AC adapter or a higher-voltage supply.
- **Soldering iron:** the tip is ~350 °C. Always return it to its stand, never leave it on unattended, and unplug it when you're done. Work on a heat-proof surface.
- **Fumes:** solder smoke is flux, not lead, but don't breathe it. Use a fan blowing it away from you or a fume extractor, and work in a ventilated room.
- **Leaded solder:** wash your hands after soldering and before eating; keep it away from kids and pets.
- **Eye protection** when clipping component legs.
- **Electrolytic capacitors** installed backwards can bulge, leak or pop. Double-check polarity, and disconnect power immediately if one gets hot.
- **Disconnect the battery** whenever you add, move or remove parts.
- **Protect your hearing and your amp:** turn the amp down or off before plugging and unplugging cables or powering the pedal; new builds can pop or squeal loudly.
