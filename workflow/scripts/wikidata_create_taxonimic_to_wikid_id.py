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
from loguru import logger
import json


# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------
def get_taxon_set(args):
    """Load taxonomic names to set.

    Args:
        args (argparser object): Object of the argument parser 

    Returns:
        taxon_dict (set): Set of CoL taxonimic names
    """

    taxon_set = set()
    with open(args.taxo_file, mode="r") as tf:
        for line in tf:
            taxon_set.add(line.strip())

    return taxon_set

def main(logger, args):
    """Create a dictionary of taxonimic name to wikidataID

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """
    
    logger.info(f'Load CoL taxonimic names ...')
    taxon_set = get_taxon_set(args)

    logger.info(f'Create taxon2wikiID dict ...')
    taxon_to_wikiID = {}
    c = 0
    dc = 0
    with open(args.arthro_file, mode="r") as af:
        for line in af:
            c += 1
            if c % 50000 == 0: logger.info(f"Entry count: {c}")
            
            arthro_wiki = json.loads(line)
            if arthro_wiki['labels']['en']['value'] in taxon_set:
                if arthro_wiki['labels']['en']['value'] in taxon_to_wikiID:
                    taxon_to_wikiID[arthro_wiki['labels']['en']['value']].append([arthro_wiki['id']])
                    dc += 1
                else:
                    taxon_to_wikiID[arthro_wiki['labels']['en']['value']] = [arthro_wiki['id']]
    
    logger.info(f"Number of ambiguous wikidataIDs: {dc} ")
    logger.info(f'Number of wiki entries: {c}, len of taxon_to_wikiID dict: {len(taxon_to_wikiID)}')

    logger.info('Wrtiting taxonomic-names-to-wikiID to file...')
    with open(args.taxo_to_wiki_file, mode="w") as twf:
        json.dump(taxon_to_wikiID, twf)


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("./logs/create_taxonimic_to_wikid_id.log", rotation="100 KB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Evaluate arthopod wikidata"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--arthro_file', metavar='arthro_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro.json', 
                        help='Path to arthropod wikidata json file.')
    parser.add_argument('-t', '--taxo_file', metavar='taxo_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/arthropod/taxonimic_name_arthro_col.txt', 
                        help='Path to taxonimic CoL names file.')
    parser.add_argument('-tw', '--taxo_to_wiki_file', metavar='taxo_to_wiki_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/taxonimic_name_to_wikiID.json', 
                        help='Path to output file (taxonimic names to wikidataID).')
    args = parser.parse_args()
    logger.info('Argparse arguments:\n'+' \n'.join(f'\t{k: <15} : {v: <80}' for k, v in vars(args).items()))

   # Run main
    main(logger, args)
    logger.info('Done!')
