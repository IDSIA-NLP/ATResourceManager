#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: syntax=python tabstop=4 expandtab

"""
Description: Convert the XML Treatments to plain text files
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
import os
from lxml import etree
from loguru import logger
import json

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


@click.command()
@click.option('--xml-dir', '-i', required=True, help='Path to all .xml treatments input files.')
@click.option('--out-dir', '-o', required=True, help='Output path for arthropods treatments text files.')
def main(xml_dir, out_dir):
    """Collecting stats about the arthropod treatment .xml files."""

    logger.info(f'Start ...')
    logger.info(f'Start extracting arthropod treatment text...')
    
    counter = 0
    
    # stats_tags = {}
    # stats_attrib = {}

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    treatment_files = [f for f in glob.glob(os.path.join(xml_dir, "*"))]
    for treatment_file in treatment_files:
        counter += 1
        if counter % 10000 == 0: logger.debug(f'Counter: {counter:_>10}')

        try:
            tree_l = etree.parse(treatment_file)
            treatment_text = tree_l.xpath('//treatment//text()')
            treatment_text = [elem.strip() for elem in treatment_text if elem != '\n']
            # Get the taxonomic name out of the first taxonomicName tag in the treatment tag
            taxonomic_name = tree_l.xpath('(//treatment//taxonomicName)[1]//text()')
            taxonomic_name = [elem.strip() for elem in taxonomic_name if elem != '\n']
            treatment_text = " ".join(taxonomic_name) + "\n" + " ".join(treatment_text)
            file_name = treatment_file.split('/')[-1].split('.')[0]
            out_file_path = f"{os.path.join(out_dir, file_name)}.txt"
            with open(out_file_path, "w") as out_file:
                out_file.write(treatment_text)
        except Exception as e:
            logger.debug(e)
            pass

    logger.info(f'Done.')


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

