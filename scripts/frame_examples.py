#!/usr/bin/env python3
"""Make the examples in the verb frames examples of their synsets, as change records.

    uv run scripts/frame_examples.py            # say what would be added
    uv run scripts/frame_examples.py --write    # add the records to the log

A verb frame ends with examples, after ``%`` (notes/verb-frames.md):

    kdo1*AG(person:1)=co4*ANY(anything:1) %zhodnotit její výkon

Each becomes an ``Example`` of the synset whose verbs name the frame.
The text after a ``%`` is kept whole: it is often several variants with
commas between (``dívali se na film, na televizi``), and cannot be cut
safely.  Left out are the examples of a frame that names only verbs
that are not in the synset, since they show another verb, and an
example the synset already has, so the script can be run again.  The
frame keeps its text.
"""

import argparse
import datetime
import logging
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

from frames_to_senses import named  # noqa: E402
from ntumc.wordnet import changes, lmf  # noqa: E402
from ntumc.wordnet.model import Entry, Frame, Item, Synset  # noqa: E402

import release  # noqa: E402

SOURCE = "wncze21.xml (DEBVisDic): the example in verb frame {} (scripts/frame_examples.py)"
REASON = "the example of a verb frame of the synset"
USER = "fcbond"

log = logging.getLogger("frame_examples")


def examples(frame: str) -> list[str]:
    """The examples at the end of a frame.

    Args:
        frame: the text of the frame

    Returns:
        The text after each ``%``, whole
    """
    return [text.strip(" ,") for text in frame.split("%")[1:] if text.strip(" ,")]


def found(items: list[Item]) -> tuple[list[tuple[str, str, str]], int]:
    """The examples to add.

    Args:
        items: the lexicon

    Returns:
        (synset, frame id, example) for each example to add, in the
        order of the synsets and their frames, and how many were left
        out because their frame names only verbs that are not in the
        synset
    """
    frames = {str(f.id): str(f.frame) for f in items if isinstance(f, Frame)}
    have = {str(s.id): {str(e.text) for e in s.examples}
            for s in items if isinstance(s, Synset)}
    verbs: dict[str, set[str]] = defaultdict(set)
    named_by: dict[str, list[str]] = defaultdict(list)
    for entry in items:
        if isinstance(entry, Entry):
            for sense in entry.senses:
                verbs[str(sense.synset)].add(str(entry.lemma))
                for frame in str(sense.subcat or "").split():
                    if frame not in named_by[str(sense.synset)]:
                        named_by[str(sense.synset)].append(frame)
    out: list[tuple[str, str, str]] = []
    left = 0
    for synset in sorted(named_by):
        for frame in named_by[synset]:
            names = named(frames[frame])
            for text in examples(frames[frame]):
                if names and not verbs[synset] & set(names):
                    left += 1
                elif text not in have[synset]:
                    have[synset].add(text)
                    out.append((synset, frame, text))
    return out, left


def records(todo: list[tuple[str, str, str]], first: int, date: str) -> list[changes.Change]:
    """The change records for the examples.

    Args:
        todo: (synset, frame id, example)
        first: the number of the first record's id
        date: the date of the records

    Returns:
        One ``add_example`` record for each
    """
    base = f"{release.WN_ID}-{release.BASE_VERSION}"
    return [changes.Change(id=f"{base}-{first + i}", action="add_example", lexicon=release.WN_ID,
                           synset=synset, new=text, user=USER, date=date,
                           source=SOURCE.format(frame), reason=REASON, base=base)
            for i, (synset, frame, text) in enumerate(todo)]


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
    todo, left = found(items)
    made = records(todo, len(log_records) + 1, datetime.date.today().isoformat())
    log.info("%d examples for %d synsets; %d left out (their frame names other verbs)",
             len(made), len({s for s, _, _ in todo}), left)
    if not args.write:
        return
    with release.CHANGES.open("a", encoding="utf-8") as f:
        for record in made:
            f.write(changes.dumps(record) + "\n")
    log.info("Added %d records to %s", len(made), release.CHANGES)


if __name__ == "__main__":
    main()
