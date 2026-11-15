#!/usr/bin/env python3
"""Load the Czech WordNet into wn with the reverse relations added.

    uv run --with wn notes/reverse_relations.py release/wncze-2.2.xml

The Czech WordNet records a relation one way only: a synset has its
hypernym, but the hypernym does not list its hyponyms.  wn stores what
the file says, so ``synset.hyponyms()`` would find nothing.  This reads
the file, adds the reverse of each relation between synsets that has
one (hypernym -> hyponym, holo_part -> mero_part, ...), and puts the
result in wn's database.
"""

import sys

import wn
from wn import lmf
from wn.constants import REVERSE_RELATIONS


def add_reverse_relations(lexicon: lmf.Lexicon) -> int:
    """Add the missing reverse of each relation between synsets.

    Args:
        lexicon: a lexicon as wn.lmf.load reads it; changed in place

    Returns:
        How many relations were added
    """
    synsets = {synset["id"]: synset for synset in lexicon["synsets"]}
    have = {(synset["id"], relation["relType"], relation["target"])
            for synset in synsets.values() for relation in synset.get("relations", [])}
    added = 0
    for source, kind, target in sorted(have):
        reverse = REVERSE_RELATIONS.get(kind)
        if reverse and target in synsets and (target, reverse, source) not in have:
            synsets[target].setdefault("relations", []).append(
                {"target": source, "relType": reverse})
            have.add((target, reverse, source))
            added += 1
    return added


def main() -> None:
    """Entry point."""
    resource = lmf.load(sys.argv[1])
    for lexicon in resource["lexicons"]:
        added = add_reverse_relations(lexicon)
        print(f"{lexicon['id']}:{lexicon['version']}: {added} reverse relations added")
    wn.add_lexical_resource(resource)

    dog = wn.synsets("pes", lexicon="wncze")[0]
    canine = dog.hypernyms()[0]
    print(canine.lemmas(), "has the hyponyms",
          [hyponym.lemmas()[0] for hyponym in canine.hyponyms()])


if __name__ == "__main__":
    main()
