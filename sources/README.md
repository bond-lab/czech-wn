# Sources

The files as we received them.  Nothing here is edited, except where
noted.

## Czech WordNet (CC BY-SA 4.0)

From the Natural Language Processing Centre, Faculty of Informatics,
Masaryk University (<https://deb.fi.muni.cz/>), sent by Adam Rambousek
on 2026-11-05, who wrote: "Feel free to combine and extend any data as
you see fit. As for the license, consider all three files as released
under CC BY-SA."  All three are DEBVisDic XML and come from the same
base; each adds different synsets.

| file | from | sha256 |
|---|---|---|
| `wncze21.xml.zip` | <https://deb.fi.muni.cz/dl/wncze21.xml.zip> | `ed96ff10a46600614f5e8f7e681fc5021e0445cbc2023b9c38f3fa505b89cff1` |
| `wncze-blahus.xml.zip` | <https://deb.fi.muni.cz/dl/wncze-blahus.xml.zip> | `7d6959315cf0775f11c327ab3a472768d6469e70c2e9e653848086b3ee255df9` |
| `wncze-ext.xml.zip` | <https://deb.fi.muni.cz/dl/wncze-ext.xml.zip> | `1c5b66926f467cd0c8e02843c966e59ff9ad69b54777d70483913d85a4b94c33` |

* `wncze21.xml.zip`: the latest version in DEBVisDic, 28,468 synsets.
  Release 2.1 is made from it.
* `wncze-blahus.xml.zip`: 40,919 synsets.  Extended automatically by
  Marek Blahuš (diploma thesis, 2011, <https://is.muni.cz/th/ukl2c/>):
  the English words of Princeton WordNet synsets were translated with
  Josef Fronek's *Velký anglicko-český slovník* (LEDA, 2006) and
  confident matches were added.  It also has derivational relations
  (`derived`, `eng_derivative`).  **Not checked by hand**: a check of 600
  synsets, reported in a bachelor's thesis, found that 30% had wrong
  or unwanted synonyms and 20% of the new synsets had the wrong
  hypernym; the version was not to be published before thorough
  editing, though it is available for research.
* `wncze-ext.xml.zip`: 28,667 synsets.  Extended a little in a
  linguistics thesis at the University of Naples (200 new synsets, with
  definitions and examples).

The verb frames (`VALENCY`) probably come from VerbaLex:
<http://hdl.handle.net/11234/1-2824>.

## PDT annotation dictionary (a different licence)

`nas_anotacni_slovnik.xml` is **not** covered by the CC BY-SA licence
of this repository.  It is the version of the Czech WordNet used to
annotate the Prague Dependency Treebank, from
<https://lindat.mff.cuni.cz/repository/handle/11858/00-097C-0000-0001-487A-4>.
Its licence is CC BY-NC-SA 3.0 (non-commercial); see the record for
the terms.

It is an older VisDic XML (23,094 synsets, ISO-8859-2, with the sense
number in a `SENSE` element and the relation type in a `TYPE` element).
One change was made to the file: `<wn>` and `</wn>` were added around
the synsets so that it parses.  It is kept for reference and is not
part of any release; `scripts/visdic2lmf.py` does not read it.

sha256 `7b507541928215e783d9d7cc402ae52ead0838372becf69c4ffa1ae645ea88dd`
