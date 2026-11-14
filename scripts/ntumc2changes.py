#!/usr/bin/env python3
"""One-off: the Czech additions made in NTU-MC, as change records against 2.1.

    uv run scripts/ntumc2changes.py NTUMC.db

Reads the NTU-MC wordnet database frozen on 2026-11-13 and writes
changes/wncze-2.1.jsonl and changes/review-2.1.tsv (what could not be
turned into a record, with the reason).  It refuses to run if the change
file already has records.  See changes/README.md for what it makes.

The database names concepts by Princeton WordNet 3.0 offsets; the Czech
WordNet by 2.0 offsets.  A database synset is found here through its ILI.
Where the Czech WordNet has no synset for the concept, one is added:

    wncze-02001223-n         the 2.0 offset, where 2.0 has the concept
    wncze-ENG30-04489008-n   the 3.0 offset, where it does not
    wncze-NTUMC-80002448-a   a concept that is only in NTU-MC, with its
                             omw-ntumc or omw-pronoun dc:identifier

Needs checkouts of NTUMC, cili, omw-ntumc and omw-pronoun beside this one.
"""

import argparse
import csv
import logging
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

from ntumc.wordnet import changes, lmf  # noqa: E402
from ntumc.wordnet.model import Entry, Synset  # noqa: E402

WN_ID = "wncze"
BASE = "wncze-2.1"
BASE_XML = ROOT / "build" / "base" / f"{BASE}.xml"
CHANGES = ROOT / "changes" / f"{BASE}.jsonl"
REVIEW = ROOT / "changes" / "review-2.1.tsv"
HELD = ROOT / "changes" / "held-2.1.tsv"
ADDITIONS = ROOT / "additions" / "2025-04"
MAP30 = ROOT.parent / "cili" / "ili-map-pwn30.tab"
MAP20 = ROOT.parent / "cili" / "older-wn-mappings" / "ili-map-pwn20.tab"
REGISTRY = ROOT.parent / "omw-ntumc" / "registry.tsv"
PRONOUNS = ROOT.parent / "omw-pronoun" / "data" / "ntumc-pronouns.tsv"

FROZEN = "NTU-MC wordnet database, frozen 2026-11-13"
POS = set("nvarscpxu")
POS20 = {"r": "b", "s": "a"}  # how the Czech WordNet writes a 2.0 part of speech

# additions/2025-04/pronouns.tab: the Czech definition of each pronoun whose
# concept NTU-MC has, by its place among the definitions (0 is the first)
PRONOUN_DEFINITIONS = {0: "77000015-n", 1: "77000021-n", 2: "77000046-n", 3: "77000041-n",
                       4: "77000053-n", 6: "77000002-n", 7: "77000019-n"}
# Czech "definitions" in the database that are not definitions
NOT_DEFINITIONS = {"80001788-v": "in English", "77000104-n": "an example, not a definition",
                   "02794670-a": "a note, not a definition"}

log = logging.getLogger("ntumc2changes")


@dataclass
class Target:
    """The Czech WordNet synset for a database synset.

    Attributes:
        id: the synset's id here
        pos: its part of speech, if it has to be made
        ili: its ILI, if it has to be made
        identifier: the concept's id in omw-ntumc or omw-pronoun, if it has one
    """

    id: str
    pos: str = ""
    ili: str = ""
    identifier: str = ""


@dataclass
class Maps:
    """What is needed to find a database synset in the Czech WordNet.

    Attributes:
        ili30: Princeton 3.0 synset -> ILI
        pwn20: ILI -> the 2.0 synset the map is surest of
        concepts: NTU-MC synset -> (omw-ntumc id, part of speech)
        pronouns: NTU-MC synset -> (omw-pronoun code, part of speech)
        by_ili: ILI -> the synsets of the base that have it
    """

    ili30: dict[str, str] = field(default_factory=dict)
    pwn20: dict[str, str] = field(default_factory=dict)
    concepts: dict[str, tuple[str, str]] = field(default_factory=dict)
    pronouns: dict[str, tuple[str, str]] = field(default_factory=dict)
    by_ili: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))


def _tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def load_maps(synsets: dict[str, Synset]) -> Maps:
    """Read the ILI maps and the two concept registries.

    Args:
        synsets: the synsets of the base, by id

    Returns:
        The maps
    """
    maps = Maps()
    with MAP30.open(encoding="utf-8") as f:
        for line in f:
            ili, synset = line.split()[:2]
            maps.ili30[synset] = ili
    surest: dict[str, float] = {}
    with MAP20.open(encoding="utf-8") as f:
        for line in f:
            ili, synset, sure = line.split()[:3]
            if float(sure) > surest.get(ili, 0.0):
                surest[ili] = float(sure)
                maps.pwn20[ili] = synset
    for row in _tsv(REGISTRY):
        if row["ntumc_synset"] and row["status"] != "withdrawn":
            maps.concepts[row["ntumc_synset"]] = (row["local_id"], row["pos"])
    for row in _tsv(PRONOUNS):
        if row["code"]:
            maps.pronouns[row["synset"]] = (f"pronoun:{row['code']}", row["pos"])
    for sid, synset in synsets.items():
        if synset.ili:
            maps.by_ili[str(synset.ili)].append(sid)
    return maps


def target(synset: str, maps: Maps, synsets: dict[str, Synset]) -> Target | str:
    """The Czech WordNet synset for a database synset.

    Args:
        synset: the id in the NTU-MC database (``07712063-n``, ``80002448-a``)
        maps: the ILI maps and registries
        synsets: the synsets of the base, by id

    Returns:
        The target, or why there is none
    """
    identifier = maps.pronouns.get(synset, ("", ""))[0]
    offset, pos = synset.split("-")
    ili = maps.ili30.get(synset) or (maps.ili30.get(f"{offset}-s") if pos == "a" else None)
    if ili is None:
        concept = maps.pronouns.get(synset) or maps.concepts.get(synset)
        if concept is None:
            return "the concept is not in CILI, omw-ntumc or omw-pronoun"
        return Target(f"{WN_ID}-NTUMC-{synset}", concept[1], "", concept[0])
    old = maps.pwn20.get(ili)
    short = f"{old[:-1]}{POS20.get(old[-1], old[-1])}" if old else None
    here = maps.by_ili.get(ili, [])
    if len(here) > 1:
        if f"{WN_ID}-{short}" not in here:
            return f"{len(here)} synsets have its ILI ({ili}): {' '.join(here)}"
        here = [f"{WN_ID}-{short}"]
    if here:
        return Target(here[0], identifier=identifier)
    if short and f"{WN_ID}-{short}" in synsets:  # there, but without this ILI
        return f"{WN_ID}-{short} is its 2.0 synset but has ILI {synsets[f'{WN_ID}-{short}'].ili!r}"
    new = f"{WN_ID}-{short}" if short else f"{WN_ID}-ENG30-{synset}"
    return Target(new, "a" if pos == "s" else pos, ili, identifier)


def from_files() -> dict[tuple[str, str], str]:
    """The (synset, lemma) pairs of additions/2025-04 and the file each is in."""
    out = {}
    for name in ("arasaac.tab", "pronouns-quick.tab"):
        with (ADDITIONS / name).open(encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) == 3 and parts[1] == "ces:lemma" and not parts[0].startswith("#"):
                    out[(parts[0], parts[2])] = name
    return out


def pronoun_definitions() -> list[tuple[str, str]]:
    """The Czech definitions of additions/2025-04/pronouns.tab that have a concept.

    Returns:
        (NTU-MC synset, Czech definition)
    """
    with (ADDITIONS / "pronouns.tab").open(encoding="utf-8") as f:
        czech = [line[2:].strip() for line in f if line.startswith("- ")]
    return [(synset, czech[n]) for n, synset in PRONOUN_DEFINITIONS.items()]


class Writer:
    """Collects the change records and what is left for review."""

    def __init__(self, base: list, maps: Maps) -> None:
        self.synsets = {str(i.id): i for i in base if isinstance(i, Synset)}
        self.maps = maps
        self.senses = {(str(s.synset), str(e.lemma))
                       for e in base if isinstance(e, Entry) for s in e.senses}
        self.identified = {sid for sid, s in self.synsets.items() if s.meta.get("dc:identifier")}
        self.made: set[str] = set()
        self.records: list[changes.Change] = []
        self.review: list[tuple[str, ...]] = []

    def add(self, action: str, who: tuple[str, str, str, str], **fields: str | None) -> None:
        """Append one record.

        Args:
            action: the action
            who: user, date, source, reason
            **fields: the action's own fields
        """
        user, date, source, reason = who
        self.records.append(changes.Change(
            id=f"{BASE}-{len(self.records) + 1}", action=action, lexicon=WN_ID, base=BASE,
            user=user, date=date or None, source=source, reason=reason, **fields))

    def synset(self, synset: str, who: tuple[str, str, str, str]) -> str | None:
        """The Czech WordNet synset for a database synset, made if need be.

        Args:
            synset: the id in the NTU-MC database
            who: user, date, source, reason of what needs the synset

        Returns:
            The synset's id, or None if there is none (the reason goes to review)
        """
        found = target(synset, self.maps, self.synsets)
        if isinstance(found, str):
            self.problem = found
            return None
        if found.id not in self.synsets and found.id not in self.made:
            self.made.add(found.id)
            concept = "its concept is in " + (
                "omw-pronoun" if found.identifier.startswith("pronoun:")
                else "omw-ntumc" if found.identifier else "Princeton WordNet 3.0")
            self.add("add_synset", (who[0], who[1], FROZEN, f"for a Czech word; {concept}"),
                     synset=found.id, pos=found.pos, new="", ili=found.ili or None,
                     identifier=found.identifier or None)
            self.identified.add(found.id)
        elif found.identifier and found.id not in self.identified:
            self.identified.add(found.id)
            self.add("set_identifier", ("fcbond", "2026-11-14",
                                        "omw-pronoun: data/ntumc-pronouns.tsv gives the NTU-MC "
                                        f"synset {synset} this concept",
                                        "names the concept across lexicons"),
                     synset=found.id, old="", new=found.identifier)
        return found.id

    def has(self, synset: str) -> bool:
        """Whether the synset is in the base or has been added."""
        return synset in self.synsets or synset in self.made


def inserted(con: sqlite3.Connection) -> dict[tuple[str, int], tuple[str, str]]:
    """Who first put each Czech sense in the database, and when.

    Returns:
        (synset, wordid) -> (user, date)
    """
    out: dict[tuple[str, int], tuple[str, str]] = {}
    rows = con.execute(
        "SELECT synset_new, wordid_new, usr_new, date_update FROM sense_log "
        "WHERE lang_new = 'ces' AND synset_old IS NULL ORDER BY date_update")
    for synset, wordid, usr, date in rows:
        out.setdefault((synset, wordid), (usr or "", date[:10]))
    return out


def corrections(con: sqlite3.Connection, w: Writer) -> set[tuple[str, str]]:
    """Records for the released senses that annotators renamed or removed.

    Args:
        con: the NTU-MC database
        w: the writer

    Returns:
        The (database synset, lemma) pairs a rename accounts for
    """
    now = {(s, lemma) for s, lemma in con.execute(
        "SELECT s.synset, w.lemma FROM sense s JOIN word w USING (wordid) WHERE s.lang = 'ces'")}
    rows = con.execute(
        "SELECT l.synset_old, l.synset_new, wo.lemma, wn.lemma, l.usr_new, l.usr_old, "
        "l.date_update FROM sense_log l LEFT JOIN word wo ON wo.wordid = l.wordid_old "
        "LEFT JOIN word wn ON wn.wordid = l.wordid_new "
        "WHERE l.lang_old = 'ces' AND l.src_old = 'wncz' ORDER BY l.date_update").fetchall()
    renamed: set[tuple[str, str]] = set()
    for synset, synset_new, old, new, usr_new, usr_old, date in rows:
        user = usr_new or usr_old
        who = (user, date[:10], f"{FROZEN}: annotator {user}", "")
        if synset_new == synset and new != old and (synset, new) in now:
            action, reason, extra = "rename_lemma", "corrected in NTU-MC", {"new": new}
        elif synset_new is None and (synset, old) not in now:
            action, reason, extra = "remove_sense", "removed in NTU-MC", {}
        else:
            continue
        here = w.synset(synset, who)
        if here is None or (here, old) not in w.senses:
            w.review.append((action, synset, old, new or "", user,
                             w.problem if here is None else "the release has no such sense"))
            continue
        w.add(action, (*who[:3], reason), synset=here, lemma=old, **extra)
        w.senses.discard((here, old))
        if action == "rename_lemma":
            w.senses.add((here, new))
            renamed.add((synset, new))
    return renamed


def additions(con: sqlite3.Connection, w: Writer, skip: set[tuple[str, str]]) -> None:
    """Records for the Czech senses that were added in NTU-MC.

    Args:
        con: the NTU-MC database
        w: the writer
        skip: (database synset, lemma) pairs already accounted for
    """
    first = inserted(con)
    files = from_files()
    rows = con.execute(
        "SELECT s.synset, s.wordid, w.lemma, w.pos, s.src, s.usr FROM sense s "
        "JOIN word w USING (wordid) WHERE s.lang = 'ces' AND s.src != 'wncz'").fetchall()
    rows.sort(key=lambda r: (first.get((r[0], r[1]), ("", "9"))[1], r[0], r[2]))
    for synset, wordid, lemma, pos, src, usr in rows:
        if (synset, lemma) in skip:
            continue
        user, date = first.get((synset, wordid), (usr, ""))
        name = files.get((synset, lemma))
        if name == "arasaac.tab":
            who = ("fcbond", date, f"additions/2025-04/{name}: word and synset pairs from "
                   "ARASAAC, made by Francis Bond, checked by Kateřina Daňková",
                   "missing word, found while annotating")
        elif name:
            who = ("fcbond", date, f"additions/2025-04/{name}: by Francis Bond",
                   "missing pronoun, found while annotating")
        elif src == "sem":
            who = (user, date, f"{FROZEN}: loaded in 2025-04 with the additions of "
                   "additions/2025-04 (src sem), but not in its files",
                   "missing word, found while annotating")
        else:
            who = (user, date, f"{FROZEN}: annotator {user}", "added in NTU-MC by an annotator")
        if "(" in lemma or "\n" in lemma:
            w.review.append(("add_sense", synset, lemma, "", user, "the lemma holds a comment"))
            continue
        here = w.synset(synset, who)
        if here is None:
            w.review.append(("add_sense", synset, lemma, "", user, w.problem))
        elif (here, lemma) in w.senses:
            w.review.append(("add_sense", synset, lemma, "", user,
                             f"no record needed: already in {here}"))
        else:
            w.senses.add((here, lemma))
            w.add("add_sense", who, synset=here, lemma=lemma,
                  pos=pos if pos in POS else None)


def texts(con: sqlite3.Connection, w: Writer) -> None:
    """Records for the Czech definitions and examples.

    Args:
        con: the NTU-MC database
        w: the writer
    """
    source = ("additions/2025-04/pronouns.tab: by Francis Bond, checked and improved "
              "by Kateřina Daňková")
    rows = [(s, "fcbond", d, source) for s, d in pronoun_definitions()]
    rows += [(s, usr, d, f"{FROZEN}: annotator {usr}") for s, usr, d in con.execute(
        "SELECT synset, usr, def FROM synset_def WHERE lang = 'ces' ORDER BY synset")]
    for synset, user, text, src in rows:
        found = target(synset, w.maps, w.synsets)
        here = found.id if isinstance(found, Target) else None
        if synset in NOT_DEFINITIONS and src.startswith(FROZEN):
            problem = NOT_DEFINITIONS[synset]
        elif here is None or not w.has(here):
            problem = "no Czech word was added for the concept"
        elif here in w.synsets and w.synsets[here].definitions:
            problem = f"{here} has a definition"
        else:
            w.add("set_definition", (user, "2025-04-06" if user == "fcbond" else "", src,
                                     "Czech definition"), synset=here, new=text.strip())
            continue
        w.review.append(("set_definition", synset, " ".join(text.split()), "", user, problem))
    seen: set[tuple[str, str]] = set()
    for synset, user, text in con.execute(
            "SELECT synset, usr, def FROM synset_ex WHERE lang = 'ces' ORDER BY synset, sid"):
        found = target(synset, w.maps, w.synsets)
        here = found.id if isinstance(found, Target) else None
        if "\n" in text:
            problem = "the example holds a comment"
        elif here is None or not w.has(here):
            problem = "no Czech word was added for the concept"
        elif (here, text.strip()) in seen or any(
                x.text == text.strip() for x in getattr(w.synsets.get(here), "examples", [])):
            problem = "no record needed: the synset has this example"
        else:
            seen.add((here, text.strip()))
            w.add("add_example", (user, "", f"{FROZEN}: annotator {user}", "Czech example"),
                  synset=here, new=text.strip())
            continue
        w.review.append(("add_example", synset, " / ".join(text.split()), "", user, problem))


def hold(records: list[changes.Change]) -> list[changes.Change]:
    """Take out the records that are held for a person, and what hangs on them.

    Two reviewers read every record that has Czech in it; a record that
    either of them questioned is in changes/held-2.1.tsv until a person
    has ruled ``add`` in its ``ruling`` column.  A synset that is left
    without a word is not added, and its definition and examples wait
    with it.

    Args:
        records: all the records

    Returns:
        The records that go in the log, numbered again
    """
    if not HELD.exists():
        return records
    held = {(r["action"], r["synset"], r["lemma"], r["text"]) for r in _tsv(HELD)
            if r["ruling"] != "add"}
    kept = [c for c in records
            if (c.action, c.synset, c.lemma or "", (c.new or "") if c.lemma is None else "")
            not in held and not (c.action == "rename_lemma"
                                 and (c.action, c.synset, c.lemma, "") in held)]
    worded = {c.synset for c in kept if c.action == "add_sense"}
    empty = {c.synset for c in kept if c.action == "add_synset"} - worded
    out = [c for c in kept if c.synset not in empty]
    for k, c in enumerate(out, 1):
        c.id = f"{BASE}-{k}"
    log.info("%d records held for a person; %d more wait for their synset",
             len(records) - len(kept), len(kept) - len(out))
    return out


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("db", type=Path, help="the frozen NTU-MC wordnet database")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if CHANGES.exists() and CHANGES.stat().st_size:
        log.error("%s already has records: this script made the first ones", CHANGES)
        sys.exit(1)
    base = list(lmf.read(BASE_XML))
    synsets = {str(i.id): i for i in base if isinstance(i, Synset)}
    w = Writer(base, load_maps(synsets))
    con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    additions(con, w, corrections(con, w))
    texts(con, w)
    records = hold(w.records)
    changes.write(CHANGES, records)
    with REVIEW.open("w", encoding="utf-8", newline="") as f:
        out = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None)
        out.writerow(("action", "ntumc_synset", "text", "new", "user", "why_no_record"))
        out.writerows(w.review)
    log.info("Wrote %d records to %s and %d lines to %s",
             len(records), CHANGES, len(w.review), REVIEW)


if __name__ == "__main__":
    main()
