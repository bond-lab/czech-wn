"""Tests of release.py and of the script that made the first change records."""
# ruff: noqa: I001  (release must be imported first: it finds ntumc)

import json
from pathlib import Path

import pytest

import release as r  # puts ../NTUMC on the path
import ntumc2changes as n
from ntumc.wordnet import changes, lmf
from ntumc.wordnet.model import Entry, Lexicon, Sense, Synset

OUT = Path(__file__).parent / "output"
WHO = {"lexicon": "wncze", "user": "tester", "source": "native check", "reason": "test",
       "base": "wncze-0"}


def base_items() -> list:
    lexicon = Lexicon(id="wncze", label="Test", language="cs", email="x@example.org",
                      license="https://example.org/", version="0",
                      namespaces={"dc": "https://globalwordnet.github.io/schemas/dc/"})
    dog = Entry(id="wncze-pes-n", lemma="pes", pos="n", senses=[
        Sense(id="wncze-00000001-n-s1", synset="wncze-00000001-n")])
    hound = Entry(id="wncze-ohař-n", lemma="ohař", pos="n", senses=[
        Sense(id="wncze-00000001-n-s2", synset="wncze-00000001-n")])
    return [lexicon, dog, hound,
            Synset(id="wncze-00000001-n", ili="i1", pos="n",
                   members="wncze-00000001-n-s1 wncze-00000001-n-s2"),
            Synset(id="wncze-00000002-n", ili="i2", pos="n")]


@pytest.fixture
def base(tmp_path, monkeypatch) -> Path:
    path = tmp_path / "wncze-0.xml"
    lmf.write(path, base_items())
    monkeypatch.setattr(r, "BASE", path)
    monkeypatch.setattr(r, "fetch_base", lambda: None)
    return path


def records(tmp_path: Path, *changes: dict) -> Path:
    path = tmp_path / "changes.jsonl"
    lines = [json.dumps({"id": f"t-{k}", **WHO, **c}, ensure_ascii=False)
             for k, c in enumerate(changes)]
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return path


def read(path: Path) -> tuple[dict[str, Entry], dict[str, Synset], Lexicon]:
    items = list(lmf.read(path))
    return ({str(e.id): e for e in items if isinstance(e, Entry)},
            {str(s.id): s for s in items if isinstance(s, Synset)},
            next(i for i in items if isinstance(i, Lexicon)))


def test_no_changes_gives_the_base_with_a_new_version(base, tmp_path):
    OUT.mkdir(exist_ok=True)
    out = OUT / "release-empty.xml"

    conflicts = r.release("1", out, records(tmp_path))

    assert conflicts == []
    assert out.read_text(encoding="utf-8").replace('version="1"', 'version="0"') == \
        base.read_text(encoding="utf-8")


def test_a_new_sense_and_entry_get_ids_like_the_others(base, tmp_path):
    OUT.mkdir(exist_ok=True)
    out = OUT / "release-added.xml"
    log = records(tmp_path,
                  {"action": "add_sense", "synset": "wncze-00000001-n", "lemma": "čokl"},
                  {"action": "add_sense", "synset": "wncze-00000002-n", "lemma": "pes"})

    conflicts = r.release("1", out, log)

    entries, synsets, lexicon = read(out)
    assert conflicts == []
    assert lexicon.version == "1"
    assert [s.id for s in entries["wncze-čokl-n"].senses] == ["wncze-00000001-n-s3"]
    assert [s.id for s in entries["wncze-pes-n"].senses] == [
        "wncze-00000001-n-s1", "wncze-00000002-n-s1"]
    assert synsets["wncze-00000001-n"].members == \
        "wncze-00000001-n-s1 wncze-00000001-n-s2 wncze-00000001-n-s3"


def test_a_synset_the_changes_add_lists_its_members(base, tmp_path):
    OUT.mkdir(exist_ok=True)
    out = OUT / "release-synset.xml"
    log = records(tmp_path,
                  {"action": "add_synset", "synset": "wncze-NTUMC-80000001-n", "pos": "n",
                   "new": "", "identifier": "ntumc00001"},
                  {"action": "add_sense", "synset": "wncze-NTUMC-80000001-n", "lemma": "pes"},
                  {"action": "add_sense", "synset": "wncze-NTUMC-80000001-n", "lemma": "fena"})

    conflicts = r.release("1", out, log)

    synset = read(out)[1]["wncze-NTUMC-80000001-n"]
    assert conflicts == []
    assert synset.members == "wncze-NTUMC-80000001-n-s1 wncze-NTUMC-80000001-n-s2"
    assert synset.meta["dc:identifier"] == "ntumc00001"


def test_a_removed_sense_goes_and_no_synset_is_dropped(base, tmp_path):
    OUT.mkdir(exist_ok=True)
    out = OUT / "release-removed.xml"
    log = records(tmp_path,
                  {"action": "remove_sense", "synset": "wncze-00000001-n", "lemma": "ohař"})

    conflicts = r.release("1", out, log)

    entries, synsets, _ = read(out)
    assert conflicts == []
    assert "wncze-ohař-n" not in entries
    assert synsets["wncze-00000001-n"].members == "wncze-00000001-n-s1"
    assert "wncze-00000002-n" in synsets  # empty, and kept


def test_a_conflict_is_reported_and_nothing_is_written(base, tmp_path):
    out = tmp_path / "not-written.xml"
    log = records(tmp_path,
                  {"action": "remove_sense", "synset": "wncze-00000001-n", "lemma": "kočka"})

    conflicts = r.release("1", out, log)

    assert len(conflicts) == 1
    assert not out.exists()


def test_a_taken_id_is_refused():
    items = base_items()
    clash = Entry(id="wncze-n-9", lemma="pes", pos="n", senses=[])
    with pytest.raises(ValueError, match="is taken"):
        r.tidy_ids([*items, clash], items)


def maps() -> n.Maps:
    out = n.Maps(ili30={"00000010-n": "i1", "00000020-n": "i5", "00000030-n": "i6",
                        "00000040-s": "i7", "00000050-n": "i8"},
                 pwn20={"i1": "00000001-n", "i5": "00000005-r", "i7": "00000007-s",
                        "i8": "00000008-n"},
                 concepts={"80000001-z": ("ntumc00001", "x")},
                 pronouns={"77000001-n": ("pronoun:1;Sg", "n"),
                           "00000020-n": ("pronoun:Plc;Prox", "n")})
    out.by_ili["i1"].append("wncze-00000001-n")
    out.by_ili["i8"] += ["wncze-00000008-n", "wncze-00000009-n"]
    return out


@pytest.mark.parametrize("synset, expected", [
    ("00000010-n", n.Target("wncze-00000001-n")),
    ("00000020-n", n.Target("wncze-00000005-b", "n", "i5", "pronoun:Plc;Prox")),
    ("00000030-n", n.Target("wncze-ENG30-00000030-n", "n", "i6")),
    ("00000040-a", n.Target("wncze-00000007-a", "a", "i7")),
    ("00000050-n", n.Target("wncze-00000008-n")),
    ("80000001-z", n.Target("wncze-NTUMC-80000001-z", "x", "", "ntumc00001")),
    ("77000001-n", n.Target("wncze-NTUMC-77000001-n", "n", "", "pronoun:1;Sg")),
])
def test_where_a_database_synset_goes(synset, expected):
    synsets = {"wncze-00000001-n": Synset(id="wncze-00000001-n", ili="i1", pos="n")}

    assert n.target(synset, maps(), synsets) == expected


def test_a_concept_nobody_has_is_left_for_review():
    assert n.target("80000002-n", maps(), {}) == \
        "the concept is not in CILI, omw-ntumc or omw-pronoun"


def test_the_first_change_log_applies_to_the_base():
    if not r.BASE.exists():
        pytest.skip("the base has not been downloaded: run release.py once")
    from ntumc.wordnet import changes

    _, conflicts = changes.apply(list(lmf.read(r.BASE)), changes.read(r.CHANGES))

    assert conflicts == []


def test_the_change_log_fits_the_base_and_no_ili_is_on_two_synsets():
    # Arrange
    if not r.BASE.exists():
        pytest.skip("base release not downloaded: run release.py once")

    # Act
    items, conflicts = changes.apply(lmf.read(r.BASE), changes.read(r.CHANGES))

    # Assert
    assert conflicts == []
    assert changes.shared_ilis(items) == []
