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
# modified : 2022-08-06
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Dummy rule to run all other rules
rule all_taxa:
  input:
    config['col_eol_taxa']
  output:
    '../results/taxa.done'
  shell:
    """
    touch {output}
    """

# Download latest Catalogue of Life (CoL) data files
rule col_get_data:
  input:
    config['col_version_file']
  output:
    col_taxa = config['col_taxa_file']
  params:
    data_dir = config['col_data_dir'],
    dl_dir = f"{config['col_data_dir']}/.."
  log:
    out = '../log/col_get_data.out',
    err = '../log/col_get_data.err'
  benchmark:
    '../log/col_get_data.prf'
  shell:
    """
    set -x
    (
    # download data file
    python scripts/col_download_latest_dwca.py \
      --version-file {input} \
      --out-dir {params.dl_dir}

    # check for sentinel file
    for f_new in $(ls {params.dl_dir}/*.new); do
      echo "Found sentinel file: $f_new"
      f_data=${{f_new%.new}}

      # clear or create data directory
      if [[ -d {params.data_dir} ]]; then
        rm -rf {params.data_dir}/*
      else
        mkdir {params.data_dir}
      fi

      # unzip data files
      unzip $f_data -d {params.data_dir}

      # clean up
      rm $f_new $f_data
      break
    done
    ) >{log.out} 2>{log.err}
    """

# Download latest Encyclopedia of Life (EOL) data files
rule eol_get_data:
  input:
    config['eol_version_file']
  output:
    eol_taxa = config['eol_taxa_file']
  params:
    data_dir = config['eol_data_dir']
  log:
    out = '../log/eol_get_data.out',
    err = '../log/eol_get_data.err'
  benchmark:
    '../log/eol_get_data.prf'
  shell:
    """
    (
    # clear or create data directory
    if [[ -d {params.data_dir} ]]; then
      rm -rf {params.data_dir}/*
    else
      mkdir {params.data_dir}
    fi

    # download data file
    python scripts/eol_download_latest_traits.py \
      --version-file {input} \
      --out-dir {params.data_dir}/../

    # unzip data files
    unzip {params.data_dir}/../traits_all.zip -d {params.data_dir}/..
    ) >{log.out} 2>{log.err}
    """

# Parse Catalogue of Life (CoL) taxa file and extract descents of Arthropoda
rule col_taxa_extract_arthropods:
  input:
    col = config['col_taxa_file']
  output:
    tax_art = config['col_taxa_arthropoda']
  log:
    out = '../log/col_taxa_extract_arthropods.out',
    err = '../log/col_taxa_extract_arthropods.err'
  benchmark:
    '../log/col_taxa_extract_arthropods.prf'
  shell:
    """
    set -x
    (
      python scripts/col_extract_arthropods.py \
        --col-file {input.col} \
        --out-file {output.tax_art}
    ) >{log.out} 2>{log.err}
    """

# Merge CoL and EOL taxa
rule col_eol_merge_taxa:
  input:
    tax_col = config['col_taxa_arthropoda'],
    tax_eol = config['eol_taxa_file']
  output:
    tax_col_eol = config['col_eol_taxa']
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
