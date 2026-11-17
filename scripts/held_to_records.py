"""Add the held senses that the NTU-MC corpus is tagged with, each marked to check.

    uv run scripts/held_to_records.py WN.db CES.db            # say what would be added
    uv run scripts/held_to_records.py WN.db CES.db --write    # add the records to the log

Run once, on 2026-11-17, for version 2.3; kept as the record of what was
done.  Running it again adds nothing.

Francis Bond's rule of 2026-11-17: nothing the corpus is tagged with is
left out of a wordnet unless the corpus is fixed as well.  The senses
that annotators added in the NTU-MC and that ``changes/held-2.1.tsv``
holds for a Czech speaker are not in the wordnet, but the corpus
(Karel Čapek, Válka s mloky) is tagged with some of them.  Those go in
now, with a note that they are to be checked: either the sense or the
tag is wrong.

For each held sense whose synset and lemma the corpus is tagged with:

* ``add_synset``, if the wordnet does not have the synset,
* ``add_sense``, as ``scripts/ntumc2changes.py`` made it,
* ``set_note`` with ``NOTE``.

The examples and definitions that passed review and waited for one of
these synsets follow.  So do the senses that the database's own copy of
the Czech wordnet has, the corpus is tagged with and release 2.1 lacks
(``set_note`` with ``NOTE_COPY``).

Two lemmas are written in lower case (``LOWER``).  Two senses are left
out because the synset has the word in its right form and it is the
corpus lemma that is wrong (``CORPUS_LEMMA``).

WN.db and CES.db are the NTU-MC wordnet and Czech corpus databases,
frozen 2026-11-13.
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

import corpus_counts  # noqa: E402
import ntumc2changes  # noqa: E402
from ntumc.wordnet import changes, lmf  # noqa: E402
from ntumc.wordnet.changes import Change  # noqa: E402
from ntumc.wordnet.model import Entry, Item, Synset  # noqa: E402

import release  # noqa: E402

DATE = "2026-11-17"
USER = "fcbond"
NOTE = ("to check: added in the NTU-MC and the corpus is tagged with it; "
        "not yet checked by a Czech speaker")
NOTE_COPY = ("to check: in the NTU-MC's copy of the Czech wordnet and the corpus is tagged "
             "with it; not in release 2.1")
RULE = ("nothing the corpus is tagged with is left out of the wordnet unless the corpus is "
        "fixed as well (Francis Bond, 2026-11-17)")
TAGGED = "NTU-MC Czech corpus (Válka s mloky), frozen 2026-11-13: tagged with it {n} times"
COPY = "NTU-MC wordnet database, frozen 2026-11-13: its copy of the Czech wordnet (src wncz)"
LOWER = {"Desetiletý": "desetiletý", "Upírat": "upírat"}
CORPUS_LEMMA = {("wncze-01550902-n", "salamander"): "the synset has salamandr",
                ("wncze-06291158-n", "MUDr"): "the synset has MUDr."}

Pair = tuple[str, str]  # synset here, lemma

log = logging.getLogger("held_to_records")


def same(word: str) -> str:
    """A word as it is compared with a corpus lemma: lower case, underscores as spaces."""
    return " ".join(word.replace("_", " ").lower().split())


def key(c: Change) -> tuple[str | None, ...]:
    """What makes two records the same change, whatever their id and reason."""
    lemma = LOWER.get(c.lemma or "", c.lemma)
    return (c.action, c.synset, lemma, None if c.action == "add_sense" else c.new)


def held_senses(made: list[Change], logged: set[tuple[str | None, ...]],
                uses: Counter[Pair]) -> list[Change]:
    """The senses that were made but not logged and that the corpus is tagged with.

    Args:
        made: every record ``ntumc2changes`` makes, held or not
        logged: the keys of the records in the logs
        uses: how often the corpus is tagged with each (synset, compared lemma)

    Returns:
        The ``add_sense`` records to add, most used first
    """
    out = [c for c in made if c.action == "add_sense" and key(c) not in logged
           and uses[(c.synset, same(c.lemma))]
           and (c.synset, c.lemma) not in CORPUS_LEMMA]
    return sorted(out, key=lambda c: (-uses[(c.synset, same(c.lemma))], c.synset, c.lemma))


def records(senses: list[Change], made: list[Change], have: set[str],
            uses: Counter[Pair], held: set[tuple[str, str, str]]) -> list[Change]:
    """The records for the senses: their synsets, the senses, the notes, what waited.

    Args:
        senses: the ``add_sense`` records to add
        made: every record ``ntumc2changes`` makes
        have: the synsets the wordnet has
        uses: how often the corpus is tagged with each (synset, compared lemma)
        held: the (action, synset, text) of the examples and definitions that are held

    Returns:
        The records in the order they apply, without ids
    """
    synsets = {c.synset: c for c in made if c.action == "add_synset"}
    out: list[Change] = []
    added: set[str] = set()
    for c in senses:
        if c.synset not in have and c.synset not in added:
            added.add(c.synset)
            out.append(synsets[c.synset])
        lemma = LOWER.get(c.lemma, c.lemma)
        n = uses[(c.synset, same(c.lemma))]
        out.append(replace(c, lemma=lemma, reason=f"{c.reason}; held for a Czech speaker, "
                                                  f"added because the corpus is tagged with it"))
        out.append(Change(action="set_note", lexicon=c.lexicon, synset=c.synset, lemma=lemma,
                          pos=c.pos, new=NOTE, user=USER, date=DATE,
                          source=TAGGED.format(n=n), reason=RULE))
    return out + [c for c in made if c.action in ("add_example", "set_definition")
                  and c.synset in added and (c.action, c.synset, c.new) not in held]


def copy_senses(con: sqlite3.Connection, uses: Counter[Pair], here: dict[str, str],
                senses: set[Pair]) -> list[Change]:
    """Records for the senses of the database's copy of the Czech wordnet.

    Args:
        con: the NTU-MC wordnet database
        uses: how often the corpus is tagged with each (synset, compared lemma)
        here: database synset -> the synset here, for the synsets the wordnet has
        senses: the (synset, compared lemma) pairs the wordnet has

    Returns:
        ``add_sense`` and ``set_note`` for each sense that is tagged and not here
    """
    out: list[Change] = []
    rows = con.execute(
        "SELECT s.synset, w.lemma, w.pos FROM sense s JOIN word w USING (wordid) "
        "WHERE s.lang = 'ces' AND s.src = 'wncz' ORDER BY s.synset, w.lemma")
    for synset, lemma, pos in rows:
        pair = (here.get(synset, ""), same(lemma))
        if not uses[pair] or pair in senses:
            continue
        who = {"lexicon": release.WN_ID, "synset": pair[0], "lemma": lemma, "user": USER,
               "date": DATE, "pos": pos if pos in ntumc2changes.POS else None}
        out.append(Change(action="add_sense", source=COPY, reason=RULE, **who))
        out.append(Change(action="set_note", new=NOTE_COPY, reason=RULE,
                          source=TAGGED.format(n=uses[pair]), **who))
    return out


def tagged_here(db: Path, items: list[Item]) -> tuple[Counter[Pair], dict[str, str]]:
    """How often the corpus is tagged with each sense, by the synset here.

    Args:
        db: the NTU-MC Czech corpus database
        items: the wordnet

    Returns:
        (synset here, compared lemma) -> uses, and database synset -> synset here
    """
    synsets = {str(i.id): i for i in items if isinstance(i, Synset)}
    maps = ntumc2changes.load_maps(synsets)
    uses: Counter[Pair] = Counter()
    here: dict[str, str] = {}
    for (lemma, tag), n in corpus_counts.tagged(db).items():
        target = ntumc2changes.target(tag, maps, synsets)
        if not isinstance(target, str):
            here[tag] = target.id
            uses[(target.id, same(lemma))] += n
    return uses, here


def made_records(wn_db: Path) -> list[Change]:
    """Every record ``ntumc2changes`` makes from the database, held or not."""
    base = list(lmf.read(ntumc2changes.BASE_XML))
    synsets = {str(i.id): i for i in base if isinstance(i, Synset)}
    w = ntumc2changes.Writer(base, ntumc2changes.load_maps(synsets))
    con = sqlite3.connect(f"file:{wn_db}?mode=ro", uri=True)
    try:
        ntumc2changes.additions(con, w, ntumc2changes.corrections(con, w))
        ntumc2changes.texts(con, w)
    finally:
        con.close()
    return w.records


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("wn", type=Path, help="the NTU-MC wordnet database (wn-ntumc.db)")
    parser.add_argument("corpus", type=Path, help="the NTU-MC Czech corpus database (ces.db)")
    parser.add_argument("--write", action="store_true",
                        help="add the records to the change log")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    release.fetch_base()
    log_records = list(changes.read(release.CHANGES))
    items, conflicts = changes.apply(list(lmf.read(release.BASE)), log_records)
    if conflicts:
        for line in conflicts:
            log.error(line)
        sys.exit(1)
    logged = {key(c) for c in [*changes.read(ntumc2changes.CHANGES), *log_records]}
    have = {str(i.id) for i in items if isinstance(i, Synset)}
    senses = {(str(s.synset), same(str(e.lemma)))
              for e in items if isinstance(e, Entry) for s in e.senses}
    uses, here = tagged_here(args.corpus, items)
    made = made_records(args.wn)
    held = {(r["action"], r["synset"], r["text"]) for r in ntumc2changes._tsv(ntumc2changes.HELD)}
    new = records(held_senses(made, logged, uses), made, have, uses, held)
    con = sqlite3.connect(f"file:{args.wn}?mode=ro", uri=True)
    try:
        new += copy_senses(con, uses, {k: v for k, v in here.items() if v in have}, senses)
    finally:
        con.close()
    new = [c for c in new if key(c) not in logged]
    base = f"{release.WN_ID}-{release.BASE_VERSION}"
    new = [replace(c, id=f"{base}-{len(log_records) + i}", base=base)
           for i, c in enumerate(new, 1)]
    for action, n in sorted(Counter(c.action for c in new).items()):
        log.info("%d %s", n, action)
    if not args.write:
        return
    with release.CHANGES.open("a", encoding="utf-8") as f:
        for record in new:
            f.write(changes.dumps(record) + "\n")
    log.info("Added %d records to %s", len(new), release.CHANGES)


if __name__ == "__main__":
    main()
