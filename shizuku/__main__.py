import argparse
import sys
import csv
import logging

from . import ShizukuRec

logger = logging.getLogger("shizuku")

parser = argparse.ArgumentParser("shizuku", description="Extract data from ShizukuRec files (AVHzY CT-3 USB multimeter) as csv.")
parser.add_argument('infile', nargs='?', type=argparse.FileType('rb'), default=sys.stdin, help="File to read")
parser.add_argument("-o", '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="File to write csv dump")
parser.add_argument("-v", '--verbose', action='store_true', help="Enable logging")


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    # create reader and writer
    logger.debug("Reading from %s", args.infile)
    rec_in = ShizukuRec(args.infile)
    logger.debug("Loaded %s", rec_in)

    logger.debug("Writing to %s", args.outfile)
    rec_out = csv.writer(args.outfile)

    # write header
    rec_out.writerow(rec_in.header)

    # write rows
    for r in rec_in.data:
        rec_out.writerow(r)

    logger.debug("Done")
