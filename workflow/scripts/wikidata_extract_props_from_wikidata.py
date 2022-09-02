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

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------
def get_prop_ids(args):
    """Load wikidata property IDs to set.

    Args:
        args (argparser object): Object of the argument parser 

    Returns:
        prop_ids (set): Set of wikidata property IDs
    """

    prop_ids = set()
    with open(args.props_file, mode="r") as f:
        for line in f:
            prop_ids.add(line.strip())

    return prop_ids

def main(logger, args):
    """Create wikidata json for all cross-reference properties and a property ID 
        to label json. 


    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """
    
    logger.info(f'Load cross-ref property IDs ...')
    prop_ids = get_prop_ids(args)

    logger.info(f'Extract cross-ref properties from wikidata ...')
    prop_id_to_label = {}
    c = 0
    pc = 0
    with bz2.open(args.wiki_file, mode='rt') as wf, open(args.wiki_props_outfile, 'w') as wpof:
        wf.read(2)
        for line in wf:
            c += 1
            if c !=0 and (c%500000 == 0):
                logger.info(f'Entry count: {c}')

            try:
                wiki_json = json.loads(line.rstrip(',\n'))

                # if wiki_json['id'].startswith("P"):
                #     print(json.dumps(wiki_json))
                #     #print(json.dumps(wiki_json, indent=4, sort_keys=True))
                #     break

                if wiki_json['id'] in prop_ids:
                    prop_id_to_label[wiki_json['id']] = wiki_json['labels']['en']['value']

                    pc += 1
                    if pc !=0 and (pc%10 == 0):
                        logger.info(f'Property count: {pc}')    

                    wpof.write(json.dumps(wiki_json)+'\n')
                    
                    
            except:
                pass


    logger.info(f"Number of found properties: {pc} ")

    logger.info('Writing property_to_label to file...')
    with open(args.props_to_label_outfile, mode="w") as twf:
        json.dump(prop_id_to_label, twf)


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("./logs/extract_props_from_wikidata.log", rotation="100 KB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Evaluate arthropod wikidata"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-wf', '--wiki_file', metavar='wiki_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/latest-all.json.bz2', 
                        help='Path to wikidata dump.')
    parser.add_argument('-pf', '--props_file', metavar='props_file', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref_prop_ids.txt', 
                        help='Path to cross-reference propertyIDs file.')
    parser.add_argument('-plof', '--props_to_label_outfile', metavar='props_to_label_outfile', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_props_to_label.json', 
                        help='Path to output file (cross-reference propertyIDs to label).')
    parser.add_argument('-wpof', '--wiki_props_outfile', metavar='wiki_props_outfile', type=str, required=False, 
                        default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_props.json', 
                        help='Path to output file (wikidata json of all cross-reference properties).')
    args = parser.parse_args()
    logger.info('Argparse arguments:\n'+' \n'.join(f'\t{k: <15} : {v: <80}' for k, v in vars(args).items()))

   # Run main
    main(logger, args)
    logger.info('Done!')
