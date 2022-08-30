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

# create OGER terminology for arthropods
rule oger_term_arthro:
  input:
    tax = config['col_eol_taxa_file']
  output:
    trm = config['oger_term_arthro']
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
