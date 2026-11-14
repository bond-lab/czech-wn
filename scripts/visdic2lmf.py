#!/usr/bin/env python3
"""Convert the Czech WordNet from DEBVisDic XML to WN-LMF, losing nothing.

    uv run scripts/visdic2lmf.py sources/wncze21.xml.zip --package

Writes release/wncze-2.1.xml and, with --package, release/wncze-2.1.tar.xz
(the XML with README.md, LICENSE and citation.bib, as the wn module
wants it).

Every field of the source has a place in the output (the table is in
README.md).  After converting, the source is rebuilt from the output and
compared with the original, fact by fact; the script fails if anything
differs.  Only three things are not carried over, and they are counted:
elements and attributes with no content, white space around a value,
and the WORD elements, which repeat the words of the literals.

Uses ntumc.wordnet from a checkout of NTU-MC beside this one (../NTUMC)
and the CILI map for Princeton WordNet 2.0 from a checkout of cili
(../cili/older-wn-mappings/ili-map-pwn20.tab).
"""

import argparse
import logging
import re
import shutil
import sys
import tarfile
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / "NTUMC"))

from ntumc.wordnet import lmf  # noqa: E402
from ntumc.wordnet.model import (  # noqa: E402
    Entry,
    Frame,
    Item,
    Lexicon,
    Relation,
    Sense,
    Synset,
    Text,
)

ILI_MAP = ROOT.parent / "cili" / "older-wn-mappings" / "ili-map-pwn20.tab"
DC = "https://globalwordnet.github.io/schemas/dc/"
CITATION = (
    "Adam Rambousek, Karel Pala and Sandra Tukačová. 2017. Overview and Future of "
    "Czech Wordnet. In LDK Workshops: OntoLex, TIAD and Challenges for Wordnets, "
    "pages 146-151. Galway, Ireland: CEUR-WS.org."
)

# DEBVisDic part of speech -> WN-LMF
POS = {"n": "n", "v": "v", "a": "a", "b": "r"}
POS_BACK = {v: k for k, v in POS.items()}

# DEBVisDic relation -> WN-LMF relation.  A relation that is not here is
# written as relType="other" with its own name in dc:type.
RELATIONS = {
    "hypernym": "hypernym",
    "hyponym": "hyponym",
    "holo_part": "holo_part",
    "holo_member": "holo_member",
    "holo_portion": "holo_substance",
    "near_antonym": "antonym",
    "similar_to": "similar",
    "also_see": "also",
    "be_in_state": "attribute",
    "subevent": "subevent",
    "causes": "causes",
    "category_domain": "domain_topic",
    "region_domain": "domain_region",
    "usage_domain": "exemplifies",
    "verb_group": "similar",
}
# WN-LMF relation -> the DEBVisDic relation it stands for when there is no dc:type
RELATIONS_BACK = {
    "hypernym": "hypernym",
    "hyponym": "hyponym",
    "holo_part": "holo_part",
    "holo_member": "holo_member",
    "holo_substance": "holo_portion",
    "antonym": "near_antonym",
    "similar": "similar_to",
    "also": "also_see",
    "attribute": "be_in_state",
    "subevent": "subevent",
    "causes": "causes",
    "domain_topic": "category_domain",
    "domain_region": "region_domain",
    "exemplifies": "usage_domain",
}

# Source elements kept in the synset's note as "key=value; key=value"
NOTED = {"SNOTE": "snote", "BCS": "bcs", "VERSION": "version", "CREATED": "created"}
NOTE_SEP = "; "
# The first of each of these has an attribute of its own; a second goes in the note
SINGLE = {"STAMP": "stamp", "NL": "nl", "DOMAIN": "domain"}
NL = {"yes": "false", "false": "true"}  # NL (not lexicalized) -> lexicalized
NL_BACK = {v: k for k, v in NL.items()}
KNOWN = {"ID", "POS", "ILI", "SYNONYM", "DEF", "USAGE", "ILR", "SUMO", "VALENCY",
         *NOTED, *SINGLE}

SAFE_ID = re.compile(r"[A-Za-z0-9_.-]+")
UNSAFE = re.compile(r"[^\w.]|_")  # not allowed in an XML name, or our escape character
SENSE_ID = re.compile(r"(.+)-s(\d+)")
ENG20_ID = re.compile(r"ENG20-(\d{8}-[nvab])")
SHORT_ID = re.compile(r"\d{8}-[nvab]")

log = logging.getLogger("visdic2lmf")
Facts = Counter[tuple]


def text(elem: ET.Element | None) -> str:
    """The text of an element without the white space around it ('' if none)."""
    return ((elem.text or "") if elem is not None else "").strip()


def read_source(path: Path) -> list[ET.Element]:
    """Read the SYNSET elements of a DEBVisDic file.

    Args:
        path: the XML file, or a zip archive holding exactly one XML file

    Returns:
        The SYNSET elements, in file order

    Raises:
        ValueError: if the archive does not hold exactly one file, or the
            root holds anything but SYNSET elements
    """
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            if len(names) != 1:
                raise ValueError(f"{path}: expected one file inside, found {names}")
            root = ET.fromstring(zf.read(names[0]))
    else:
        root = ET.parse(path).getroot()
    other = {child.tag for child in root} - {"SYNSET"}
    if other:
        raise ValueError(f"{path}: unexpected elements {sorted(other)}")
    return list(root)


def load_ili_map(path: Path) -> dict[str, str]:
    """Read a CILI map: lines of ILI id, tab, synset (offset-pos).

    Args:
        path: the map, e.g. cili's older-wn-mappings/ili-map-pwn20.tab

    Returns:
        synset (``00001740-a``) -> ILI id (``i1``)
    """
    out = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and parts[0].startswith("i"):
                out[parts[1]] = parts[0]
    return out


def ili_key(sid: str) -> str | None:
    """The key in the CILI map of a Princeton WordNet 2.0 synset id.

    Args:
        sid: a source synset id, e.g. ``ENG20-00001740-b``

    Returns:
        ``00001740-r``, or None if the id is not a Princeton 2.0 one
    """
    m = re.fullmatch(r"ENG20-(\d{8})-([nvab])", sid)
    return f"{m.group(1)}-{POS[m.group(2)]}" if m else None


def source_facts(synsets: list[ET.Element]) -> tuple[Facts, Counter[str]]:
    """Everything a DEBVisDic file says, as a multiset of facts.

    Args:
        synsets: the SYNSET elements

    Returns:
        The facts, and how many things were left out, by kind: empty
        elements and attributes, and WORD elements

    Raises:
        ValueError: for an element this converter does not know, or WORD
            elements that are not the words of the literals
    """
    facts: Facts = Counter()
    left: Counter[str] = Counter()

    def add(kind: str, sid: str, *value: str | int) -> None:
        if any(v != "" for v in value if isinstance(v, str)):
            facts[(kind, sid, *value)] += 1
        else:
            left[f"empty {kind}"] += 1

    for ss in synsets:
        sid = text(ss.find("ID"))
        facts[("synset", sid)] += 1
        unknown = {c.tag for c in ss} - KNOWN
        if unknown or len(ss.findall("ID")) != 1 or len(ss.findall("POS")) > 1:
            raise ValueError(f"{sid}: cannot convert {sorted(unknown) or 'two ID or POS'}")
        seen: Counter[str] = Counter()
        k = v = 0
        for c in ss:
            seen[c.tag] += 1
            n = seen[c.tag]
            if c.tag == "POS":
                add("pos", sid, text(c))
            elif c.tag in ("ILI", "STAMP", "NL", "DOMAIN", *NOTED):
                add(c.tag.lower(), sid, text(c))
            elif c.tag in ("DEF", "USAGE"):
                add(c.tag.lower(), sid, n, text(c))
            elif c.tag == "ILR":
                if text(c):
                    add("ilr", sid, c.get("type", ""), text(c))
                else:
                    left["ILR with no target"] += 1
            elif c.tag == "SUMO":
                add("sumo", sid, c.get("type", ""), text(c))
            elif c.tag == "VALENCY":
                v += 1
                for f, frame in enumerate(c, start=1):
                    if frame.tag != "FRAME":
                        raise ValueError(f"{sid}: VALENCY/{frame.tag}")
                    add("frame", sid, v, f, text(frame))
            elif c.tag == "SYNONYM":
                words = []
                for lit in c:
                    if lit.tag == "WORD":
                        left["WORD"] += 1
                        words.append(text(lit))
                    elif lit.tag != "LITERAL" or len(lit):
                        raise ValueError(f"{sid}: SYNONYM/{lit.tag} or a child of LITERAL")
                    elif text(lit):
                        k += 1
                        facts[("literal", sid, k, text(lit),
                               lit.get("sense", ""), lit.get("lnote", ""))] += 1
                    else:
                        left["empty literal"] += 1
                wanted = [w for lit in c.findall("LITERAL") for w in text(lit).split()]
                if sorted(words) != sorted(wanted):
                    raise ValueError(f"{sid}: WORD elements are not the words of the literals")
    return facts, left


def _note(pairs: list[tuple[str, str]]) -> str | None:
    """Pack key=value pairs into one note attribute."""
    for key, value in pairs:
        if NOTE_SEP in value or "\n" in value:
            raise ValueError(f"cannot keep {key}={value!r} in a note")
    return NOTE_SEP.join(f"{k}={v}" for k, v in pairs) or None


def _pairs(note: str | None) -> list[tuple[str, str]]:
    """Unpack a note attribute written by ``_note``."""
    return [tuple(p.split("=", 1)) for p in note.split(NOTE_SEP)] if note else []  # type: ignore[misc]


def escape_lemma(lemma: str) -> str:
    """A lemma written with only the characters an XML id may have.

    Args:
        lemma: the written form

    Returns:
        The lemma, with every other character (and ``_``) as ``_XXXX_``
    """
    return UNSAFE.sub(lambda m: f"_{ord(m.group()):04X}_", lemma)


def short_id(sid: str) -> str:
    """The part of a synset's id after the lexicon id.

    Args:
        sid: a source synset id, e.g. ``ENG20-00001740-b`` or ``CZE-00000002-z``

    Returns:
        The id without ``ENG20-`` (``00001740-b``); any other id unchanged

    Raises:
        ValueError: if another kind of id looks like a shortened one
    """
    m = ENG20_ID.fullmatch(sid)
    if m:
        return m.group(1)
    if SHORT_ID.fullmatch(sid):
        raise ValueError(f"synset id {sid!r} would be read back as ENG20-{sid}")
    return sid


def source_id(short: str) -> str:
    """The source synset id that ``short_id`` shortened.

    Args:
        short: the part of a synset's id after the lexicon id

    Returns:
        The id as the source has it
    """
    return f"ENG20-{short}" if SHORT_ID.fullmatch(short) else short


def _relation(wn_id: str, kind: str, target: str) -> Relation:
    link = RELATIONS.get(kind, "other")
    rel = Relation(link=link, target=f"{wn_id}-{short_id(target)}")
    if RELATIONS_BACK.get(link) != kind:
        rel.meta["dc:type"] = kind
    return rel


def _synset(ss: ET.Element, wn_id: str, ili_map: dict[str, str]) -> tuple[Synset, list[str]]:
    """One SYNSET as a WN-LMF synset (without its members) and its verb frames."""
    sid = text(ss.find("ID"))
    if not SAFE_ID.fullmatch(sid):
        raise ValueError(f"synset id {sid!r} cannot be part of an XML id")
    out = Synset(id=f"{wn_id}-{short_id(sid)}")
    notes: list[tuple[str, str]] = []
    groups = [[text(f) for f in valency if text(f)] for valency in ss.findall("VALENCY")]
    frames = [f for group in groups for f in group]
    if len(set(frames)) != len(frames):
        raise ValueError(f"{sid}: the same frame twice")
    if any(len(group) != 1 for group in groups):  # else one VALENCY for each frame
        notes.append(("valency", " ".join(str(len(group)) for group in groups)))
    seen: Counter[str] = Counter()

    pos = text(ss.find("POS"))
    if pos:
        out.pos = POS[pos]
    else:  # two synsets have none: take it from the id, which ends in it
        out.pos = POS.get(sid[-1:], "n") if re.search(r"-[nvab]$", sid) else "n"
        notes.append(("inferred", "pos"))

    ilis = [text(i) for i in ss.findall("ILI") if text(i)]
    mapped = ili_map.get(ili_key(sid) or "")
    if ilis:
        # A 2.0 synset that 3.0 split has several: CILI's map says which is its own
        out.ili = mapped if mapped in ilis else ilis[0]
        rest = list(ilis)
        rest.remove(out.ili)
        notes += [("ili", i) for i in rest]
    elif mapped:
        out.ili = mapped
        notes.append(("inferred", "ili"))
    else:
        out.ili = ""

    for c in ss:
        seen[c.tag] += 1
        value = text(c)
        if c.tag == "ILR" and value:
            out.relations.append(_relation(wn_id, c.get("type", ""), value))
        elif c.tag == "SUMO" and (value or c.get("type")):
            notes.append(("sumo", f"{c.get('type', '')} {value}"))
        elif not value or c.tag in ("ID", "POS", "ILI", "SYNONYM", "ILR", "SUMO", "VALENCY"):
            continue
        elif c.tag == "DEF":
            out.definitions.append(Text(text=value))
        elif c.tag == "USAGE":
            out.examples.append(Text(text=value))
        elif c.tag in NOTED or seen[c.tag] > 1:
            notes.append(((NOTED | SINGLE)[c.tag], value))
        elif c.tag == "STAMP":
            user, _, date = value.partition(" ")
            out.meta["dc:contributor"] = user
            if date:
                out.meta["dc:date"] = date
        elif c.tag == "DOMAIN":
            out.meta["dc:subject"] = value
        elif value in NL:
            out.lexicalized = NL[value]
        else:  # NL with some other value: not lexicalized, and the value is kept
            out.lexicalized = "false"
            notes.append(("nl", value))
    if note := _note(notes):
        out.meta["note"] = note
    return out, frames


def convert(synsets: list[ET.Element], ili_map: dict[str, str], lexicon: Lexicon) -> list[Item]:
    """Turn DEBVisDic synsets into the items of a WN-LMF lexicon.

    Args:
        synsets: the SYNSET elements
        ili_map: Princeton WordNet 2.0 synset -> ILI id
        lexicon: the header of the new lexicon

    Returns:
        The lexicon, its entries, its synsets and its frames, in the
        order WN-LMF wants

    Raises:
        ValueError: for a value that cannot be written (see the message)
    """
    wn_id = str(lexicon.id)
    entries: dict[tuple[str, str], Entry] = {}
    out_synsets: dict[str, Synset] = {}
    all_frames: dict[str, Frame] = {}  # the wn module wants each frame once
    for ss in synsets:
        synset, frames = _synset(ss, wn_id, ili_map)
        if synset.id in out_synsets:
            raise ValueError(f"two synsets with the id {synset.id}")
        members = []
        literals = [lit for lit in ss.iter("LITERAL") if text(lit)]
        if frames and not literals:
            raise ValueError(f"{synset.id}: frames, but no word to hang them on")
        for frame in frames:
            if frame not in all_frames:
                all_frames[frame] = Frame(id=f"{wn_id}-frame-{len(all_frames) + 1}", frame=frame)
        for k, lit in enumerate(literals, start=1):
            sense = Sense(id=f"{synset.id}-s{k}", synset=synset.id)
            number = lit.get("sense", "")
            if number.isascii() and number.isdigit():
                sense.n = number
            elif number:
                sense.meta["dc:identifier"] = number
            if lit.get("lnote"):
                sense.meta["note"] = lit.get("lnote")
            if frames:
                sense.subcat = " ".join(str(all_frames[f].id) for f in frames)
            key = (text(lit), str(synset.pos))
            if key not in entries:
                entries[key] = Entry(id=f"{wn_id}-{escape_lemma(key[0])}-{key[1]}",
                                     lemma=key[0], pos=key[1])
            entries[key].senses.append(sense)
            members.append(str(sense.id))
        if members:
            synset.members = " ".join(members)
        out_synsets[str(synset.id)] = synset

    if len({e.id for e in entries.values()}) != len(entries):
        raise ValueError("two entries with the same id")
    shared = {str(e.id) for e in entries.values()} & set(out_synsets)
    if shared:
        raise ValueError(f"an entry and a synset with the same id: {sorted(shared)}")
    # WN-LMF wants the target of a relation in the file
    for synset in list(out_synsets.values()):
        for rel in synset.relations:
            if rel.target not in out_synsets:
                sid = str(rel.target)[len(wn_id) + 1:]
                pos = POS[sid[-1]] if re.search(r"-[nvab]$", sid) else str(synset.pos)
                out_synsets[str(rel.target)] = Synset(
                    id=rel.target, pos=pos, ili=ili_map.get(ili_key(sid) or "", ""),
                    meta={"note": "inferred=synset"})
    return [lexicon, *entries.values(), *out_synsets.values(), *all_frames.values()]


def lmf_facts(items: list[Item]) -> Facts:
    """What the DEBVisDic source of a converted lexicon said.

    Args:
        items: the items ``convert`` made, or the same read back from XML

    Returns:
        The facts of the source, as ``source_facts`` gives them
    """
    wn_id = str(next(i for i in items if isinstance(i, Lexicon)).id)
    cut = len(wn_id) + 1
    facts: Facts = Counter()
    frames = {str(i.id): str(i.frame) for i in items if isinstance(i, Frame)}
    senses = {str(s.id): s for i in items if isinstance(i, Entry) for s in i.senses}
    for item in items:
        if isinstance(item, Entry):
            for sense in item.senses:
                m = SENSE_ID.fullmatch(str(sense.id))
                assert m and m.group(1) == sense.synset, sense.id
                facts[("literal", source_id(str(sense.synset)[cut:]), int(m.group(2)), item.lemma,
                       sense.n or sense.meta.get("dc:identifier", ""),
                       sense.meta.get("note", ""))] += 1
        elif isinstance(item, Synset):
            sid = source_id(str(item.id)[cut:])
            notes = _pairs(item.meta.get("note"))
            inferred = {v for k, v in notes if k == "inferred"}
            if "synset" in inferred:
                continue
            facts[("synset", sid)] += 1
            if "pos" not in inferred:
                facts[("pos", sid, POS_BACK[str(item.pos)])] += 1
            if item.ili and "ili" not in inferred:
                facts[("ili", sid, item.ili)] += 1
            for key, value in notes:
                if key == "sumo":
                    facts[("sumo", sid, *value.split(" ", 1))] += 1
                elif key not in ("inferred", "valency"):
                    facts[(key, sid, value)] += 1
            # the frames are on every sense of the synset: read them off the first
            first = senses[str(item.members).split()[0]] if item.members else None
            subcat = iter(str(first.subcat).split() if first and first.subcat else [])
            sizes = dict(notes).get("valency")
            for v, size in enumerate(sizes.split() if sizes else [1] * len(frames), start=1):
                for f, frame in zip(range(1, int(size) + 1), subcat):
                    facts[("frame", sid, v, f, frames[frame])] += 1
            for n, d in enumerate(item.definitions, start=1):
                facts[("def", sid, n, d.text)] += 1
            for n, e in enumerate(item.examples, start=1):
                facts[("usage", sid, n, e.text)] += 1
            for rel in item.relations:
                kind = rel.meta.get("dc:type") or RELATIONS_BACK[str(rel.link)]
                facts[("ilr", sid, kind, source_id(str(rel.target)[cut:]))] += 1
            if "dc:contributor" in item.meta:
                stamp = [item.meta["dc:contributor"], item.meta.get("dc:date")]
                facts[("stamp", sid, " ".join(x for x in stamp if x))] += 1
            if "dc:subject" in item.meta:
                facts[("domain", sid, item.meta["dc:subject"])] += 1
            if item.lexicalized and not _first_nl_in_note(item, notes):
                facts[("nl", sid, NL_BACK[str(item.lexicalized)])] += 1
    return facts


def _first_nl_in_note(item: Synset, notes: list[tuple[str, str]]) -> bool:
    """Whether the synset's own NL value is the one kept in the note.

    An NL value other than yes or false is written as lexicalized="false"
    with the value in the note; a second NL element also goes in the note,
    but then its value is yes or false or follows a first that is.
    """
    values = [v for k, v in notes if k == "nl"]
    return item.lexicalized == "false" and bool(values) and values[0] not in NL


def check(synsets: list[ET.Element], items: list[Item]) -> list[str]:
    """Compare what the source says with what the lexicon says.

    Args:
        synsets: the SYNSET elements of the source
        items: the converted lexicon

    Returns:
        One line per fact that is in one and not the other; empty when
        nothing was lost and nothing was made up
    """
    want, _ = source_facts(synsets)
    got = lmf_facts(items)
    return ([f"lost: {f}" for f in (want - got).elements()]
            + [f"made up: {f}" for f in (got - want).elements()])


def package(xml: Path, wn_id: str) -> Path:
    """Write the wn package directory and its .tar.xz beside the XML.

    Args:
        xml: the lexicon
        wn_id: the lexicon's id, which names the directory

    Returns:
        The tarball
    """
    pkg = xml.parent / wn_id
    shutil.rmtree(pkg, ignore_errors=True)  # a package holds exactly one XML
    pkg.mkdir(parents=True)
    for path in (xml, ROOT / "LICENSE", ROOT / "README.md", ROOT / "citation.bib"):
        shutil.copy(path, pkg / path.name)
    tar = xml.with_suffix(".tar.xz")
    with tarfile.open(tar, "w:xz") as tf:
        tf.add(pkg, arcname=wn_id)
    return tar


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("source", type=Path, help="DEBVisDic XML, or a zip holding it")
    parser.add_argument("-o", "--outdir", type=Path, default=ROOT / "release")
    parser.add_argument("--id", default="wncze", help="lexicon id (default: wncze)")
    parser.add_argument("--version", default="2.1", help="version (default: 2.1)")
    parser.add_argument("--label", default="Czech WordNet")
    parser.add_argument("--source-url", default="https://deb.fi.muni.cz/dl/wncze21.xml.zip",
                        help="where the source file came from")
    parser.add_argument("--ili-map", type=Path, default=ILI_MAP)
    parser.add_argument("--package", action="store_true", help="also write the .tar.xz")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    lexicon = Lexicon(
        id=args.id, label=args.label, language="cs", email="bond@ieee.org",
        license="https://creativecommons.org/licenses/by-sa/4.0/", version=args.version,
        url="https://github.com/bond-lab/czech-wn", citation=CITATION,
        namespaces={"dc": DC},
        meta={"dc:publisher": "Natural Language Processing Centre, Faculty of Informatics, "
                              "Masaryk University, Brno",
              "dc:source": args.source_url})
    synsets = read_source(args.source)
    facts, left = source_facts(synsets)
    items = convert(synsets, load_ili_map(args.ili_map), lexicon)
    out = args.outdir / f"{args.id}-{args.version}.xml"
    out.parent.mkdir(parents=True, exist_ok=True)
    lmf.write(out, items)

    problems = check(synsets, list(lmf.read(out)))
    for line in problems[:50]:
        log.error(line)
    if problems:
        log.error("%d differences between %s and %s", len(problems), args.source, out)
        sys.exit(1)
    kinds = Counter(f[0] for f in facts.elements())
    log.info("Source facts, all found again in the output: %s",
             ", ".join(f"{n} {k}" for k, n in sorted(kinds.items())))
    log.info("Not carried over: %s", ", ".join(f"{n} {k}" for k, n in sorted(left.items())))
    made = Counter(type(i).__name__ for i in items)
    inferred = Counter(v for i in items if isinstance(i, Synset)
                       for k, v in _pairs(i.meta.get("note")) if k == "inferred")
    log.info("Wrote %s: %s; inferred: %s", out, dict(made), dict(inferred))
    if args.package:
        log.info("Wrote %s", package(out, args.id))


if __name__ == "__main__":
    main()
