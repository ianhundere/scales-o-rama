import importlib.util
import os
import random
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(ROOT, 'scale-o-rama.py')

_spec = importlib.util.spec_from_file_location('scale_o_rama', SCRIPT)
som = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(som)

LETTERS = 'CDEFGAB'
BASE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

NUMERALS = {
    'major': 'I ii iii IV V vi vii°',
    'dorian': 'i ii bIII IV v vi° bVII',
    'phrygian': 'i bII bIII iv v° bVI bvii',
    'lydian': 'I II iii #iv° V vi vii',
    'mixolydian': 'I ii iii° IV v vi bVII',
    'minor': 'i ii° bIII iv v bVI bVII',
    'aeolian': 'i ii° bIII iv v bVI bVII',
    'locrian': 'i° bII biii iv bV bVI bvii',
}


def tokens(scale):
    return re.findall(som.NOTE_RE, scale)


def pitch(note):
    return (BASE[note[0]] + note.count('#') - note.count('b')) % 12


def run_cli(*args, stdin=''):
    return subprocess.run([sys.executable, SCRIPT, *args], input=stdin,
                          capture_output=True, text=True, cwd=ROOT, timeout=30)


class NoteReTests(unittest.TestCase):
    def test_double_sharps(self):
        self.assertEqual(tokens('D#E#F##G##A#B#C##'),
                         ['D#', 'E#', 'F##', 'G##', 'A#', 'B#', 'C##'])

    def test_double_flat(self):
        t = tokens('EbFbGbAbBbbCbDb')
        self.assertEqual(len(t), 7)
        self.assertEqual(t[4], 'Bbb')

    def test_round_trip(self):
        for mode, group in som.scales.items():
            for scale in group:
                self.assertEqual(''.join(tokens(scale)), scale, (mode, scale))


class ScaleDataTests(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(set(som.scales),
                         {'major', 'minor', 'dorian', 'phrygian', 'lydian',
                          'mixolydian', 'aeolian', 'locrian'})
        for mode, group in som.scales.items():
            self.assertEqual(len(group), 12, mode)

    def test_letters_distinct_and_in_order(self):
        for mode, group in som.scales.items():
            for scale in group:
                t = tokens(scale)
                self.assertEqual(len(t), 7, (mode, scale))
                start = LETTERS.index(t[0][0])
                expected = [LETTERS[(start + i) % 7] for i in range(7)]
                self.assertEqual([n[0] for n in t], expected, (mode, scale))

    def test_step_pattern(self):
        for mode, group in som.scales.items():
            off = som.MODE_OFFSETS[mode]
            steps = som.MAJOR_STEPS[off:] + som.MAJOR_STEPS[:off]
            for scale in group:
                p = [pitch(n) for n in tokens(scale)]
                got = [(p[(i + 1) % 7] - p[i]) % 12 for i in range(7)]
                self.assertEqual(got, steps, (mode, scale))

    def test_distinct_tonics(self):
        for mode, group in som.scales.items():
            self.assertEqual(len({pitch(tokens(s)[0]) for s in group}), 12, mode)

    def test_minor_equals_aeolian(self):
        self.assertEqual(set(som.scales['minor']), set(som.scales['aeolian']))


class ChordTests(unittest.TestCase):
    def test_all_scales(self):
        for mode, group in som.scales.items():
            for scale in group:
                chords, numerals = som.mode_chords(scale, mode)
                self.assertEqual(len(chords), 7)
                self.assertEqual(numerals, NUMERALS[mode].split(), (mode, scale))
                for chord, note, num in zip(chords, tokens(scale), numerals):
                    if num.endswith('°'):
                        suffix = '°'
                    elif num.lstrip('b#')[0].islower():
                        suffix = 'm'
                    else:
                        suffix = ''
                    self.assertEqual(chord, note + suffix, (mode, scale))

    def test_d_sharp_dorian(self):
        chords, numerals = som.mode_chords('D#E#F#G#A#B#C#', 'dorian')
        self.assertEqual(chords, 'D#m E#m F# G# A#m B#° C#'.split())
        self.assertEqual(numerals, 'i ii bIII IV v vi° bVII'.split())

    def test_d_sharp_lydian(self):
        chords, numerals = som.mode_chords('D#E#F##G##A#B#C##', 'lydian')
        self.assertEqual(chords, 'D# E# F##m G##° A# B#m C##m'.split())
        self.assertEqual(numerals, 'I II iii #iv° V vi vii'.split())


class ChallengeTests(unittest.TestCase):
    KEYS = {'scale', 'root', 'mode', 'tempo', 'time_sig', 'structure', 'mood',
            'constraint', 'color_note', 'color', 'chords', 'progression',
            'harmonic_rhythm', 'groove', 'arc', 'texture', 'palette',
            'production', 'wildcard', 'first_move', 'title'}

    def test_generate_many(self):
        random.seed(12345)
        for _ in range(200):
            c = som.generate_challenge()
            self.assertEqual(set(c), self.KEYS)
            for k, v in c.items():
                self.assertTrue(v, k)
                leaves = v.values() if isinstance(v, dict) else v if isinstance(v, list) else [v]
                for leaf in leaves:
                    self.assertTrue(leaf, k)
                    self.assertNotRegex(str(leaf), r'[{}]', k)
            t = tokens(c['scale'])
            self.assertIn(c['scale'], som.scales[c['mode']])
            self.assertEqual(c['root'], t[0])
            self.assertIn(c['color_note'], t)
            self.assertEqual(set(c['progression']), {'numerals', 'chords', 'name'})


GROUPS = {
    's': {'mode', 'scale', 'root', 'chords', 'color_note', 'color', 'progression',
          'harmonic_rhythm'},
    'c': {'progression', 'harmonic_rhythm'},
    'p': {'palette', 'texture', 'production', 'constraint', 'wildcard'},
}

FILTER_SETS = [
    {}, {'mode': 'dorian'}, {'key': 'A'}, {'key': 'Gb', 'mode': 'major'},
    {'mode': 'locrian', 'key': 'Cb'}, {'mood': 'dreamy', 'tempo': 120},
    {'mode': 'lydian', 'key': 'D#', 'mood': 'odd, "custom" {mood}', 'tempo': 1},
]


class FilterTests(unittest.TestCase):
    def check_brief(self, c, filters):
        self.assertEqual(set(c), ChallengeTests.KEYS)
        for k, v in c.items():
            if k == 'mood':
                continue  # free text, echoed as-is
            leaves = v.values() if isinstance(v, dict) else v if isinstance(v, list) else [v]
            for leaf in leaves:
                self.assertTrue(leaf, k)
                self.assertNotRegex(str(leaf), r'[{}]', k)
        t = tokens(c['scale'])
        self.assertIn(c['scale'], som.scales[c['mode']])
        self.assertEqual(c['root'], t[0])
        self.assertEqual(c['chords'], som.mode_chords(c['scale'], c['mode'])[0])
        self.assertEqual(c['color_note'], t[som.COLOR_NOTES[c['mode']][0]])
        prog = c['progression']['chords'].split()
        self.assertTrue(set(prog) <= set(c['chords']))
        names = [name for _, name in som.MOVEMENTS[c['mode']]]
        self.assertIn(c['progression']['name'], names)
        fills = {tpl.format(movement=c['progression']['chords'], instrument=c['palette'][0],
                            root=c['root'], color_note=c['color_note'], first_chord=prog[0])
                 for tpl in som.FIRST_MOVES}
        self.assertIn(c['first_move'], fills)
        if 'mode' in filters:
            self.assertEqual(c['mode'], filters['mode'])
        if 'key' in filters:
            self.assertEqual(pitch(c['root']), pitch(filters['key']))
        if 'mood' in filters:
            self.assertEqual(c['mood'], filters['mood'])
        if 'tempo' in filters:
            self.assertEqual(c['tempo'], filters['tempo'])

    def test_pitch_class(self):
        expected = {'C': 0, 'B#': 0, 'Dbb': 0, 'F##': 7, 'Cb': 11, 'E#': 5, 'Gb': 6, 'Bbb': 9}
        for note, pc in expected.items():
            self.assertEqual(som.pitch_class(note), pc, note)

    def test_every_key_every_mode(self):
        for mode in som.scales:
            for pc_note in ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']:
                c = som.generate_challenge(mode=mode, key=pc_note)
                self.assertEqual(pitch(c['root']), pitch(pc_note), (mode, pc_note))

    def test_enharmonic_key_uses_scale_spelling(self):
        c = som.generate_challenge(mode='major', key='Gb')
        self.assertEqual((c['root'], c['scale']), ('F#', 'F#G#A#BC#D#E#'))

    def test_key_only_any_mode(self):
        random.seed(7)
        modes = {som.generate_challenge(key='A')['mode'] for _ in range(200)}
        self.assertEqual(modes, set(som.scales))

    def test_filtered_generate_many(self):
        for filters in FILTER_SETS:
            random.seed(99)
            for _ in range(200):
                self.check_brief(som.generate_challenge(**filters), filters)

    def test_partial_rerolls(self):
        for filters in FILTER_SETS:
            random.seed(2024)
            c = som.generate_challenge(**filters)
            for i in range(200):
                part = 'scp'[i % 3]
                new = som.reroll(c, part, **filters)
                self.check_brief(new, filters)
                changed = {k for k in c if c[k] != new[k]}
                self.assertTrue(changed <= GROUPS[part] | {'first_move'}, (part, changed))
                c = new
            for _ in range(50):
                c = som.reroll(c, 'all', **filters)
                self.check_brief(c, filters)

    def test_rerolls_change_their_group(self):
        # each part must actually reroll a field unique to its group
        random.seed(11)
        base = som.generate_challenge()
        for part, fields in [('s', ('scale', 'root')), ('c', ('progression',)),
                             ('p', ('palette',)), ('all', ('title',))]:
            changed = set()
            for _ in range(50):
                new = som.reroll(base, part)
                changed |= {f for f in fields if new[f] != base[f]}
            self.assertEqual(changed, set(fields), part)

    def test_reroll_keys(self):
        self.assertEqual(som.REROLL_KEYS, {'': 'all', 'r': 'all', 's': 's', 'c': 'c', 'p': 'p'})

    def test_reroll_does_not_mutate(self):
        random.seed(3)
        c = som.generate_challenge()
        snapshot = {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
                    for k, v in c.items()}
        for part in 'scp':
            som.reroll(c, part)
        self.assertEqual(c, snapshot)


class SongArgTests(unittest.TestCase):
    def test_mode_arg(self):
        self.assertEqual(som._mode_arg('Dorian'), 'dorian')
        with self.assertRaises(som.argparse.ArgumentTypeError):
            som._mode_arg('bluesy')

    def test_key_arg(self):
        for raw, want in [('bb', 'Bb'), ('f##', 'F##'), ('gb', 'Gb'), ('C', 'C'), ('BBB', 'Bbb')]:
            self.assertEqual(som._key_arg(raw), want)
        for bad in ['H', '', 'C#b', 'Cx', 'c###']:
            with self.assertRaises(som.argparse.ArgumentTypeError, msg=bad):
                som._key_arg(bad)

    def test_tempo_arg(self):
        self.assertEqual(som._tempo_arg('120'), 120)
        for bad in ['0', '-5', 'fast', '1.5']:
            with self.assertRaises(som.argparse.ArgumentTypeError, msg=bad):
                som._tempo_arg(bad)

    def test_mood_arg(self):
        self.assertEqual(som._mood_arg('Dreamy Haze'), 'Dreamy Haze')
        self.assertEqual(som._mood_arg('  dreamy '), 'dreamy')
        with self.assertRaises(som.argparse.ArgumentTypeError):
            som._mood_arg('  ')


class CliTests(unittest.TestCase):
    def test_lookup_args(self):
        r = run_cli('lookup', 'D#', 'E#')
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertIn('dorian: D#E#F#G#A#B#C#', lines)
        expected = ['{}: {}'.format(key, scale)
                    for key, group in som.scales.items() for scale in group
                    if {'D#', 'E#'} <= set(tokens(scale))]
        self.assertEqual(lines, expected)

    def test_lookup_stdin(self):
        r = run_cli('lookup', stdin='C E G\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        # the input() prompt has no trailing newline, so strip it off the first line
        out = r.stdout.split("lookup: ", 1)[1]
        self.assertIn('major: CDEFGAB', out.splitlines())

    def test_lookup_no_valid_notes(self):
        r = run_cli('lookup', 'xyz')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), 'No valid notes entered.')

    def test_random_arg(self):
        r = run_cli('random', 'dorian')
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertIn(lines[0], som.scales['dorian'])
        self.assertEqual(lines[1], "That's a nice sounding dorian scale!")

    def test_random_stdin_retry(self):
        r = run_cli('random', stdin='nope\nall\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('Sorry, invalid choice.'), 1)
        all_scales = {s for g in som.scales.values() for s in g}
        # prompts have no trailing newline, so the scale follows the last prompt
        tail = r.stdout.rsplit(': ', 1)[1].splitlines()
        self.assertIn(tail[0], all_scales)
        self.assertEqual(tail[1], "That's a nice sounding random scale!")

    def test_song(self):
        r = run_cli('song')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith('--- song guide ---'))
        self.assertIn('Title:', r.stdout)

    def scale_line(self, out):
        return [l for l in out.splitlines() if l.startswith('Scale:')]

    def test_song_mode_filter(self):
        r = run_cli('song', '--mode', 'Dorian')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('--- song guide ---'), 1)
        self.assertIn('Dorian', self.scale_line(r.stdout)[0])

    def test_song_mode_and_key(self):
        r = run_cli('song', '--mode', 'dorian', '--key', 'D')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.scale_line(r.stdout), ['Scale:      D Dorian (DEFGABC)'])

    def test_song_root_alias_enharmonic(self):
        r = run_cli('song', '--root', 'gb', '--mode', 'major')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.scale_line(r.stdout), ['Scale:      F# Major (F#G#A#BC#D#E#)'])

    def test_song_key_only(self):
        r = run_cli('song', '--key', 'A')
        self.assertEqual(r.returncode, 0, r.stderr)
        root = self.scale_line(r.stdout)[0].split()[1]
        self.assertEqual(pitch(root), pitch('A'))

    def test_song_mood_tempo(self):
        r = run_cli('song', '--mood', 'dreamy', '--tempo', '120')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Mood:       dreamy', r.stdout.splitlines())
        self.assertIn('Tempo:      120 BPM', r.stdout.splitlines())

    def test_song_bad_args(self):
        for args in [('--mode', 'bluesy'), ('--key', 'H'), ('--tempo', '0'), ('--tempo', 'fast')]:
            r = run_cli('song', *args)
            self.assertEqual(r.returncode, 2, args)
            self.assertIn('usage:', r.stderr)
            self.assertEqual(r.stdout, '')

    def test_song_not_tty_no_prompt(self):
        r = run_cli('song', stdin='q\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('--- song guide ---'), 1)
        self.assertNotIn('quit', r.stdout)

    def test_song_interactive_rerolls(self):
        r = run_cli('song', '-i', '--mode', 'lydian', stdin='s\nc\np\n\nq\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('--- song guide ---'), 5)
        self.assertEqual(r.stdout.count(' Lydian ('), 5)

    def test_song_interactive_unknown(self):
        r = run_cli('song', '-i', stdin='x\nq\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('--- song guide ---'), 1)
        self.assertEqual(r.stdout.count('unknown choice'), 1)

    def test_song_interactive_eof(self):
        r = run_cli('song', '-i')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('--- song guide ---'), 1)
        self.assertNotIn('Traceback', r.stderr)


if __name__ == '__main__':
    unittest.main()
