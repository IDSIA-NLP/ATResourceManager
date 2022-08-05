#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Converters the arthropod and traits files in OGER terminologies.
Author: Joseph Cornelius
August 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
import glob
from loguru import logger
import pandas as pd
import numpy as np
import csv
import itertools
from nltk.corpus import stopwords


# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------
def create_arthro_term(logger, args):
    """Create arthropod terminology.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    if args.input_file_path is not None:
        input_file_path = args.input_file_path
    else:
        input_file_path = '../../data/latest_dwca/Taxon_arthro_eol_wikidata_sm.tsv'

    if args.output_file_path is not None:
        output_file_path = args.output_file_path
    else:
        output_file_path = '../../data/bth_oger/col_arthropods.tsv'

    logger.info(f'Read stopwords file: {args.stopwords}...')
    with open(args.stopwords, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f]


    logger.info('Read col file and transform it to oger readable terminology...')
    

    df = pd.read_csv(input_file_path, sep='\t')

    # Filter all Genus names that are in Stop Word list
    logger.info(f'Arthropod dataframe length BEFORE stopword filter: {df.shape[0]}')
    mask = (df["taxonomicName"].str.lower().isin(stopwords)) & (df["dwc:taxonRank"]=="GENUS")
    df = df[~mask]
    logger.info(f'Arthropod dataframe length AFTER stopword filter: {df.shape[0]}')

    df_out = df[['dwc:taxonID', 'taxonomicName']].copy()
    df_out = df_out.rename(columns={'dwc:taxonID': 'original_id', 'taxonomicName': 'term'})
    df_out['preferred_term'] = df_out['term']
    df_out['cui'] = 'CUI-less'
    df_out['resource'] = 'CoL'
    df_out['entity_type'] = 'Arthropod'

    df_out = df_out[['cui', 'resource', 'original_id', 'term', 'preferred_term', 'entity_type']]

    logger.info(f'Write col arthropods to a .tsv file...')

    df_out.to_csv(output_file_path, index=False, sep='\t')


def get_synonyms_dataframe(df_out):
    """Create a new DataFrame from the synonyms.

    Args:
        df_out (Pandas DataFrame object): Pandas DataFrame

    Returns:
        (Pandas DataFrame object): Pandas DataFrame
    """
    newrows = []
    for row in df_out.iterrows():
        synonyms = row[1]['synonyms']
        if isinstance(synonyms, str):
            synonyms_li = synonyms.split(",")

            if len(synonyms_li) > 0:
                for synonym in synonyms_li:
                    newrows.append({
                        "cui":row[1]['cui'], 
                        "resource":row[1]['resource'], 
                        "original_id":row[1]['original_id'],
                        "term": synonym.strip(),
                        "preferred_term":row[1]['preferred_term'], 
                    "entity_type":row[1]['entity_type']
                    })

    return pd.DataFrame(newrows)


def create_trait_feeding_term(logger, args):
    """Create feeding trait terminology.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    if args.input_file_path is not None:
        input_file_path = args.input_file_path
    else:
        input_file_path = '../../data/traits/terms_arthro_traits_curated_feeding.tsv'

    if args.output_file_path is not None:
        output_file_path = args.output_file_path
    else:
        output_file_path = '../../data/bth_oger/traits_feeding.tsv'

    logger.info('Read traits file and transform it to oger readable terminology...')

    df = pd.read_csv(input_file_path, sep='\t')

    df['name'].replace('', np.nan, inplace=True)
    df.dropna(subset=['name'], inplace=True)

    df_out = df[['uri', 'name']].copy()
    df_out = df_out.rename(columns={'uri': 'original_id', 'name': 'term'})
    df_out['preferred_term'] = df_out['term']
    df_out['cui'] = 'CUI-less'
    df_out['resource'] = df['resource']
    df_out['entity_type'] = 'Trait-Feeding'

    df_out['synonyms'] = df['synonyms']

    df_out_new = get_synonyms_dataframe(df_out)
    df_out = pd.concat([df_out, df_out_new], ignore_index=True)

    df_out = df_out[['cui', 'resource', 'original_id', 'term', 'preferred_term', 'entity_type']]

    logger.info(f'Write col arthropods to a .tsv file...')

    df_out.to_csv(output_file_path, index=False, sep='\t')



def create_trait_habitat_term(logger, args):
    """Create habitat trait terminology.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    if args.input_file_path is not None:
        input_file_path = args.input_file_path
    else:
        input_file_path = '../../data/traits/terms_arthro_traits_curated_habitat.tsv'

    if args.output_file_path is not None:
        output_file_path = args.output_file_path
    else:
        output_file_path = '../../data/bth_oger/traits_habitat.tsv'

    logger.info('Read traits file and transform it to oger readable terminology...')

    df = pd.read_csv(input_file_path, sep='\t')

    df['name'].replace('', np.nan, inplace=True)
    df.dropna(subset=['name'], inplace=True)

    if 'uri' in df.columns:
        df_out = df[['uri', 'name']].copy()
    else:
        df_out = df[['name']].copy()
        df_out['uri'] = [f"ARTH{i:04d}" for i in range(df.shape[0])]
    df_out = df_out.rename(columns={'uri': 'original_id', 'name': 'term'})
    df_out['preferred_term'] = df_out['term']
    df_out['cui'] = 'CUI-less'
    df_out['resource'] = df['resource']
    df_out['entity_type'] = 'Trait-Habitat'
    df_out['synonyms'] = df['synonyms']

    df_out_new = get_synonyms_dataframe(df_out)
    df_out = pd.concat([df_out, df_out_new], ignore_index=True)

    # Sort the dataframe to obtain the right order
    df_out = df_out[['cui', 'resource', 'original_id', 'term', 'preferred_term', 'entity_type']]

    logger.info(f'Write col arthropods to a .tsv file...')

    df_out.to_csv(output_file_path, index=False, sep='\t')



def create_trait_morph_term(logger, args):
    """Create habitat trait terminology.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    if args.input_file_path is not None:
        input_file_path = args.input_file_path
    else:
        input_file_path = '../../data/traits/terms_arthro_traits_curated_morphology.tsv'

    if args.output_file_path is not None:
        output_file_path = args.output_file_path
    else:
        output_file_path = '../../data/bth_oger/traits_morphology.tsv'

    logger.info('Read traits file and transform it to oger readable terminology...')

    df = pd.read_csv(input_file_path, sep='\t')

    df['name'].replace('', np.nan, inplace=True)
    df.dropna(subset=['name'], inplace=True)

    if 'uri' in df.columns:
        df_out = df[['uri', 'name']].copy()
    else:
        df_out = df[['name']].copy()
        df_out['uri'] = [f"ARTM{i:04d}" for i in range(df.shape[0])]
    df_out = df_out.rename(columns={'uri': 'original_id', 'name': 'term'})
    df_out['preferred_term'] = df_out['term']
    df_out['cui'] = 'CUI-less'
    df_out['resource'] = df['resource']
    df_out['entity_type'] = 'Trait-Morphology'
    df_out['synonyms'] = df['synonyms']

    df_out_new = get_synonyms_dataframe(df_out)
    df_out = pd.concat([df_out, df_out_new], ignore_index=True)

    # Sort the dataframe to obtain the right order
    df_out = df_out[['cui', 'resource', 'original_id', 'term', 'preferred_term', 'entity_type']]

    logger.info(f'Write col arthropods to a .tsv file...')

    df_out.to_csv(output_file_path, index=False, sep='\t')


def create_trait_eol_term(logger, args):
    """Create EOL trait terminology.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    if args.input_file_path is not None:
        input_file_path = args.input_file_path
    else:
        input_file_path = '../../data/encyclopedia_of_life/trait_bank/traits_arthro_relationship.tsv'

    if args.output_file_path is not None:
        output_file_path = args.output_file_path
    else:
        output_file_path = '../../data/bth_oger/traits_eol.tsv'

    logger.info('Read traits file and transform it to oger readable terminology...')

    df = pd.read_csv(input_file_path, sep='\t')

    df = df.drop_duplicates(subset=["term_name"])

    df_out = df[['predicate', 'term_name']].copy()

    df_out = df_out.rename(columns={'predicate': 'original_id', 'term_name': 'term'})
    df_out['preferred_term'] = df_out['term']
    df_out['cui'] = 'CUI-less'
    df_out['resource'] = 'EOL'
    df_out['entity_type'] = 'Trait-EOL'

    # Sort the dataframe to obtain the right order
    df_out = df_out[['cui', 'resource', 'original_id', 'term', 'preferred_term', 'entity_type']]

    logger.info(f'Write eol traits to a .tsv file...')

    df_out.to_csv(output_file_path, index=False, sep='\t')


def create_arthro_eol_term(logger, args):
    """Create EOL arthropod terminology.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    if args.input_file_path is not None:
        input_file_path = args.input_file_path
    else:
        input_file_path = '../../data/encyclopedia_of_life/trait_bank/pages_arthro.csv'

    if args.output_file_path is not None:
        output_file_path = args.output_file_path
    else:
        output_file_path = '../../data/bth_oger/eol_arthropods.tsv'

    logger.info(f'Read stopwords file: {args.stopwords}...')
    with open(args.stopwords, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f]


    logger.info('Read EOL file and transform it to oger readable terminology...')
    

    df = pd.read_csv(input_file_path)
    df = df.drop_duplicates(subset=["canonical"])

    # Filter all Genus names that are in Stop Word list
    logger.info(f'Arthropod dataframe length BEFORE stopword filter: {df.shape[0]}')
    mask = df["canonical"].str.lower().isin(stopwords)
    df = df[~mask]
    logger.info(f'Arthropod dataframe length AFTER stopword filter: {df.shape[0]}')

    df_out = df[['page_id', 'canonical']].copy()
    df_out = df_out.rename(columns={'page_id': 'original_id', 'canonical': 'term'})
    df_out['preferred_term'] = df_out['term']
    df_out['cui'] = 'CUI-less'
    df_out['resource'] = 'EOL'
    df_out['entity_type'] = 'Arthropod-EOL'

    df_out = df_out[['cui', 'resource', 'original_id', 'term', 'preferred_term', 'entity_type']]

    logger.info(f'Write EOL arthropods to a .tsv file...')

    df_out.to_csv(output_file_path, index=False, sep='\t')


def main(logger, args):
    """Choose between different terminologies to create.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    if args.terminology == 'arthro':
        logger.info(f'Start creating the arthropod terminology.')
        create_arthro_term(logger, args)

    elif args.terminology == 'trait_feeding':
        logger.info(f'Start creating the trait feeding terminology.')
        create_trait_feeding_term(logger, args)
    
    elif args.terminology == 'trait_habitat':
        logger.info(f'Start creating the trait habitat terminology.')
        create_trait_habitat_term(logger, args)

    elif args.terminology == 'trait_morph':
        logger.info(f'Start creating the trait morphology terminology.')
        create_trait_morph_term(logger, args)

    elif args.terminology == 'trait_eol':
        logger.info(f'Start creating the trait EOL terminology.')
        create_trait_eol_term(logger, args)

    elif args.terminology == 'arthro_eol':
        logger.info(f'Start creating the trait EOL terminology.')
        create_arthro_eol_term(logger, args)
    
    else:
        logger.info(f'Invalid terminology!')


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------
if __name__ == '__main__':

    # Setup logger
    logger.add("../../logs/make_oger_terminology.log", rotation="20 MB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Application description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-t', '--terminology', metavar='terminology', type=str, required=True,
                        default='arthro', choices=['arthro', 'arthro_eol', 'trait_eol', 'trait_feeding', 
                        'trait_habitat', 'trait_morph'], help='Which terminology should be created?')
    parser.add_argument('-i', '--input_file_path', metavar='input_file_path', type=str, required=False,
                        help='Path to input file.')
    parser.add_argument('-o', '--output_file_path', metavar='output_file_path', type=str, required=False,
                        help='Path to output .tsv file.')
    parser.add_argument('-s', '--stopwords', metavar='stopwords', type=str, required=False,
                        default="./most_freq_20k.txt", help='Path to output .tsv file.')
    args = parser.parse_args()

   # Run main
    main(logger, args)

    logger.info(f'Done.')
