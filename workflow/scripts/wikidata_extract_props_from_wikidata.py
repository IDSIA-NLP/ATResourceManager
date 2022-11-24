# vim: syntax=python tabstop=4 expandtab
# -*- coding: utf-8 -*-

"""
Description:
  Evaluate arthropod wikidata
Authors:
  Joseph Cornelius
  Harald Detering
Novenber 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
import json
import bz2

from loguru import logger

# ----------------------------------------- Functions ----------------------------------------
def get_prop_ids(props_file):
    """Load wikidata property IDs to set.

    Args:
        props_file: Psth to input file with Wikidata properties (TXT). 

    Returns:
        prop_ids (set): Set of wikidata property IDs.
    """

    prop_ids = set()
    with open(props_file, mode="r") as f:
        for line in f:
            prop_ids.add(line.strip())

    return prop_ids

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------

@click.command()
@click.option('-wf', '--wiki_file', metavar='wiki-file', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/latest-all.json.bz2', 
              help='Path to wikidata dumpc (JSON.bz2).')
@click.option('-pf', '--props-file', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_arthro_crossref_prop_ids.txt', 
              help='Path to cross-reference propertyIDs file (TXT).')
@click.option('-plof', '--props-to-label-outfile', 
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_props_to_label.json', 
              help='Path to output file (cross-reference propertyIDs to label, JSON).')
@click.option('-wpof', '--wiki-props-outfile',
              #default='/mnt/BIGSCRATCH/joseph/wiki/wikidata/results/wikidata_props.json', 
              help='Path to output file (wikidata JSON of all cross-reference properties).')
def main(wiki_file, props_file, 
         props_to_label_outfile, wiki_props_outfile):
    """Create wikidata json for all cross-reference properties and a property ID 
       to label json. 
    """
    
    # TODO: write CLI params to log
    #logger.info('Argparse arguments:\n'+' \n'.join(f'\t{k: <15} : {v: <80}' for k, v in vars(args).items()))

    # Setup logger
    #logger.add("./logs/extract_props_from_wikidata.log", rotation="100 KB")
    logger.info(f'Start ...')

    logger.info(f'Load cross-ref property IDs ...')
    prop_ids = get_prop_ids(props_file)

    logger.info(f'Extract cross-ref properties from wikidata ...')
    prop_id_to_label = {}
    c = 0
    pc = 0
    with bz2.open(wiki_file, mode='rt') as wf, open(wiki_props_outfile, 'w') as wpof:
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
    with open(props_to_label_outfile, mode="w") as twf:
        json.dump(prop_id_to_label, twf)

    logger.info('Done!')

# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
