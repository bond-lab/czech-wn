# Czech WordNet

The Czech WordNet is a lexical database of Czech.  Nouns, verbs,
adjectives and adverbs are grouped into sets of synonyms (synsets),
each standing for one concept, and the synsets are linked by semantic
relations such as hypernymy, meronymy and antonymy.  Almost all synsets
are linked to Princeton WordNet and, through the Interlingual Index, to
wordnets of other languages; 254 are concepts that Princeton WordNet
does not have.  Some synsets have a definition, examples, or verb
valency frames.

| release 2.1 | nouns | verbs | adjectives | adverbs | all |
|---|---:|---:|---:|---:|---:|
| words | 25,144 | 6,665 | 2,063 | 217 | 34,089 |
| senses | 33,423 | 10,588 | 3,236 | 259 | 47,506 |
| synsets | 21,016 | 5,159 | 2,129 | 166 | 28,470 |

There are 34,257 relations between synsets, 949 definitions, 132
examples and 1,341 verb frames; 28,181 synsets are linked to the
Interlingual Index.

The Czech WordNet was created by the **Natural Language Processing
Centre, Faculty of Informatics, Masaryk University, Brno** (Karel
Pala, Adam Rambousek, Aleš Horák and colleagues).  It was built since
1998, in the EuroWordNet and BalkaNet projects, and is kept in their
[DEBVisDic](https://deb.fi.muni.cz/) editor.

It is now maintained and extended by the **Computational Linguistics
Lab at Palacký University, Olomouc** (<https://bond-lab.github.io/>),
in this repository.

* The original data and its editor: <https://deb.fi.muni.cz/>
* Copyright © 1998–2025 Natural Language Processing Centre, Faculty of
  Informatics, Masaryk University
* Licence: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
  (see `LICENSE`), by permission of Adam Rambousek, 2026-11-05.  One
  file, `sources/nas_anotacni_slovnik.xml`, has a different licence

The wordnet is released in
[WN-LMF](https://globalwordnet.github.io/schemas/) (WordNet Lexical
Markup Framework), the XML format of the Global WordNet Association, so
that it can be used with the
[wn](https://github.com/goodmami/wn) module and edited together with
other wordnets:

```python
import wn
wn.download("https://github.com/bond-lab/czech-wn/releases/download/v2.1/wncze-2.1.tar.xz")
wn.synsets("pes", lexicon="wncze")
```

The wordnet records a relation one way only: a synset has its
hypernym, but the hypernym does not list its hyponyms, so
`synset.hyponyms()` finds nothing.  `notes/reverse_relations.py` loads
the XML file into `wn` with the reverse relations added.

## Please cite

> Adam Rambousek, Karel Pala and Sandra Tukačová. 2017.
> [Overview and Future of Czech Wordnet](https://repozitar.cz/repo/26626/452493/).
> In *LDK Workshops: OntoLex, TIAD and Challenges for Wordnets*,
> pages 146–151. Galway, Ireland: CEUR-WS.org.

BibTeX is in `citation.bib`; more references are in
`notes/references.md`.

## Releases

* **2.1** is the latest version in DEBVisDic (`wncze21.xml`, 28,468
  synsets) converted to WN-LMF with nothing changed.  How each field
  was converted, and the check that nothing was lost, are in
  `notes/conversion.md`.
* **Later releases** are the last release and an ordered log of changes
  (`changes/`), as for the Japanese, Chinese and Malay/Indonesian
  wordnets of [NTU-MC](https://github.com/bond-lab/NTUMC), the Nanyang
  Technological University Multilingual Corpus, a sense-tagged corpus
  with its own wordnets.  `CHANGELOG.md` has the major changes of each
  release, and `changes/README.md` the details.

Synsets are identified by their Princeton WordNet 2.0 synset
(`wncze-02001223-n`), or by a Czech id for the 254 concepts that
Princeton WordNet does not have (`wncze-CZE-00000002-z`).

An earlier version (1.0, 2008) is distributed by ELRA, under other
licences: <https://live.european-language-grid.eu/catalogue/lcr/2364>.

## What is here

| | |
|---|---|
| `CHANGELOG.md` | the major changes in each release |
| `changes/` | the changes since 2.1, one record per line; see `changes/README.md` |
| `release.py` | makes the next release: the last release plus the changes |
| `sources/` | the files as Masaryk University gave them to us: three versions of the Czech WordNet, and the PDT annotation dictionary, which has **a different licence**; see `sources/README.md` |
| `notes/` | how 2.1 was converted (`conversion.md`); the verb frames (`verb-frames.md`); loading with reverse relations (`reverse_relations.py`); references (`references.md`) |
| `scripts/visdic2lmf.py` | made release 2.1 from the source |
| `scripts/` | the scripts that made change records: from the NTU-MC wordnet (`ntumc2changes.py`), from Princeton WordNet (`princeton_links.py`), from the NTU-MC Czech corpus (`corpus_counts.py`) and from the verb frames (`frames_to_senses.py`, `frame_examples.py`) |
| `additions/` | words added in 2025 while annotating *War with the Newts*; now change records |
| `tests/` | tests of the conversion and of the release |

## Making a release

```
uv run release.py 2.2     # -> release/wncze-2.2.xml, release/wncze-2.2.tar.xz
```

It downloads the released 2.1 once and checks it, applies the changes,
and checks the result against the WN-LMF DTD and with the validation of
`wn`.  It needs `NTUMC` checked out beside this repository (and
`schemas`, for the DTD).

## Tests

```
uv run --group dev pytest
uv run --group dev ruff check .
```
