# vim: syntax=python tabstop=2 expandtab
# coding: utf-8

rule get_col:
  output:
    '../results/col.done'
  shell:
    """
    touch {output}
    """
