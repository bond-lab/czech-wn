"""Tests of scripts/princeton_links.py."""
# ruff: noqa: I001  (release must be imported first: it finds ntumc)

import release  # noqa: F401  (puts ../NTUMC on the path)
import princeton_links as p
from ntumc.wordnet.model import Relation, Synset


def lexicon() -> list:
    return [Synset(id="wncze-1-n", ili="i1", pos="n"),
            Synset(id="wncze-2-n", ili="i2", pos="n",
                   relations=[Relation(link="hypernym", target="wncze-1-n")]),
            Synset(id="wncze-3-n", ili="i3", pos="n"),
            Synset(id="wncze-4-n", ili="i4", pos="n"),
            Synset(id="wncze-5a-n", ili="i5", pos="n"),
            Synset(id="wncze-5b-n", ili="i5", pos="n")]


def test_links_keeps_a_relation_from_a_new_synset():
    # Arrange
    relations = [("i3", "hypernym", "i1")]

    # Act
    found, left = p.links(relations, lexicon(), {"wncze-3-n"})

    # Assert
    assert found == [("wncze-3-n", "hypernym", "wncze-1-n")]
    assert left == []


def test_links_turns_a_hyponym_round():
    # Arrange
    relations = [("i3", "hyponym", "i4"), ("i3", "mero_part", "i4")]

    # Act
    found, _ = p.links(relations, lexicon(), {"wncze-3-n"})

    # Assert
    assert found == [("wncze-4-n", "holo_part", "wncze-3-n"),
                     ("wncze-4-n", "hypernym", "wncze-3-n")]


def test_links_leaves_out_what_does_not_touch_a_new_synset_or_is_there():
    # Arrange
    relations = [("i4", "hypernym", "i1"), ("i2", "hypernym", "i1"),
                 ("i3", "derivation", "i1"), ("i3", "hypernym", "i9"),
                 ("i3", "hypernym", "i5")]

    # Act
    found, left = p.links(relations, lexicon(), {"wncze-3-n", "wncze-2-n"})

    # Assert
    assert found == []
    assert left == []


def test_links_does_not_give_an_old_synset_a_second_hypernym():
    # Arrange
    relations = [("i3", "hyponym", "i2")]

    # Act
    found, left = p.links(relations, lexicon(), {"wncze-3-n"})

    # Assert
    assert found == []
    assert left == [("wncze-2-n", "hypernym", "wncze-3-n")]


def test_records_are_numbered_on_from_the_log():
    # Arrange
    found = [("wncze-3-n", "hypernym", "wncze-1-n"), ("wncze-3-n", "similar", "wncze-4-n")]

    # Act
    made = p.records(found, 1413, "2026-11-15")

    # Assert
    assert [r.id for r in made] == ["wncze-2.1-1413", "wncze-2.1-1414"]
    assert made[0].action == "add_relation"
    assert (made[1].synset, made[1].link, made[1].target) == (
        "wncze-3-n", "similar", "wncze-4-n")
    assert made[0].source and made[0].reason and made[0].user


def test_links_does_not_copy_usage_labels():
    # Arrange
    relations = [("i3", "is_exemplified_by", "i1"), ("i1", "exemplifies", "i3")]

    # Act
    found, left = p.links(relations, lexicon(), {"wncze-3-n"})

    # Assert
    assert found == []
    assert left == []


def test_links_writes_entailment_as_subevent_and_leaves_region_out():
    # Arrange
    relations = [("i3", "entails", "i1"), ("i3", "domain_region", "i4"),
                 ("i4", "has_domain_region", "i3")]

    # Act
    found, left = p.links(relations, lexicon(), {"wncze-3-n"})

    # Assert
    assert found == [("wncze-3-n", "subevent", "wncze-1-n")]
    assert left == []


def test_links_keeps_the_hypernym_a_synset_has_even_when_all_are_linked():
    # Arrange
    relations = [("i2", "hypernym", "i4"), ("i2", "instance_hypernym", "i3"),
                 ("i3", "hypernym", "i1"), ("i3", "hypernym", "i4")]
    everything = {"wncze-1-n", "wncze-2-n", "wncze-3-n", "wncze-4-n"}

    # Act
    found, left = p.links(relations, lexicon(), everything)

    # Assert
    assert found == [("wncze-3-n", "hypernym", "wncze-1-n"),
                     ("wncze-3-n", "hypernym", "wncze-4-n")]
    assert left == [("wncze-2-n", "hypernym", "wncze-4-n"),
                    ("wncze-2-n", "instance_hypernym", "wncze-3-n")]
