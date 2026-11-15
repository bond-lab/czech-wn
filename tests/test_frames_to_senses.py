"""Tests of scripts/frames_to_senses.py."""
# ruff: noqa: I001  (release must be imported first: it finds ntumc)

import release  # puts ../NTUMC on the path
import frames_to_senses as f
from ntumc.wordnet.model import Entry, Frame, Sense


def lexicon() -> list:
    def verb(lemma: str, n: int, subcat: str, synset: str = "wncze-1-v") -> Entry:
        return Entry(id=f"wncze-{lemma}-v", lemma=lemma, pos="v", senses=[
            Sense(id=f"{synset}-s{n}", synset=synset, subcat=subcat)])
    return [verb("podplatit", 1, "f1 f2 f3"), verb("koupit si", 2, "f1 f2 f3"),
            verb("uplatit", 3, "f1 f2 f3"), verb("jít", 1, "f4", "wncze-2-v"),
            Frame(id="f1", frame="{podplatit, koupit si} kdo1*AG(person:1)=koho4*PAT(person:1)"),
            Frame(id="f2", frame="kdo1*AG(person:1)=X %bez sloves"),
            Frame(id="f3", frame="{podmazat} kdo1*AG(person:1)=koho4 %none of the synset"),
            Frame(id="f4", frame="?{jít, chodit} kdo1*AG(person:1)=[kam]")]


def test_named_reads_the_verbs_at_the_start():
    # Act
    verbs = [f.named("{podplatit, koupit si} kdo1"), f.named("?{jít} kdo1"),
             f.named("fig {vyjít} co1"), f.named("kdo1*AG(person:1)=X")]

    # Assert
    assert verbs == [["podplatit", "koupit si"], ["jít"], ["vyjít"], []]


def test_placed_takes_a_frame_off_the_verbs_it_does_not_name():
    # Act
    todo = f.placed(lexicon())

    # Assert
    assert todo == {("wncze-1-v", "uplatit"): ("f1 f2 f3", "f2 f3")}


def test_records_carry_the_old_and_new_frames():
    # Arrange
    todo = {("wncze-1-v", "uplatit"): ("f1 f2 f3", "f2 f3")}

    # Act
    made = f.records(todo, 7, "2026-11-15")

    # Assert
    assert [(r.id, r.action, r.synset, r.lemma, r.old, r.new) for r in made] == [
        (f"wncze-{release.BASE_VERSION}-7", "set_frames", "wncze-1-v", "uplatit",
         "f1 f2 f3", "f2 f3")]


def test_placed_gives_a_verb_without_frames_the_frame_that_names_it():
    # Arrange
    late = Entry(id="wncze-chodit-v", lemma="chodit", pos="v", senses=[
        Sense(id="wncze-2-v-s2", synset="wncze-2-v")])
    plain = Entry(id="wncze-kráčet-v", lemma="kráčet", pos="v", senses=[
        Sense(id="wncze-2-v-s3", synset="wncze-2-v")])
    generic = Frame(id="f5", frame="kdo1*AG(person:1)=[kam] %bez sloves")
    items = [*lexicon(), late, plain, generic]
    items[3].senses[0].subcat = "f4 f5"  # jít has the frame that names no verb too

    # Act
    todo = f.placed(items)

    # Assert
    assert todo == {("wncze-1-v", "uplatit"): ("f1 f2 f3", "f2 f3"),
                    ("wncze-2-v", "chodit"): ("", "f4")}
