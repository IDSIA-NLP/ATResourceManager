#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: syntax=python tabstop=4 expandtab

"""
Description: Convert the downloaded PMC .xml files to plain text
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
from loguru import logger
from lxml import etree as et
import re 
import csv
import os

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------

@click.command()
@click.option('--in-dir-xml', '-i', required=True, help='Path to single .xml files.')
@click.option('--out-dir-root', '-o', required=True, help='Path to create output dirs for text articles.')
@click.option('--formatted', '-f', is_flag=True, help='Use format from the XML and DO NOT remove tabs and new lines')
def main(in_dir_xml, out_dir_root, formatted):
    """Extract <body> text from PMC .xml articles and writes text to .csv file."""

    # Setup logger
    #logger.add("../../logs/pmc_xml_to_text.log", rotation="20 MB")
    logger.info(f'Start ...')
    logger.info(f'Start extracting text from articles ...')
    
    if not os.path.exists(out_dir_root):
        os.makedirs(out_dir_root)
    
    counter = 0
    lines = []

    pmc_articles = [ f for f in glob.glob(os.path.join(in_dir_xml, "*.xml"))]
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
            if formatted:
                abstract = "".join(abstract)
            else:
                # Remove newlines, tabs and multiple whitespaces
                abstract = [t.strip() for t in abstract if t != '\n']
                abstract = " ".join(abstract)
                abstract = re.sub(r"\s\s+", " ", abstract) 
                abstract = abstract.strip()

            # Get text of the body tag
            body_text = tree.xpath('//body//text()')
            if formatted:
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
    if formatted:
        out_dir_txt_fmt = os.path.join(out_dir_root, 'pmc_txt_formatted')
        if not os.path.exists(out_dir_txt_fmt):
            os.makedirs(out_dir_txt_fmt)
    
        for pmc_id, text in lines:
            out_file_txt_fmt = os.path.join(out_dir_txt_fmt, f'{pmc_id}.txt')
            with open(out_file_txt_fmt, "w", encoding='utf-8', newline='') as f:
                f.write(text)
    else:
        out_dir_txt = os.path.join(out_dir_root, 'pmc_txt')
        if not os.path.exists(out_dir_txt):
            os.makedirs(out_dir_txt)

        for pmc_id, text in lines:
            out_file_txt = os.path.join(out_dir_txt, f'{pmc_id}.txt')
            with open(out_file_txt, "w", encoding='utf-8', newline='') as f:
                f.write(text)

    logger.info(f'Done.')


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # Run main
    main()

