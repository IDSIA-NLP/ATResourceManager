#!/usr/bin/env python3
# vim: syntax=python tabstop=2 expandtab
# -*- coding: utf-8 -*-

"""
Description: 
Authors:
  Joseph Cornelius
  Harald Detering
November 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
import json
import bz2

from loguru import logger
from collections import Counter

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------

@click.command()
@click.option('-f', '--ref-file', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref.json', 
              help='Path to arthropod cross-ref properties.')
@click.option('-o', '--out-file', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref_stats.json', 
              help='Path to output file.')
def main(ref_file, out_file):
    """Evaluate arthropod wikidata

    Get number of occurrences for each properties and the count of properties 
    per wikidata arthropod.


    Args:
        ref_file : Path to arthropod cross-ref properties.
        out_file : Path to output file.

    Returns:
        None
    """

    # Setup logger
    logger.add("./logs/crossref_arthro_stats.log", rotation="100 KB")
    logger.info(f'Start ...')
    # TODO: write CLI args to log
    #logger.info('Argparse arguments:\n'+' \n'.join(f'\t{k: <15} : {v: <80}' for k, v in vars(args).items()))

    arthro_to_ref_count = {}
    all_refs = []
    logger.info(f'Read arthropods ...')
    c = 0 
    with open(ref_file, mode="r") as f:

        for line in f:
            c += 1
            if c % 50000 == 0: logger.info(f"Entry count: {c}")
            
            arthro_wiki = json.loads(line)

            try:
                arthro_to_ref_count[arthro_wiki['id']] = {
                    "cross-ref-count": len(arthro_wiki['crossRef']),
                    "label": arthro_wiki['label'],
                    "cross-ref": arthro_wiki['crossRef'],
                }
                all_refs += arthro_wiki['crossRef']
                        
            except:
                pass
    
    logger.info(f'Write stats to file.')
    out_dict = {}
    out_dict['occurrence'] = dict(Counter(all_refs))
    out_dict['wikidata'] = arthro_to_ref_count
    with open(out_file, mode="w") as of:
        json.dump(out_dict, of)
    
    logger.info('Done!')

# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
