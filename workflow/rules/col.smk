# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Download and transform Catalogue of Life (CoL) resources.
#     data: https://download.checklistbank.org/col/
#     web:  https://www.catalogueoflife.org/
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-07-26
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Download latest Catalogue of Life (CoL) data files
# TODO: implement caching to prevent unnecessary downloading
rule get_col:
  output:
    config['col_taxa_file_path']
  shell:
    """
    touch {output}
    """

# Parse Catalogue of Life (CoL) taxa file and extract descents of Arthropoda
rule col_taxa_extract_arthropods:
  input:
    col = config['col_taxa_file_path']
  output:
    tax_art = config['col_taxa_arthropoda'],
    tax_art_sm = config['col_taxa_arthropoda_sm'],
  log:
    '../log/col_taxa_extract_arthropods.log'
  shell:
    """
    set -x
    time (
      python scripts/extract_col.py --log {log} \
        {input.col} \
        {output.tax_art} \
        {output.tax_art_sm}
    )
    """
