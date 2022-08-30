# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Convert gold standard annotations (manually curated).
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-08-24
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Dummy rule to run sub-workflow
rule anno_all:
  input:
    config['anno_out_dir']
  output:
    '../results/annotations.done',
  shell:
    """
    touch {output}
    """

rule anno_convert:
  input:
    ann = config['anno_members_dir'],
    lgd = config['anno_legend_file'],
    htm = config['anno_html_dir']
  output:
    directory(config['anno_out_dir'])
  log:
    '../log/anno_convert.log'
  benchmark:
    '../log/anno_convert.prf'
  shell:
    """
    python scripts/annotations_create_eval_dataset.py \
      --in-dir-anno {input.ann} \
      --in-file-legend {input.lgd} \
      --in-dir-html {input.htm} \
      --out-dir {output} \
    1>{log} 2>&1
    """
