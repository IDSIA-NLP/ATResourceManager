#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: ...
Author: ...
Month Year
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
from loguru import logger
import pandas as pd
import json
import numpy as np

# Setup logger
logger.add("./wikidata_merge_wikidata_col.log", rotation="20 MB")
logger.info(f'Start ...')
# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------
def main(args):
    """Merge wikidata info with COL taxons.

    Args:
        args (argparse object): Argparse arguments

    Returns:
    """

    logger.info(f'Start merging Wikidata and COL...')
    df_col_arthro_sm = pd.read_csv(args.taxon_file, sep="\t")

    with open(args.wiki_arthro_cross_stats_file, mode='r') as f:
        crossref_stats = json.load(f)
    
    with open(args.wiki_props_label_file, mode='r') as f:
        prop_to_label = json.load(f)

    prop_label_count = []
    for k, v in prop_to_label.items():
        prop_label_count.append([k,v, crossref_stats["occurrence"][k]])

    df_prop_label_count = pd.DataFrame(prop_label_count, columns=["wikidata:id", "wikidata:label", "occurence_count"])


    # Get Wikidata ID for taxonimic names
    with open(args.taxon_to_wiki_file, mode='r') as f:
        taxnoimic_to_wiki_id = json.load(f)
    
    def get_wikidata_id(taxonimic_name):
        try:
            ids_list = taxnoimic_to_wiki_id[taxonimic_name]
            return "|".join(ids_list)
        except:
            return np.nan

    df_col_arthro_sm['wikidata:ids'] = df_col_arthro_sm['taxonomicName'].apply(get_wikidata_id)


    # Get Wikidata property (cross-reference) IDs and properties count
    def get_wikidata_crossref(wiki_ids):
        if pd.isnull(wiki_ids):
            return np.nan
        
        ids = wiki_ids.split("|")
        if len(ids) == 1:
            props = crossref_stats["wikidata"][ids[0]]['cross-ref']          
        else:
            props = [prop for _id in ids for prop in crossref_stats["wikidata"][_id]['cross-ref']]
            props = list(set(props))
        
        if len(props) == 0:
            return np.nan
        else:
            return "|".join(props)

    df_col_arthro_sm['wikidata:cross_ref'] = df_col_arthro_sm['wikidata:ids'].apply(get_wikidata_crossref)


    # Get cross-references count
    def get_wikidata_crossref_count(wiki_ids):
    
        if pd.isnull(wiki_ids):
            return np.nan
        
        ids = wiki_ids.split("|")
        if len(ids) == 1:
            props = [crossref_stats["wikidata"][ids[0]]['cross-ref-count']]       
        else:
            props = [crossref_stats["wikidata"][_id]['cross-ref-count'] for _id in ids ]
        
        if len(props) == 0:
            return np.nan
        else:
            return "|".join(map(str, props))

    df_col_arthro_sm['wikidata:cross_ref_count'] = df_col_arthro_sm['wikidata:ids'].apply(get_wikidata_crossref_count)


    #  Write new DataFrames to file
    df_prop_label_count.to_csv(args.wiki_arthro_props_file, sep='\t', index=False)
    df_col_arthro_sm.to_csv(args.taxon_wiki_file, sep='\t', index=False)
# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup argument parser
    description = "Application description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-t', '--taxon_file', metavar='taxon_file', type=str, required=False, 
                        default='../../data/latest_dwca/Taxon_arthro_eol_sm.tsv', help='Path to ...')

    parser.add_argument('-wc', '--wiki_arthro_cross_stats_file', metavar='wiki_arthro_cross_stats_file', type=str, required=False, 
                        default='../../data/wikidata/wikidata_arthro_crossref_stats.json', help='Path to ...')

    parser.add_argument('-wp', '--wiki_props_label_file', metavar='wiki_props_label_file', type=str, required=False, 
                        default='../../data/wikidata/wikidata_props_to_label.json', help='Path to ...')

    parser.add_argument('-tw', '--taxon_to_wiki_file', metavar='taxon_to_wiki_file', type=str, required=False, 
                        default='../../data/wikidata/taxonimic_name_to_wikiID.json', help='Path to ...')

    parser.add_argument('-wa', '--wiki_arthro_props_file', metavar='wiki_arthro_props_file', type=str, required=False, 
                        default='../../data/wikidata/wikidata_arthro_properties.tsv', help='Path to ...')

    parser.add_argument('-taw', '--taxon_wiki_file', metavar='taxon_wiki_file', type=str, required=False, 
                        default='../../data/latest_dwca/Taxon_arthro_eol_wikidata_sm.tsv', help='Path to ...')
   
    
    args = parser.parse_args()

   # Run main
    main(args)
    logger.info("Done!")

