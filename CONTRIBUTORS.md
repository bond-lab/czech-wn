# Contributors

## Creators

The Czech WordNet is the work of the Natural Language Processing Centre,
Faculty of Informatics, Masaryk University, Brno
(<https://deb.fi.muni.cz/>, <https://nlp.fi.muni.cz/>).  The people
named in its publications are

- Karel Pala
- Adam Rambousek
- Aleš Horák
- Pavel Smrž
- Sandra Tukačová

Many more people edited it.  The source records who last changed a
synset, by account name (`xcapek1`, `hugo`, `kar`, `smrz`, ...), and the
WN-LMF lexicon keeps that name in `dc:contributor`.  We do not know the
person behind every account, so they are not listed here by name.

Marek Blahuš made the extended version in
`sources/wncze-blahus.xml.zip` in his diploma thesis (2011, advisor
Karel Pala).  That version is built on one with derivational relations,
made by Karel Pala and Dana Hlaváčková (2007).

Adam Rambousek gave us the three files in `sources/` and the licence
(2026-11-05).

## Additions

The words in `additions/2025-04/` were made by Francis Bond and checked
and improved by Kateřina Daňková.

Students in two courses at Palacký University (*Syntax and Semantics*,
Asian Studies (KAS/[45]UJ2): 2024, 2025; and *Lexicology*, Linguistics
(KOL/LEXI): 2026) used the wordnet in tagging Karel Čapek's *Válka s
Mloky* "War with the Newts". They proposed new senses, synsets,
definitions and example as part of this.

Concepts that are not in Princeton WordNet are named by omw-ntumc
(<https://github.com/bond-lab/omw-ntumc>) and omw-pronoun
(<https://github.com/omwn/omw-pronoun>).

## Conversion to WN-LMF

- Francis Bond

`visdic2lmf.py` follows `visdic2lmf.py` in
curated-wordnets and the earlier `ces2tab.py`, which was based on a
Jupyter notebook from the DEBVisDic group.
