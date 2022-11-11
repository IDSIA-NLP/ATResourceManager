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
    config['col_eol_taxa'],
    config['eol_taxa_arthro_file'],
    config['eol_traits_arthro_file'],
    config['eol_terms_arthro_file'],
    config['eol_traits_arthro_rel_file']
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
    '../log/col_get_data.log'
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
    if [[ -f "{params.dl_dir}/*.new" ]]; then
      for f_new in $(ls {params.dl_dir}/*.new || true); do
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
    fi
    ) >{log} 2>&1
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
    '../log/eol_get_data.log'
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
    ) >{log} 2>&1
    """

# Parse Catalogue of Life (CoL) taxa file and extract descendents of Arthropoda
rule col_taxa_extract_arthropods:
  input:
    col = config['col_taxa_file']
  output:
    tax_art = config['col_taxa_arthropoda']
  log:
    '../log/col_taxa_extract_arthropods.log'
  benchmark:
    '../log/col_taxa_extract_arthropods.prf'
  shell:
    """
    set -x
    (
      python scripts/col_extract_arthropods.py \
        --col-file {input.col} \
        --out-file {output.tax_art}
    ) >{log} 2>&1
    """

# Parse Encyclopedia of Life (EOL) taxa, traits and relationships and extract descendents of Arthropoda
rule eol_taxa_traits_extract_arthropods:
  input:
    taxa = config['eol_taxa_file'],
    traits = config['eol_traits_file'],
    terms = config['eol_terms_file']
  output:
    taxa = config['eol_taxa_arthro_file'],
    traits = config['eol_traits_arthro_file'],
    terms = config['eol_terms_arthro_file'],
    rel = config['eol_traits_arthro_rel_file']
  log:
    '../log/eol_taxa_traits_extract_arthropods.log'
  benchmark:
    '../log/eol_taxa_traits_extract_arthropods.prf'
  shell:
    """
    set -x
    python scripts/eol_extract_arthro_and_traits.py \
      --pages {input.taxa} \
      --traits {input.traits} \
      --terms {input.terms} \
      --pages-arthro {output.taxa} \
      --traits-arthro {output.traits} \
      --terms-arthro {output.terms} \
      --trait-arthro-rel {output.rel} \
    >{log} 2>&1
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
