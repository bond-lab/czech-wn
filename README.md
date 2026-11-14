# Czech WordNet

The Czech WordNet was created by the **Natural Language Processing
Centre, Faculty of Informatics, Masaryk University, Brno** (Karel
Pala, Adam Rambousek, Aleš Horák and colleagues).  It was built since
1998, in the EuroWordNet and BalkaNet projects, and is kept in their
[DEBVisDic](https://deb.fi.muni.cz/) editor.

* Home of the data and its editor: <https://deb.fi.muni.cz/>
* Copyright © 1998–2025 Natural Language Processing Centre, Faculty of
  Informatics, Masaryk University
* Licence: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
  (see `LICENSE`), by permission of Adam Rambousek, 2026-11-05.  One
  file, `sources/nas_anotacni_slovnik.xml`, has a different licence

This repository holds the files as Masaryk University gave them to us,
and a script that turns them into
[WN-LMF](https://globalwordnet.github.io/schemas/), the format of the
Global WordNet Association, so that they can be used with the
[wn](https://github.com/goodmami/wn) module and edited together with
other wordnets.  We changed nothing in the data.

## Please cite

> Adam Rambousek, Karel Pala and Sandra Tukačová. 2017.
> [Overview and Future of Czech Wordnet](https://repozitar.cz/repo/26626/452493/).
> In *LDK Workshops: OntoLex, TIAD and Challenges for Wordnets*,
> pages 146–151. Galway, Ireland: CEUR-WS.org.

BibTeX for this and the references below is in `citation.bib`.

## What is here

| | |
|---|---|
| `sources/` | the files as we received them: three versions of the Czech WordNet, and the PDT annotation dictionary, which has **a different licence**; see `sources/README.md` |
| `scripts/visdic2lmf.py` | makes the WN-LMF lexicon from a source file |
| `release.py` | makes the next release: the last release plus the changes |
| `changes/` | the changes since 2.1, one record per line; see `changes/README.md` |
| `scripts/ntumc2changes.py` | one-off: made the first change records from the NTU-MC wordnet database |
| `additions/` | words added in 2025 while annotating *War with the Newts*; now change records |
| `tests/` | tests of the conversion and of the release |

The three versions come from the same base and each adds different
synsets.  Release 2.1 is made from `wncze21.xml.zip`, the latest
version in DEBVisDic (28,468 synsets).  `wncze-blahus.xml.zip` (40,919
synsets) was extended automatically from a bilingual dictionary and has
not been checked by hand; `wncze-ext.xml.zip` (28,667 synsets) was
extended a little in a thesis at the University of Naples.

In the sources, synsets are identified by their Princeton WordNet 2.0
synset (`ENG20-02001223-n`), or by a Czech id for the 254 concepts that
Princeton WordNet does not have (`CZE-00000002-z`).  In WN-LMF these
are `wncze-02001223-n` and `wncze-CZE-00000002-z`.

An earlier version (1.0, 2008) is distributed by ELRA, under other
licences: <https://live.european-language-grid.eu/catalogue/lcr/2364>.

## Release 2.1

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

### Where each field went

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

### Nothing is lost

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

### Known problems, left as they are in the source

* 82 Interlingual Index ids are on more than one synset (Princeton 2.0
  synsets that 3.0 merged).
* 3 synsets have the same word twice, with different sense numbers.
* The account name in 984 `STAMP`s has a broken character (`u?ivatel`,
  for *uživatel* 'user').
* 33 synsets with a Princeton 2.0 id have no Interlingual Index id.

## After 2.1

From 2.1 on the lexicon is kept as the released file plus an ordered
list of changes, as for the Japanese, Chinese and Malay/Indonesian
wordnets of NTU-MC:

```
uv run release.py 2.2     # -> release/wncze-2.2.xml, release/wncze-2.2.tar.xz
```

It downloads the released 2.1 once and checks it, and needs `NTUMC`
checked out beside this repository (and `schemas`, to check the result
against the WN-LMF DTD).

The first changes bring in the words, definitions and examples added
to Czech in the NTU-MC wordnet: 813 senses, 508 synsets, 4 definitions
and 82 examples.  Another 130 additions are held until a Czech speaker
has looked at them.  Nothing is released yet.  See `changes/README.md`.

## Tests

```
uv run --group dev pytest
uv run --group dev ruff check .
```

## References

* Adam Rambousek, Karel Pala and Sandra Tukačová. 2017. Overview and
  Future of Czech Wordnet. In *LDK Workshops: OntoLex, TIAD and
  Challenges for Wordnets*, pages 146–151. Galway: CEUR-WS.org.
  <http://ceur-ws.org/Vol-1899/>
* Karel Pala and Pavel Smrž. 2004. Building Czech Wordnet. *Romanian
  Journal of Information Science and Technology* 7(1–2): 79–88.
* Piek Vossen, editor. 1998. *EuroWordNet: A Multilingual Database with
  Lexical Semantic Networks*. Dordrecht: Kluwer.
* Dan Tufiş, Dan Cristea and Sofia Stamou. 2004. BalkaNet: Aims,
  Methods, Results and Perspectives. A General Overview. *Romanian
  Journal of Information Science and Technology* 7(1–2): 9–43.
* Marek Blahuš. 2011. *Extending Czech WordNet Using a Bilingual
  Dictionary*. Diploma thesis, Faculty of Informatics, Masaryk
  University, Brno. Advisor: Karel Pala. <https://is.muni.cz/th/ukl2c/>
* Aleš Horák, Karel Pala, Adam Rambousek and Martin Povolný. 2006.
  DEBVisDic – First Version of New Client-Server Wordnet Browsing and
  Editing Tool. In *Proceedings of the Third International WordNet
  Conference (GWC 2006)*, pages 325–328. Brno: Masaryk University.
* Francis Bond, Piek Vossen, John P. McCrae and Christiane Fellbaum.
  2016. CILI: the Collaborative Interlingual Index. In *Proceedings of
  the 8th Global WordNet Conference (GWC 2016)*, pages 50–57. Bucharest.
