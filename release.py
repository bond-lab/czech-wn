#!/usr/bin/env python3
"""Make the next release of the Czech WordNet: the last release plus the changes.

    uv run release.py VERSION    # e.g. 2.3

The base is the released wncze-BASE_VERSION.xml, downloaded once to
build/base/ and checked against its checksum.  The changes are
changes/wncze-BASE_VERSION.jsonl (see changes/README.md).  A change that
does not fit the base is a conflict: they are listed, and nothing is
written until they are settled.

No synset is dropped for being empty: the Czech WordNet is a wordnet in
its own right, so a synset goes only when a change record removes it.

New entries and senses get ids made like the others in this lexicon
(``wncze-pes-n``, ``wncze-02001223-n-s3``).

Writes release/wncze-VERSION.xml and the wn package
release/wncze-VERSION.tar.xz (the XML with README, LICENSE and
citation.bib).  The XML is checked against the WN-LMF 1.4 DTD if
xmllint and a checkout of the schemas (../schemas) are there, and with
the validation of the wn module: an error, or an ILI on two synsets,
stops the release.

Uses ntumc.wordnet from a checkout of NTU-MC beside this one (../NTUMC).
"""

import argparse
import hashlib
import io
import logging
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "NTUMC"))
sys.path.insert(0, str(ROOT / "scripts"))

from ntumc.wordnet import changes, lmf, validate  # noqa: E402
from ntumc.wordnet.model import Entry, Item, Lexicon, Synset  # noqa: E402
from visdic2lmf import SENSE_ID, escape_lemma, package  # noqa: E402

WN_ID = "wncze"
BASE_VERSION = "2.2"
BASE_URL = ("https://github.com/bond-lab/czech-wn/releases/download/"
            f"v{BASE_VERSION}/{WN_ID}-{BASE_VERSION}.tar.xz")
BASE_XZ_SHA256 = "b331c2256a5608d848c79a7d4ee9925aa86f03214ee278ecde80b63ff4d5c023"
BASE_XML_SHA256 = "b8db5dac8c7e8b0cf1d111bf599f1d7417e9752bb1cb10ec88edd34ff36ebed2"
BASE = ROOT / "build" / "base" / f"{WN_ID}-{BASE_VERSION}.xml"
CHANGES = ROOT / "changes" / f"{WN_ID}-{BASE_VERSION}.jsonl"
DTD = ROOT.parent / "schemas" / "WN-LMF-1.4.dtd"

log = logging.getLogger("release")


def fetch_base(path: Path = BASE) -> None:
    """Download the base release to path, unless it is there; check it.

    Args:
        path: where the base XML is kept

    Raises:
        ValueError: if the download or the file does not match its checksum.
    """
    if not path.exists():
        log.info("Downloading %s", BASE_URL)
        with urllib.request.urlopen(BASE_URL) as resp:
            data = resp.read()
        if hashlib.sha256(data).hexdigest() != BASE_XZ_SHA256:
            raise ValueError(f"{BASE_URL}: checksum mismatch")
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:xz") as tf:
            member = tf.extractfile(f"{WN_ID}/{path.name}")
            if member is None:
                raise ValueError(f"{BASE_URL}: no {path.name} inside")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(member.read())
    if hashlib.sha256(path.read_bytes()).hexdigest() != BASE_XML_SHA256:
        raise ValueError(f"{path} is not the released {WN_ID} {BASE_VERSION}")


def tidy_ids(items: list[Item], base: list[Item]) -> dict[str, str]:
    """Give the entries and senses that are not in the base ids like the others'.

    ``changes.apply`` numbers what it adds as wnja and COW do.  Here an
    entry is ``wncze-LEMMA-POS`` and a sense is its synset's id and
    ``-sK``, K counting on from the synset's last sense.

    Args:
        items: the lexicon after the changes; changed in place
        base: the lexicon before the changes

    Returns:
        The ids changed, old to new

    Raises:
        ValueError: if a new id is already used
    """
    wn_id = str(next(i for i in items if isinstance(i, Lexicon)).id)
    old_entries = {e.id for e in base if isinstance(e, Entry)}
    old_senses = {s.id for e in base if isinstance(e, Entry) for s in e.senses}
    used = {i.id for i in items if isinstance(i, Entry | Synset)}
    last: dict[str, int] = {}
    for entry in (i for i in items if isinstance(i, Entry)):
        used.update(s.id for s in entry.senses)
        for sense in entry.senses:
            m = SENSE_ID.fullmatch(str(sense.id))
            if sense.id in old_senses and m and m.group(1) == sense.synset:
                last[m.group(1)] = max(last.get(m.group(1), 0), int(m.group(2)))
    renamed: dict[str, str] = {}

    def rename(old: str, new: str) -> str:
        if new in used:
            raise ValueError(f"cannot rename {old}: {new} is taken")
        used.add(new)
        renamed[old] = new
        return new

    for entry in (i for i in items if isinstance(i, Entry)):
        if entry.id not in old_entries:
            entry.id = rename(str(entry.id),
                              f"{wn_id}-{escape_lemma(str(entry.lemma))}-{entry.pos}")
        for sense in entry.senses:
            if sense.id not in old_senses:
                last[str(sense.synset)] = last.get(str(sense.synset), 0) + 1
                sense.id = rename(str(sense.id), f"{sense.synset}-s{last[str(sense.synset)]}")
    members: dict[str, list[str]] = {}
    for entry in (i for i in items if isinstance(i, Entry)):
        for sense in entry.senses:
            members.setdefault(str(sense.synset), []).append(str(sense.id))
            for rel in sense.relations:
                rel.target = renamed.get(str(rel.target), rel.target)
    for item in (i for i in items if isinstance(i, Synset)):
        if item.members:
            item.members = " ".join(renamed.get(m, m) for m in item.members.split())
        elif item.members is None and item.id in members:  # a synset the changes added
            item.members = " ".join(sorted(members[str(item.id)],
                                           key=lambda m: int(m.rsplit("-s", 1)[1])))
    return renamed


def valid(xml: Path) -> bool:
    """Check the XML against the WN-LMF DTD, if the tools are there.

    Args:
        xml: the file to check

    Returns:
        False if xmllint found the file invalid; True if valid or not checked
    """
    if not DTD.exists() or shutil.which("xmllint") is None:
        log.warning("Not checked against the DTD: needs xmllint and %s", DTD)
        return True
    done = subprocess.run(["xmllint", "--nonet", "--noout", "--dtdvalid", str(DTD), str(xml)],
                          capture_output=True, text=True, check=False)
    if done.returncode in (3, 4):  # validation error; other warnings are about the DOCTYPE URL
        log.error(done.stderr.strip())
        return False
    return True


def release(version: str, out: Path, records: Path = CHANGES) -> list[str]:
    """Apply the change records to the base and write the new release.

    Args:
        version: the version of the new release
        out: the XML file to write; not written if there are conflicts
        records: the change records

    Returns:
        The conflicts, one line each.
    """
    fetch_base()
    base = list(lmf.read(BASE))
    items, conflicts = changes.apply(list(lmf.read(BASE)), changes.read(records))
    if conflicts:
        return conflicts
    renamed = tidy_ids(items, base)
    log.info("%d new entries and senses", len(renamed))
    next(i for i in items if isinstance(i, Lexicon)).version = version
    out.parent.mkdir(parents=True, exist_ok=True)
    lmf.write(out, items)
    return []


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version", help="version of the new release, e.g. 2.3")
    parser.add_argument("-o", "--outdir", default=str(ROOT / "release"),
                        help="output directory (default: release/)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.version == BASE_VERSION:
        log.error("%s is the base: give the version of the new release", BASE_VERSION)
        sys.exit(1)
    out = Path(args.outdir) / f"{WN_ID}-{args.version}.xml"
    conflicts = release(args.version, out)
    if conflicts:
        for line in conflicts:
            log.error(line)
        sys.exit(1)
    if not valid(out) or not validate.check(out):
        sys.exit(1)
    log.info("Wrote %s and %s", out, package(out, WN_ID))


if __name__ == "__main__":
    main()
