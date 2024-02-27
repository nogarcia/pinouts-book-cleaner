# Pinouts Book Cleaner

The [Pinouts Book](https://pinouts.org) by [NODE](https://n-o-d-e.net) and Baptiste is an _excellent_ resource with a nice, clean design, but quickly scrolling through it can be headache inducing because of its alternating black-and-white color scheme. This Python script uses [CPDF](https://community.coherentpdf.com) and [Ghostscript](https://www.ghostscript.com) to invert the colors on the right pages to produce a PDF version with all white backgrounds. The processed version is a little easier on the eyes while scrolling and potentially more printable. :)

# Using

First make sure you have [CPDF](https://github.com/coherentgraphics/cpdf-binaries) and [Ghostscript](https://www.ghostscript.com/releases/gsdnld.html) installed and **added to your PATH**. Grab a copy of the book from [https://pinouts.org]. Then clone/download this repository and run the script:

```shell
$ git clone https://github.com/nogarcia/pinouts-book-cleaner
$ cd pinouts-book-cleaner
$ python clean.py path/to/original-pinouts.pdf path/to/output.pdf
```

# License

This repository is licensed under the [MIT License](./LICENSE.md), but both the Pinouts Book and the resultance file from this script are licensed [CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/) (no version specified, defer to original authors.)
