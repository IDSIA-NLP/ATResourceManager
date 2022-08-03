#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: syntax=python tabstop=4 expandtab

"""
Description: Merge Catalog of Life (CoL) arthropods with the Encyclopedia of Life (EoL) arthropods
Authors:
    Joseph Cornelius
    Harald Detering
August 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
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
FIELD_GENERICNAME = 'dwc:genericName'


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
    if 'nan' != str(row[FIELD_GENERICNAME]) and 'nan' != str(row["dwc:specificEpithet"]) and 'nan' != str(row["dwc:infraspecificEpithet"]):
        return ' '.join([str(row[FIELD_GENERICNAME]), str(row["dwc:specificEpithet"]), str(row["dwc:infraspecificEpithet"])])

    # row["dwc:taxonRank"] == 'SPECIES'
    elif 'nan' != str(row[FIELD_GENERICNAME]) and 'nan' != str(row["dwc:specificEpithet"]) and 'nan' == str(row["dwc:infraspecificEpithet"]):
        return ' '.join([str(row[FIELD_GENERICNAME]), str(row["dwc:specificEpithet"])])

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

@click.command()
@click.option('--col-taxa', required=True, help='Catalogue of Life (CoL) taxa file')
@click.option('--eol-taxa', required=True, help='Encyclopedia of Life (EOL) pages file')
@click.option('--out-file', required=True, help='File to write output to')
@click.option('--log', default='col_eol_merge.log', help='File receiving log messages')
def main(col_taxa, eol_taxa, out_file, log):
    """Merge Catalog of Life (CoL) arthropods with the Encyclopedia of Life (EoL) arthropods."""

    #! REPLACE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    col_arthro_file_path = "./Taxon_arthro.tsv"
    eol_pages_file_path = "../../../ArthroTraitMine_Data/encyclopedia_of_life/trait_bank/pages.csv"
    col_eol_merged_file_path = "./Taxon_arthro_eol.tsv"
    #! REPLACE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    logger.add(log, rotation="200 KB")
    logger.info('Start ...')

    # Load CoL and EoL files into Pandas DataFrames
    df_col = pd.read_csv(col_taxa, sep='\t')
    df_eol_pages = pd.read_csv(eol_taxa)

    # check field names (gbif:genericName changed to dwc:genericName at some point)
    cols_genericName = [x for x in df_col.columns if 'genericname' in x.lower()]
    assert len(cols_genericName) == 1, \
        f"ERROR: expected one column named '<pfx>:genericName', got {len(cols_genericName)}"
    FIELD_GENERICNAME = cols_genericName[0]

    df_col['taxonomicName'] = df_col[['dwc:taxonRank', FIELD_GENERICNAME, 'dwc:specificEpithet',
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

   
if __name__ == '__main__':
    main()
