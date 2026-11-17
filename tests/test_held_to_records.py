"""Tests of scripts/held_to_records.py."""
# ruff: noqa: I001  (release must be imported first: it finds ntumc)

import sqlite3
from collections import Counter

import release  # puts ../NTUMC and scripts on the path
import held_to_records as h
from ntumc.wordnet.changes import Change


def sense(synset: str, lemma: str) -> Change:
    """A sense as ntumc2changes makes it."""
    return Change(action="add_sense", lexicon="wncze", synset=synset, lemma=lemma, pos="v",
                  user="s1", reason="added in NTU-MC by an annotator")


def test_same_compares_in_lower_case_with_spaces():
    # Arrange
    lemma = "Dát_se"
    # Act
    compared = h.same(lemma)
    # Assert
    assert compared == "dát se"


def test_held_senses_are_those_tagged_and_not_logged_most_used_first():
    # Arrange
    made = [sense("wncze-1-v", "smět"), sense("wncze-1-v", "moci"), sense("wncze-2-v", "Upírat"),
            sense("wncze-3-v", "nést"), sense("wncze-01550902-n", "salamander")]
    logged = {h.key(sense("wncze-1-v", "moci"))}
    uses = Counter({("wncze-1-v", "smět"): 2, ("wncze-1-v", "moci"): 27,
                    ("wncze-2-v", "upírat"): 5, ("wncze-01550902-n", "salamander"): 1})
    # Act
    found = h.held_senses(made, logged, uses)
    # Assert
    assert [(c.synset, c.lemma) for c in found] == [("wncze-2-v", "Upírat"),
                                                    ("wncze-1-v", "smět")]


def test_records_add_the_synset_once_then_sense_and_note_then_what_waited():
    # Arrange
    made = [Change(action="add_synset", synset="wncze-2-v", pos="v", new=""),
            sense("wncze-2-v", "Upírat"), sense("wncze-2-v", "zírat"),
            Change(action="add_example", synset="wncze-2-v", new="Upíral na něho zrak"),
            Change(action="add_example", synset="wncze-2-v", new="held"),
            Change(action="add_example", synset="wncze-1-v", new="for a synset we have")]
    uses = Counter({("wncze-2-v", "upírat"): 5, ("wncze-2-v", "zírat"): 1})
    senses = [made[1], made[2]]
    # Act
    out = h.records(senses, made, {"wncze-1-v"}, uses, {("add_example", "wncze-2-v", "held")})
    # Assert
    assert [(c.action, c.lemma or c.new) for c in out] == [
        ("add_synset", ""), ("add_sense", "upírat"), ("set_note", "upírat"),
        ("add_sense", "zírat"), ("set_note", "zírat"), ("add_example", "Upíral na něho zrak")]
    assert out[2].new == h.NOTE and "5 times" in out[2].source
    assert "the corpus is tagged with it" in out[1].reason


def test_copy_senses_are_tagged_senses_of_the_copy_that_are_not_here():
    # Arrange
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE word (wordid INTEGER, lemma TEXT, pos TEXT)")
    con.execute("CREATE TABLE sense (synset TEXT, wordid INTEGER, lang TEXT, src TEXT)")
    con.executemany("INSERT INTO word VALUES (?, ?, ?)",
                    [(1, "národ", "n"), (2, "lid", "n"), (3, "stát", "n"), (4, "země", "n")])
    con.executemany("INSERT INTO sense VALUES (?, ?, ?, ?)",
                    [("08166552-n", 1, "ces", "wncz"), ("08166552-n", 2, "ces", "wncz"),
                     ("08166552-n", 3, "ces", "wncz"), ("08166552-n", 4, "ces", "ntumc")])
    uses = Counter({("wncze-7-n", "národ"): 1, ("wncze-7-n", "lid"): 4, ("wncze-7-n", "země"): 2})
    # Act
    out = h.copy_senses(con, uses, {"08166552-n": "wncze-7-n"}, {("wncze-7-n", "lid")})
    # Assert
    assert [(c.action, c.synset, c.lemma) for c in out] == [
        ("add_sense", "wncze-7-n", "národ"), ("set_note", "wncze-7-n", "národ")]
    assert out[1].new == h.NOTE_COPY and out[0].lexicon == release.WN_ID
