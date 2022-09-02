#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Read in the arthropods .json file and get all cross-references
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

def main(logger, args):
    """Extract cross-references and properties from wikidata json. Writes for each
    wikidata entry the cross-references info to .json file and all the cross-
    reference property IDs to a .txt file. 

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None

    Notes:
        The cross-reference is stored in the wikidata json as follows: 
            1. Each entry has a list of properties stored in wiki_entry['claims'].
            2. Each property (e.g. ``PropertyID``) has a list of mainsnak stored 
                in wiki_entry['claims'][PropertyID].
            3. If the PropertyID is of the type of a cross-reference, then there 
                is an ``element`` in ``wiki_entry['claims'][PropertyID]`` for which 
                ``element['mainsnak']['datatype']== "external-id"``.
    """

    all_props = set()
    c = 0
    logger.info(f'Extracting cross-references...')
    with open(args.arthro_file, mode="r") as f, open(args.crossref_file, 'w') as cr_file:

        for line in f:
            c += 1
            if c % 50000 == 0: logger.info(f"Entry count: {c}")
            
            arthro_wiki = json.loads(line)

            # logger.info(f"ID:{arthro_wiki['id']: >20}\nLabel:{arthro_wiki['labels']['en']['value']: >60}")
            arthro_dict = {}
            try:
                
                arthro_dict['id'] = arthro_wiki['id']
                arthro_dict['label'] = arthro_wiki['labels']['en']['value']
                arthro_dict['crossRef']  = []
                arthro_dict['claims'] = {} 
                for claim in arthro_wiki['claims']:
                    
                    for elem in arthro_wiki['claims'][claim]:
                        try: 
                            if elem['mainsnak']['datatype'] == "external-id":
                                arthro_dict['crossRef'].append(claim)
                                all_props.add(claim)
                                if claim in arthro_dict['claims']:
                                    arthro_dict['claims'][claim].append(elem)
                                else:
                                    arthro_dict['claims'][claim] = [elem]
                                # print("claim:", claim)
                                # print("elem:", elem)
                                # print("arthro_wiki['claims'][claim]:", arthro_wiki['claims'][claim])
                        except:
                            pass
            except:
                pass
            arthro_dict['crossRef'] = list(set(arthro_dict['crossRef']))
            cr_file.write(json.dumps(arthro_dict)+'\n')
            # print(arthro_dict)
            # break

    logger.info('Wrtiting property IDs to file...')
    with open(args.prop_ids_file, mode="w") as prop_file:
        for item in all_props:
            prop_file.write(f"{item}\n")


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("./logs/extract_crossref_arthro_wikidata.log", rotation="100 KB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Evaluate arthopod wikidata"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--arthro_file', metavar='arthro_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro.json', 
                        help='Path to arthropod wikidata json file.')
    parser.add_argument('-c', '--crossref_file', metavar='crossref_file', type=str, required=False, 
                            default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref.json', 
                            help='Path to output file for arthro wikidata with cross references.')
    parser.add_argument('-p', '--prop_ids_file', metavar='prop_ids_file', type=str, required=False, 
                            default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref_prop_ids.txt', 
                            help='Path to output file for wikidata property IDs list.')
    args = parser.parse_args()
    logger.info('Argparse arguments:\n'+' \n'.join(f'\t{k: <15} : {v: <80}' for k, v in vars(args).items()))

   # Run main
    main(logger, args)
    logger.info('Done!')
