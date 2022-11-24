#!/usr/bin/env python3
# vim: syntax=python tabstop=4 expandtab
# coding: utf-8

"""
Description: Merge wikidata info with COL taxons
Author:
  Joseph Cornelius
  Harald Detering
November 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
from loguru import logger
import pandas as pd
import json
import numpy as np

# ----------------------------------------- Functions ----------------------------------------

def get_wikidata_id(taxonomic_name):
    try:
        ids_list = taxa_to_wiki_id[taxonomic_name]
        return "|".join(ids_list)
    except:
        return np.nan

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

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------

@click.commad()
@click.option('-t', '--taxon-file', 
              #default='../results/Taxon_arthro_eol.tsv',
              help='Input file with Arthropod taxa merged from CoL and EOL (TSV).')
@click.option('-wc', '--wiki-arthro-cross-stats-file', 
              #default='../../data/wikidata/wikidata_arthro_crossref_stats.json',
              help='Input file with wikidata cross-ref stats (JSON).')
@click.option('-wp', '--wiki-props-label-file', 
              #default='../../data/wikidata/wikidata_props_to_label.json',
              help='Input file with properties-to-label mappings (JSON).')
@click.option('-tw', '--taxon-to-wiki-file', 
              #default='../../data/wikidata/taxonomic_name_to_wikiID.json',
              help='Input file with taxon name-to-wikiID mappings (JSON))')
# TODO: ?? Output of wikidata_extract_props_from_wikidata necessary ??
@click.option('-wa', '--wiki-arthro-props-file', 
              #default='../../data/wikidata/wikidata_arthro_properties.tsv',
              help='Output file with Arthropod wikidata properties counts (TSV).')
@click.option('-taw', '--taxon-wiki-file', 
              #default='../results/Taxon_arthro_eol_wikidata.tsv',
              help='Output file with Arthropod wikidata attributes (TSV).')
def main(taxon_file, wiki_arthro_cross_stats_file, wiki_props_label_file, taxon_to_wiki_file,
         wiki_arthro_props_file, taxon_wiki_file):
    """Merge wikidata info with COL taxons."""

    # Setup logger
    #logger.add("./wikidata_merge_wikidata_col.log", rotation="20 MB")
    logger.info(f'Start ...')
    logger.info(f'Start merging Wikidata and COL...')
    
    df_col_arthro = pd.read_csv(taxon_file, sep="\t")

    with open(wiki_arthro_cross_stats_file, mode='r') as f:
        crossref_stats = json.load(f)
    
    with open(wiki_props_label_file, mode='r') as f:
        prop_to_label = json.load(f)

    prop_label_count = []
    for k, v in prop_to_label.items():
        prop_label_count.append([k,v, crossref_stats["occurrence"][k]])

    df_prop_label_count = pd.DataFrame(prop_label_count, columns=["wikidata:id", "wikidata:label", "occurence_count"])

    # Get Wikidata ID for taxonomic names
    with open(taxon_to_wiki_file, mode='r') as f:
        taxa_to_wiki_id = json.load(f)
    
    df_col_arthro['wikidata:ids'] = df_col_arthro['taxonomicName'].apply(get_wikidata_id)
    df_col_arthro['wikidata:cross_ref'] = df_col_arthro['wikidata:ids'].apply(get_wikidata_crossref)
    df_col_arthro['wikidata:cross_ref_count'] = df_col_arthro['wikidata:ids'].apply(get_wikidata_crossref_count)

    #  Write new DataFrames to file
    df_prop_label_count.to_csv(wiki_arthro_props_file, sep='\t', index=False)
    df_col_arthro.to_csv(taxon_wiki_file, sep='\t', index=False)

    logger.info("Done!")

# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

