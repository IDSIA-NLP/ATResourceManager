#!/usr/bin/env python3
# vim: syntax=python tabstop=4 expandtab

import click
import bz2
import json
from datetime import datetime
from loguru import logger

# TODO:
#  1. Get all the arthropods by entity['labels']
#     1.1 Read all the CoL arthopods canonicals and store them in a dict
#     1.2 get all the json objects where entity['labels] in arthroDict
#
# 2.  Get all the cross references from the arthropods entity json.
#     2.1 The get all the claims with:
#            for example: PropertyID = "P1929" 
#            ==> if entity['claims'][PropertyID]['mainsnak']['datatype'] == "external-id"
#
# 3. Query all the collected PropertyIDs to get the source name (e.g. GBIF)


# ----------------------------------------- Functions ----------------------------------------

def ana_wiki(filename, n=10, s='Q18'):
    c = 0
    with bz2.open(filename, mode='rt') as f, open('out_file', 'w') as o:
        f.read(2)
        for _, line in zip(range(n), f):
            try:
                wiki_json = json.loads(line.rstrip(',\n'))
                c += 1
                if c !=0 and (c%100000 == 0):
                    print(f'Counter: {c}')

                if wiki_json["id"] == s:
                    print(f"Label english:\t{wiki_json['labels']['en']}")
                    print(f"ID:\t{wiki_json['id']}")
                    print(f"Wiki keys{wiki_json.keys()}")
            
                    break

            # print(json.loads(line.rstrip(',\n')))

            # yield json.loads(line.rstrip(',\n'))
            except json.decoder.JSONDecoderError as e:
                print(e)
                continue



def get_arthropods_from_wiki(wiki_file, out_file, arthro_dict, logger):
    c = 0
    ac = 0
    with bz2.open(wiki_file, mode='rt') as in_f, open(out_file, 'w') as out_f:
        in_f.read(2)
        for line in in_f:
            c += 1
            if c !=0 and (c%500000 == 0):
                logger.info(f'Entry count: {c}')
            try:
                wiki_json = json.loads(line.rstrip(',\n'))
                try:
                    # if wiki entry 'is instance of' (P31) taxon (Q16521)
                    is_taxon = False
                    for instance in wiki_json['claims']['P31']:
                        if instance['mainsnak']['datavalue']['value']['id'] == 'Q16521':
                            is_taxon = True
                    
                    if is_taxon:
                        # check if wiki entry is arthropod
                        label_en = wiki_json['labels']['en']['value']

                        if label.lower() in arthro_dict:
                            #* print(f"ID:\t{wiki_json['id']: >40}\nLabel:\t{label_en: >40}\n")
                            #* print(f"Wiki keys{wiki_json.keys()}")

                            out_f.write(json.dumps(wiki_json)+'\n')
                            ac += 1
                            if ac !=0 and (ac%50000 == 0):
                                logger.info(f'Arthropod count: {ac}')

                except:
                    pass

            except Exception as e:
                logger.opt(exception=True).warning(e)
                logger.opt(exception=True).warning(line)
                pass

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------

@click.command()
@click.option('-w', '--wikidata-file', 
              #default='/work/FAC/FBM/DEE/rwaterho/evofun/harry/wikidata/latest-all.json.bz2',
              help='Input file containing Wikidata data dump (JSON).')
@click.option('-a', '--arthro-file',
              #default='/work/FAC/FBM/DEE/rwaterho/evofun/harry/ATResourceManager/results/col_taxonomic_names.txt',
              help='Input file with Arthropod taxon names (TXT).')
@click.option('-o', '--output-file',
              #default='/work/FAC/FBM/DEE/rwaterho/evofun/harry/ATResourceManager/results/wikidata_arthro.json',
              help='Output file to which to write Arthropod data (JSON).')
def main(wikidata_file, output_file, arthro_file):
    """Extract Arthropod data from Wikidata JSON data dump."""

    logger.info(f'Start ...')

    logger.info(f"Wikidata file:\t{wikidata_file}")
    logger.info(f"Output file:\t{output_file}")
    logger.info(f"Arthropod file:\t{arthro_file}\n")

    # store taxonomic names in dict
    logger.info(f"Load taxonomic names...")
    arthro_dict = {}
    data = []
    with open(arthro_file, mode='r') as af:
        for line in af:
            arthro_dict[line.strip()] = line.strip()
            data.append(line.lower())

    # sanity check
    logger.debug(f"Sanity check: # unique({len(arthro_dict)}) == # total({len(data)})")

    logger.info(f"Extracting arthropods from Wikidata...\n")
    get_arthropods_from_wiki(wikidata_file, output_file, arthro_dict, logger)

    logger.info('Done.')
    #print(f'\n\nEnd at: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    #ana_wiki(wikidata_file, n=1000000, s='Q18')


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
