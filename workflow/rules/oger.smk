# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Create OGER terminologies from taxa and trait files.
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-08-31
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Dummy rule to run all the rules.
rule oger_all:
  input:
    config['oger_term_arthro_col'],
    config['oger_term_arthro_eol'],
    config['oger_term_feeding'],
    config['oger_term_habitat'],
    config['oger_term_morph'],
    config['oger_term_eol']
  output:
    '../results/oger.done',
  shell:
    """
    touch {output}
    """

# create OGER terminology for CoL arthropods
rule oger_term_arthro:
  input:
    taxa = config['oger_input_arthro_col'],
    stop = config['oger_stopwords_file']
  output:
    config['oger_term_arthro_col']
  log:
    '../log/oger_term_arthro.log'
  benchmark:
    '../log/oger_term_arthro.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.taxa} \
        --stopwords-file {input.stop} \
        --out-file {output} \
        --terminology arthro \
    >{log} 2>&1
    """

# create OGER terminology for EOL arthropods
rule oger_term_arthro_eol:
  input:
    taxa = config['oger_input_arthro_eol'],
    stop = config['oger_stopwords_file']
  output:
    config['oger_term_arthro_eol']
  log:
    '../log/oger_term_arthro_eol.log'
  benchmark:
    '../log/oger_term_arthro_eol.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input.taxa} \
        --stopwords-file {input.stop} \
        --out-file {output} \
        --terminology arthro_eol \
    >{log} 2>&1
    """

# create OGER terminology for 'feeding' trait
rule oger_term_feeding:
  input:
    config['oger_input_feeding']
  output:
    config['oger_term_feeding']
  log:
    '../log/oger_term_feeding.log'
  benchmark:
    '../log/oger_term_feeding.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input} \
        --out-file {output} \
        --terminology trait_feeding \
    >{log} 2>&1
    """

# create OGER terminology for 'habitat' trait
rule oger_term_habitat:
  input:
    config['oger_input_habitat']
  output:
    config['oger_term_habitat']
  log:
    '../log/oger_term_habitat.log'
  benchmark:
    '../log/oger_term_habitat.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input} \
        --out-file {output} \
        --terminology trait_habitat \
    >{log} 2>&1
    """

# create OGER terminology for 'morphology' trait
rule oger_term_morph:
  input:
    config['oger_input_morph']
  output:
    config['oger_term_morph']
  log:
    '../log/oger_term_morph.log'
  benchmark:
    '../log/oger_term_morph.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input} \
        --out-file {output} \
        --terminology trait_morph \
    >{log} 2>&1
    """

# create OGER terminology for EOL traits
rule oger_term_eol:
  input:
    config['oger_input_eol']
  output:
    config['oger_term_eol']
  log:
    '../log/oger_term_eol.log'
  benchmark:
    '../log/oger_term_eol.prf'
  shell:
    """
    set -x
    python scripts/oger_make_terminology.py \
        --in-file {input} \
        --out-file {output} \
        --terminology trait_eol \
    >{log} 2>&1
    """
