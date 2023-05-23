# Python std lib
import argparse, sys, os, json

from ltmParser import parseLTM
from ltmRenderer import render


def main():
    # Accept either STDIN or File pointer
    # python ltm.py -in file.ltm -outdir ~/output
    # cat model.ltm | python ltm.py -outdir ~/output

    argparser = argparse.ArgumentParser(
        prog="ltm.py", description="Lightweight Transactional Modeller"
    )
    argparser.add_argument(
        "-i",
        "--infile",
        help="Input LTM file, STDIN will be used if infile not provided",
    )
    argparser.add_argument(
        "-o",
        "--outdir",
        required=True,
        help="Output directory for images, dotfiles and markdown files",
    )
    argparser.add_argument(
        "-a",
        "--arch",
        action="store_true",
        help="Generate summary architecture from individual transactions",
    )
    argparser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Generate a markdown report that contains all the images (OUTDIR/report.md)",
    )
    argparser.add_argument(
        "--title", help="Provide a title for the architecture report"
    )
    argparser.add_argument(
        "-l",
        "--label",
        action="store_true",
        help="Print strings on individual arrows in diagrams",
    )
    argparser.add_argument(
        "-n", "--number", action="store_true", help="Use labels that refer to labels"
    )
    argparser.add_argument(
        "-m",
        "--model",
        action="store_true",
        help="Write the JSON model to the output dir (OUTDIR/model.json)",
    )
    argparser.add_argument(
        "--single",
        help="Single Diagram Mode - provide a single filename to write a diagram to - only prints the first scene (really only used for Obsidian)",
    )
    argparser.add_argument(
        "--html",
        action="store_true",
        help="Print an HTML table for a single scene",
    )

    args = argparser.parse_args()

    if not os.path.exists(args.outdir):
        print(
            "Error: Please provide a valid path for -o/--outdir. Did you forget to create it?"
        )
        sys.exit(-1)

    fd = None
    if args.infile is not None:
        fd = open(args.infile, "r")
    else:
        fd = sys.stdin

    doc = parseLTM(fd)

    if args.model:
        with open(f"{args.outdir}/model.json", "w") as fd:
            fd.write(json.dumps(doc, indent=4, sort_keys=True))

    # print(json.dumps(doc, indent=4, sort_keys=True), end="")

    ## These were the original rendering parameters for jtg.py
    parms = {
        "generateArchDiagram": args.arch,
        "report": args.report,
        "label": args.label,
        "number": args.number,
        "fileNameOverride": args.single,
        "singleMode":True if args.single else False,
        "printSingleModeHtml": args.html
    }

    render(doc, args.outdir, **parms)


if __name__ == "__main__":
    # test()
    main()
