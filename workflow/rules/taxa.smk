# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Download and transform resources from
#   Catalogue of Life (CoL)
#     data: https://download.checklistbank.org/col/
#     web:  https://www.catalogueoflife.org/
#   Encyclopedia of Life (EOL)
#     data: https://editors.eol.org/other_files/SDR/traits_all.zip
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-08-03
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Dummy rule to run all other rules
rule all_taxa:
  input:
    config['col_eol_taxa.tsv']
  output:
    '../results/taxa.done'
  shell:
    """
    touch {output}
    """

# Download latest Catalogue of Life (CoL) data files
rule get_col:
  input:
    config['col_version_file']
  output:
    col_taxa = config['col_taxa_file']
  params:
    data_dir = config['col_data_dir']
  log:
    out = '../log/get_col.out',
    err = '../log/get_col.err'
  shell:
    """
    set -x
    time (
    python scripts/col_download_latest_dwca.py \
      --log ../log/col_download_latest_dwca.log \
      --version-file {input}
      --out-dir {params.data_dir}
    touch {output}
    ) >{log.out} 2>{log.err}
    """

# Download latest Encyclopedia of Life (EOL) data files
rule get_col:
  input:
    config['col_taxa_file'],
    config['col_taxa_arthropoda']
  output:
    col_taxa = config['col_taxa_file']
  shell:
    """
    touch {output}
    """

# Parse Catalogue of Life (CoL) taxa file and extract descents of Arthropoda
rule col_taxa_extract_arthropods:
  input:
    col = config['col_taxa_file']
  output:
    tax_art = config['col_taxa_arthropoda']
  log:
    '../log/col_taxa_extract_arthropods.log'
  shell:
    """
    set -x
    time (
      python scripts/extract_col.py --log {log} \
        --col-file {input.col} \
        --out-file {output.tax_art} \
        --out-file-sm {output.tax_art_sm}
    )
    """

# Merge CoL and EOL taxa
rule col_eol_merge_taxa:
  input:
    tax_col = config['col_taxa_arthropoda'],
    tax_eol = config['eol_taxa_file']
  output:
    tax_col_eol = '../resources/col_eol_taxa.tsv'
  log:
    '../log/col_eol_merge_taxa.log'
  shell:
    """
    set -x
    time (
    python scripts/col_eol_merge.py \
      --log {log} \
      --col-taxa {input.tax_col} \
      --eol-taxa {input.tax_eol} \
      --out-file {output.tax_col_eol}
    )
    """
