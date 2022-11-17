#!/usr/bin/env python3
# vim: syntax=python tabstop=2 expandtab
# -*- coding: utf-8 -*-

"""
Description: Read in the arthropods .json file and get all cross-references
Authors:
  Joseph Cornelius
  Harald Detering
November 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
from loguru import logger
import json


# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------

@click.command()
@click.option('-a', '--arthro-file', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro.json', 
              help='Path to arthropod wikidata json file.')
@click.option('-c', '--crossref-file', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref.json', 
              help='Path to output file for arthro wikidata with cross references.')
@click.option('-p', '--prop-ids-file', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref_prop_ids.txt', 
              help='Path to output file for wikidata property IDs list.')
def main(arthro_file, crossref_file, prop_ids_file):
    """Evaluate arthopod wikidata
    
    Extract cross-references and properties from wikidata json. Writes for each
    wikidata entry the cross-references info to .json file and all the cross-
    reference property IDs to a .txt file. 

    Args:
        arthro_file   : Path to arthropod wikidata json file.
        crossref_file : Path to output file for arthro wikidata with cross references.
        prop_ids_file : Path to output file for wikidata property IDs list.

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

    # Setup logger
    #logger.add("./logs/extract_crossref_arthro_wikidata.log", rotation="100 KB")
    logger.info(f'Start ...')
    # TODO: write CLI args to log
    #logger.info('Argparse arguments:\n'+' \n'.join(f'\t{k: <15} : {v: <80}' for k, v in vars(args).items()))

    all_props = set()
    c = 0

    logger.info(f'Extracting cross-references...')
    with open(arthro_file, mode="r") as f, open(crossref_file, 'w') as cr_file:

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
    with open(prop_ids_file, mode="w") as prop_file:
        for item in all_props:
            prop_file.write(f"{item}\n")
    
    logger.info('Done!')

# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
