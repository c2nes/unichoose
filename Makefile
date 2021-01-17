
unichoose: data/data.go
	go build .

data/data.go: data.json
	go generate ./data

data.json: ucd.nounihan.grouped.xml common/annotations/en.xml common/annotationsDerived/en.xml make_data.py
	python3 make_data.py > data.json

ucd.nounihan.grouped.xml: ucd.nounihan.grouped.zip
	unzip -o $< $@
	touch $@

common/annotations/en.xml: cldr-common-38.1.zip
	unzip -o $< $@
	touch $@

common/annotationsDerived/en.xml: cldr-common-38.1.zip
	unzip -o $< $@
	touch $@

ucd.nounihan.grouped.zip:
	curl -fLO "https://www.unicode.org/Public/UCD/latest/ucdxml/ucd.nounihan.grouped.zip"

cldr-common-38.1.zip:
	curl -fLO "https://unicode.org/Public/cldr/38.1/cldr-common-38.1.zip"

PropertyValueAliases.txt:
	curl -fLO "https://www.unicode.org/Public/UCD/latest/ucd/PropertyValueAliases.txt"

PropertyAliases.txt:
	curl -fLO "https://www.unicode.org/Public/UCD/latest/ucd/PropertyAliases.txt"

fetch-docs: PropertyAliases.txt PropertyValueAliases.txt

fmt:
	black *.py

clean:
	rm -rf *.json *.xml *.zip common/ data/data.go unichoose

.PHONY: fetch-docs fmt clean bins
