
unichoose is a simple Unicode character selector with [Rofi](https://github.com/davatorium/rofi) and [fzf](https://github.com/junegunn/fzf) frontends.

# Getting started

Requirements,

* `rofi` or `fzf`
* `go` (setup only)
* `python3` (setup only)
* `curl` (setup only)
* `make` (setup only)
* `unzip` (setup only)

Setup,

```
git clone https://github.com/c2nes/unichoose
cd unichoose
make

# Install somewhere in $PATH (optional)
sudo cp unichoose /usr/local/bin
```

Usage,

``` shellsession
$ ./unichoose -h
usage: ./unichoose [options] [--] [rofi/fzf options...]

  -h     show this help
  -rofi  rofi mode (default)
  -fzf   fzf mode
  -n     suppress newline in output

# Try entering "smiling" and choose "smiling face with open mouth"
$ ./unichoose
😃
```

Screen shot,

![Screenshot of unichoose](screenshot.png)
