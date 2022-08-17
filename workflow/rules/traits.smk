# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Download and transform resources from
#   PLAZI treatment bank
#     web:  http://plazi.org/treatmentbank/
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-08-17
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Dummy rule to run all other rules
rule all_traits:
  input:
    #config['col_eol_taxa']
  output:
    '../results/traits.done'
  shell:
    """
    touch {output}
    """

# TODO: download treatment XML files (>400k) from PLAZI

# Convert PLAZI treatment XML to text
rule plazi_xml_to_txt:
  input:
    config['plazi_trait_xml_dir']
  output:
    directory(config['plazi_trait_txt_dir'])
  log:
    out = '../log/plazi_xml_to_txt.out'
  benchmark:
    '../log/plazi_xml_to_txt.prf'
  shell:
    """
    python scripts/plazi_treatment_to_text.py \
      --xml-dir {input} \
      --out-dir {output} \
    1>{log.out} 2>&1
    """
