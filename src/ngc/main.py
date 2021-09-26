#!/usr/bin/env python
""" ngc - n-grams count
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import getopt
import logging
import os
import re
import string
import sys

import unicode2ascii

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: ngc - n-grams count v1.0.2 (September 26, 2021) by Hubert Tournier $"

# Default parameters. Can be superseded by command line options
parameters = {
    "Convert": {
        "Unicode to ASCII": False,
        "Upper to lower case": False,
        "Lower to upper case": False,
        "Spaces to one space": False,
        },
    "Discard": {
        "Unicode characters": False,
        "Upper case letters": False,
        "Lower case letters": False,
        "Connection symbols": False, # ' -
        "Digits": False,
        "Punctuation": False, # . , ; : ! ?
        "Other printable symbols": False,
        "Spaces": False, # space tab return formfeed vtab
        "Control characters": False,
        },
    "Length": 1,
    "Fixed block": False, # Sliding-window mode by default
    "Word boundary": False,
    "Partial": {
        "Discard": False,
        "Keep": True,
        "Justify": False,
        },
    "Show": {
        "Text": False,
        "N-grams": True,
        "Summary": False,
        },
    }

occurrences = {}

summary = {
    "Upper case letters": 0,
    "Lower case letters": 0,
    "Connection symbols": 0,
    "Digits": 0,
    "Punctuation": 0,
    "Other printable symbols": 0,
    "Spaces": 0,
    "Other spaces": 0,
    "Control characters": 0,
    "Unicode letters": 0,
    "Unicode marks": 0,
    "Unicode numbers": 0,
    "Unicode punctuations": 0,
    "Unicode symbols": 0,
    "Unicode separators": 0,
    "Unicode others": 0,
    "All unicode characters": 0,
    "All characters": 0,
    "All n-grams": 0
    }


################################################################################
def initialize_debugging(program_name):
    """Debugging set up"""
    console_log_format = program_name + ": %(levelname)s: %(message)s"
    logging.basicConfig(format=console_log_format, level=logging.DEBUG)
    logging.disable(logging.INFO)


################################################################################
def display_help():
    """Displays usage and help"""
    print("usage: ngc [-b|--block] [-c|--convert ARGS] [--debug]", file=sys.stderr)
    print("       [-d|--discard ARGS] [--help|-?] [-l|--length ARG]", file=sys.stderr)
    print("       [-p|--partial ARG] [-q|--quiet] [-s|--summary] [-t|--text]", file=sys.stderr)
    print("       [--version] [-w|--word] [--] [filename ...]", file=sys.stderr)
    print("  -----------------   ----------------------------------------------------",
        file=sys.stderr
        )
    print("  -b|--block          Use fixed- instead of sliding-windows blocks", file=sys.stderr)
    print("  -c|--convert ARGS   Convert text input. A combination of:", file=sys.stderr)
    print("      ARG = a         - Unicode characters to ASCII (remove accents)", file=sys.stderr)
    print("      ARG = l         - Upper case letters to lower", file=sys.stderr)
    print("      ARG = u         - Lower case letters to upper", file=sys.stderr)
    print("      ARG = s         - Spaces-like characters to 1 space", file=sys.stderr)
    print("                      ARGS l and u can't be used at the same time", file=sys.stderr)
    print("  -d|--discard ARGS   Discard characters. A combination of:", file=sys.stderr)
    print("      ARG = U         - Unicode characters", file=sys.stderr)
    print("      ARG = u         - Upper case letters", file=sys.stderr)
    print("      ARG = l         - Lower case letters", file=sys.stderr)
    print("      ARG = L         - All letters", file=sys.stderr)
    print("      ARG = c         - Connection symbols ('-)", file=sys.stderr)
    print("      ARG = d         - Digits", file=sys.stderr)
    print("      ARG = p         - Punctuation (.,;:!?)", file=sys.stderr)
    print("      ARG = o         - Other printable symbols", file=sys.stderr)
    print("      ARG = s         - Spaces (space, tab, return, formfeed, vtab)", file=sys.stderr)
    print("      ARG = n         - Non printable Control characters", file=sys.stderr)
    print("  -l|--length ARG     Length of the n-gram. Defaults to 1", file=sys.stderr)
    print("  -p|--partial ARG    What to do with partial blocks? One among:", file=sys.stderr)
    print("      ARG = d         - Discard", file=sys.stderr)
    print("      ARG = k         - Keep as-is", file=sys.stderr)
    print("      ARG = j         - Keep but right-justify with spaces", file=sys.stderr)
    print("  -q|--quiet          Don't show occurrences and frequency by n-gram", file=sys.stderr)
    print("  -s|--summary        Show a summary of what was processed", file=sys.stderr)
    print("  -t|--text           Show modified text input", file=sys.stderr)
    print("  -w|--word           Respect Word boundaries (delimited by spaces)", file=sys.stderr)
    print("  --debug             Enable debug mode", file=sys.stderr)
    print("  --help|-?           Print usage and this help message and exit", file=sys.stderr)
    print("  --version           Print version and exit", file=sys.stderr)
    print("  --                  Options processing terminator", file=sys.stderr)
    print(file=sys.stderr)


################################################################################
def process_environment_variables():
    """Process environment variables"""

    if "NGC_DEBUG" in os.environ.keys():
        logging.disable(logging.NOTSET)


################################################################################
def process_command_line():
    """Process command line"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    # option letters followed by : expect an argument
    # same for option strings followed by =
    character_options = "bc:d:l:p:qstw?"
    string_options = [
        "block",
        "convert=",
        "debug",
        "discard=",
        "help",
        "length=",
        "partial=",
        "quiet",
        "summary",
        "text",
        "version",
        "word",
        ]

    try:
        options, remaining_arguments = getopt.getopt(
            sys.argv[1:], character_options, string_options
        )
    except getopt.GetoptError as error:
        logging.critical(error)
        display_help()
        sys.exit(1)

    for option, argument in options:

        if option in ("-b", "--block"):
            parameters["Fixed block"] = True

        elif option in ("-c", "--convert"):
            if 'l' in argument and 'u' in argument:
                logging.critical("-c|--convert parameter can't contain [lu] at the same time")
                sys.exit(1)

            if 'a' in argument:
                parameters["Convert"]["Unicode to ASCII"] = True
            if 'l' in argument:
                parameters["Convert"]["Upper to lower case"] = True
            if 'u' in argument:
                parameters["Convert"]["Lower to upper case"] = True
            if 's' in argument:
                parameters["Convert"]["Spaces to one space"] = True

        elif option in ("-d", "--discard"):
            if 'U' in argument:
                parameters["Discard"]["Unicode characters"] = True
            if 'u' in argument:
                parameters["Discard"]["Upper case letters"] = True
            if 'l' in argument:
                parameters["Discard"]["Lower case letters"] = True
            if 'L' in argument:
                parameters["Discard"]["Upper case letters"] = True
                parameters["Discard"]["Lower case letters"] = True
            if 'c' in argument:
                parameters["Discard"]["Connection symbols"] = True
            if 'd' in argument:
                parameters["Discard"]["Digits"] = True
            if 'p' in argument:
                parameters["Discard"]["Punctuation"] = True
            if 'o' in argument:
                parameters["Discard"]["Other printable symbols"] = True
            if 's' in argument:
                parameters["Discard"]["Spaces"] = True
            if 'n' in argument:
                parameters["Discard"]["Control characters"] = True

        elif option in ("-l", "--length"):
            if argument.isdigit() and int(argument) >= 0:
                parameters["Length"] = int(argument)
            else:
                logging.critical("-l|--length parameter must be a strictly positive integer")
                sys.exit(1)

        elif option in ("-p", "--partial"):
            if len(argument) > 1 or argument not in ('d', 'k', 'j'):
                logging.critical("-p|--partial parameter must be a single character among [dkj]")
                sys.exit(1)

            if argument == 'd':
                parameters["Partial"]["Discard"] = True
                parameters["Partial"]["Keep"] = False
            elif argument == 'j':
                parameters["Partial"]["Justify"] = True
                parameters["Partial"]["Keep"] = False

        elif option in ("-q", "--quiet"):
            parameters["Show"]["N-grams"] = False

        elif option in ("-s", "--summary"):
            parameters["Show"]["Summary"] = True

        elif option in ("-t", "--text"):
            parameters["Show"]["Text"] = True

        elif option in ("-w", "--word"):
            parameters["Word boundary"] = True

        elif option == "--debug":
            logging.disable(logging.NOTSET)

        elif option in ("--help", "-?"):
            display_help()
            sys.exit(0)

        elif option == "--version":
            print(ID.replace("@(" + "#)" + " $" + "Id" + ": ", "").replace(" $", ""))
            sys.exit(0)

    logging.debug("process_command_line(): parameters:")
    logging.debug(parameters)
    logging.debug("process_command_line(): remaining_arguments:")
    logging.debug(remaining_arguments)

    return remaining_arguments


################################################################################
def handle_partial_n_gram(text):
    """Analyze n-grams frequency in a string"""
    # pylint: disable=C0103
    global occurrences, summary
    # pylint: enable=C0103

    if not parameters["Partial"]["Discard"]:
        if parameters["Partial"]["Justify"]:
            for _ in range(parameters["Length"] - len(text)):
                text += " "

        if text in occurrences:
            occurrences[text] += 1
        else:
            occurrences[text] = 1
        summary["All n-grams"] += 1


################################################################################
def frequency_analysis(text):
    """Analyze n-grams frequency in a string"""
    # pylint: disable=C0103
    global occurrences, summary
    # pylint: enable=C0103

    if parameters["Show"]["Summary"]:
        for character in text:
            if ord(character) < 128:
                if character in string.ascii_uppercase:
                    summary["Upper case letters"] += 1
                elif character in string.ascii_lowercase:
                    summary["Lower case letters"] += 1
                elif character in ("'", "-"):
                    summary["Connection symbols"] += 1
                elif character in string.digits:
                    summary["Digits"] += 1
                elif character in (".", ",", ";", ":", "!", "?"):
                    summary["Punctuation"] += 1
                elif character == " ":
                    summary["Spaces"] += 1
                elif character in string.whitespace:
                    summary["Other spaces"] += 1
                elif (ord(character) < 32 and ord(character) not in (9, 11, 12, 13)) \
                or ord(character) == 127:
                    summary["Control characters"] += 1
                else:
                    summary["Other printable symbols"] += 1
            else:
                summary["All unicode characters"] += 1
                if unicode2ascii.is_unicode_letter(character):
                    summary["Unicode letters"] += 1
                elif unicode2ascii.is_unicode_mark(character):
                    summary["Unicode marks"] += 1
                elif unicode2ascii.is_unicode_number(character):
                    summary["Unicode numbers"] += 1
                elif unicode2ascii.is_unicode_punctuation(character):
                    summary["Unicode punctuations"] += 1
                elif unicode2ascii.is_unicode_symbol(character):
                    summary["Unicode symbols"] += 1
                elif unicode2ascii.is_unicode_separator(character):
                    summary["Unicode separators"] += 1
                else:
                    summary["Unicode others"] += 1

    if len(text) <= parameters["Length"]:
        if text:
            handle_partial_n_gram(text)
    else:
        i = 0
        while i < len(text) + 1 - parameters["Length"]:
            sequence = text[i:i + parameters["Length"]]
            if sequence in occurrences:
                occurrences[sequence] += 1
            else:
                occurrences[sequence] = 1
            summary["All n-grams"] += 1
            if parameters["Fixed block"]:
                i += parameters["Length"]
            else:
                i += 1
        if i < len(text):
            handle_partial_n_gram(text[i:])


################################################################################
def process_line(line):
    """Process a text line"""
    # pylint: disable=C0103
    global summary
    # pylint: enable=C0103

    line = line.rstrip(os.linesep)

    # Conversions:
    if parameters["Convert"]["Unicode to ASCII"]:
        line = unicode2ascii.unicode_to_ascii_string(line)
    if parameters["Convert"]["Upper to lower case"]:
        line = line.lower()
    if parameters["Convert"]["Lower to upper case"]:
        line = line.upper()

    # Discards:
    if parameters["Discard"]["Unicode characters"]:
        line = "".join([c for c in line if ord(c) < 128])
    if parameters["Discard"]["Upper case letters"]:
        line = re.sub(r"[A-Z]+", "", line)
    if parameters["Discard"]["Lower case letters"]:
        line = re.sub(r"[a-z]+", "", line)
    if parameters["Discard"]["Connection symbols"]:
        line = re.sub(r"[-']+", "", line)
    if parameters["Discard"]["Digits"]:
        line = re.sub(r"[0-9]+", "", line)
    if parameters["Discard"]["Punctuation"]:
        line = re.sub(r"[\.,;:!\?]+", "", line)
    if parameters["Discard"]["Other printable symbols"]:
        line = re.sub(r"[\"#$&@\[\\\]_`{|}~%()\*+/<=>^]+", "", line)
    if parameters["Discard"]["Spaces"]:
        line = re.sub(r"[" + string.whitespace + r"]+", "", line)
    if parameters["Discard"]["Control characters"]:
        line = "".join(
            [c for c in line if not (ord(c) < 9 or (ord(c) > 13 and ord(c) < 32) or ord(c) == 127)]
            )

    # Late conversions:
    if parameters["Convert"]["Spaces to one space"]:
        line = re.sub(r"[" + string.whitespace + r"]+", " ", line)

    if parameters["Show"]["Text"]:
        print(line)

    if parameters["Word boundary"]:
        # Splitting words on all kind of whitespaces:
        for word in line.split():
            if word:
                frequency_analysis(word)
                summary["All characters"] += len(word)
    else:
        frequency_analysis(line)
        summary["All characters"] += len(line)


################################################################################
def process_file(filename):
    """Process the file designated by filename, line by line"""
    with open(filename, "r") as file:
        for line in file.readlines():
            process_line(line)


################################################################################
def compute_kappa_plaintext():
    """Return kappa_plaintext for the processed input stream"""
    # pylint: disable=C0103
    global occurrences, summary
    # pylint: enable=C0103

    # See https://en.wikipedia.org/wiki/Index_of_coincidence
    index = 0.0
    for occurrence in occurrences.values():
        index += occurrence * (occurrence - 1)
    return index / (summary["All n-grams"] * (summary["All n-grams"] - 1))


################################################################################
def compute_coincidence_index(kappa_plaintext):
    """Return coincidence index for a given kappa_plaintext and alphabet"""
    # pylint: disable=C0103
    global summary
    # pylint: enable=C0103

    if summary["Unicode separators"]:
        # Unknown alphabet size
        return 0

    alphabet_size = 0
    if summary["Upper case letters"]:
        alphabet_size += len(string.ascii_uppercase)
    if summary["Lower case letters"]:
        alphabet_size += len(string.ascii_lowercase)
    if summary["Digits"]:
        alphabet_size += len(string.digits)
    if summary["Connection symbols"]:
        alphabet_size += len("'-")
    if summary["Punctuation"]:
        alphabet_size += len(".,;:?!")
    if summary["Other printable symbols"]:
        alphabet_size += len("\"#$&@[\\]_`{|}~%()*+/<=>^")
    if summary["Spaces"]:
        alphabet_size += 1
    if summary["Other spaces"]:
        alphabet_size += len(string.whitespace) - 1
    if summary["Control characters"]:
        alphabet_size += 29

    return kappa_plaintext * alphabet_size


################################################################################
def main():
    """The program's main entry point"""
    program_name = os.path.basename(sys.argv[0])

    initialize_debugging(program_name)
    process_environment_variables()
    arguments = process_command_line()

    exit_status = 0

    # Reading from files whose name were given as arguments:
    if len(arguments):
        for filename in arguments:
            if os.path.isfile(filename):
                process_file(filename)
            else:
                logging.error("The argument '%s' is not a filename", filename)
                exit_status = 1

    # Reading from standard input as there are no arguments:
    else:
        for line in sys.stdin:
            process_line(line)

    # Displaying occurrences and frequency by n-gram:
    if parameters["Show"]["N-grams"]:
        if parameters["Show"]["Text"]:
            print("--")
        decreasing_occurrences = dict(sorted(occurrences.items(), key=lambda t: t[1], reverse=True))
        for key, value in decreasing_occurrences.items():
            print("'{}'\t{}\t{:.2f}%".format(key, value, (value/summary["All n-grams"])*100))

    # Displaying summary:
    if parameters["Show"]["Summary"]:
        print("==")
        for key, value in summary.items():
            print("{:23s}\t{:d}".format(key, value))

        print()
        kappa_plaintext = compute_kappa_plaintext()
        coincidence_index = compute_coincidence_index(kappa_plaintext)
        print("{:23s}\t{}".format("Kappa-plaintext", kappa_plaintext))
        print("{:23s}\t{}".format("Index of coincidence", coincidence_index))

    sys.exit(exit_status)


if __name__ == "__main__":
    main()
