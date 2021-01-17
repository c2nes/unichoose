import json
import sys

import xml.etree.ElementTree as ET

# Code point sequence -> set(keywords)
merged_keywords = dict()
control_chars = set()

# -----------------------------------------------------------------------------
# Process CLDR annotations
#
# See https://unicode.org/reports/tr35/tr35-general.html#Annotations
# -----------------------------------------------------------------------------

for path in ("common/annotations/en.xml", "common/annotationsDerived/en.xml"):
    tree = ET.parse(path)
    root = tree.getroot()

    for anno in root.find("annotations").findall("annotation"):
        cp = anno.get("cp")

        # Per https://unicode.org/reports/tr35/tr35-general.html#Annotations
        #
        # "The cp attribute value has two formats: either a single string, or if
        #  contained within […] a UnicodeSet. The latter format can contain
        #  multiple code points or strings."
        #
        # I do not know whether multi code point sequences are allowed (which
        # would make parsing more difficult and I am lazy), but this feature
        # does not seem to be used in the current versions of the annotations
        # and derived annotations files anyway so we just ignore these entries
        # if we happen to find them.
        if cp[0] == "[" and cp[-1] == "]":
            continue

        if anno.get("type") == "tts":
            keywords = set(kw.strip() for kw in anno.text.split(":", 1))
        else:
            keywords = set(kw.strip() for kw in anno.text.split("|"))

        if cp not in merged_keywords:
            merged_keywords[cp] = keywords
        else:
            merged_keywords[cp].update(keywords)

# -----------------------------------------------------------------------------
# Process UCD
#
# See https://unicode.org/reports/tr42/ and section "4.4 Properties" specifically
# -----------------------------------------------------------------------------

NS = {"ucd": "http://www.unicode.org/ns/2003/ucd/1.0"}

# Only list Latin, Greek and Common (Zyyy) characters.
# See "Script (sc)" in PropertyValueAliases.txt (make fetch-docs).
INCLUDE_SCRIPTS = set(["Latn", "Grek", "Zyyy"])

tree = ET.parse("ucd.nounihan.grouped.xml")
root = tree.getroot()

for group in root.find("ucd:repertoire", NS).findall("ucd:group", NS):
    for char in group.findall("ucd:char", NS):
        # Merge char and group attributes
        attrs = dict(group.attrib)
        attrs.update(char.attrib)

        # General_Category
        gc = attrs.get("gc")

        # Skip unassigned characters (Cn)
        if gc[0] == "Cn":
            continue

        # Skip combining marks
        if gc[0] == "M":
            continue

        # Skip modifiers (Modifier_Letter and Modifier_Symbol)
        if gc in ("Lm", "Sk"):
            continue

        # Skip deprecated codepoints
        if attrs.get("Dep") == "Y":
            continue

        # Only include certain scripts
        if attrs.get("sc") not in INCLUDE_SCRIPTS:
            continue

        # Ignore ranges
        if attrs.get("first-cp"):
            continue

        # Get name
        na = attrs.get("na")

        # "If a code point has the attribute na (either directly or by
        #  inheritence from an enclosing group), then occurrences of the
        #  character # in the name are to be interpreted as the value of the
        #  code point"
        if "#" in na:
            continue

        # Build keyword list from na, na1 and any name aliases
        na1 = attrs.get("na1", "")
        keywords = set([na, na1])

        for alias in char.findall("ucd:name-alias", NS):
            keywords.add(alias.get("alias"))

        cp = attrs.get("cp")
        cp = chr(int(cp, 16))
        if cp not in merged_keywords:
            merged_keywords[cp] = keywords
        else:
            merged_keywords[cp].update(keywords)

        if gc[0] == "C":
            control_chars.add(cp)

# -----------------------------------------------------------------------------
# Format output
# -----------------------------------------------------------------------------

# Re-write as sorted array
output = []
for cp, keywords in merged_keywords.items():
    # Convert to lowercase and remove duplicates/empty values
    keywords = set(kw.lower() for kw in keywords if kw)
    keywords = list(sorted(keywords, key=lambda kw: (len(kw), kw)))
    is_control = cp in control_chars
    display = repr(cp)[1:-1] if is_control else cp
    output.append(
        {"cp": cp, "keywords": keywords, "display": display, "is_control": is_control}
    )
output.sort(key=lambda char: (len(char["cp"]), char["cp"]))

json.dump(output, sys.stdout)
sys.stdout.write("\n")
