import argparse
import re

import fitz

# Total number of pages in the book
total_page_count = 322

# Page numbers with dark backgrounds
inverted_pages = [
    1, 2, 3,             # Header
    8, 9,                # Connectors: title page
    *range(10, 65, 2),   # Connectors
    66, 67,              # Memory: title page
    *range(68, 79, 2),   # Memory
    80, 81,              # Boards: title page
    *range(82, 285, 2),  # Boards
    286, 287,            # Chips: title page
    *range(288, 319, 2), # Chips
    320, 321, 322        # Footer
]

# Page numbers with light backgrounds (i.e., everything else)
keep_pages = [i for i in range(1, total_page_count + 1) if i not in inverted_pages]

"""
Regex to match four floating point numbers, i.e. "0 0 0 0", "0.1 0.2 0.3 0.4", or ".1 .2 .3 .4"
Explanation: 
( # <- Capturing group, single number
    (?: # <- Non-capturing group, matches non-fractional part
        [0-9]*[.] # <- Any number of digits followed by a dot
    )? # <- Zero or one of this group
    [0-9]+ # <- One or more digits
)
"""
cmyk_args_regex = b"((?:[0-9]*[.])?[0-9]+) ((?:[0-9]*[.])?[0-9]+) ((?:[0-9]*[.])?[0-9]+) ((?:[0-9]*[.])?[0-9]+)"

# Matches "[num] [num] [num] [num] k"
fill_regex = re.compile(cmyk_args_regex + b" (k)")

# Matches "[num] [num] [num] [num] K"
stroke_regex = re.compile(cmyk_args_regex + b" (K)")

# Passed into re.sub to invert the K channel of stroke and fill color operations
def invert_sub(match: re.Match):
    c, m, y, k, op = match.groups()

    if op == b"k" and k == b".98":
        # Dark fill should translate to pure white, not gray
        return b"%b %b %b %b %b" % (c, m, y, b"0", op)
    elif op == b"k" and k == b"0":
        # Pure white fill should translate to dark color, not pure black
        return b"%b %b %b %b %b" % (c, m, y, b".98", op)
    else:
        # Otherwhise, everything else should be naively inverted.
        k = 1 - float(k)
        k = str(k).encode('ascii')
        return b"%b %b %b %b %b" % (c, m, y, k, op)
    
# These are unused because invert_sub programatically inverts now, but this is what it should _ideally_ produce for the book.
color_map = {
    # Fills
    b"0 0 0 1 k": b"0 0 0 0 k", # Full black to full white
    b"0 0 0 .98 k":
    b"0 0 0 0 k", # Dark to full white
    b"0 0 0 0 k": b"0 0 0 .98 k", # Full white to dark
    b"0 0 0 .8 k": b"0 0 0 .2 k", # Dark gray to light gray
    b"0 0 0 .2 K": b"0 0 0 .8 K", # Light gray to dark gray

    # Strokes
    b"0 0 0 0 K": b"0 0 0 1 K", # Full white to full black
    b"0 0 0 1 K": b"0 0 0 0 K", # Full black to full white
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Pinouts Book Cleaner", 
        description="Post-processes the Pinouts Book by NODE and Baptiste to be more suitable for printing and scrolling."
    )

    parser.add_argument("input", help="Path to the original PDF. You can download the latest version at https://pinouts.org")
    parser.add_argument("output", help="Path to the output PDF.")
    parser.add_argument("-d", "--dark", help='Enable "dark mode." Replaces white backgrounds with dark backgrounds.', action='store_true')

    args = parser.parse_args()

    doc = fitz.open(args.input)

    page_nums = keep_pages if args.dark else inverted_pages

    for page_num in page_nums:
        page = doc[page_num - 1]

        # Unifying the contents of the page doesn't leave it exactly as it was before, but it's a lot simpler to deal with, and hopefully there's no visual effects.
        page.clean_contents()
        xref = page.get_contents()[0]

        old_stream = doc.xref_stream(xref)

        new_stream = fill_regex.sub(invert_sub, old_stream)
        new_stream = stroke_regex.sub(invert_sub, new_stream)

        doc.update_stream(xref, new_stream)
    doc.save(args.output)
