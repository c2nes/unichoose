import json
import sys

import xml.etree.ElementTree as ET

NS = {"ucd": "http://www.unicode.org/ns/2003/ucd/1.0"}

tree = ET.parse("ucd.nounihan.grouped.xml")
root = tree.getroot()

# See https://unicode.org/reports/tr42/ and section "4.4 Properties" specifically


def attr(name, char, group):
    value = char.get(name) or group.get(name)
    if value:
        return value

    # "The Name_Alias property is represented by zero or more
    #  name-alias child elements."
    if name == "na":
        for alias in char.findall("ucd:name-alias", NS):
            if alias.get("type") != "abbreviation":
                return alias.get("alias")

    return None


# Only list Latin, Greek and Common (Zyyy) characters.
# See "Script (sc)" in PropertyValueAliases.txt (make fetch-docs).
scripts = set(["Latn", "Grek", "Zyyy"])

output = []

for group in root.find("ucd:repertoire", NS).findall("ucd:group", NS):
    for char in group.findall("ucd:char", NS):
        # General_Category
        gc = attr("gc", char, group)

        # Skip control characters including unassigned characters (Cn)
        if gc[0] == "C":
            continue

        # Skip combining marks
        if gc[0] == "M":
            continue

        # Skip modifiers (Modifier_Letter and Modifier_Symbol)
        if gc in ("Lm", "Sk"):
            continue

        # Skip deprecated codepoints
        if attr("Dep", char, group) == "Y":
            continue

        # Only include certain scripts
        if attr("sc", char, group) not in scripts:
            continue

        # Ignore ranges
        if attr("first-cp", char, group):
            continue

        # Get name or name alias
        na = attr("na", char, group)

        # "If a code point has the attribute na (either directly or by
        #  inheritence from an enclosing group), then occurrences of the
        #  character # in the name are to be interpreted as the value of the
        #  code point"
        if "#" in na:
            continue

        cp = attr("cp", char, group)

        attrs = dict(group.attrib)
        attrs.update(char.attrib)

        attrs["_name"] = na
        attrs["_char"] = chr(int(cp, 16))
        attrs = dict((k, v) for k, v in attrs.items() if v)

        output.append(attrs)

json.dump(output, sys.stdout)
sys.stdout.write("\n")
