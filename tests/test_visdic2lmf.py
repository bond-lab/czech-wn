"""Tests of visdic2lmf: each source field has a place, and nothing is lost."""
# ruff: noqa: I001  (visdic2lmf must be imported first: it finds ntumc)

from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

import visdic2lmf as v  # puts ../NTUMC on the path
from ntumc.wordnet import lmf
from ntumc.wordnet.model import Entry, Frame, Lexicon, Synset

OUT = Path(__file__).parent / "output"
SOURCE = """<wn>
<SYNSET>
  <ILI>i2</ILI><ILI>i1</ILI>
  <ID>ENG20-00000001-n</ID>
  <POS>n</POS>
  <SYNONYM>
    <LITERAL sense="2" lnote="hovor.">pes</LITERAL>
    <LITERAL sense="x1" lnote="">psí rod</LITERAL>
    <LITERAL sense="" lnote=""></LITERAL>
    <WORD>pes</WORD><WORD>psí</WORD><WORD>rod</WORD>
  </SYNONYM>
  <ILR type="hypernym">ENG20-00000002-n</ILR>
  <ILR type="verb_group">CZE-00000009-z</ILR>
  <ILR type="eng_derivative">ENG20-00000003-b</ILR>
  <ILR type="hypernym"/>
  <DEF> šelma psovitá </DEF>
  <DEF>druhá definice</DEF>
  <USAGE>pes štěká</USAGE>
  <SNOTE>ssjč1</SNOTE>
  <SNOTE>did</SNOTE>
  <STAMP>kar 2010/04/12</STAMP>
  <BCS>3</BCS>
  <VERSION>21</VERSION>
  <CREATED>deb 2017-01-02 03:04:05</CREATED>
  <DOMAIN>zoologie</DOMAIN>
  <SUMO type="+">Canine</SUMO>
  <NL>false</NL>
</SYNSET>
<SYNSET>
  <ID>ENG20-00000002-n</ID>
  <POS/>
  <NL>yes</NL>
  <BCS/>
  <DEF>zvíře</DEF>
</SYNSET>
<SYNSET>
  <ID>ENG20-00000003-b</ID>
  <POS>b</POS>
  <SYNONYM><LITERAL sense="1" lnote="">psovsky</LITERAL><WORD>psovsky</WORD></SYNONYM>
</SYNSET>
<SYNSET>
  <ID>CZE-00000004-z</ID>
  <POS>v</POS>
  <SYNONYM>
    <LITERAL sense="1" lnote="">štěkat</LITERAL><WORD>štěkat</WORD>
    <LITERAL sense="1" lnote="">pes</LITERAL><WORD>pes</WORD>
  </SYNONYM>
  <VALENCY><FRAME>kdo1*AG=na koho4</FRAME><FRAME>kdo1*AG</FRAME></VALENCY>
  <VALENCY><FRAME>co1*AG</FRAME></VALENCY>
  <NL>true</NL>
</SYNSET>
<SYNSET>
  <ID>CZE-00000005-z</ID>
  <POS>v</POS>
  <SYNONYM><LITERAL sense="2" lnote="">štěkat</LITERAL><WORD>štěkat</WORD></SYNONYM>
  <VALENCY><FRAME>kdo1*AG</FRAME></VALENCY>
</SYNSET>
</wn>
"""
ILI = {"00000001-n": "i1", "00000002-n": "i7", "00000003-r": "i9"}


def lexicon() -> Lexicon:
    return Lexicon(id="wncze", label="Test", language="cs", email="x@example.org",
                   license="https://example.org/", version="0", namespaces={"dc": v.DC})


@pytest.fixture
def synsets() -> list[ET.Element]:
    return list(ET.fromstring(SOURCE))


@pytest.fixture
def items(synsets):
    return v.convert(synsets, ILI, lexicon())


def synset(items, sid: str) -> Synset:
    return next(i for i in items if isinstance(i, Synset) and i.id == f"wncze-{sid}")


def test_nothing_is_lost(synsets, items):
    assert v.check(synsets, items) == []


def test_nothing_is_lost_through_the_xml_file(synsets, items):
    OUT.mkdir(exist_ok=True)
    path = OUT / "test.xml"

    lmf.write(path, items)

    assert v.check(synsets, list(lmf.read(path))) == []


def test_a_lost_fact_is_reported(synsets, items):
    synset(items, "ENG20-00000001-n").definitions.pop()

    problems = v.check(synsets, items)

    assert problems == ["lost: ('def', 'ENG20-00000001-n', 2, 'druhá definice')"]


def test_what_is_left_out_is_counted(synsets):
    _, left = v.source_facts(synsets)

    assert left == {"WORD": 7, "empty literal": 1, "ILR with no target": 1,
                    "empty pos": 1, "empty bcs": 1}


def test_synset_fields(items):
    ss = synset(items, "ENG20-00000001-n")

    assert (ss.pos, ss.ili, ss.lexicalized) == ("n", "i1", "true")
    assert [d.text for d in ss.definitions] == ["šelma psovitá", "druhá definice"]
    assert [e.text for e in ss.examples] == ["pes štěká"]
    assert ss.members == "wncze-ENG20-00000001-n-s1 wncze-ENG20-00000001-n-s2"
    assert ss.meta == {
        "dc:contributor": "kar", "dc:date": "2010/04/12", "dc:subject": "zoologie",
        "note": "ili=i2; snote=ssjč1; snote=did; bcs=3; version=21; "
                "created=deb 2017-01-02 03:04:05; sumo=+ Canine"}


def test_relations_keep_their_own_name_where_it_is_not_the_usual_one(items):
    rels = synset(items, "ENG20-00000001-n").relations

    assert [(r.link, r.target, r.meta) for r in rels] == [
        ("hypernym", "wncze-ENG20-00000002-n", {}),
        ("similar", "wncze-CZE-00000009-z", {"dc:type": "verb_group"}),
        ("other", "wncze-ENG20-00000003-b", {"dc:type": "eng_derivative"})]


def test_a_missing_relation_target_gets_a_marked_synset(items):
    stub = synset(items, "CZE-00000009-z")

    assert (stub.pos, stub.ili, stub.meta) == ("n", "", {"note": "inferred=synset"})


def test_missing_pos_and_ili_are_filled_in_and_marked(items):
    no_pos = synset(items, "ENG20-00000002-n")
    adverb = synset(items, "ENG20-00000003-b")

    assert (no_pos.pos, no_pos.ili, no_pos.lexicalized) == ("n", "i7", "false")
    assert no_pos.meta["note"] == "inferred=pos; inferred=ili"
    assert (adverb.pos, adverb.ili) == ("r", "i9")


def test_an_unusual_nl_value_is_kept(items):
    ss = synset(items, "CZE-00000004-z")

    assert ss.lexicalized == "false"
    assert ss.meta["note"] == "valency=2 1; nl=true"


def test_one_entry_for_a_word_and_a_part_of_speech(items):
    entries = {(e.lemma, e.pos): e for e in items if isinstance(e, Entry)}

    assert set(entries) == {("pes", "n"), ("psí rod", "n"), ("psovsky", "r"),
                            ("štěkat", "v"), ("pes", "v")}
    assert entries[("psí rod", "n")].id == "wncze-psí_0020_rod-n"
    assert [(s.synset, s.n) for s in entries[("štěkat", "v")].senses] == [
        ("wncze-CZE-00000004-z", "1"), ("wncze-CZE-00000005-z", "2")]


def test_sense_number_and_note(items):
    senses = {s.id: s for e in items if isinstance(e, Entry) for s in e.senses}

    first = senses["wncze-ENG20-00000001-n-s1"]
    second = senses["wncze-ENG20-00000001-n-s2"]
    assert (first.n, first.meta) == ("2", {"note": "hovor."})
    assert (second.n, second.meta) == (None, {"dc:identifier": "x1"})


def test_a_frame_is_written_once_and_shared(items):
    frames = {f.frame: f.id for f in items if isinstance(f, Frame)}
    senses = {s.id: s for e in items if isinstance(e, Entry) for s in e.senses}

    assert frames == {"kdo1*AG=na koho4": "wncze-frame-1", "kdo1*AG": "wncze-frame-2",
                      "co1*AG": "wncze-frame-3"}
    assert senses["wncze-CZE-00000004-z-s2"].subcat == "wncze-frame-1 wncze-frame-2 wncze-frame-3"
    assert senses["wncze-CZE-00000005-z-s1"].subcat == "wncze-frame-2"


def test_unknown_element_is_refused():
    bad = list(ET.fromstring("<wn><SYNSET><ID>CZE-1</ID><NEW>x</NEW></SYNSET></wn>"))

    with pytest.raises(ValueError, match="NEW"):
        v.source_facts(bad)


def test_words_that_are_not_the_literals_are_refused():
    bad = list(ET.fromstring(
        "<wn><SYNSET><ID>CZE-1</ID><SYNONYM><LITERAL>pes</LITERAL><WORD>kočka</WORD>"
        "</SYNONYM></SYNSET></wn>"))

    with pytest.raises(ValueError, match="WORD"):
        v.source_facts(bad)


def test_ili_key():
    assert v.ili_key("ENG20-00001740-b") == "00001740-r"
    assert v.ili_key("CZE-00000002-z") is None
