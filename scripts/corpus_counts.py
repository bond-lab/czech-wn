#!/usr/bin/env python3
"""How often each sense is tagged in the NTU-MC Czech corpus, as change records.

    uv run scripts/corpus_counts.py CES.db            # say what would be added
    uv run scripts/corpus_counts.py CES.db --write    # add the records to the log

The NTU-MC Czech corpus (Karel Čapek, Válka s mloky) has words tagged
with concepts.  For each word and concept tagged, this adds a
``set_count`` record giving how often, if the Czech WordNet has that
sense.  A count that is already right is left alone, so the script can
be run again.  Tags for senses the wordnet does not have are counted
and reported, not added.

The corpus names concepts by Princeton WordNet 3.0 or NTU-MC ids; they
are found here as in scripts/ntumc2changes.py.
"""

import argparse
import datetime
import logging
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

import ntumc2changes  # noqa: E402
from ntumc.wordnet import changes, lmf  # noqa: E402
from ntumc.wordnet.model import Entry, Item, Synset  # noqa: E402

import release  # noqa: E402

CORPUS = "NTU-MC"
SOURCE = "NTU-MC Czech corpus (Válka s mloky), frozen 2026-11-13 (scripts/corpus_counts.py)"
REASON = "how often the sense is tagged in the corpus"
USER = "fcbond"

log = logging.getLogger("corpus_counts")


def tagged(db: Path) -> Counter[tuple[str, str]]:
    """Count the tags of the corpus.

    Args:
        db: the NTU-MC Czech corpus database

    Returns:
        How often each (lemma, NTU-MC synset) is tagged
    """
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT clemma, tag, COUNT(*) FROM concept "
            "WHERE tag GLOB '[0-9]*' AND clemma IS NOT NULL GROUP BY clemma, tag")
        return Counter({(lemma, tag): n for lemma, tag, n in rows})
    finally:
        con.close()


def counts(tags: Counter[tuple[str, str]],
           items: list[Item]) -> tuple[Counter[tuple[str, str]], Counter[str]]:
    """The counts of the senses the lexicon has.

    Args:
        tags: how often each (lemma, NTU-MC synset) is tagged
        items: the lexicon

    Returns:
        How often each (synset here, lemma) is tagged, and how many tags
        were left out, by reason
    """
    synsets = {str(i.id): i for i in items if isinstance(i, Synset)}
    named = {s.meta["dc:identifier"]: sid for sid, s in synsets.items()
             if s.meta.get("dc:identifier")}
    senses = {(str(s.synset), str(e.lemma))
              for e in items if isinstance(e, Entry) for s in e.senses}
    maps = ntumc2changes.load_maps(synsets)
    found: Counter[tuple[str, str]] = Counter()
    left: Counter[str] = Counter()
    for (lemma, tag), n in tags.items():
        target = ntumc2changes.target(tag, maps, synsets)
        if isinstance(target, str):
            left["no synset for the concept"] += n
            continue
        sid = target.id if target.id in synsets else named.get(target.identifier)
        if sid is None:
            left["the synset is not in the lexicon"] += n
        elif (sid, lemma) not in senses:
            left["the word is not in the synset"] += n
        else:
            found[(sid, lemma)] += n
    return found, left


def records(found: Counter[tuple[str, str]], items: list[Item],
            first: int, date: str) -> list[changes.Change]:
    """The change records for the counts that are not there yet.

    Args:
        found: how often each (synset, lemma) is tagged
        items: the lexicon
        first: the number of the first record's id
        date: the date of the records

    Returns:
        One ``set_count`` record for each count that differs
    """
    have = {(str(s.synset), str(e.lemma)): c.text
            for e in items if isinstance(e, Entry) for s in e.senses
            for c in s.counts if c.meta.get("dc:source") == CORPUS}
    base = f"{release.WN_ID}-{release.BASE_VERSION}"
    todo = sorted((key, n) for key, n in found.items() if have.get(key) != str(n))
    return [changes.Change(id=f"{base}-{first + i}", action="set_count", lexicon=release.WN_ID,
                           synset=synset, lemma=lemma, new=str(n), corpus=CORPUS, user=USER,
                           date=date, source=SOURCE, reason=REASON, base=base)
            for i, ((synset, lemma), n) in enumerate(todo)]


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("db", type=Path, help="the NTU-MC Czech corpus database (ces.db)")
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
    found, left = counts(tagged(args.db), items)
    made = records(found, items, len(log_records) + 1, datetime.date.today().isoformat())
    log.info("%d senses tagged %d times; %d records to add",
             len(found), sum(found.values()), len(made))
    for why, n in sorted(left.items()):
        log.info("%d tags left out: %s", n, why)
    if not args.write:
        return
    with release.CHANGES.open("a", encoding="utf-8") as f:
        for record in made:
            f.write(changes.dumps(record) + "\n")
    log.info("Added %d records to %s", len(made), release.CHANGES)


if __name__ == "__main__":
    main()
