import sys
import io
import subprocess
import argparse
import tempfile

import ghostscript

def run_cpdf(args):
    process = subprocess.run([
        "cpdf",
        *args
    ], 
    capture_output=True)

    if process.returncode != 0:
        print("CPDF call failed! Error below:", file=sys.stderr)
        print(process.stderr.decode(), file=sys.stderr)
        sys.exit(1)

def split_cpdf(in_file, temp_folder):
   run_cpdf(["-split", in_file, "-o", f"{temp_folder}/page-%%%.pdf"])

def merge_cpdf(in_files, temp_folder):
    run_cpdf(["-merge", *in_files, "-o", f"{temp_folder}/temp.pdf"])

def copy_annotations_cpdf(original_file, out_file, temp_folder):
    run_cpdf(["-copy-annotations", original_file,  f"{temp_folder}/temp.pdf", "-o", out_file])

total_page_count = 323
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Pinouts Book Cleaner", 
        description="Post-processes the Pinouts Book by NODE and Baptiste to be more suitable for printing and scrolling."
    )

    parser.add_argument("input", help="Path to the original PDF. You can download the latest version at https://pinouts.org")
    parser.add_argument("output", help="Path to the output PDF.")

    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as temp_folder:
        print("Splitting pages...")
        split_cpdf(args.input, temp_folder)

        keep_pages = [i for i in range(1, total_page_count) if i not in inverted_pages]

        for i in inverted_pages:
            # These values best create a fully white background.
            # 1.2 - C, 1.2 - M, 1.2 - Y, 1 * K
            injected_postscript = "{1.2 exch sub}{1.2 exch sub}{1.2 exch sub}{1 mul} setcolortransfer"

            gs_args = [
                "printable-pinout",
                "-o", f"{temp_folder}/inverted-{i:03d}.pdf",
                "-sDEVICE=pdfwrite",
                "-c", injected_postscript, 
                "-f", f"{temp_folder}/page-{i:03d}.pdf"
            ]

            stdout = io.BytesIO()
            stderr = io.BytesIO()

            print(f"Inverting page {i}/{total_page_count}...")
            ghostscript.Ghostscript(*gs_args, stdin=None, stdout=stdout, stderr=stderr)

        out_pages = [(i, False) for i in keep_pages] + [(i, True) for i in inverted_pages]
        out_pages.sort(key=lambda x: x[0])

        concat_paths = []
        for i, inverted in out_pages:
            if inverted:
                concat_paths.append(f"{temp_folder}/inverted-{i:03d}.pdf")
            else:
                concat_paths.append(f"{temp_folder}/page-{i:03d}.pdf")

        print("Merging pages...")
        merge_cpdf(concat_paths, temp_folder)

        print("Copying ToC links...")
        copy_annotations_cpdf(args.input, args.output, temp_folder)

        print("Done!")
