#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Merge Catalog of Life (CoL) arthropods with the Encyclopedia of Life (EoL) arthropods
Author: Joseph Cornelius
July 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import pandas as pd
import string
import re
import numpy as np
from loguru import logger


# --------------------------------------------------------------------------------------------
#                                         GLOBAL VARs
# --------------------------------------------------------------------------------------------

EXPR = '\\s*[[a-zA-Z-]\s*]*\.|\s*[[a-zA-Z-]*\s*&]*|\s*[a-zA-Z-]*\,.*$'
TABLE = str.maketrans(dict.fromkeys(string.punctuation))


# --------------------------------------------------------------------------------------------
#                                           FUNCTIONS
# --------------------------------------------------------------------------------------------

def create_canonical(row):
    """Create the canonical arthropod name from the CoL data.

    Args:
        row (pandas.core.series.Series): Pandas DataFrame row

    Returns:
        str: The canonical arthropod name.
    """
    # row["dwc:taxonRank"] in ['SUBSPECIES','INFRASPECIFIC_NAME','VARIET','FORM']
    if 'nan' != str(row["gbif:genericName"]) and 'nan' != str(row["dwc:specificEpithet"]) and 'nan' != str(row["dwc:infraspecificEpithet"]):
        return ' '.join([str(row["gbif:genericName"]), str(row["dwc:specificEpithet"]), str(row["dwc:infraspecificEpithet"])])

    # row["dwc:taxonRank"] == 'SPECIES'
    elif 'nan' != str(row["gbif:genericName"]) and 'nan' != str(row["dwc:specificEpithet"]) and 'nan' == str(row["dwc:infraspecificEpithet"]):
        return ' '.join([str(row["gbif:genericName"]), str(row["dwc:specificEpithet"])])

    # row["dwc:taxonRank"] in ['GENUS',FAMILY, ORDER,...]
    elif not ((row["dwc:taxonRank"] in ['SUBSPECIES', 'INFRASPECIFIC_NAME', 'VARIET', 'FORM', 'SPECIES'])):
        s = re.sub(EXPR, '', str(
            row['dwc:scientificName'])).strip().split(" ")[0]
        return s.translate(TABLE)  # remove punctuation

    else:
        s = re.sub(EXPR, '', str(row['dwc:scientificName']))
        return s.translate(TABLE)  # remove punctuation


def get_eol_page_id(term, canonical_2_page_id={}):
    """Look up the EoL PageID for a canonical arthropod name.

    Args:
        term (str): Term to match with the canonical arthropod name.
        canonical_2_page_id (dict, optional): Canonical arthropod name to EoL PageID dictionary. Defaults to {}.

    Returns:
        str: EoL PageID
    """
    try:
        return "|".join(map(str, canonical_2_page_id[term.lower()]))
    except:
        return np.NaN


# --------------------------------------------------------------------------------------------
#                                           RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    #! REPLACE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    col_arthro_file_path = "./Taxon_arthro.tsv"
    eol_pages_file_path = "../../../ArthroTraitMine_Data/encyclopedia_of_life/trait_bank/pages.csv"
    col_eol_merged_file_path = "./Taxon_arthro_eol.tsv"
    #! REPLACE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    logger.add("./merge_col_eol.log", rotation="200 KB")
    logger.info('Start ...')

    # Load CoL and EoL files into Pandas DataFrames
    df_col = pd.read_csv(col_arthro_file_path, sep='\t')
    df_eol_pages = pd.read_csv(eol_pages_file_path)

    df_col['taxonomicName'] = df_col[['dwc:taxonRank', 'gbif:genericName', 'dwc:specificEpithet',
                                      'dwc:scientificName', 'dwc:infraspecificEpithet']].apply(create_canonical, axis=1)

    # Create canonical_2_page_id dictionary
    canonical_2_page_id = {k.lower(): g["page_id"].tolist() for k, g in df_eol_pages.groupby("canonical")}

    logger.debug(f"First five elements from canonical_2_page_id dict:\n{list(canonical_2_page_id.items())[:5]}")

    df_col["eol:pageIDs"] = df_col["taxonomicName"].apply(get_eol_page_id, canonical_2_page_id=canonical_2_page_id)

    logger.info(f'Number of entries without EoL page: {df_col["eol:pageIDs"].isna().sum()}')
    logger.info(f'Number of entries with EoL page: {df_col["eol:pageIDs"].count()}')
    logger.debug(f"Final DataFrame head:\n{df_col.head()}")

    # Write new DataFrame to file
    df_col.to_csv(col_eol_merged_file_path, sep='\t')

   
