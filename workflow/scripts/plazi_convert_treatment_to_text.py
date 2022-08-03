#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Convert the XML Treatments to plain text files
Author: Joseph Cornelius
July 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
import glob
import os
from lxml import etree
from loguru import logger
import json

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------

def main(logger, args):
    """Collecting stats about the arthropod treatment .xml files.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    logger.info(f'Start extracting arthropod treatment text...')
    
    counter = 0
    
    # stats_tags = {}
    # stats_attrib = {}

    if not os.path.exists(args.out_path):
        os.makedirs(args.out_path)
    
    treatment_files = [ f for f in glob.glob(args.data_path + "*")]
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
            out_file_path = f"{args.out_path}{file_name}.txt"
            with open(out_file_path, "w") as out_file:
                out_file.write(treatment_text)
        except Exception as e:
            logger.debug(e)
            pass



# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("../../logs/extract_treatments_text.log", rotation="1 MB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Application description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-d', '--data_path', metavar='data_path', type=str, required=False, 
                        default='../../data/plazi/plazi_arthro.xml/', help='Path to all .xml treatments files.')
    parser.add_argument('-ot', '--out_path', metavar='out_path', type=str, required=False, 
                        default='../../data/plazi/plazi_arthro_text/', 
                        help='Output path for arthropods treatments text files.')
    args = parser.parse_args()

   # Run main
    main(logger, args)

    logger.info(f'Done.')