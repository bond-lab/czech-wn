# How release 2.1 was made from the DEBVisDic source

Release 2.1 is the latest version of the Czech WordNet in DEBVisDic
(`sources/wncze21.xml.zip`) in WN-LMF, with nothing changed.  Later
releases are 2.1 and the changes in `changes/`; nothing is converted
from the source again.

```
uv run scripts/visdic2lmf.py sources/wncze21.xml.zip --package
```

writes `release/wncze-2.1.xml` and the package `release/wncze-2.1.tar.xz`.
It needs two other repositories checked out beside this one: `NTUMC`
(for `ntumc.wordnet`, which writes the XML) and `cili` (for the map from
Princeton WordNet 2.0 to the Interlingual Index).

| | nouns | verbs | adjectives | adverbs | all |
|---|---:|---:|---:|---:|---:|
| synsets | 21,014 | 5,159 | 2,129 | 166 | 28,468 |
| senses | 33,423 | 10,588 | 3,236 | 259 | 47,506 |

There are 34,089 words, 34,257 relations between synsets, 949
definitions, 132 examples and 1,341 verb frames.  28,181 synsets are
linked to the Interlingual Index.

## Where each field went

| DEBVisDic | WN-LMF |
|---|---|
| `ID` | the synset's id: `wncze-` and the source id, without `ENG20-` to keep it short (`ENG20-02001223-n` is `wncze-02001223-n`; `CZE-00000002-z` is `wncze-CZE-00000002-z`).  An id of eight digits and a part of speech is a Princeton WordNet 2.0 offset |
| `POS` | `partOfSpeech`; `b` (adverb) is written `r` |
| `ILI` | `ili`.  36 synsets have several (the 2.0 synset was split in 3.0): the one CILI's map gives is in `ili`, the others in the note as `ili=` |
| `LITERAL` | a `Sense` of the entry for that word and part of speech; the sense's id is the synset's id and the literal's place in it (`-s1`), and `members` keeps the order |
| `LITERAL/@sense` | `n` on the sense (one is not a number: `dc:identifier`) |
| `LITERAL/@lnote` | `note` on the sense |
| `DEF` | `Definition` |
| `USAGE` | `Example` |
| `ILR` | `SynsetRelation`; see below |
| `STAMP` | `dc:contributor` (the account) and `dc:date` |
| `NL` | `lexicalized`: `yes` is `"false"`, `false` is `"true"` |
| `DOMAIN` | `dc:subject` |
| `VALENCY/FRAME` | `SyntacticBehaviour`, named in `subcat` on each sense of the synset.  A frame used by several synsets is written once.  Where a `VALENCY` has more than one `FRAME`, the note says how they are grouped (`valency=2 1`) |
| `SNOTE`, `BCS`, `VERSION`, `CREATED`, `SUMO` | the synset's `note`, as `snote=ssjč1; bcs=3` |

WN-LMF has no field for the base concept level (`BCS`), the editor's
notes and version, or SUMO, so they share the note; a field that
appears twice is written twice.

Relations keep their direction: only the direction in the source is
written (a hypernym, not the matching hyponym).

| DEBVisDic | WN-LMF | | DEBVisDic | WN-LMF |
|---|---|---|---|---|
| `hypernym` | `hypernym` | | `be_in_state` | `attribute` |
| `holo_part` | `holo_part` | | `subevent` | `subevent` |
| `holo_member` | `holo_member` | | `causes` | `causes` |
| `holo_portion` | `holo_substance` | | `category_domain` | `domain_topic` |
| `near_antonym` | `antonym` | | `region_domain` | `domain_region` |
| `similar_to` | `similar` | | `usage_domain` | `exemplifies` |
| `also_see` | `also` | | `verb_group` | `similar`, with `dc:type="verb_group"` |

Any other relation (`eng_derivative`, and `derived` and `particle` in
the thesis version) is `relType="other"` with its name in `dc:type`.

## Nothing is lost

After converting, the script rebuilds what the source said from the
WN-LMF file and compares the two, fact by fact (193,797 facts for 2.1).
It fails if a fact is missing or one has appeared.  The same check
passes for the other two files.  Three things are not carried over:

* elements and attributes with nothing in them (12 literals, 12
  relations with no target, 21 `DOMAIN`, 21 `SUMO`, 3 `DEF`, 2 `BCS`,
  2 `POS`);
* white space around a value;
* the `WORD` elements, which repeat the words of the literals (the
  script checks that they do).

Three things are added, and each is marked in the synset's note:

* `inferred=ili`: 164 synsets have no `ILI` in the source (mostly
  adverbs) but CILI's map has one for their Princeton 2.0 synset;
* `inferred=pos`: 3 synsets have no part of speech; it is taken from
  the id;
* `inferred=synset`: 2 synsets (`CZE-00000081-z`, `CZE-00001129-z`) are
  the target of a relation but are not in the source.  WN-LMF wants the
  target in the file, so each gets an empty synset.

## Known problems, left in 2.1 as they are in the source

* 69 Interlingual Index ids are each on two synsets (two Princeton 2.0
  synsets mapped to one concept).  Corrected in 2.2.
* 3 synsets have the same word twice.  Corrected in 2.2.
* 2 verb synsets are marked as a noun and an adverb.  Corrected in 2.2.
* The account name in 984 `STAMP`s has a broken character (`u?ivatel`,
  for *uživatel* 'user').
* 33 synsets with a Princeton 2.0 id have no Interlingual Index id.
