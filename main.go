package main

import (
	"bytes"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"strconv"

	"github.com/c2nes/unichoose/data"
)

func main() {
	flag.Usage = func() {
		out := flag.CommandLine.Output()
		fmt.Fprintf(out, `usage: %s [options] [--] [rofi/fzf options...]

  -h     show this help
  -rofi  rofi mode (default)
  -fzf   fzf mode
  -n     suppress newline in output
`, os.Args[0])
	}

	var rofi bool
	var fzf bool
	var suppressNewline bool

	flag.BoolVar(&rofi, "rofi", false, "rofi mode (default)")
	flag.BoolVar(&fzf, "fzf", false, "fzf mode")
	flag.BoolVar(&suppressNewline, "n", false, "suppress newline")
	flag.Parse()

	rest := flag.Args()
	if rofi && fzf {
		log.Fatal("Only one of -rofi and -fzf may be specified")
	}

	// Default to rofi mode if no mode specified
	if !rofi && !fzf {
		rofi = true
	}

	var cmd *exec.Cmd

	if rofi {
		args := []string{"-dmenu", "-i", "-p", "unichoose", "-format", "i", "-no-custom"}
		args = append(args, rest...)
		cmd = exec.Command("rofi", args...)
		cmd.Stdin = bytes.NewBufferString(data.RofiInput)
	} else {
		args := []string{"-d", "\\t", "--with-nth=2.."}
		args = append(args, rest...)
		cmd = exec.Command("fzf", args...)
		cmd.Stdin = bytes.NewBufferString(data.FZFInput)
	}

	cmd.Stderr = os.Stderr

	pipe, err := cmd.StdoutPipe()
	if err != nil {
		log.Fatal(err)
	}

	if err := cmd.Start(); err != nil {
		log.Fatal(err)
	}

	out, err := ioutil.ReadAll(pipe)
	if err != nil {
		log.Fatal(err)
	}

	if err := cmd.Wait(); err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			os.Exit(exitErr.ExitCode())
		}

		log.Fatal(err)
	}

	idx := bytes.IndexAny(out, "\t\n")
	if idx > 0 {
		s := string(out[:idx])
		n, err := strconv.Atoi(s)
		if err != nil {
			// Assume some sort of unusual output (e.g. --help output)
			os.Stdout.Write(out)
		} else {
			c := data.CharIndex[n]
			if suppressNewline {
				fmt.Print(c)
			} else {
				fmt.Println(c)
			}
		}
	}
}
