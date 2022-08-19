#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: syntax=python tabstop=4 expandtab

"""
Description: Download PMC XML articles based on the DOIs extracted from the PLAZI treatments.
Authors:
  Joseph Cornelius
  Harald Detering
August 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
from loguru import logger
import pandas as pd
import requests
import numpy as np
import csv
import time
import re
import xml.etree.ElementTree as ET
import os


# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------

def clean_doi(doi):
    """Clean DOI strings.

    Args:
        doi (str): DOI string

    Returns:
        str: DOI string
    """
    if doi == "" or pd.isna(doi):
        return doi
    
    if not "10." in doi:
        logger.debug(f"DOI doesn't start with 10. : {doi}")
        return np.nan
    
    return re.sub(r'^.*?10.', '10.', doi)


def batched_conversion_DOI_to_PMID(docDOIs_batched):
    """Convert the bachted DOIs to their corresponding PMIDs.

    Args:
        docDOIs_batched (list): list of DOIs batches

    Returns:
        list: list of PMID and PMCIDS
    """
    out_list = []
    needHeader = True
    for idx, docDOI_batch in enumerate(docDOIs_batched):
        
        doi_batch_str = ",".join(docDOI_batch)
        
        url = f'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={doi_batch_str}&format=csv&versions=no'
        response = requests.get(url)
        
        if response.status_code == 200:
            decoded_content = response.content.decode('utf-8')
            # transform csv response to list
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            csv_response_list = list(cr)
            if needHeader:
                out_list += csv_response_list[:1]
                needHeader = False
            out_list += csv_response_list[1:]
            
        else:
            logger.debug(f"Status code:{response.status_code}\tError in batch: {idx}")
            logger.debug(doi_batch_str)
        
        time.sleep(3)

    return out_list


def write_single_pmc_xml(pmc_articles, out_path, batch_num):
    """Write each pmc article to separate file.

    Args:
        pmc_articles (str): String with all the XML articles.
        out_path (str): Path to pmc xml article directory.
        batch_num (int): Number of the current batch.
    """
    counter = 0
    try:
        root = ET.fromstring(pmc_articles)
        # extract each article and write it to a file
        for child in root.findall('.//article'):
            counter += 1
            if counter % 50 == 0: logger.debug(f'Batch: {batch_num} - Count: {counter:_>3}')

            pmcid = ""
            for elem in child.findall('.//article-id'):
                if elem.attrib['pub-id-type'] == 'pmc':
                    pmcid = elem.text
                    
            writetree = ET.ElementTree(child) 
            writetree.write(os.path.join(out_path, f'article_pmcid-PMC{pmcid}.xml'))

    except Exception as e:
        logger.debug(e)
        pass


def download_pmc_articles(pmc_ids_batched, xml_path): 
    """Batched download of the PMC XML articles.

    Args:
        pmc_ids_batched (list): List of batched PMCIDs.
        xml_path (str): Path to pmc xml article directory.

    Returns:
        set: Set of downloaded PMC articles.
    """
    received_pmc_articles = set()

    for idx, pmc_batch in enumerate(pmc_ids_batched):
        logger.info(f'Processing batch {idx}, # pmcIDs {len(pmc_batch)}')
        
        pmc_batch_str = ",".join(pmc_batch)
        
        url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_batch_str}&retmode=xml'
        response = requests.get(url)
        
        if response.status_code == 200:

            logger.info(f"Batch:{idx} - Start to write single PMC XML files...")
            write_single_pmc_xml(response.text, xml_path, idx)
   
            try:
                root = ET.fromstring(response.text)
                for child in root.findall('.//article-id'):
                    try:
                        if child.attrib['pub-id-type'] == 'pmc':
                            received_pmc_articles.add(child.text)
                    except:
                        logger.debug(f"Batch:{idx} - PubID type is not PMC")
                        pass
            except:
                pass
            
        else:
            logger.debug(f"Status code:{response.status_code}\tError in batch: {idx}")
        
        time.sleep(3)
    
    return received_pmc_articles


def add_PM_C_ID(doi, ppd_dict, pm_c_key):
    """Pair clean DOIs with PMIDs / PMCIDs.

    Args:
        doi (str): DOI string.
        ppd_dict (dict): DOIs to PMIDs / PMCIDs.
        pm_c_key (str): PM / PMC key string.

    Returns:
        str: PMID/PMCID strings.
    """
    if pd.isna(doi):
        return np.nan
    doi_n = re.sub('[^0-9a-zA-Z\.\-\/]+', '', doi)
    try:
        pm_c_id = ppd_dict[doi_n][pm_c_key]
        return pm_c_id
    except:
        return np.nan



@click.command()
@click.option('--in-file-csv', '-i', required=True, help='Path to PLAZI DOI csv file.')
@click.option('--out-file-pmid', '-o1', required=True, help='Output path for DOI to PMID file.')
@click.option('--out-file-doi-pmid', '-o2', required=True, help='Output path for the PLAZI DOI csv file extended by the PMIDs.')
@click.option('--out-dir-xml', '-xp', required=True, help='Output path to PMC XML directory.')
@click.option('--doi-2-pmid', '-d2p', is_flag=True, help='Write a file with DOIs and there corresponding PMIDs?')
@click.option('--batch-size', '-bs', type=int, default=200, help='Download batch size (maximum value is 200).')
def main(in_file_csv, out_file_pmid, out_file_doi_pmid, out_dir_xml, doi_2_pmid, batch_size):
    """Check/clean DOIs and download the corresponding PMC XML articles."""
    
    assert 200 >= batch_size > 0, "Batch size is not in the range of [1,200]"

    # Setup logger
    #logger.add("../../logs/download_pmc_articles.log", rotation="1 MB")
    logger.info(f'Start ...')
    logger.info("Load DOIs and clean them...")
    df = pd.read_csv(in_file_csv)
    df.head()  


    df['document:ID-DOIClean'] = df['document:ID-DOI'].apply(clean_doi)
    df['treatment:ID-DOIClean'] = df['treatment:ID-DOI'].apply(clean_doi)


    # Check if the document is equal to the treatment DOI. This means that the document DOI points only to the treatment file
    logger.info("Check if document is equal to treatment DOI...")
    df['documentIsTreatment'] = np.where(
        ((df['document:ID-DOIClean']==df['treatment:ID-DOIClean']) | (pd.isna(df['document:ID-DOIClean']) & pd.isna(df['treatment:ID-DOIClean']))),
        True, 
        False)

    # Get the unique document DOIs that are not treatments
    df_sm = df[df['documentIsTreatment'] == False]
    docDOIs = df_sm['document:ID-DOIClean'].dropna().unique()

    logger.debug(f"Sanity check, docDOIs first elements:\n{docDOIs[:4]}")
    logger.debug(f"Sanity check, docDOIs length: {len(docDOIs)}")

    # Get PMIDs for the PLAZI document DOIs
    logger.info("Get PMIDs/PMCIDs for the DOIs gathered from the treatments...")
    # Clean DOIs
    docDOIs = [re.sub('[^0-9a-zA-Z\.\-\/]+', '', doi) for doi in docDOIs]

    # Divide docDOIs in sublist of max length 200
    docDOIs_batched = [docDOIs[i:i + batch_size] for i in range(0, len(docDOIs), batch_size)] 

    logger.debug(f"DOIs batch size: {batch_size}")
    logger.debug(f"Sanity check, is docDOIs_batched == docDOIs length: {len(docDOIs_batched) == int(len(docDOIs)/200) + (len(docDOIs)%200>0)}")

    # PMC Dataframe
    out_list = batched_conversion_DOI_to_PMID(docDOIs_batched)
    df_pm = pd.DataFrame(out_list[1:], columns=out_list[0])
    logger.debug(f"Sanity check, DF shape:{df_pm.shape}, # of unique PMIDs: {df_pm.PMID.nunique()}, # of unique PMCIDs: {df_pm.PMCID.nunique()}, # of unique DOIs: {df_pm.DOI.nunique()}")

    # Write to file
    if doi_2_pmid:
        logger.info("Write DOI to PMID to a file.")
        df_pm.to_csv(out_file_pmid, index=False)

    # Download the PMC papers from PubMed Central. 
    logger.info("Download the papers from PubMed...")

    # The PubMed articles only contain the abstract where as the PMC articles contain the full-text.
    pmc_ids = df_pm['PMCID'].tolist()
    pmc_ids = list(filter(lambda x: x != "", pmc_ids))
    logger.debug(f"Length of PMCID list.{len(pmc_ids)}")

    pmc_ids_batched = [pmc_ids[i:i + batch_size] for i in range(0, len(pmc_ids), batch_size)] 

    logger.debug(f"Sanity check: pmc_ids batched == pmc length: {len(pmc_ids_batched) == int(len(pmc_ids)/200) + (len(pmc_ids)%200>0)}")
    logger.debug(f"Download batch size: {batch_size}")
    logger.debug(f"Number if batches: {len(pmc_ids_batched)}")

    if not os.path.exists(out_dir_xml):
        os.makedirs(out_dir_xml)

    # Start the download and write XMLs to file
    received_pmc_articles = download_pmc_articles(pmc_ids_batched, out_dir_xml)
    logger.debug(f"Received PMC articles: {len(received_pmc_articles)}") 

    # Create ppd dictionary
    ppd = df_pm[['PMID','PMCID','DOI']].values.tolist()
    ppd = list(filter(lambda x: x[0] != "" or x[1] != "", ppd))
    ppd_dict = {e[2]: {'pmid':e[0], 'pmcid':e[1]} for e in ppd}
    logger.debug(f"Length of DOI to PMID to PMCID dictionary: {len(ppd_dict)}")
    
    # Create file DOI, PMID, PMCID csv file
    df['pmID'] = df['document:ID-DOIClean'].apply(add_PM_C_ID, args=(ppd_dict, 'pmid',))
    df['pmcID'] = df['document:ID-DOIClean'].apply(add_PM_C_ID, args=(ppd_dict, 'pmcid',))
    df = df.rename(columns={"pmid": "pmID", "pmcid": "pmcID"})
    logger.info("Write finale csv to file...")
    df.to_csv(out_file_doi_pmid, index=False)

# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # Run main
    main()

    logger.info(f'Done.')






