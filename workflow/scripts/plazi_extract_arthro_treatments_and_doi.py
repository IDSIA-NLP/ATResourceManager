#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Extract the Treatments concerning arthropods.
Author: Joseph Cornelius
July 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
import glob
import xml.etree.ElementTree as ET
from loguru import logger
from shutil import copyfile
import os
import csv


# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------
def get_dois(treatment_file):
    treatment_id = treatment_file.split('/')[-1].split('.')[0]
    csv_list_docDOI = ""
    csv_list_docMTitle = ""
    csv_list_treatDOI = ""

    try:
        tree = ET.parse(treatment_file)
        root = tree.getroot()
        
        # Document attributes
        try:
            csv_list_docMTitle = root.attrib["masterDocTitle"]
        except:
            pass

        try:
            csv_list_docDOI = root.attrib["ID-DOI"]
        except:
            pass
        
        # Treatment attribute
        treat_element = root.find(".//treatment")
        csv_list_treatDOI = treat_element.attrib["ID-DOI"]

    except:
        pass

    return [treatment_id, csv_list_docDOI, csv_list_docMTitle, csv_list_treatDOI]


def is_arthropod(treatment_file):
    """Check if .xml treatment file is about a arthropod.

    Args:
        treatment_file (string): path to and filename of the treatment file.

    Returns:
        Binary: Binary determining if file is about a arthropod.
    """
    try:
        tree = ET.parse(treatment_file)
        root = tree.getroot()

        # get thr first 'taxonomicName' element and check if the phylum==Arthropoda
        element = root.find('.//taxonomicName')
        if "Arthropoda" == element.attrib['phylum']:
            return True
        else:
            return False
    except:
        return False


def main(logger, args):
    """Copy arthropod treatment files to new directory.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    logger.info(f'Start copying arthropod treatments...')
    
    # List to collect DOI infos
    doi_infos =[['palziID', 'document:ID-DOI', 'document:masterDocTitle','treatment:ID-DOI']]

    counter = 0
    counter_arthro = 0
    
    treatment_files = [ f for f in glob.glob(args.data_path + "*")]

    if not os.path.exists(args.out_path):
        os.makedirs(args.out_path)

    for treatment_file in treatment_files:
        counter += 1
        if counter % 10000 == 0: logger.debug(f'Counter: {counter:_>10}')

        if is_arthropod(treatment_file):
            counter_arthro += 1
            if counter_arthro % 10000 == 0: logger.debug(f'Arthropod counter: {counter_arthro:_>10}')
            treatment_file_name = treatment_file.split('/')[-1]
            copyfile(treatment_file, args.out_path + treatment_file_name)


            doi_infos.append(get_dois(treatment_file))

    logger.info(f'Writing Plazi plaziID - IDDOI csv ...')
    with open(args.out_path_doi, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(doi_infos)
# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("../../logs/extract_arthro_treatments.log", rotation="1 MB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Application description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-d', '--data_path', metavar='data_path', type=str, required=False, 
                        default='../../data/plazi/plazi.xml/', help='Path to all .xml treatments files.')
    parser.add_argument('-o', '--out_path', metavar='out_path', type=str, required=False, 
                        default='../../data/plazi/plazi_arthro.xml/', help='Output path for arthropods treatments files.')
    parser.add_argument('-od', '--out_path_doi', metavar='out_path_doi', type=str, required=False, 
                        default='../../data/plazi/plazi_arthro_plaziID-IDDOI.csv', 
                        help='Output path for arthropod treatmentID - ID_DOI pair file.')
    args = parser.parse_args()

   # Run main
    main(logger, args)

    logger.info(f'Done.')