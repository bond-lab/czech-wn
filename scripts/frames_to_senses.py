#!/usr/bin/env python3
"""Put each verb frame on the verbs it names, as change records.

    uv run scripts/frames_to_senses.py            # say what would change
    uv run scripts/frames_to_senses.py --write    # add the records to the log

The source has the frames on the synset, so in 2.1 every verb of a
synset names all its frames.  Many frames begin with the verbs they are
for (``{podplatit, koupit si} kdo1*AG...``).  Where at least one of
those verbs is in the synset, the frame stays on them and is taken off
the synset's other verbs.  A frame that names no verb, or only verbs
that are not in the synset, stays on all of them.  See
notes/verb-frames.md.

A ``set_frames`` record is written for each sense whose frames change;
one that is already right is left alone, so the script can be run again.
"""

import argparse
import datetime
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

from ntumc.wordnet import changes, lmf  # noqa: E402
from ntumc.wordnet.model import Entry, Frame, Item  # noqa: E402

import release  # noqa: E402

SOURCE = "wncze21.xml (DEBVisDic): the verbs the frame names (scripts/frames_to_senses.py)"
REASON = "the frames of the synset that are for this verb"
USER = "fcbond"
VERBS = re.compile(r"\??\s*(?:fig\s*)?#?\{([^}]*)\}")

log = logging.getLogger("frames_to_senses")


def named(frame: str) -> list[str]:
    """The verbs a frame says it is for.

    Args:
        frame: the text of the frame

    Returns:
        The verbs in braces at its start; empty if there are none
    """
    m = VERBS.match(frame)
    return [v.strip() for v in m.group(1).split(",") if v.strip()] if m else []


def placed(items: list[Item]) -> dict[tuple[str, str], tuple[str, str]]:
    """The frames each sense should name, where that differs from now.

    Args:
        items: the lexicon

    Returns:
        (synset, lemma) -> the sense's frames now and as they should be,
        each as frame ids with spaces between
    """
    frames = {str(f.id): str(f.frame) for f in items if isinstance(f, Frame)}
    senses: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for entry in items:
        if isinstance(entry, Entry):
            for sense in entry.senses:
                if sense.subcat:
                    senses[str(sense.synset)][str(entry.lemma)] = str(sense.subcat).split()
    out: dict[tuple[str, str], tuple[str, str]] = {}
    for synset, by_lemma in senses.items():
        for lemma, now in by_lemma.items():
            keep = []
            for frame in now:
                verbs = [v for v in named(frames[frame]) if v in by_lemma]
                if not verbs or lemma in verbs:
                    keep.append(frame)
            if keep != now:
                out[(synset, lemma)] = (" ".join(now), " ".join(keep))
    return out


def records(todo: dict[tuple[str, str], tuple[str, str]],
            first: int, date: str) -> list[changes.Change]:
    """The change records for the senses whose frames change.

    Args:
        todo: (synset, lemma) -> the frames now and as they should be
        first: the number of the first record's id
        date: the date of the records

    Returns:
        One ``set_frames`` record for each
    """
    base = f"{release.WN_ID}-{release.BASE_VERSION}"
    return [changes.Change(id=f"{base}-{first + i}", action="set_frames", lexicon=release.WN_ID,
                           synset=synset, lemma=lemma, old=old, new=new, user=USER, date=date,
                           source=SOURCE, reason=REASON, base=base)
            for i, ((synset, lemma), (old, new)) in enumerate(sorted(todo.items()))]


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
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
    todo = placed(items)
    made = records(todo, len(log_records) + 1, datetime.date.today().isoformat())
    log.info("%d senses in %d synsets change their frames; %d are left with none",
             len(made), len({s for s, _ in todo}), sum(not new for _, new in todo.values()))
    if not args.write:
        return
    with release.CHANGES.open("a", encoding="utf-8") as f:
        for record in made:
            f.write(changes.dumps(record) + "\n")
    log.info("Added %d records to %s", len(made), release.CHANGES)


if __name__ == "__main__":
    main()
