#!/usr/bin/env python3
"""Link the synsets the changes added to the rest, as Princeton WordNet links them.

    uv run scripts/princeton_links.py            # say what would be added
    uv run scripts/princeton_links.py --write    # add the records to the log
    uv run scripts/princeton_links.py --all      # for every synset, not only the new

A synset added for a Princeton concept (changes/README.md) comes with
its ILI and no relations.  This finds, in Princeton WordNet 3.0, each
relation between such a concept and another concept the Czech WordNet
has, and adds it as an ``add_relation`` record at the end of the change
log.  A relation that is already there is left alone, so the script can
be run again after more synsets are added.  With ``--all`` it does the
same for every synset that has an ILI.

The relations are written the way release 2.1 has them:

* one way only for hypernym, holonym and domain (``hypernym`` on the
  narrower synset, ``holo_part`` on the part, ``domain_topic`` on the
  member), so a Princeton ``hyponym`` becomes the other synset's
  ``hypernym``;
* antonymy between synsets, though Princeton has it between words;
* Princeton's ``entails`` as ``subevent``, as 2.1 has it;
* nothing for derivation and pertainym: they hold between English words;
* nothing for usage (``exemplifies``): that an English word is colloquial
  or archaic says nothing about the Czech one;
* nothing for region (``domain_region``).  BE CAREFUL with these: the
  link is right for the Princeton concept (a *publican* is British, a
  *deputy* French), but a Czech synset on that ILI often has a general
  word (*hostinský*, *poslanec*), and the region would be wrong for it.
  A region link needs a person to look at the Czech words.

A synset that has a hypernym keeps it: where Princeton gives it
another, that is counted and not added.

Princeton WordNet is read with wn (``omw-en:1.4``, which must be
downloaded: ``uv run python -m wn download omw-en:1.4``).
"""

import argparse
import datetime
import logging
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

from ntumc.wordnet import changes, lmf  # noqa: E402
from ntumc.wordnet.model import Item, Synset  # noqa: E402

import release  # noqa: E402

PRINCETON = "omw-en:1.4"
SOURCE = "Princeton WordNet 3.0 (omw-en 1.4)"
REASON = "the two concepts are related so in Princeton WordNet"
USER = "fcbond"

# Princeton relation -> the relation here, from the same synset
KEEP = {"hypernym", "instance_hypernym", "holo_part", "holo_member", "holo_substance",
        "antonym", "similar", "also", "attribute", "causes", "subevent", "domain_topic"}
# Princeton relation -> what 2.1 calls it
RENAME = {"entails": "subevent"}
# Princeton relation -> the relation here, from the other synset
TURN = {"hyponym": "hypernym", "instance_hyponym": "instance_hypernym",
        "mero_part": "holo_part", "mero_member": "holo_member",
        "mero_substance": "holo_substance", "has_domain_topic": "domain_topic"}
# relations Princeton has between words that 2.1 has between synsets
FROM_SENSES = {"antonym", "also", "similar"}

Triple = tuple[str, str, str]

log = logging.getLogger("princeton_links")


def princeton() -> Iterator[Triple]:
    """Yield the relations of Princeton WordNet 3.0 between concepts.

    Yields:
        The ILI of a synset, the relation, and the ILI of the other synset
    """
    import wn  # here, so that the rest can be used without it

    for synset in wn.Wordnet(PRINCETON).synsets():
        if not synset.ili:
            continue
        for link, targets in synset.relations().items():
            for target in targets:
                if target.ili:
                    yield synset.ili, link, target.ili
        for sense in synset.senses():
            for link, targets in sense.relations().items():
                if link in FROM_SENSES:
                    for target in targets:
                        if target.synset().ili:
                            yield synset.ili, link, target.synset().ili


HYPERNYMS = {"hypernym", "instance_hypernym"}


def links(relations: Iterable[Triple], items: Iterable[Item],
          new: set[str]) -> tuple[list[Triple], list[Triple]]:
    """The relations to add: those that touch a new synset and are not there.

    A concept that several synsets here stand for is not linked: which
    of them is meant is not known.

    Args:
        relations: ILI, Princeton relation, ILI
        items: the lexicon
        new: the ids of the synsets to link

    Returns:
        The relations to add, and the hypernyms left out because the
        synset has a hypernym already; each is synset, relation and
        target as this lexicon writes them, sorted
    """
    by_ili: dict[str, list[Synset]] = defaultdict(list)
    for item in items:
        if isinstance(item, Synset) and item.ili:
            by_ili[str(item.ili)].append(item)
    found: set[Triple] = set()
    left: set[Triple] = set()
    hyponyms = {str(i.id) for i in items if isinstance(i, Synset)
                and any(r.link in HYPERNYMS for r in i.relations)}
    for a, link, b in relations:
        link = RENAME.get(link, link)
        if link in TURN:
            a, link, b = b, TURN[link], a
        elif link not in KEEP:
            continue
        if len(by_ili.get(a, ())) != 1 or len(by_ili.get(b, ())) != 1 or a == b:
            continue
        source, target = by_ili[a][0], by_ili[b][0]
        if not {str(source.id), str(target.id)} & new:
            continue
        if any(r.link == link and r.target == target.id for r in source.relations):
            continue
        triple = (str(source.id), link, str(target.id))
        if link in HYPERNYMS and source.id in hyponyms:
            left.add(triple)
        else:
            found.add(triple)
    return sorted(found), sorted(left)


def records(found: list[Triple], first: int, date: str) -> list[changes.Change]:
    """The change records for the relations.

    Args:
        found: synset, relation and target
        first: the number of the first record's id
        date: the date of the records

    Returns:
        One ``add_relation`` record for each
    """
    base = f"{release.WN_ID}-{release.BASE_VERSION}"
    return [changes.Change(id=f"{base}-{first + n}", action="add_relation",
                           lexicon=release.WN_ID, synset=synset, link=link, target=target,
                           user=USER, date=date, source=SOURCE, reason=REASON, base=base)
            for n, (synset, link, target) in enumerate(found)]


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="add the records to the change log")
    parser.add_argument("--all", action="store_true",
                        help="link every synset that has an ILI, not only the new ones")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    release.fetch_base()
    old = {str(i.id) for i in lmf.read(release.BASE) if isinstance(i, Synset)}
    log_records = list(changes.read(release.CHANGES))
    items, conflicts = changes.apply(list(lmf.read(release.BASE)), log_records)
    if conflicts:
        for line in conflicts:
            log.error(line)
        sys.exit(1)
    new = {str(i.id) for i in items
           if isinstance(i, Synset) and i.ili and (args.all or i.id not in old)}
    found, left = links(princeton(), items, new)
    log.info("%d hypernyms not added: the synset has a hypernym", len(left))
    linked = {s for s, _, t in found for s in (s, t)} & new
    log.info("%d relations for %d of the %d synsets%s",
             len(found), len(linked), len(new),
             "" if args.all else " added for Princeton concepts")
    if not args.write:
        for synset, link, target in found:
            sys.stdout.write(f"{synset}\t{link}\t{target}\n")
        return
    made = records(found, len(log_records) + 1, datetime.date.today().isoformat())
    with release.CHANGES.open("a", encoding="utf-8") as f:
        for record in made:
            f.write(changes.dumps(record) + "\n")
    log.info("Added %d records to %s", len(made), release.CHANGES)


if __name__ == "__main__":
    main()
