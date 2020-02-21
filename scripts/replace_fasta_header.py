#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to replace fasta header with new header

# Thursday, 16 January 2020, 09:24AM

"""

# authorship and License information
__author__ = "Gemy George Kaithakottil"
__copyright__ = "Copyright 2020"
__license__ = "GNU General Public License v3.0"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "Gemy.Kaithakottil@gmail.com"
__status__ = "Production"
__version__ = "0.1"


# import libraries
import argparse
from argparse import RawTextHelpFormatter
import os
import re
import sys
import logging


# change logging format - https://realpython.com/python-logging/
# format is - time, process_id, user, log level, message
logging.basicConfig(format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# check python version
try:
    assert sys.version_info >= (3, 7)
except AssertionError:
    logging.error(f"Python >=3.7 is required.\nCurrent is Python {sys.version}.\nExiting...")
    sys.exit(1)

# get script name
script =  os.path.basename(sys.argv[0])

# process id
def parse_id(id):
    fasta_info = {}
    with open(id, 'r') as filehandle:
        for line in filehandle:
            line = line.rstrip("\n")
            # remove blank and comments
            if re.match(r'^\s*$',line) or line.startswith("#"):
                pass
            else:
                current_id, new_id = line.split()
                if current_id not in fasta_info:
                    fasta_info[current_id] = new_id
                else:
                    logging.error(f"Duplicate fasta id entry '{current_id}'")
                    sys.exit(1)
    return fasta_info

# replace_fasta_header
def replace_fasta_header(fasta_info, fasta, keep):
    with open(fasta, 'r') as filehandle:
        for line in filehandle:
            line = line.rstrip("\n")
            # remove blank and comments
            if re.match(r'^\s*$',line) or line.startswith("#"):
                pass
            elif line.startswith(">"):
                id_search = re.search('>([^\s]+)',line) # get fasta header
                if id_search:
                    id = id_search.group(1)
                else:
                    logging.error(
                        f"Cannot extract fasta header from the file '{fasta}' line below:\n"
                        f"{line}\n")
                # print(id)
                if id in fasta_info:
                    can_print_rest = True
                    if keep:
                        print(f">{fasta_info[id]} prev_id={id}")
                    else:
                        print(f">{fasta_info[id]}")
                else:
                    can_print_rest = False
            else:
                if can_print_rest:
                    print(line)
                else:
                    pass

def main():
    parser = argparse.ArgumentParser(description="Script to replace fasta header with new header", formatter_class=RawTextHelpFormatter,
            epilog="Note:\n"
            + "[current-new.id.txt] tab-delimited format\n"
            + "current_id   new_id\n"
            + "\nExample command:\n"
            + script + " --fasta [file.fasta] --id [id.txt]" + "\n\nContact:" + __author__ + "(" + __email__ + ")")
    parser.add_argument("--fasta", required=True, nargs='?', help="Provide fasta file")
    parser.add_argument("--id", required=True, nargs='?', help="Provide id format [current-new.id.txt]")
    parser.add_argument("--keep", action='store_true' , help="Retain current fasta header with 'prev_id' tag")
    args = parser.parse_args()
    fasta = args.fasta
    keep = args.keep
    id = args.id

    fasta_info = parse_id(id)
    replace_fasta_header(fasta_info, fasta, keep)

if __name__ == "__main__":
    main()
