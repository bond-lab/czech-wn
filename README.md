# Czech WordNet

[![DOI](https://zenodo.org/badge/960630050.svg)](https://doi.org/10.5281/zenodo.24256732)

The Czech WordNet is a lexical database of Czech.  Nouns, verbs,
adjectives and adverbs are grouped into sets of synonyms (synsets),
each standing for one concept, and the synsets are linked by semantic
relations such as hypernymy, meronymy and antonymy.  Almost all synsets
are linked to Princeton WordNet and, through the Interlingual Index, to
wordnets of other languages; about 400 are concepts that Princeton
WordNet does not have.  Some synsets have a definition, examples, or
verb valency frames.

| release 2.2 | nouns | verbs | adjectives | adverbs | other | all |
|---|---:|---:|---:|---:|---:|---:|
| words | 25,284 | 6,728 | 2,243 | 389 | 18 | 34,662 |
| senses | 33,614 | 10,733 | 3,465 | 469 | 21 | 48,302 |
| synsets | 21,144 | 5,211 | 2,288 | 322 | 12 | 28,977 |

There are 34,831 relations between synsets, 968 definitions, 1,459
examples and 1,341 verb frames; 28,491 synsets are linked to the
Interlingual Index, and 1,736 senses have their count in a tagged
corpus.  The other words are pronouns and the like.

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
wn.download("https://github.com/bond-lab/czech-wn/releases/download/v2.2/wncze-2.2.tar.xz")
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
* **2.2** adds the words, examples and definitions made while tagging
  Karel Čapek's *Válka s mloky* in NTU-MC, examples from the verb
  frames, relations from Princeton WordNet and sense counts, and
  corrects errors of the source.
* **From 2.2 on** a release is the last release and an ordered log of changes
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
| `changes/` | the changes since the last release (`wncze-2.2.jsonl`) and those that made 2.2 from 2.1, one record per line; see `changes/README.md` |
| `release.py` | makes the next release: the last release plus the changes |
| `sources/` | the files as Masaryk University gave them to us: three versions of the Czech WordNet, and the PDT annotation dictionary, which has **a different licence**; see `sources/README.md` |
| `notes/` | how 2.1 was converted (`conversion.md`); the verb frames (`verb-frames.md`); loading with reverse relations (`reverse_relations.py`); references (`references.md`) |
| `scripts/visdic2lmf.py` | made release 2.1 from the source |
| `scripts/` | the scripts that made change records: from the NTU-MC wordnet (`ntumc2changes.py`), from Princeton WordNet (`princeton_links.py`), from the NTU-MC Czech corpus (`corpus_counts.py`) and from the verb frames (`frames_to_senses.py`, `frame_examples.py`) |
| `additions/` | words added in 2025 while annotating *War with the Newts*; now change records |
| `tests/` | tests of the conversion and of the release |

## Making a release

```
uv run release.py 2.3     # -> release/wncze-2.3.xml, release/wncze-2.3.tar.xz
```

It downloads the last release once and checks it, applies the changes,
and checks the result against the WN-LMF DTD and with the validation of
`wn`.  It needs `NTUMC` checked out beside this repository (and
`schemas`, for the DTD).

## Tests

```
uv run --group dev pytest
uv run --group dev ruff check .
```
