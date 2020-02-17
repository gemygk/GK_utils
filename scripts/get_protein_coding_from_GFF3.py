#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to get protein coding models from GFF3 file based on biotype

# Monday, 17 February 2020, 10:36AM
"""

# authorship and License information
__author__ = "Gemy George Kaithakottil"
__copyright__ = "Copyright 2020"
__license__ = "MIT"
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
from collections import defaultdict

# check python version
if sys.version_info[0] < 3:
    raise Exception(
        "Please source Python 3, sourcing 'source python_miniconda-4.7.12_py3.7_gk' will do")

# get script name
script =  os.path.basename(sys.argv[0])

# get the GTF/GFF3 attributes
SEQID, SOURCE, TYPE, START, END, SCORE, STRAND, PHASE, ATTRIBUTE  = range(9)

logging.basicConfig(
    format='%(message)s', datefmt='%d-%b-%y %H:%M:%S')

def get_id(file, line, attribute, field):
    if field == "ID":
        try:
            # Check for GFF3 file
            id_search = re.search('ID=([^;]+)', attribute)
            if id_search:
                id = id_search.group(1)
            else:
                logging.error(
                    f"Error: Cannot extract ID from the file '{file}' line below."
                    f" Please check if ID=(for GFF3 input) attribute is present'\n{line}\n")
        except AttributeError as err:
            logging.error(
                f"Error: {err}. '{field}' cannot be extracted from the file '{file}' line below\n{line}")
    elif field == "Parent":
        try:
            # Check for GFF3 file
            id_search = re.search('Parent=([^;]+)', attribute)
            if id_search:
                id = id_search.group(1)
            else:
                logging.error(
                    f"Error: Cannot extract Parent id from the file '{file}' line below."
                    f" Please check if Parent=(for GFF3 input) attribute is present'\n{line}\n")
        except AttributeError as err:
            logging.error(
                f"Error: {err}. '{field}' cannot be extracted from the file '{file}' line below\n{line}")
    try:
        id
    except NameError as err:
        logging.error(
            f"Error: Cannot extract transcript id from the file '{file}', exiting..")
        sys.exit(1)

    return(id)

# process file
def get_protein_coding_from_GFF3(file, gba, gb):
    # get all the gene biotype we care about from gene type
    search_string = f"{gba}={gb}"  # we make "gene_biotype=protein_coding" format here
    gene_info = defaultdict(int)
    with open(file, 'r') as filehandle:
        for line in filehandle:
            line = line.rstrip("\n")
            if re.match(r'^\s*$',line) or line.startswith("#"):
                continue
            else:
                x = line.split("\t")
                if re.search("^(gene)$", x[TYPE], re.I):
                    if re.search(search_string, line, re.I):
                        gene_id = get_id(file, line, x[ATTRIBUTE], "ID")
                        if gene_id not in gene_info:
                            gene_info[gene_id] = 1
    logging.error(
        f"# Count of protein coding genes: {len(gene_info)}")

    if len(gene_info) == 0:
        logging.error(
            f"Error: There are not gene type matching the search string {search_string}, exiting..")
        sys.exit(1)

    # get all the mRNA|transcript|match lines having above gene as its parent attribute
    trans_info = defaultdict(int)
    with open(file, 'r') as filehandle:
        for line in filehandle:
            line = line.rstrip("\n")
            if re.match(r'^\s*$', line) or line.startswith("#"):
                continue
            else:
                x = line.split("\t")
                if re.search("^(mRNA|transcript|match)$", x[TYPE], re.I):
                    gene_id = get_id(file, line, x[ATTRIBUTE], "Parent")
                    if gene_id in gene_info:
                        trans_id = get_id(file, line, x[ATTRIBUTE], "ID")
                        if trans_id not in trans_info:
                            trans_info[trans_id] = 1
    logging.error(
        f"# Count of protein coding transcripts: {len(trans_info)}")

    # now print all the features that matches above dictionaries
    with open(file, 'r') as filehandle:
        for line in filehandle:
            line = line.rstrip("\n")
            if re.match(r'^\s*$', line) or line.startswith("#"):
                print(line)
            else:
                x = line.split("\t")
                if re.search("^(gene)$", x[TYPE], re.I):
                    gene_id = get_id(file, line, x[ATTRIBUTE], "ID")
                    if gene_id in gene_info:
                        print(line)
                elif re.search("^(mRNA|transcript|match)$", x[TYPE], re.I):
                    trans_id = get_id(file, line, x[ATTRIBUTE], "ID")
                    if trans_id in trans_info:
                        print(line)
                elif re.search("^(exon|CDS|five_prime_UTR|three_prime_UTR)$", x[TYPE], re.I):
                    parent_id = get_id(file, line, x[ATTRIBUTE], "Parent")
                    if parent_id in trans_info:
                        print(line)
                else:
                    continue

def main():
    parser = argparse.ArgumentParser(description="Script to get protein coding models from GFF3 file based on biotype", formatter_class=RawTextHelpFormatter,
                                     epilog="Example command:\n\t"
                                     + script +
                                     " --file [file.gff3] --gene_biotype_alias [biotype]"
                                     + "\n\nNote:"
                                     + "\nFor 'gene' type, [GENE_BIOTYPE_ALIAS], give the 'key' as 'gene_biotype' if the gene attribute to be considered has 'gene_biotype=protein_coding' in the attribute field\n"
                                     + "For 'gene' type, [GENE_BIOTYPE], give the 'value' as 'protein_coding' if the gene attribute to be considered has 'gene_biotype=protein_coding' in the attribute field\n"
                                     + "\nThe output will be in same order as input file\n"
                                     "\n\nContact:" + __author__ + "(" + __email__ + ")")
    parser.add_argument("-f", "--file", required=True,
                        nargs='?', help="Provide GFF3 file")
    parser.add_argument("--gene_biotype_alias", required=True,
                        nargs='?', help="Provide the attribute 'key' to be used considered [eg: gene_biotype]")
    parser.add_argument("--gene_biotype", required=True,
                        nargs='?', help="Provide the attribute 'value' to be used considered [eg: protein_coding]")
    args = parser.parse_args()
    file = args.file
    gba = args.gene_biotype_alias
    gb = args.gene_biotype
    get_protein_coding_from_GFF3(file, gba, gb)

if __name__ == "__main__":
    main()
