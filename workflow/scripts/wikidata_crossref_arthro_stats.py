# -*- coding: utf-8 -*-

"""
Description: 
Author: Joseph Cornelius
April 2021
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
import json
import bz2

from loguru import logger
from collections import Counter

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------

def main(logger, args):
    """Get number of occurrences for each properties and the count of properties 
        per wikidata arthropod.


    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """
    arthro_to_ref_count = {}
    all_refs = []
    logger.info(f'Read arthropods ...')
    c = 0 
    with open(args.ref_file, mode="r") as f:

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
    with open(args.out_file, mode="w") as of:
        json.dump(out_dict, of)
# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("./logs/crossref_arthro_stats.log", rotation="100 KB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Evaluate arthropod wikidata"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-f', '--ref_file', metavar='ref_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref.json', 
                        help='Path to arthropod cross-ref properties.')
    parser.add_argument('-o', '--out_file', metavar='out_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref_stats.json', 
                        help='Path to arthropod cross-ref properties.')
    args = parser.parse_args()
    logger.info('Argparse arguments:\n'+' \n'.join(f'\t{k: <15} : {v: <80}' for k, v in vars(args).items()))

   # Run main
    main(logger, args)
    logger.info('Done!')
