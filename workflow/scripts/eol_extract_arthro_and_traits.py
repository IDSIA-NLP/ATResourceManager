#!/usr/bin/env python3
# vim: syntax=python tabstop=2 expandtab
# -*- coding: utf-8 -*-

"""
Description: Extract Arthropod taxa, traits, terms and relationship from Encyclopedia of Life (EOL).
Authors:
  Joseph Cornelius
  Harald Detering
September 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
from loguru import logger
import pandas as pd 
import re
import numpy as np


# ----------------------------------------- Declarations ----------------------------------------

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


# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------

@click.command()
# '../../data/encyclopedia_of_life/trait_bank/pages.csv'
@click.option('-p', '--pages', required=True, help='Path to EOL pages file')
#'../../data/encyclopedia_of_life/trait_bank/traits.csv'
@click.option('-t', '--traits', required=True, help='Path to EOL traits file')
# '../../data/encyclopedia_of_life/trait_bank/terms.csv'
@click.option('-i', '--terms',required=True, help='Path to EOL terms file')
#  '../../data/encyclopedia_of_life/trait_bank/pages_arthro.csv'
@click.option('-pa', '--pages-arthro', required=True, help='Output path to EOL pages arthropod file')
# '../../data/encyclopedia_of_life/trait_bank/traits_arthro.csv' 
@click.option('-ta', '--traits-arthro', required=True, help='Output path to EOL traits arthropod file')
# '../../data/encyclopedia_of_life/trait_bank/terms_arthro_trait_predicates.csv'
@click.option('-ia', '--terms-arthro', required=True, help='Output path to EOL terms arthropod file')
# '../../data/encyclopedia_of_life/trait_bank/traits_arthro_relationship.tsv'
@click.option('-ot', '--trait-arthro-rel', required=True, help='Output path to EOL trait-arthropod relationship file')
def main(pages, traits, terms, pages_arthro, traits_arthro, terms_arthro, trait_arthro_rel):
    """Extract EOL taxa, traits and terms associated with Arthropoda."""

    # Setup logger
    #logger.add("./LOG_FILE.log", rotation="20 MB")
    logger.info(f'Start ...')
    logger.info(f'Start computing pages_arthro...')

    df_pages = pd.read_csv(pages)
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
    df_pages_arthro.to_csv(pages_arthro)


    # ------------------------------------------
    # GET THE ARTHROPOD TRAIT DATA
    logger.info(f'Start computing traits_arthro...')

    df_traits = pd.read_csv(traits, low_memory=False)
    arthro_page_ids = df_pages_arthro.page_id.unique()

    arthro_trait_filter = df_traits["page_id"].isin(arthro_page_ids)
    df_traits_arthro = df_traits[arthro_trait_filter]

    logger.debug(f"traits_arthro shape: {df_traits_arthro.shape}")
    logger.debug(f"traits_arthro columns: {df_traits_arthro.columns}")
    logger.debug(f"traits_arthro head: \n{df_traits_arthro.head()}")

    df_traits_arthro.to_csv(traits_arthro)

    # ------------------------------------------
    # GET THE ARTHROPOD TERM DATA
    logger.info(f'Start computing terms_arthro...')

    df_terms = pd.read_csv(terms)
    arthro_predicates = df_traits_arthro.predicate.unique()
    arthro_term_filter = df_terms["uri"].isin(arthro_predicates)
    df_terms_arthro = df_terms[arthro_term_filter]

    logger.debug(f"terms_arthro shape: {df_terms_arthro.shape}")
    logger.debug(f"terms_arthro columns: {df_terms_arthro.columns}")
    logger.debug(f"terms_arthro head: \n{df_terms_arthro.head()}")

    df_terms_arthro.to_csv(terms_arthro, index=False)

    
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

    # Prepare columns for output
    df_out_traits = df_out.drop_duplicates().copy()
    df_out_pages = df_pages_arthro[['page_id','canonical']].groupby(['page_id'])['canonical'].first().reset_index()
    df_out_terms = df_terms[['uri','name','type']].groupby(['uri'])[['name','type']].first().reset_index()
    df_out_terms = df_out_terms.rename(columns={'name': 'term_name', 'type': 'term_type'})

    # Merge output DataFrames
    df_out = pd.merge(df_out_traits, df_out_pages, on='page_id', how='left')
    df_out = pd.merge(df_out, df_out_terms, left_on='predicate', right_on='uri', how='left')

    # Add canonical name of Taxon
    #df_out["canonical"] = df_out['page_id'].apply(lambda x: df_pages_arthro[df_pages_arthro["page_id"]==x]["canonical"].iloc[0])
    # Add predicate term
    #df_out["term_name"] = df_out['predicate'].apply(lambda x: df_terms[df_terms["uri"]==x]["name"].iloc[0])
    # Add predicate term type
    #df_out["term_type"] = df_out['predicate'].apply(lambda x: df_terms[df_terms["type"]==x]["name"].iloc[0])

    logger.debug(f"trait_arthro_rel shape: {df_out.shape}")
    logger.debug(f"trait_arthro_rel columns: {df_out.columns}")
    logger.debug(f"trait_arthro_rel head: \n{df_out.head()}")

    df_out.to_csv(trait_arthro_rel, index=False, sep='\t')


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # Run main
    main()
