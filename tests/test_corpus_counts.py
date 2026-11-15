"""Tests of scripts/corpus_counts.py."""
# ruff: noqa: I001  (release must be imported first: it finds ntumc)

import sqlite3
from collections import Counter
from pathlib import Path

import release  # puts ../NTUMC on the path
import corpus_counts as c
from ntumc.wordnet.model import Count, Entry, Sense, Synset

OUT = Path(__file__).parent / "output"


def lexicon() -> list:
    return [Entry(id="wncze-pes-n", lemma="pes", pos="n", senses=[
                Sense(id="wncze-1-n-s1", synset="wncze-1-n",
                      counts=[Count(text="3", meta={"dc:source": "NTU-MC"})])]),
            Entry(id="wncze-vlk-n", lemma="vlk", pos="n", senses=[
                Sense(id="wncze-2-n-s1", synset="wncze-2-n")]),
            Synset(id="wncze-1-n", ili="i1", pos="n"),
            Synset(id="wncze-2-n", ili="i2", pos="n")]


def test_tagged_counts_lemma_and_synset_and_skips_other_tags():
    # Arrange
    OUT.mkdir(exist_ok=True)
    db = OUT / "corpus_counts.db"
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    with con:
        con.execute("CREATE TABLE concept (sid INTEGER, cid INTEGER, clemma TEXT, tag TEXT)")
        con.executemany("INSERT INTO concept VALUES (?, ?, ?, ?)", [
            (1, 1, "pes", "02084071-n"), (1, 2, "pes", "02084071-n"),
            (2, 1, "vlk", "02114100-n"), (2, 2, "a", "x"), (2, 3, "b", None)])
    con.close()

    # Act
    tags = c.tagged(db)

    # Assert
    assert tags == Counter({("pes", "02084071-n"): 2, ("vlk", "02114100-n"): 1})


def test_records_leaves_out_a_count_that_is_already_right():
    # Arrange
    found = Counter({("wncze-1-n", "pes"): 3, ("wncze-2-n", "vlk"): 2})

    # Act
    made = c.records(found, lexicon(), 10, "2026-11-15")

    # Assert
    assert [(r.id, r.action, r.synset, r.lemma, r.new, r.corpus) for r in made] == [
        (f"wncze-{release.BASE_VERSION}-10", "set_count", "wncze-2-n", "vlk", "2", "NTU-MC")]


def test_records_changes_a_count_that_differs():
    # Arrange
    found = Counter({("wncze-1-n", "pes"): 5})

    # Act
    made = c.records(found, lexicon(), 1, "2026-11-15")

    # Assert
    assert [(r.synset, r.new) for r in made] == [("wncze-1-n", "5")]
