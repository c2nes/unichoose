
unicode.tsv: unicode.json
	python3 make_tsv.py < unicode.json > unicode.tsv

unicode.json: ucd.nounihan.grouped.xml make_json.py
	python3 make_json.py > unicode.json

ucd.nounihan.grouped.xml: ucd.nounihan.grouped.zip
	unzip -o ucd.nounihan.grouped.zip
	touch ucd.nounihan.grouped.xml

ucd.nounihan.grouped.zip:
	curl -fLO "https://www.unicode.org/Public/UCD/latest/ucdxml/ucd.nounihan.grouped.zip"

PropertyValueAliases.txt:
	curl -fLO "https://www.unicode.org/Public/UCD/latest/ucd/PropertyValueAliases.txt"

PropertyAliases.txt:
	curl -fLO "https://www.unicode.org/Public/UCD/latest/ucd/PropertyAliases.txt"

fetch-docs: PropertyAliases.txt PropertyValueAliases.txt

fmt:
	black *.py

clean:
	rm -f unicode.json unicode.tsv ucd.nounihan.grouped.xml ucd.nounihan.grouped.zip PropertyValueAliases.txt PropertyAliases.txt

.PHONY: fetch-docs fmt clean
