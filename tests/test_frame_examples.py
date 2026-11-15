"""Tests of scripts/frame_examples.py."""
# ruff: noqa: I001  (release must be imported first: it finds ntumc)

import release  # puts ../NTUMC on the path
import frame_examples as x
from ntumc.wordnet.model import Entry, Frame, Sense, Synset, Text


def lexicon() -> list:
    return [Entry(id="wncze-dívat_se-v", lemma="dívat se", pos="v", senses=[
                Sense(id="wncze-1-v-s1", synset="wncze-1-v", subcat="f1 f2 f3")]),
            Synset(id="wncze-1-v", ili="i1", pos="v",
                   examples=[Text(text="dívá se z okna")]),
            Frame(id="f1", frame="{dívat se} kdo1*AG(person:1)=na co4 "
                                 "%dívali se na film, na televizi %dívá se z okna"),
            Frame(id="f2", frame="{koukat} kdo1*AG(person:1)=X %kouká jako blázen"),
            Frame(id="f3", frame="kdo1*AG(person:1)=X")]


def test_examples_keeps_the_text_after_each_percent_whole():
    # Act
    texts = x.examples("kdo1=co4 %dívali se na film, na televizi% dívá se z okna, ")

    # Assert
    assert texts == ["dívali se na film, na televizi", "dívá se z okna"]


def test_found_leaves_out_what_is_there_and_frames_for_other_verbs():
    # Act
    todo, left = x.found(lexicon())

    # Assert
    assert todo == [("wncze-1-v", "f1", "dívali se na film, na televizi")]
    assert left == 1


def test_records_name_the_frame_as_the_source():
    # Act
    made = x.records([("wncze-1-v", "f1", "dívali se na film")], 3, "2026-11-15")

    # Assert
    assert [(r.id, r.action, r.synset, r.new) for r in made] == [
        (f"wncze-{release.BASE_VERSION}-3", "add_example", "wncze-1-v", "dívali se na film")]
    assert "f1" in made[0].source
