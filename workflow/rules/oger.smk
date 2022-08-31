# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Create OGER terminologies from taxa and trait files.
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-08-30
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Dummy rule to run all the rules.
rule oger_all:
  input:
    config['oger_term_arthro']
  output:
    '../results/oger.done',
  shell:
    """
    touch {output}
    """

'arthro', 'arthro_eol', 'trait_eol', 'trait_feeding', 'trait_habitat', 'trait_morph'

# create OGER terminology for CoL arthropods
rule oger_term_arthro:
  input:
    tax = config['col_eol_taxa_file']
  output:
    trm = config['oger_term_arthro_col']
  log:
    '../log/oger_term_arthro.log'
  benchmark:
    '../log/oger_term_arthro.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.tax} \
        --out-file {output.trm} \
        --terminology arthro \
    \ >{log} 2>&1
    """

# create OGER terminology for EOL arthropods
rule oger_term_arthro_eol:
  input:
    # '../../data/latest_dwca/Taxon_arthro_eol_wikidata_sm.tsv'
    tax = config['col_eol_taxa_file']
  output:
    trm = config['oger_term_arthro_eol']
  log:
    '../log/oger_term_arthro_eol.log'
  benchmark:
    '../log/oger_term_arthro_eol.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.tax} \
        --out-file {output.trm} \
        --terminology arthro_eol \
    \ >{log} 2>&1
    """

# create OGER terminology for 'feeding' trait
rule oger_term_feeding:
  input:
    tax = config['col_eol_taxa_file']
  output:
    trm = config['oger_term_feeding']
  log:
    '../log/oger_term_feeding.log'
  benchmark:
    '../log/oger_term_feeding.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.tax} \
        --out-file {output.trm} \
        --terminology trait_feeding \
    \ >{log} 2>&1
    """

# create OGER terminology for 'habitat' trait
rule oger_term_habitat:
  input:
    tax = config['col_eol_taxa_file']
  output:
    trm = config['oger_term_habitat']
  log:
    '../log/oger_term_habitat.log'
  benchmark:
    '../log/oger_term_habitat.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.tax} \
        --out-file {output.trm} \
        --terminology trait_habitat \
    \ >{log} 2>&1
    """

# create OGER terminology for 'morphology' trait
rule oger_term_morph:
  input:
    tax = config['col_eol_taxa_file']
  output:
    trm = config['oger_term_morph']
  log:
    '../log/oger_term_morph.log'
  benchmark:
    '../log/oger_term_morph.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.tax} \
        --out-file {output.trm} \
        --terminology trait_morph \
    \ >{log} 2>&1
    """

# create OGER terminology for EOL traits
rule oger_term_eol:
  input:
    tax = config['col_eol_taxa_file']
  output:
    trm = config['oger_term_eol']
  log:
    '../log/oger_term_eol.log'
  benchmark:
    '../log/oger_term_eol.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.tax} \
        --out-file {output.trm} \
        --terminology trait_eol \
    \ >{log} 2>&1
    """
