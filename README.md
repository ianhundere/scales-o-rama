# Scales-O-Rama

## Synopsis
A Python program that finds scales based on individual notes or chooses a scale randomly from the major or minor scales, or any modal scale.


## Features
- Randomizes scales for the indecisive musician (e.g. major, minor, dorian, phrygian, lydian, mixolydian, and locrian scales)
- Allows the user to find scales that matches their riffs
- The itertools module is used to flatten the dictionary of scales into values allowing scales to be randomized
- If the incorrect option is chosen, the user is alerted to enter "random", "lookup", or "song"
- **Song mode** gives you a starting point for a new track: a set of creative limits to push against, not a finished plan

## Song mode

Run `som song` (or `som s`, or pick `song` at the prompt) and you get a song guide:

```
--- song guide ---
Scale:      B Aeolian (BC#DEF#GA)
Color note: G (the b6): the ache; sit on it, then fall to the 5th
Chords:     Bm  C#°  D  Em  F#m  G  A
Movement:   i - iv - bVII - bIII  ->  Bm Em A D  ("night drive")
Harmony:    two bars per chord

Tempo:      141 BPM
Time sig:   7/8
Groove:     push every downbeat a 16th early

Structure:  verse-chorus-bridge
Arc:        first half acoustic, second half electronic
Mood:       playful
Texture:    granular shimmer

Palette:    something bowed, string section, Rhodes
Production: resample the whole loop and build part two from the audio
Constraint: the melody may only use 5 notes of the scale
Wildcard:   sing it before you play it

First move: program the groove first, then find a bass line using only B and G
Title:      "copper orchard"
```

- **Harmony**: the scale's diatonic chords (spelled like the scale), the mode's color note, and a chord movement typical of that mode (e.g. the dorian `i - IV` vamp, the phrygian `i - bII` lean, the lydian `I - II` lift), plus a harmonic-rhythm rule
- **Rhythm**: tempo, time signature, and a groove/feel prompt
- **Shape & color**: form, an arrangement arc, a mood, and a sonic texture
- **Limits**: a 3-instrument palette, a production move, a hard constraint, and an oblique-style wildcard card for when you get stuck
- **First move**: one concrete ten-minute task to start with, plus a working title

Nothing is saved and nothing is exported. Reroll until something grabs you, then close the terminal and go make it.

## Install / Run

`som` is the launcher — it resolves its own location, so it works from a clone
anywhere (including through a symlink):

```bash
ln -sf "$(realpath som)" ~/bin/som   # then just run: som
som song                              # optional mode arg skips the first prompt (random/lookup/song or r/l/s)
```

## Future Features
- Add sounds to mirror the chosen scale for the randomize function
- Add MIDI support to play scales via an instrument

![Scales-O-Rama Video](/Scale-o-Rama.gif)
