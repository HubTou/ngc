# Installation
pip install [pnu-ngc](https://pypi.org/project/pnu-ngc/)

# ngc(1)

## NAME
ngc - n-grams count

## SYNOPSIS
**ngc**
\[-b|--block\]
\[-c|--convert ARGS\]
\[-d|--discard ARGS\]
\[-l|--length ARG\]
\[-p|--partial ARG\]
\[-q|--quiet\]
\[-s|--summary\]
\[-t|--text\]
\[-w|--word\]
\[--debug\]
\[--help|-?\]
\[--version\]
\[--\]
\[filename ...\]

## DESCRIPTION
The **ngc** utility is used for counting the number of occurrences and computing the frequency of [n-grams](https://en.wikipedia.org/wiki/N-gram) in [cryptanalysis](https://en.wikipedia.org/wiki/Cryptanalysis).

For n=1, the n-gram is simply a letter or character. For n=2, the n-gram is called a bigram or digraph. And so on...

The **-l** option is for setting the length of the n-gram (the default is 1 character), and the **-b** option for using a fixed-window instead of the default sliding one ("ABCD" giving "AB" and "CD" instead of "AB", "BC" and "CD").

The **-c** option is used to perform some prior conversions on your input data: Unicode characters removal (especially accented ones), upper to lower case conversions (or the reverse), extra spaces removal (this last one is performed after other conversions).

You can also use the **-d** option to discard selected categories of characters (for example if you only want to keep letters).

If you want to check your input data after these transformations, you can use the **-t** option to print it.

If you want to print only this, you can use the **-q** option.

And if you want to print some stats on the remaining characters, you can print a summary with the **-s** option.
This summary also includes the [coincidence index](https://en.wikipedia.org/wiki/Index_of_coincidence) of your input text.

Finally, you can use the **-w** option to process your input word by word instead of line by line.
If you selected the fixed-window **-b** option, you can decide what to do with partial blocks with the **-p** option:
between keeping them as-is, discarding them, or filling them with spaces in order to have only n-grams of the same length.

The **ngc** utility processes all the indicated file names as one file.
If none are provided, it processes the standard input, thus behaving as a filter.

### OPTIONS
Options | Use
------- | ---
-b\|--block|Use fixed- instead of sliding-windows blocks
-c\|--convert ARGS|Convert text input. A combination of:
&nbsp;|**a** / Unicode characters to ASCII (remove accents)
&nbsp;|**l** / Upper case letters to lower
&nbsp;|**u** / Lower case letters to upper
&nbsp;|**s** / Spaces-like characters to 1 space
&nbsp;|Warning: **l** and **u** can't be used at the same time
-d\|--discard ARGS|Discard characters. A combination of:
&nbsp;|**U** / Unicode characters
&nbsp;|**u** / Upper case letters
&nbsp;|**l** / Lower case letters
&nbsp;|**L** / All letters
&nbsp;|**c** / Connection symbols (apostrophe and hyphen)
&nbsp;|**d** / Digits
&nbsp;|**p** / Punctuation (.,;:?!)
&nbsp;|**o** / Other printable symbols
&nbsp;|**s** / Spaces (space, tab, return, formfeed, vtab)
&nbsp;|**n** / Non printable control characters
-l\|--length ARG|Length of the n-gram. Defaults to 1
-p\|--partial ARGS|What to do with partial blocks? One among:
&nbsp;|**d** / Discard
&nbsp;|**k** / Keep as-is (default)
&nbsp;|**j** / Keep but right-justify with spaces
-q\|--quiet|Don't show occurrences and frequency by n-gram
-s\|--summary|Show a summary of what was processed
-t\|--text|Show modified text input
-w\|--word|Respect Word boundaries (delimited by spaces)
--debug|Enable debug mode
--help\|-?|Print usage and a short help message and exit
--version|Print version and exit
--|Options processing terminator

## ENVIRONMENT
The NGC_DEBUG environment variable can also be set to any value to enable debug mode.

## EXIT STATUS
The **ngc** utility exits 0 on success, and >0 if an error occurs.

## SEE ALSO
[wc(1)](https://www.freebsd.org/cgi/man.cgi?query=wc),
[caesar(1)](https://www.freebsd.org/cgi/man.cgi?query=caesar),
[Frequency analysis](https://en.wikipedia.org/wiki/Frequency_analysis),
[Index of coincidence](https://en.wikipedia.org/wiki/Index_of_coincidence)

## STANDARDS
The **ngc** utility is not a standard UNIX/POSIX command.

It tries to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for [Python](https://www.python.org/) code.

## HISTORY
This utility was made for [The PNU project](https://github.com/HubTou/PNU), while playing with a reimplementation of the [caesar(1)](https://www.freebsd.org/cgi/man.cgi?query=caesar) utility.

## LICENSE
This utility is available under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

## AUTHORS
[Hubert Tournier](https://github.com/HubTou)

