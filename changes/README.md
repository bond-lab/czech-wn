# Changes

From release 2.1 on, the master copy of the Czech WordNet in WN-LMF is

* the last release, now `wncze-2.2.xml` (fetched from the GitHub
  release and checked against its checksum by `release.py`), and
* `wncze-2.2.jsonl`: every change made since, one per line, in order.

`uv run release.py 2.3` applies the changes to the base and writes two
lexicons, each with its package:

* `release/wncze-min-2.3.xml` (id `wncze-min`), the minimal lexicon:
  what the Czech WordNet itself says.  For a concept CILI does not have
  yet it holds the words and the concept's identifier
  (`dc:identifier="ntumc02686"`); the English definition and the
  relations are in the shared lexicon `omw-ntumc`.  Cygnet takes this
  one, with omw-ntumc beside it.
* `release/wncze-2.3.xml` (id `wncze`), the export: the minimal lexicon
  with what `omw-ntumc` says put back (128 definitions and 113
  relations), for users of `wn`, who want one file.

`release.py` fails if the export lacks anything the lexicon said before
it was split.  `omw-ntumc` is read from a checkout beside this one,
built at the version `release.py` pins (`uv run build.py 0.1` at tag
`v0.1`).  Release 2.2 was one lexicon, `wncze`, which said nothing of
the omw-ntumc concepts but their words: it is the minimal lexicon in
all but name.

After a release, the minimal XML is the base and a new, empty log is
started; the old file stays as the history.  `release.py` exports a
minimal base before it applies the changes, so the records are always
for `wncze`.  `wncze-2.1.jsonl` holds the 6,266 changes that made 2.2 from
2.1; the rest of this page describes them.

2.1 itself is made from the DEBVisDic source by
`scripts/visdic2lmf.py`; nothing later is rebuilt from that source.

## Since 2.2

`wncze-2.2.jsonl`:

* Six synsets that are Princeton 2.0 synsets but had no ILI get the ILI
  of their Princeton 3.0 concept (*nezvyklý*, *kněžské svěcení*,
  *španělská omáčka*, *cappucinno*, *mnohem více*, *andezit*).  The
  map from 2.0 missed them, mostly because 2.0 misspells the English
  word.  See issue 8.
* 75 more Princeton 2.0 synsets with no ILI and no definition get the
  English definition Princeton WordNet 2.0 gives them
  (`set_definition`, language `en`): the 49 that lost a wrong ILI in
  2.2 and 26 that never had one, such as *amorální* "without moral
  standards or principles" and *upocený* "being wet with perspiration".
  Without a definition nothing says what such a synset means, and
  Cygnet drops it.  Most are adjectives that Princeton 3.0 no longer
  has (english-wordnet issue 1465); when a synset gets an ILI, the
  English definition can go.
* *moci* 'can' (`ntumc02041`) gets a Czech definition and, as its
  example, a sentence of the corpus.
* 70 senses that the NTU-MC corpus is tagged with go in, each with the
  note "to check" (`scripts/held_to_records.py`, 2026-11-17).  The
  rule is Francis Bond's: nothing the corpus is tagged with is left out
  of the wordnet unless the corpus is fixed as well.  67 are annotators'
  additions that `held-2.1.tsv` held for a Czech speaker (*ale*,
  *muset*, *smět*, 202 tags in all); 3 are in the database's own copy
  of the Czech wordnet but not in release 2.1 (*nějaký*, *spravedlivý*,
  *národ*).  With them come 31 synsets, the 9 examples and 1 definition
  that waited for those synsets, and a count for each sense.
  *desetiletý* and *upírat* are written in lower case.  Two are left
  out because the synset has the word in its right form and the corpus
  lemma is to be corrected: *salamander* (*salamandr*) and *MUDr*
  (*MUDr.*).  The senses still need a Czech speaker: either the sense
  or the tag is wrong.

## A change record

```json
{"id": "wncze-2.1-594", "action": "add_sense", "lexicon": "wncze",
 "synset": "wncze-NTUMC-80002475-x", "lemma": "to", "pos": "x",
 "user": "s73", "date": "2025-04-23",
 "source": "NTU-MC wordnet database, frozen 2026-11-13: annotator s73",
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

A synset added for a Princeton concept has its ILI and no definition;
its relations are added from Princeton WordNet (below).  A synset added for an NTU-MC concept has
only the identifier; its definition and relations are in omw-ntumc or
omw-pronoun.

## The first log (2026-11-14)

`wncze-2.1.jsonl` starts with the 1,412 changes that bring in what was
added to Czech in the NTU-MC wordnet database since it was loaded from
the Czech WordNet in April 2024.  They were made by
`scripts/ntumc2changes.py` from the database frozen on 2026-11-13.
The database names concepts by Princeton WordNet 3.0; each was found
here through its ILI.

| records | action | from |
|---:|---|---|
| 1 | `remove_sense` | a released sense that an annotator removed |
| 2 | `rename_lemma` | released senses that annotators corrected |
| 508 | `add_synset` | concepts the Czech WordNet did not have: 350 by their 2.0 id, 8 by their 3.0 id, 117 from omw-ntumc, 33 pronoun concepts |
| 2 | `set_identifier` | existing synsets that are pronoun concepts |
| 502 | `add_sense` | NTU-MC annotators |
| 280 | `add_sense` | `additions/2025-04/arasaac.tab` |
| 10 | `add_sense` | `additions/2025-04/pronouns-quick.tab` |
| 21 | `add_sense` | loaded with those files (source `sem`) but not in them |
| 4 | `set_definition` | `additions/2025-04/pronouns.tab` |
| 82 | `add_example` | NTU-MC annotators |

The user of a record is the account that first entered the sense in
NTU-MC (`s109`), and its date the day it was entered.  The senses from
`additions/2025-04/` were loaded by a test account; their user is
`fcbond`, who made the files, and the source names the file.  103
records have no date: the database does not date definitions and
examples.

Applied to 2.1 they give 34,727 words, 48,318 senses and 28,978 synsets
(2.1: 34,089, 47,506 and 28,470), with no conflicts.

### Held for a person

Two reviewers (Claude Sonnet 5.5, 2026-11-15, each working alone) read
every record with Czech in it: 927 senses, 110 examples, 13 definitions
and 4 corrections.  Each saw the Czech word, the English words and
definition of the concept, and the Czech words already in the synset,
and answered ok, doubt or wrong.  They agreed that 924 are ok.

The other 130 are **not in the log**.  They are in `held-2.1.tsv`, with
both answers and reasons, until a person who knows Czech has ruled:
114 senses, 8 definitions, 7 examples and 1 removal.  A model's doubt
is not a reason to drop what a person added, and reviewers are known to
question words that are fine (a looser or narrower word, a derived
form), so nothing is rejected yet.  Because of them, 56 synsets are not
added, and 21 examples and 1 definition wait for their synset.

On 2026-11-17 the 67 held senses that the corpus is tagged with were
added after all, marked "to check" (see "Since 2.2"); their `ruling`
says `in the log, to check`.  The other 47 senses stay held.

To rule, write `add` or `drop` in the `ruling` column.  While the log
holds only these first records, `scripts/ntumc2changes.py` can make it
again (empty the file first), and then includes the rows ruled `add`.  Once the log has other
records, an accepted row is added as a new record at the end.

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

## Links for the new synsets (2026-11-15)

The 361 synsets added for Princeton concepts (the 358 above and three
pronoun concepts that Princeton also has) came with no relations.
`scripts/princeton_links.py` reads Princeton WordNet 3.0 (omw-en 1.4,
through `wn`) and adds each relation between such a concept and another
that the Czech WordNet has, found through the ILIs: 381 `add_relation`
records, for 158 of the synsets (66 of 83 nouns, 22 of 24 verbs, 61 of
121 adjectives, 9 of 133 adverbs).

| records | relation |
|---:|---|
| 128 | `similar` |
| 76 | `hypernym` |
| 38 | `also` |
| 37 | `holo_part` |
| 30 | `antonym` |
| 22 | `domain_region` |
| 17 | `instance_hypernym` |
| 16 | `holo_member` |
| 10 | `attribute` |
| 6 | `exemplifies` |
| 1 | `domain_topic` |

They are written as 2.1 writes relations: `hypernym`, `holo_part` and
the domains one way only, on the narrower synset, the part and the
member (so 160 of the records are on a synset of 2.1 and point to a new
one); antonymy between synsets.  Derivation and pertainym, which link
59 more of the synsets in Princeton, are relations between English
words and are not copied.

The six `exemplifies` relations were a mistake and are taken out again
by six `remove_relation` records: they said that *všude*, *přece*,
*patrně*, *rozlícený* are colloquial, *odtud* archaic and *víc* a
comparative, because the English words of the concept are.  A usage
label belongs to a word of one language.  The script no longer copies
them, which leaves 375 relations.

A synset of 2.1 that has a hypernym keeps it.  Seven are given another
by Princeton 3.0 and are not changed: six kinds of trousers (*džínsy*,
*pumpky*, ...), which 2.1 has under *kalhoty* `wncze-04315668-n` and
3.0 under the new `wncze-ENG30-04489008-n` (also *kalhoty*; the two
are now one, see below), and *rovnostranný trojúhelník*.

The other 203 new synsets, mostly adverbs, still have no relations.
Run the script again (`--write`) after more synsets are added; it adds
only what is missing.

## One ILI, one synset (2026-11-15)

In 2.1, 69 ILIs are each on two synsets.  The ILIs are in the source,
and are those of CILI's map from Princeton 2.0: where 3.0 moved a word
or joined two synsets, two 2.0 synsets got one ILI.  Princeton 2.0 says
what each synset is.

*kalhoty* is corrected.  2.0 *trousers, pants* (`wncze-04315668-n`)
had the ILI of *bloomers* (i50863), which is *dámské kalhotky*
`wncze-02753844-n`.  Its concept is 3.0 *trouser, pant* (i60589), for
which an annotator's *kalhoty* had made `wncze-ENG30-04489008-n`.  A
`merge_synset` record joins that to the old synset and a `set_ili`
record gives the old synset i60589.

`shared-ili-2.1.tsv` lists the other 68, with both definitions.  They
are settled by 68 `set_ili` records (ruled by fcbond, 2026-11-15), so
that no ILI is on two synsets:

* 68 synsets keep the ILI: the one whose 2.0 definition is the 3.0
  definition (51), or is nearest to it (17);
* 18 get another ILI: a 3.0 synset that has their 2.0 definition and
  that no synset here has (17), or the other ILI the source gives (1);
* 50 lose the ILI: no 3.0 synset has their definition.  For 19 of
  them the two synsets share a Czech word, and where 3.0 joined the
  two concepts they could still be merged (`merge_synset`).

## A word once in a synset (2026-11-15)

The source lists a word twice in three synsets (*ulevit*,
*individualismus*, *vedoucí osobnost*), and 2.1 kept both senses.
Three `remove_sense` records, each naming one sense by its id
(`sense`), take the second away.

## Two verbs (2026-11-15)

The source gives two verb synsets another part of speech:
`wncze-00660033-v` (*cenzurovat*) is a noun and `wncze-00663238-v`
(*odmítnout účast*) an adverb, each under a verb.  A `set_pos` record
makes each a verb, and its word with it.

## Counts from the corpus (2026-11-15)

The NTU-MC Czech corpus is Karel Čapek's *Válka s mloky*, tagged with
concepts by students at Palacký University.  1,736 `set_count` records
(`scripts/corpus_counts.py`, from the corpus frozen on 2026-11-13) give
how often each sense is tagged: 5,744 tags in all, as
`<Count dc:source="NTU-MC">`.

287 tags are for a sense the wordnet does not have and are not counted:
131 for a synset that is not here and 155 for a word that is not in the
synset (most are among the held additions), and 1 for a concept in no
registry.

## Frames on the verbs they name (2026-11-15)

In 2.1 every verb of a synset names all the synset's frames.  887
`set_frames` records (`scripts/frames_to_senses.py`) leave a frame that
begins with verbs of its synset on those verbs only.  See
`notes/verb-frames.md`.

## Examples from the verb frames (2026-11-15)

A verb frame ends with examples.  1,243 `add_example` records
(`scripts/frame_examples.py`) make them examples of the synset too, for
793 synsets; each names its frame as the source.  The text is kept
whole, since it cannot be cut at its commas safely.  Of 100 read, 91
show a verb of the synset.  The 96 examples of frames that name only
verbs their synset does not have are left out.  See
`notes/verb-frames.md`.

## Before the release (2026-11-15)

**Relations between synsets of 2.1.**  `scripts/princeton_links.py
--all` does for every synset with an ILI what it did for the new ones:
269 `add_relation` records for relations that Princeton WordNet 3.0 has
between two concepts of the Czech WordNet and the Czech WordNet lacked
(73 `similar`, 55 `domain_topic`, 38 `hypernym`, 34 `holo_part`, 32
`also`, 30 `antonym`, 7 others).  A synset that has a hypernym keeps
it: Princeton gives another to 410, and they are not changed.
Princeton's `entails` is `subevent` here, and none was missing.

**Region links: be careful.**  Princeton's `domain_region` is right for
its concept, but a Czech synset on that ILI often has a general word.
Of the 22 added for new synsets, 8 are taken out again by
`remove_relation` records: *hostinský* is not of the United Kingdom,
nor *poslanec*, *legionář*, *obec*, *stav*, *trikolora* and *vtipné
rčení* of France or Italy.  The 14 that stay are things of a place
(*suši*, *karate*, *francouzština*).  The script no longer copies
region links: each needs a person to look at the Czech words.

**Lemmas.**  16 `rename_lemma` and 3 `add_sense` records clean 13
lemmas of the source: a sense number in the lemma (*topit-2*, *požít
#2*, *věda o smrti:1*; seven), punctuation at its end (*porušení
zákona,*; two), and two words written as one (*téct, téci*; *přitékat,
přitéci*; *vtékat, vtéci*, where the second becomes a sense of its own;
*pleva, plevy*).

**Notes and definitions in lemmas.**  `lemma-notes-2.1.tsv` lists the
111 senses whose lemma has brackets or is a description, and what was
done with each:

* 64 have a note in brackets after the word: what it is said of (*zmar
  (plánů)*, *ouško (jehly)*), its complement (*přejít (na co)*) or its
  register (*medicína (hovor.)*, *vajgl( slang)*).  The note goes on
  the sense (`set_note`, added to a note the sense already has) and the
  lemma is the word alone (`rename_lemma`).
* 15 are a description beside the real word of the synset (*látka
  snižující hladinu cukru v krvi* beside *antidiabetikum*).  The
  description becomes the definition of the synset, which had none
  (`set_definition`; three misprints corrected), and is no longer a
  word of it (`remove_sense`).
* 32 are left as they are, for a Czech speaker (issue 6): a word in
  brackets that may be part of the term (*(houpací) síť*), a variant
  (*tromb(us)*), or a description that is the only word of its synset.

**Two more parts of speech.**  `wncze-10676415-n` (*vliv*, *účinek*)
was an adjective in the source and `wncze-00236555-a` a noun; each has
a `set_pos` record.  The only word of the second is *testik*, which
looks like a test entry (issue 6).

**Relations read by two reviewers.**  The antonym, `similar` and `also`
relations taken from Princeton hold between the concepts, but not
always between the Czech words on them.

* Four antonym pairs are taken out after a check against the antonyms
  of the Czech Wiktionary (the extract of kaikki.org, 10,791 pairs):
  *malý* and *hodně, mnoho*; *rád* and *vážný*; *mračit se* and
  *zesvětlit*; *boční* and *spodní*.
* Two reviewers (Claude Sonnet 5.5, 2026-11-15, each working alone, on
  sheets in different orders, not told where the relations came from)
  then read the 171 pairs that were left: 101 `similar`, 43 `also`, 27
  antonym.  They agreed that 118 are ok.  The 26 that neither accepted
  are taken out again (50 `remove_relation` records) and wait in
  `held-links-2.1.tsv` for a person; the 27 that one of them accepted
  stay, and are in the same table (issue 7).

578 relations from Princeton are left.

**Frames after the lemmas were cleaned.**  `scripts/frames_to_senses.py`
now looks at every verb of a synset, so that a frame is on the verbs it
names once they have their plain lemma (*vyložit*, *téci*, *navázat*)
or were added later (*říkat*): 12 more `set_frames` records, and 2 more
examples.  A verb added to a synset later gets only the frames that
name it.

## Validation

After writing the XML, `release.py` checks it against the WN-LMF DTD
and runs the validation of the `wn` module (NTU-MC
`ntumc.wordnet.validate`).  An error stops the release, and so do an
ILI on two synsets (`W302`), a word twice in a synset (`W202`) and two
entries for one word in a synset (`W203`).  The other warnings are
counted in the log: 25 empty synsets, 35 repeated definitions, one
hypernym of another part of speech and about 9,200 relations with no
reverse (the source has `hypernym` and `holo_part` one way only).

## To decide

* The pronouns are here as in COW, as synsets carrying an omw-pronoun
  identifier.  omw-pronoun has its own Czech lexicon
  (`omw-pronoun-cs`); the words could live only there.
* *kde* and *kam* are both on `pronoun:Plc;Int`; omw-pronoun tells
  place from goal.
* `instance_hypernym` is new here: 2.1 follows Princeton 2.0 and has
  `hypernym` for instances too.
* Whether to merge any of the 19 pairs in `shared-ili-2.1.tsv` that
  share a Czech word and now differ only in that one has no ILI.
