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
import re
import numpy as np

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------
class Graph:
    def __init__(self, egdes):
        self.egdes = egdes
        self.graph_dict = {}
        
        for parent, child in self.egdes:
            if parent in self.graph_dict:
                self.graph_dict[parent].append(child)
            else:
                self.graph_dict[parent] = [child]
                
                
    def get_paths(self, parent, child, path=[]):
        path = path + [parent]
        
        if parent == child:
            return [path]
        
        if parent not in self.graph_dict:
            return []
        
        paths = []
        for node in self.graph_dict[parent]:
            if node not in path:
                new_paths = self.get_paths(node, child, path)
                for p in new_paths:
                    paths.append(p)
        
        return paths
    
    def get_children(self, parent, children=[]):
        children = children + [parent]
        
        if parent not in self.graph_dict:
            #print("empty")
            return children
        
        all_children = []
        for node in self.graph_dict[parent]:
            #print("in child: ", node)
            if node not in children:
                #print("not in children | ", node)
                new_children = self.get_children(node, children)
                for c in new_children:
                    #print("new child: ", c)
                    all_children.append(c)
        
        return list(set(all_children))

# ----------------------------------------- Functions ----------------------------------------

def main(logger, args):
    """[summary]

    Args:
        logger ([type]): [description]

    Returns:
        [type]: [description]
    """

    logger.info(f'Start computing pages_arthro...')

    df_pages = pd.read_csv(args.pages)
    df_pages["parent_id"] = df_pages["parent_id"].fillna(0)
    df_pages = df_pages.astype({"page_id": int, "parent_id": int})

    # Get parent2leaf chain
    g_edges = df_pages[["parent_id", "page_id"]].to_records(index=False)
    col_graph = Graph(g_edges)
    
    #! The ID of Arthropod is 164, this serves us as a root.
    arthropd_ids = col_graph.get_children(164)

    # get all arthropods pages
    df_filter = df_pages["page_id"].isin(arthropd_ids)
    df_pages_arthro = df_pages[df_filter].copy()

    edges = df_pages_arthro[["parent_id", "page_id"]].to_records(index=False)

    child2parent = {}
    for parentChild in edges:
        if parentChild[1] not in child2parent.keys():
            child2parent[parentChild[1]] = [parentChild[0]]
        else:
            child2parent[parentChild[1]].append(parentChild[0])

    def get_path(child, path=[], targetParent=164):
        try: 
            path.insert(0, child)
            if child != targetParent:
                parents = child2parent[child] 

                for parent in parents:

                    if parent != targetParent:
                        r = get_path(parent, path=path)
                        
                        if r == "break":
                            pass
                        else:
                            path = r
                            
                    else:
                        path.insert(0, parent)

            return path
        except Exception as e:
            return "break"         

    df_pages_arthro["parentLeafChain"] = df_pages_arthro["page_id"].apply(lambda x: "|".join(map(str, get_path(x, path=[]))))
    f = df_pages_arthro["parentLeafChain"].str.contains("164|")
    df_pages_arthro[f]

    

    logger.debug(f"pages_arthro shape: {df_pages_arthro.shape}")    
    logger.debug(f"pages_arthro columns: {df_pages_arthro.columns}")
    logger.debug(f"pages_arthro head: \n{df_pages_arthro.head()}")
    df_pages_arthro.to_csv(args.pages_arthro)


    # ------------------------------------------
    # GET THE ARTHROPOD TRAIT DATA
    logger.info(f'Start computing traits_arthro...')

    df_traits = pd.read_csv(args.traits)
    arthro_page_ids = df_pages_arthro.page_id.unique()

    arthro_trait_filter = df_traits["page_id"].isin(arthro_page_ids)
    df_traits_arthro = df_traits[arthro_trait_filter]

    logger.debug(f"traits_arthro shape: {df_traits_arthro.shape}")
    logger.debug(f"traits_arthro columns: {df_traits_arthro.columns}")
    logger.debug(f"traits_arthro head: \n{df_traits_arthro.head()}")

    df_traits_arthro.to_csv(args.traits_arthro)

    # ------------------------------------------
    # GET THE ARTHROPOD TERM DATA
    logger.info(f'Start computing terms_arthro...')

    df_terms = pd.read_csv(args.terms)
    arthro_predicates = df_traits_arthro.predicate.unique()
    arthro_term_filter = df_terms["uri"].isin(arthro_predicates)
    df_terms_arthro = df_terms[arthro_term_filter]

    logger.debug(f"terms_arthro shape: {df_terms_arthro.shape}")
    logger.debug(f"terms_arthro columns: {df_terms_arthro.columns}")
    logger.debug(f"terms_arthro head: \n{df_terms_arthro.head()}")

    df_terms_arthro.to_csv(args.terms_arthro, index=False)

    
    # ------------------------------------------
    # CREATE TRAIT ATRTHRO RELATIONSHIPS
    logger.info(f'Start computing traits_arthro_relationship...')
    
    df_out = df_traits_arthro[[
    'eol_pk',
    'page_id',
    'resource_pk',
    'resource_id',
    'source',
    'scientific_name',
    'predicate',
    'object_page_id',
    'value_uri',
    'normal_measurement',
    'normal_units_uri',
    'normal_units',
    'measurement',
    'units_uri',
    'units',
    'literal'
    ]]

    # Add canonical name of Taxon
    df_out["canonical"] = df_out['page_id'].apply(lambda x: df_pages_arthro[df_pages_arthro["page_id"]==x]["canonical"].iloc[0])
    # Add predicate term
    df_out["term_name"] = df_out['predicate'].apply(lambda x: df_terms[df_terms["uri"]==x]["name"].iloc[0])
    # Add predicate term type
    df_out["term_type"] = df_out['predicate'].apply(lambda x: df_terms[df_terms["type"]==x]["name"].iloc[0])

    logger.debug(f"trait_arthro_rel shape: {df_out.shape}")
    logger.debug(f"trait_arthro_rel columns: {df_out.columns}")
    logger.debug(f"trait_arthro_rel head: \n{df_out.head()}")

    df_out.to_csv(args.trait_arthro_rel, index=False, sep='\t')


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("./LOG_FILE.log", rotation="20 MB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Application description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-p', '--pages', metavar='pages', type=str, required=False, 
                        default='../../data/encyclopedia_of_life/trait_bank/pages.csv', 
                        help='Path to EOL pages file')
    parser.add_argument('-t', '--traits', metavar='traits', type=str, required=False, 
                        default='../../data/encyclopedia_of_life/trait_bank/traits.csv', 
                        help='Path to EOL traits file')
    parser.add_argument('-i', '--terms', metavar='terms', type=str, required=False, 
                        default='../../data/encyclopedia_of_life/trait_bank/terms.csv', 
                        help='Path to EOL terms file')
    
    parser.add_argument('-pa', '--pages_arthro', metavar='pages', type=str, required=False, 
                        default='../../data/encyclopedia_of_life/trait_bank/pages_arthro.csv', 
                        help='Output path to EOL pages arthropod file')
    parser.add_argument('-ta', '--traits_arthro', metavar='traits', type=str, required=False, 
                        default='../../data/encyclopedia_of_life/trait_bank/traits_arthro.csv', 
                        help='Output path to EOL traits arthropod file')
    parser.add_argument('-ia', '--terms_arthro', metavar='terms_arthro', type=str, required=False, 
                        default='../../data/encyclopedia_of_life/trait_bank/terms_arthro_trait_predicates.csv', 
                        help='Output path to EOL terms arthropod file')

    parser.add_argument('-ot', '--trait_arthro_rel', metavar='trait_arthro_rel', type=str, required=False, 
                        default='../../data/encyclopedia_of_life/trait_bank/traits_arthro_relationship.tsv', 
                        help='Output path to EOL terms arthropod file')
    args = parser.parse_args()

   # Run main
    main(logger, args)