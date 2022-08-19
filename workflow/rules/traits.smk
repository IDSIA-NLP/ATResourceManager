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
rule plazi_extract_arthro_treatments_and_doi:
  input:
    config['plazi_xml_dir']
  output:
    xml = directory(config['plazi_arthro_txt_dir']),
    csv = config['plazi_arthro_id_doi']
  log:
    out = '../log/plazi_extract_arthro_treatments_and_doi.log'
  benchmark:
    '../log/plazi_extract_arthro_treatments_and_doi.prf'
  shell:
    """
    python scripts/plazi_extract_arthro_treatments_and_doi.py \
      --xml-dir {input} \
      --out-dir-xml {output.xml} \
      --out-file-ids {output.csv} \
    1>{log.out} 2>&1
    """

# Convert PLAZI treatment XML to text
rule plazi_xml_to_txt:
  input:
    config['plazi_arthro_xml_dir']
  output:
    directory(config['plazi_arthro_txt_dir'])
  log:
    out = '../log/plazi_xml_to_txt.log'
  benchmark:
    '../log/plazi_xml_to_txt.prf'
  shell:
    """
    python scripts/plazi_treatment_to_text.py \
      --xml-dir {input} \
      --out-dir {output} \
    1>{log.out} 2>&1
    """

# Download PMC articles
rule plazi_download_pmc:
  input:
    csv = config['plazi_arthro_id_doi']
  output:
    d2p = config['plazi_arthro_doi_pmid_map'],
    csv = config['plazi_arthro_doi_pmid'],
    xml = directory(config['plazi_arthro_pmc_xml'])
  log:
    out = '../log/plazi_download_pmc.log'
  benchmark:
    '../log/plazi_download_pmc.prf'
  shell:
    """
    python scripts/plazi_download_pmc_articles.py \
      --in-file-csv {input.csv} \
      --out-file-pmid {output.d2p} \
      --out-file-doi-pmid {output.csv} \
      --out-dir-xml {output.xml} \
      --doi-2-pmid \
      --batch-size 200 \
    1>{log.out} 2>&1
    """

# Convert PMC article XML to text
rule plazi_pmc_xml_to_txt:
  input:
    config['plazi_arthro_pmc_xml']
  output:
    directory(config['plazi_pmc_txt_dir'])
  params:
    out_dir_root=config['plazi_root_dir']
  log:
    out = '../log/plazi_pmc_xml_to_txt.log'
  benchmark:
    '../log/plazi_pmc_xml_to_txt.prf'
  shell:
    """
    python scripts/plazi_pmc_xml_to_text.py \
      --in-dir-xml {input} \
      --out-dir-root {params.out_dir_root} \
    1>{log.out} 2>&1
    """
