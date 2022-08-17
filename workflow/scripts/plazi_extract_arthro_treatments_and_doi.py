#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: syntax=python tabstop=4 expandtab

"""
Description: Extract the Treatments concerning arthropods.
Authors:
  Joseph Cornelius
  Harald Detering
August 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import click
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


@click.command()
@click.option('--xml-dir', '-i', required=True, help='Path to all .xml treatments files.')
@click.option('--out-dir-xml', '-ox', required=True, help='Output path for arthropods treatments files.')
@click.option('--out-file-ids', '-oi', required=True, help='Output path for arthropod treatmentID - ID_DOI pair file.')
def main(xml_dir, out_dir_xml, out_file_ids):
    """Copy arthropod treatment files to new directory."""

    logger.info(f'Start ...')
    logger.info(f'Start copying arthropod treatments...')
    
    # List to collect DOI infos
    doi_infos =[['plaziID', 'document:ID-DOI', 'document:masterDocTitle','treatment:ID-DOI']]

    counter = 0
    counter_arthro = 0
    
    treatment_files = [f for f in glob.glob(os.path.join(xml_dir, "*"))]

    if not os.path.exists(out_dir_xml):
        os.makedirs(out_dir_xml)

    for treatment_file in treatment_files:
        counter += 1
        if counter % 10000 == 0: logger.debug(f'Counter: {counter:_>10}')

        if is_arthropod(treatment_file):
            counter_arthro += 1
            if counter_arthro % 10000 == 0: logger.debug(f'Arthropod counter: {counter_arthro:_>10}')
            treatment_file_name = treatment_file.split('/')[-1]
            copyfile(treatment_file, os.path.join(out_dir_xml, treatment_file_name))

            doi_infos.append(get_dois(treatment_file))

    logger.info(f'Writing Plazi plaziID - IDDOI csv ...')
    with open(out_file_ids, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(doi_infos)

    logger.info(f'Done.')

# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("../../logs/extract_arthro_treatments.log", rotation="1 MB")
    logger.info(f'Start ...')

    # Run main
    main()

