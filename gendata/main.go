package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
)

type UniChar struct {
	Display  string   `json:"display"`
	Char     string   `json:"cp"`
	Keywords []string `json:"keywords"`
}

func generate(unichars []*UniChar) error {
	fzfInput := &strings.Builder{}
	for i, char := range unichars {
		fmt.Fprintf(fzfInput, "%d\t%s\t%s\n", i, char.Display, strings.Join(char.Keywords, " | "))
	}

	rofiInput := &strings.Builder{}
	for _, char := range unichars {
		fmt.Fprintf(rofiInput, "%s\t%s\n", char.Display, strings.Join(char.Keywords, " | "))
	}

	out, err := os.Create("data.go")
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = fmt.Fprintf(out, "package data\nconst FZFInput = %q\n", fzfInput.String())
	if err != nil {
		return err
	}

	_, err = fmt.Fprintf(out, "const RofiInput = %q\n", rofiInput.String())
	if err != nil {
		return err
	}

	_, err = fmt.Fprint(out, "var CharIndex = [...]string{")
	if err != nil {
		return err
	}

	for _, char := range unichars {
		_, err = fmt.Fprintf(out, "%q,", char.Char)
		if err != nil {
			return err
		}
	}

	_, err = fmt.Fprint(out, "}\n")
	if err != nil {
		return err
	}

	return nil
}

func main() {
	input := os.Args[1]
	file, err := os.Open(input)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	var unichars []*UniChar
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&unichars); err != nil {
		log.Fatal(err)
	}

	if err := generate(unichars); err != nil {
		log.Fatal(err)
	}
}
