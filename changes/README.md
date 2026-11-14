# Changes

From release 2.1 on, the master copy of the Czech WordNet in WN-LMF is

* the last release, `wncze-2.1.xml` (fetched from the GitHub release and
  checked against its checksum by `release.py`), and
* `wncze-2.1.jsonl`: every change made since, one per line, in order.

`uv run release.py 2.2` applies the changes to the base and writes
`release/wncze-2.2.xml` and its package.  After a release, the new XML
is the base and a new, empty `wncze-2.2.jsonl` is started; the old file
stays as the history.

2.1 itself is made from the DEBVisDic source by
`scripts/visdic2lmf.py`; nothing later is rebuilt from that source.

## A change record

```json
{"id": "wncze-2.1-6", "action": "add_sense", "lexicon": "wncze",
 "synset": "wncze-NTUMC-80002448-a", "lemma": "Desetiletý", "pos": "a",
 "user": "s67", "date": "2024-04-13",
 "source": "NTU-MC wordnet database, frozen 2026-11-13: annotator s67",
 "reason": "added in NTU-MC by an annotator", "base": "wncze-2.1"}
```

To make a change, add a line at the end.  Never edit or delete an
earlier line: to undo a change, add the opposite one.

* `id` is unique; `user`, `source` (the evidence: a person, a
  dictionary, a corpus) and `reason` are required.
* A model alone is not a source for an addition.
* No synset is dropped for being empty.  COW and Wordnet Bahasa extend
  the English wordnet and drop a synset that says nothing; the Czech
  WordNet has its own structure, so a synset goes only by a
  `remove_synset` record.
* New entries and senses get ids like the others: `wncze-pes-n`, and
  the synset's id with `-s` and the next number.

The actions and the fields each needs are in NTU-MC
`docs/wordnet-model.md`.

## Ids of new synsets

| id | concept |
|---|---|
| `wncze-02001223-n` | a Princeton WordNet 2.0 synset, as in the source (`ENG20-02001223-n`) |
| `wncze-ENG30-04489008-n` | a Princeton WordNet 3.0 synset that 2.0 does not have |
| `wncze-CZE-00000002-z` | a Czech concept from the source |
| `wncze-NTUMC-80002448-a` | a concept made in NTU-MC; its `dc:identifier` names it in omw-ntumc (`ntumc02685`) or omw-pronoun (`pronoun:1;Sg`) |

A synset added for a Princeton concept has its ILI and nothing else: no
definition and no relations.  A synset added for an NTU-MC concept has
only the identifier; its definition and relations are in omw-ntumc or
omw-pronoun.

## The first log (2026-11-14)

`wncze-2.1.jsonl` starts with the 1,620 changes that bring in what was
added to Czech in the NTU-MC wordnet database since it was loaded from
the Czech WordNet in April 2024.  They were made by
`scripts/ntumc2changes.py` from the database frozen on 2026-11-13.
The database names concepts by Princeton WordNet 3.0; each was found
here through its ILI.

| records | action | from |
|---:|---|---|
| 2 | `remove_sense` | released senses that annotators removed |
| 2 | `rename_lemma` | released senses that annotators corrected |
| 564 | `add_synset` | concepts the Czech WordNet did not have: 375 by their 2.0 id, 8 by their 3.0 id, 147 from omw-ntumc, 34 pronoun concepts |
| 2 | `set_identifier` | existing synsets that are pronoun concepts |
| 590 | `add_sense` | NTU-MC annotators |
| 304 | `add_sense` | `additions/2025-04/arasaac.tab` |
| 10 | `add_sense` | `additions/2025-04/pronouns-quick.tab` |
| 23 | `add_sense` | loaded with those files (source `sem`) but not in them |
| 7 | `set_definition` | `additions/2025-04/pronouns.tab` |
| 6 | `set_definition` | NTU-MC annotators |
| 110 | `add_example` | NTU-MC annotators |

The user of a record is the account that first entered the sense in
NTU-MC (`s109`), and its date the day it was entered.  The senses from
`additions/2025-04/` were loaded by a test account; their user is
`fcbond`, who made the files, and the source names the file.  139
records have no date: the database does not date definitions and
examples.

Applied to 2.1 they give 34,800 words, 48,431 senses and 29,034 synsets
(2.1: 34,089, 47,506 and 28,470), with no conflicts.

### Not turned into records

`review-2.1.tsv` lists the 13 things that have no record, and why:

* three words whose lemma holds a comment (`nazdar (informal, usually
  among friends)`), and an example that does;
* three texts entered as Czech definitions that are not (one in English,
  one an example, one a note);
* one word for a concept that is in no registry (`01551633-n`, *mnoho*);
* three examples for concepts that have no Czech word;
* one removal of a sense the release does not have, and one sense that
  is already in the release.

Also waiting:

* `additions/2025-04/pronouns.tab` has definitions for honorific *vy*
  and for plural *oni*, *ony* and *ona*.  NTU-MC has one concept for
  the third person plural and none for the honorific, so these four
  have no synset to go on yet.
* `additions/2025-04/pronouns-quick.tab` ends with 42 words noted as
  missing, with no synset.

## To decide

* The pronouns are here as in COW, as synsets carrying an omw-pronoun
  identifier.  omw-pronoun has its own Czech lexicon
  (`omw-pronoun-cs`); the words could live only there.
* *kde* and *kam* are both on `pronoun:Plc;Int`; omw-pronoun tells
  place from goal.
* The 383 synsets added for Princeton concepts have no relations.
