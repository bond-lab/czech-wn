# Changelog

The major changes in each release.  Every change since 2.1 is a record
in `changes/`; see `changes/README.md` for the details.

## 2.2 (not yet released)

34,662 words, 48,302 senses, 28,977 synsets.

### Added

* 813 senses, 82 examples and 4 definitions added to Czech in the
  NTU-MC wordnet (2024-2025), most by students at Palacký University
  tagging Karel Čapek's *Válka s mloky*, with 508 new synsets for them.
* 636 relations from Princeton WordNet 3.0: 367 that link the new
  synsets to the rest, and 269 between synsets of 2.1 that lacked them.
* 1,243 examples for 793 verb synsets, from the examples in their verb
  frames.
* Counts for 1,736 senses: how often each is tagged in the NTU-MC Czech
  corpus.

### Fixed

* No ILI is on two synsets: 69 were, through the source's map from
  Princeton WordNet 2.0.  18 synsets get the right ILI, 50 lose a wrong
  one, and the two synsets for *kalhoty* are merged.
* A word is in a synset once: three were there twice.
* Four synsets have the part of speech of their concept; the source
  had another.
* Lemmas are words: a sense number, punctuation or a second word in
  the lemma is gone (13 lemmas); a note in brackets (*zmar (plánů)*,
  *medicína (hovor.)*) is now a note on the sense (64); and a
  description listed as a word is now the definition of its synset
  (15).

### Changed

* A verb frame that names verbs of its synset is on those verbs only,
  not on every verb of the synset (887 senses).
* The lexicon is now the last release and an ordered log of changes
  (`release.py`), not a conversion of the DEBVisDic source.
* A release must pass the validation of the `wn` module.

## 2.1 (2026-11-14)

34,089 words, 47,506 senses, 28,470 synsets.

* The first release in WN-LMF: the latest version of the Czech WordNet
  in DEBVisDic (`wncze21.xml`), converted without loss
  (`scripts/visdic2lmf.py`), under CC BY-SA 4.0.
* The three source versions are released with it.
