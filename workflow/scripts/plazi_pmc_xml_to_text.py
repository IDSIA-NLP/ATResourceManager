#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Convert the downloaded PMC .xml files to plain text
Author: Joseph Cornelius
August 2022
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
import glob
from loguru import logger
from lxml import etree as et
import re 
import csv
import os

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------

def main(logger, args):
    """Extract <body> text from PMC .xml articles and writes text to .csv file.

    Args:
        logger (logger instance): Instance of the loguru logger
        args (argparser object): Object of the argument parser 

    Returns:
        None
    """

    logger.info(f'Start extracting text from articles ...')
    
    if not os.path.exists(args.out_path):
        os.makedirs(args.out_path)
    
    counter = 0
    lines = []

    pmc_articles = [ f for f in glob.glob(args.data_path + "*.xml")]
    for pmc_article in pmc_articles:
        counter += 1
        if counter % 100 == 0: logger.debug(f'Counter: {counter:_>4}')

        try:
            tree = et.parse(pmc_article)

            # Get the PMC-ID
            for pmc_id in tree.xpath("//article-id[@pub-id-type=\'pmc\']"):
                pmc_id = f'PMC{pmc_id.text}'

            # Remove all tables from the bodu
            for table in tree.xpath("//table-wrap"):
                table.getparent().remove(table) 

            # Get text of the body tag
            abstract = tree.xpath('//abstract//text()')
            if args.formatted:
                abstract = "".join(abstract)
            else:
                # Remove newlines, tabs and multiple whitespaces
                abstract = [t.strip() for t in abstract if t != '\n']
                abstract = " ".join(abstract)
                abstract = re.sub(r"\s\s+", " ", abstract) 
                abstract = abstract.strip()

            # Get text of the body tag
            body_text = tree.xpath('//body//text()')
            if args.formatted:
                body_text = "".join(body_text)
            else:
                # Remove newlines, tabs and multiple whitespaces
                body_text = [t.strip() for t in body_text if t != '\n']
                body_text = " ".join(body_text)
                body_text = re.sub(r"\s\s+", " ", body_text) 
                body_text = body_text.strip()
            

            text = abstract + " " + body_text

            lines.append([pmc_id, text])

        except Exception as e:
            logger.debug(e)
            pass


    logger.info(f'Write text articles to file...')
    if args.formatted:
        if not os.path.exists(args.out_path+'pmc_txt_formatted/'):
            os.makedirs(args.out_path+'pmc_txt_formatted/')
    
        for pmc_id, text in lines:
            with open(args.out_path+f'pmc_txt_formatted/{pmc_id}.txt', "w", encoding='utf-8', newline='') as f:
                f.write(text)
    else:

        if not os.path.exists(args.out_path+'pmc_txt/'):
            os.makedirs(args.out_path+'pmc_txt/')

        for pmc_id, text in lines:
            with open(args.out_path+f'pmc_txt/{pmc_id}.txt', "w", encoding='utf-8', newline='') as f:
                f.write(text)

            


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("../../logs/pmc_xml_to_text.log", rotation="20 MB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Application description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-d', '--data_path', metavar='data_path', type=str, required=False, 
                        default='../../data/plazi/pmc/pmc_xml/', help='Path to single .xml files.')
    parser.add_argument('-o', '--out_path', metavar='out_path', type=str, required=False, 
                        default='../../data/plazi/pmc/', 
                        help='Output path to text articles.')
    parser.add_argument('-f', '--formatted', metavar='formatted', type=bool, required=False, 
                        default=False, 
                        help='Use format from the XML and DO NOT remove tabs and new lines')
    args = parser.parse_args()

   # Run main
    main(logger, args)

    logger.info(f'Done.')