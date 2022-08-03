#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: syntax=python tabstop=4 expandtab

"""
Description: Down sample the Catalog of Life (CoL) data to arthropods related entries.
Authors: 
  Joseph Cornelius
  Harald Detering
July 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
import pandas as pd
from loguru import logger

from simple_graph import SimpleGraph

# --------------------------------------------------------------------------------------------
#                                    COMMAND-LINE INTERFACE
# --------------------------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description='Downsample the Catalog of Life (CoL) data to arthropods related entries.')
    parser.add_argument('--col-file', required=True, help='CoL TSV file containing taxa (Taxon.tsv).')
    parser.add_argument('--out-file', required=True, help='Output file for filtered taxa (TSV).')
    parser.add_argument('--out-file-sm', required=True, help='Output file for filtered taxa (TSV, fewer columns).')

    parser.add_argument('--log', default='extract_col.log', help='TXT file receiving log messages.')

    args = parser.parse_args()
    return args

# --------------------------------------------------------------------------------------------
#                                           FUNCTIONS
# --------------------------------------------------------------------------------------------

def create_child2parent(df, logger):
    """Create a child to parent dictionary.

    Args:
        df (pandas.DataFrame): The CoL pandas DataFrame.
        logger (loguru._logger.Logger): Logger

    Returns:
        dict: Child to parent dictionary.
    """
    edges = df[["dwc:parentNameUsageID", "dwc:taxonID"]].to_records(index=False)

    child2parent = {}
    for parentChild in edges:
        if parentChild[1] not in child2parent.keys():
            child2parent[parentChild[1]] = parentChild[0]
        else:
            logger.error("Error: Parent is not in path to the RT root.")

    return child2parent


def get_path(child, path=[], targetParent="RT", child2parent={}):
    """Get the path from a child node to a target root node (here RT).

    Args:
        child (str): TaxonID of child node.
        path (list, optional): Current path from leaf to root node. Defaults to [].
        targetParent (str, optional): Target root node (here RT). Defaults to "RT".
        child2parent (dict, optional): Child to parent dictionary. Defaults to {}.

    Returns:
        list: Path from leaf to target root node (here RT.
    """
    parent = child2parent[child]
    path.insert(0, child) 
    if child != targetParent:
        if parent != targetParent:
            path = get_path(parent, path=path, child2parent=child2parent)
        else:
            path.insert(0, parent)

    return path

# --------------------------------------------------------------------------------------------
#                                           RUN
# --------------------------------------------------------------------------------------------

def main(args):
    log_file_path = args.log
    col_file_path = args.col_file
    col_arthro_file_path = args.out_file
    col_arthro_small_file_path = args.out_file_sm
    

    logger.add(log_file_path, rotation="200 KB")
    logger.info('Start ...')
    logger.info('Load CoL file, this can take a few seconds.')

    df_col = pd.read_csv(col_file_path, sep='\t')
    logger.debug(f"CoL DataFrame shape: {df_col.shape}")

    # check field names (gbif:genericName changed to dwc:genericName at some point)
    cols_genericName = [x for x in df_col.columns if 'genericname' in x.lower()]
    assert len(cols_genericName) == 1, \
        f"ERROR: expected one column named '<pfx>:genericName', got {len(cols_genericName)}"
    field_genericName = cols_genericName[0]

    # Remove not "accepted" entries and entries without a parent node
    df_col = df_col[df_col["dwc:taxonomicStatus"].str.upper()=="ACCEPTED"]
    df_col.dropna(subset=['dwc:parentNameUsageID']).shape 

    # ---------------------------------------- Sanity Check --------------------------------------

    # logger.info("Sanity Check with only 5000 entries")
    # df_col_sc = df_col.head(5000)
    # g_edges = df_col_sc[["dwc:parentNameUsageID", "dwc:taxonID"]].to_records(index=False)
    # logger.debug(f"Number of edges: {len(g_edges)}")
    # col_graph = SimpleGraph(g_edges)
    # logger(f"Children of node 3TV4{col_graph.get_children('3TV4')}")
    # ---------------------------------------- Compute Graph --------------------------------------
    
    logger.info("Start building the col graph.")
    
    g_edges = df_col[["dwc:parentNameUsageID", "dwc:taxonID"]].to_records(index=False)
    col_graph = SimpleGraph(g_edges)

    # get all IDs that have RT (arthropod) as parent
    arthropod_ids = col_graph.get_children("RT")
    logger.debug(f"Number of arthropod nodes {len(arthropod_ids)}")

    # Sanity checks
    logger.debug(f"Sanity Check: Path of random node to root (RT): {col_graph.get_paths('RT','4GQ9Y')}")
    logger.debug(f"Sanity Check: Are all nodes in the path in the right order?  {df_col[df_col['dwc:taxonID']=='4GQ9Y']}")

    # Create arthropod DataFrame 
    logger.info("Create arthropod DataFrame and get path from leaf to arthropod node...")

    df_filter = df_col["dwc:taxonID"].isin(arthropod_ids)
    df_new = df_col[df_filter].copy()
    logger.debug(f"CoL Arthro DataFrame shape: {df_new.shape}")

    # Get the path from Leaf to the arthropod node ("RT")
    child2parent = create_child2parent(df_new, logger)
    df_new["parentLeafChain"] = df_new["dwc:taxonID"].apply(lambda x: "|".join(get_path(x, path=[], child2parent=child2parent)))

    # Save to file
    df_new.to_csv(col_arthro_file_path, sep='\t')

    # Save to file reduce df to necessary columns
    df_new_s = df_new[["dwc:taxonID", "dwc:parentNameUsageID","dwc:taxonomicStatus", "dwc:taxonRank","dwc:scientificName",field_genericName, "dwc:specificEpithet", "dwc:infraspecificEpithet", "parentLeafChain"]]
    df_new_s.to_csv(col_arthro_small_file_path, sep='\t')

if __name__ == '__main__':
    args = parse_args()
    main(args)
