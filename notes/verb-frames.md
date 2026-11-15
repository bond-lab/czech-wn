# Verb frames

Release 2.1 has 1,341 verb valency frames, on 816 synsets (2,266
senses).  A frame says which complements a verb takes in that sense:
their form in Czech, their semantic role, and what kind of thing fills
them, with an example.

```
kdo1*AG(person:1)=co4*ANY(anything:1) %zhodnotit její výkon
```

'somebody (nominative, agent, a person) evaluates something
(accusative, anything): *zhodnotit její výkon* "to evaluate her
performance"'.

484 of the synsets have one frame, 202 have two, and 130 have three or
more.

## Where they come from

The frames were written for the Czech WordNet in the BalkaNet project:
about 1,500 were put on Czech verb synsets then (Pala and Horák 2008).
The synsets that have them here are stamped 2003-2004 and 2008-2010.
The same frames were tried on the Bulgarian and Romanian wordnets,
through the Interlingual Index: about a quarter of the Bulgarian frames
could be taken from Czech unchanged, and over 500 of the 600 brought
into Romanian were valid as they were or with small changes.

The VerbaLex valency lexicon of Masaryk University was built from
these frames, together with the VALLEX 1.0 and BRIEF lexicons
(Hlaváčková and Horák 2005).  It writes its frames another way and has
grown to about 10,500 verbs and 19,000 frames.  The frames in this
release are the wordnet's own, as they are in the source.

## The roles

A role has two levels (Hlaváčková and Horák 2005; Pala and Horák
2008).  The first is a general label, most of them taken from the
EuroWordNet Top Ontology: `AG`, `PAT`, `SUBS`.  The second is a
Princeton WordNet 2.0 word and its sense number, mostly from the Base
Concepts: `person:1`, `beverage:1`.  Any hyponym of it can fill the
complement, so the second level is a selectional restriction given in
terms of the wordnet itself.  `AG(person:1)`, `AG(animal:1)` and
`AG(institution:1)` are a person, an animal and an institution that
does something.

The papers speak of about 30 first-level labels and 200 second-level
ones.  The frames here have 53 labels and 252 fillers.  The most common
labels are `AG` (1,182 times), `PAT` (262), `OBJ` (257), `LOC` (183),
`ACT` (177), `ENT` (145), `ANY` (98), `SUBS` (67), `MAN` (65), `EVEN`
(64), `REC` (58) and `STATE` (58); the most common fillers are
`person:1` (1,413), `object:1` (217) and `act:2` (139).

Hlaváčková and Horák (2005) define some of the labels:

| | |
|---|---|
| `AG` | the animate entity that instigates or causes what the verb denotes, extended to an inanimate entity that does something actively (a machine) |
| `PAT` | an entity that is not the agent but is directly involved in or affected by what the verb denotes |
| `OBJ` | a tangible and visible entity |
| `SUBS` | that which has mass and occupies space |
| `ART` | a man-made object taken as a whole |
| `PART` | a portion of a natural object, or something less than the whole of a human artifact |
| `INS` | a device that requires skill for proper use |
| `EVEN` | something that happens at a given place and time |
| `STATE` | the way something is with respect to its main attributes |

The subject is not always an agent: it can be an object, a substance,
or an abstract thing such as an act (`ACT`), knowledge (`KNOW`), an
event, information (`INFO`) or a state.

## The notation

The papers show frames in this notation but do not define every mark,
and the source does not describe it.  The table gives what the papers
say and, where they are silent, what the 1,341 frames show; the counts
say how many frames have each thing.

| | | frames |
|---|---|---:|
| `{podplatit, koupit si}` | at the start: the verbs of the synset that the frame is for | 808 |
| `=` | where the verb goes: the subject is on its left and the other complements on its right | 1,335 |
| `kdo1`, `co4`, `na koho4`, `čím7` | a complement, as a form of *kdo* 'who' or *co* 'what', which tells an animate from an inanimate one, with a preposition if it needs one; the number is its case (1 nominative, 2 genitive, 3 dative, 4 accusative, 6 locative, 7 instrumental) | |
| `*AG(person:1)` | the complement's role, on two levels | |
| `(TIME(time:2)\|ACT(act:2))` | `\|` between alternatives: roles, fillers or forms | 517 |
| `[kde]`, `[kam]`, `[jak]` | a complement given by a question word ('where', 'where to', 'how'), mostly place and manner; not explained in the papers | 228 |
| `$(že)`, `$(inf)`, `$(aby)` | a clause with that conjunction, or an infinitive; not explained in the papers | 69 |
| `&` | joins two complements that go together; not explained in the papers | 48 |
| `X` | no complement on that side: `kdo1*AG(person:1)=X` for an intransitive verb, `X=` for one with no subject (*lilo jako z konve*); not explained in the papers | 58 |
| `?` | probably: the complements after it are optional (`koho4*PAT(person:1)? před čím7*ANY(anything:1)` for *chrání své děti, ochránil ji před pomluvami*); not explained in the papers | 311 |
| `%` | what follows is one or more examples | 1,323 |

The reading of `?` rests on the examples.  Where a frame has two or
more examples, a complement with a preposition that comes after `?` is
missing from one of them in 23 frames of 51; one in a frame without `?`
is missing in 10 of 57.  The weather verbs fit too: `{pršet} X=? jak`
for *prší hodně*.

Six frames are not in this notation: they are a phrase (*pít krev
komu3*) or a note.

## In WN-LMF

Each frame is a `SyntacticBehaviour` of the lexicon, with the text of
the frame unchanged in `subcategorizationFrame`.  Every sense in the
synset names the synset's frames in `subcat`:

```xml
<LexicalEntry id="wncze-zhodnotit-v">
  <Lemma writtenForm="zhodnotit" partOfSpeech="v" />
  <Sense id="wncze-CZE-1006986700-s1" synset="wncze-CZE-1006986700" subcat="wncze-frame-1" n="1" />
</LexicalEntry>
...
<SyntacticBehaviour id="wncze-frame-1"
    subcategorizationFrame="kdo1*AG(person:1)=co4*ANY(anything:1) %zhodnotit její výkon" />
```

The source puts the frames on the synset and WN-LMF puts them on the
senses, so in 2.1 every verb of a synset names all its frames, also a
frame that is for some of them only (`{koupit si}`).

From 2.2 a frame that begins with verbs of its synset is on those verbs
only (`scripts/frames_to_senses.py`): 887 senses in 322 synsets change
their frames, by `set_frames` records, and the links between senses and
frames go from 4,112 to 2,807.  143 verbs are left with no frame: the
frames of their synset are for its other verbs.  A frame that names no
verb (487 of them), or only verbs that are not in its synset (99),
stays on all the verbs of the synset.

The examples are part of the frame's text, after `%`.  From 2.2 they
are also `Example` elements of the synset
(`scripts/frame_examples.py`): 1,243 of them, each the whole text after
a `%`, since many are several variants with commas between (*dívali se
na film, na televizi, na požár domu*).  The 96 examples of frames that
name only verbs their synset does not have are not copied.

Where the source groups
a synset's frames in more than one `VALENCY`, the synset's note says
how (`valency=2 1`).

## References

* Dana Hlaváčková and Aleš Horák. 2005. VerbaLex – New Comprehensive
  Lexicon of Verb Valencies for Czech. In Radovan Garabík, editor,
  *Computer Treatment of Slavic and East European Languages: Third
  International Seminar, Bratislava, Slovakia, 10–12 November 2005,
  Proceedings*, pages 107–115. Bratislava: Veda.
  <https://nlp.fi.muni.cz/publications/slovko2005_ydana_hales/slovko2005_ydana_hales.pdf>
* Karel Pala and Aleš Horák. 2008. Can Complex Valency Frames be
  Universal? In Petr Sojka and Aleš Horák, editors, *Proceedings of
  Second Workshop on Recent Advances in Slavonic Natural Languages
  Processing, RASLAN 2008*, pages 41–48. Brno: Masaryk University.
  <https://nlp.fi.muni.cz/raslan/2008/papers/5.pdf>
* Karel Pala and Pavel Smrž. 2004. Building Czech Wordnet. *Romanian
  Journal of Information Science and Technology* 7(1–2): 79–88.
